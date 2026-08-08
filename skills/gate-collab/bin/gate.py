#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gate — 让两个 AI（一个写、一个审）在各自窗口里"隔空留言"协作的小工具。

设计来源：YouTube《Claude Code 写、Codex 审：不用复制粘贴》中作者自制的 gate。
本实现为功能等同的本地复刻，纯 Python 标准库，无第三方依赖。

核心思路
- 留言存在项目下独立的 .gate/ 目录里（自带 git 仓库），不进主仓库历史、不推远端。
- 每个频道由第一条消息自动创建，消息按 M0001、M0002… 自动编号，只能往后追加。
- 消息记录发言者、回复对象（reply_to）、当时主仓库的提交号，回复关系用缩进展示。
- 三种关键消息：handoff（交活）/ review（挑错）/ fixed（处理完）。
  fixed 回复 review 时，自动关闭那条风险；全部关闭 = Review Risk Down。

用法
  gate init [--author 名字]            # 初始化 .gate/ 并写入 .gitignore
  gate send <频道> <内容> [--type 类型] [--reply M0001] [--author 名字]
  gate chat <频道>                     # 看群（带线程缩进）
  gate list                            # 列出所有频道
  gate status <频道>                    # 风险统计，全部关闭才退出码 0
  gate review-risk-down <频道>          # status 的别名（对应视频里的 Review Risk Down）
  gate pr-summary <频道>                # 生成可直接贴进 PR 描述的中文 markdown
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path

GATE_DIR_NAME = ".gate"
CHANNELS_DIR = "channels"
CONFIG_FILE = "config.json"
LOCK_FILE = ".lock"

# 中文别名 -> 内部类型
TYPE_ALIASES = {
    "交活": "handoff",
    "挑错": "review",
    "处理完": "fixed",
    "风险": "review",
}
VALID_TYPES = ("note", "handoff", "review", "fixed")


# ---------------------------------------------------------------- 基础工具

def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def find_gate_dir(start: Path | None = None) -> Path | None:
    """从当前目录向上找 .gate/。"""
    cur = (start or Path.cwd()).resolve()
    for d in [cur, *cur.parents]:
        if (d / GATE_DIR_NAME).is_dir():
            return d / GATE_DIR_NAME
    return None


def ensure_gate_dir(start: Path | None = None) -> Path:
    """找不到就自动初始化（对应视频里'发第一句话群就有了'）。"""
    gate = find_gate_dir(start)
    if gate:
        return gate
    root = (start or Path.cwd()).resolve()
    gate = root / GATE_DIR_NAME
    gate.mkdir(parents=True, exist_ok=True)
    (gate / CHANNELS_DIR).mkdir(exist_ok=True)
    git_init(gate)
    append_gitignore(root, GATE_DIR_NAME)
    log(f"[gate] 已自动初始化 {gate}")
    return gate


def run(cmd: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=30
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        log(f"[gate] 提示: 无法执行 {cmd[0]}（{e}），已跳过")
        return subprocess.CompletedProcess(cmd, 1, "", "")


def git_init(gate: Path) -> None:
    if not (gate / ".git").exists():
        run(["git", "init", "-q"], cwd=gate)
    # 给独立仓库配置本地身份，避免提交失败
    for key, val in (("user.name", "gate"), ("user.email", "gate@local")):
        out = run(["git", "config", "--local", key], cwd=gate)
        if out.returncode != 0 or not out.stdout.strip():
            run(["git", "config", "--local", key, val], cwd=gate)


def git_commit(gate: Path, msg: str) -> None:
    """每条消息追加后自动提交进 .gate 独立仓库，形成不可篡改的对话历史。"""
    if not (gate / ".git").exists():
        return
    run(["git", "add", "-A"], cwd=gate)
    run(["git", "commit", "-q", "-m", msg], cwd=gate)


def append_gitignore(root: Path, line: str) -> None:
    gi = root / ".gitignore"
    if gi.exists() and line in gi.read_text(encoding="utf-8").splitlines():
        return
    with gi.open("a", encoding="utf-8") as f:
        if gi.exists() and gi.stat().st_size and not gi.read_text(encoding="utf-8").endswith("\n"):
            f.write("\n")
        f.write(f"{line}\n")
    log(f"[gate] 已把 `{line}/` 写入 {gi}（留言不进主仓库历史）")


def project_commit(start: Path | None = None) -> str:
    """记录发消息时主仓库的提交号，让每条留言绑到当时的代码状态。"""
    out = run(["git", "rev-parse", "--short", "HEAD"], cwd=(start or Path.cwd()))
    if out.returncode == 0 and out.stdout.strip():
        return out.stdout.strip()
    return "-"


def config_path(gate: Path) -> Path:
    return gate / CONFIG_FILE


def load_config(gate: Path) -> dict:
    p = config_path(gate)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_config(gate: Path, cfg: dict) -> None:
    config_path(gate).write_text(
        json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def resolve_author(gate: Path | None, flag: str | None) -> str:
    if flag:
        return flag
    env = os.environ.get("GATE_AUTHOR")
    if env:
        return env
    if gate:
        cfg = load_config(gate)
        if cfg.get("author"):
            return cfg["author"]
    out = run(["git", "config", "user.name"])
    if out.returncode == 0 and out.stdout.strip():
        return out.stdout.strip()
    return "anonymous"


# ---------------------------------------------------------------- 频道存储

def safe_channel(channel: str) -> str:
    """频道名做安全化，作为文件名；显示名不变。"""
    return "".join(c if c.isalnum() or c in "_-." else "_" for c in channel)


def channel_file(gate: Path, channel: str) -> Path:
    return gate / CHANNELS_DIR / f"{safe_channel(channel)}.jsonl"


def load_channel(gate: Path, channel: str) -> list[dict]:
    f = channel_file(gate, channel)
    if not f.exists():
        return []
    msgs = []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            msgs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return msgs


def require_channel(gate: Path, channel: str) -> list[dict]:
    msgs = load_channel(gate, channel)
    if not msgs:
        log(f"[gate] 频道不存在：{channel}（先发第一条消息自动建群）")
        sys.exit(2)
    return msgs


def next_id(msgs: list[dict]) -> str:
    return f"M{len(msgs) + 1:04d}"


def append_message(gate: Path, channel: str, record: dict) -> str:
    """追加写入并加文件锁，避免两个 AI 同时发消息时编号撞车。"""
    f = channel_file(gate, channel)
    mid = ""
    with f.open("a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            fh.seek(0, os.SEEK_END)
            existing = load_channel(gate, channel)  # 拿到锁后再数一遍
            mid = next_id(existing)
            record = {**record, "id": mid}
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
    git_commit(gate, f"{mid} [{record['type']}] {channel} by {record['author']}")
    return mid


# ---------------------------------------------------------------- 展示

def fmt_time(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%m-%d %H:%M")
    except ValueError:
        return ts


def render_message(msg: dict, level: int) -> str:
    indent = "  " * level
    head = f"{indent}{msg['id']} [{msg['type']}] {msg['author']}"
    if msg.get("reply_to"):
        head += f" → {msg['reply_to']}"
    head += f" · {fmt_time(msg['ts'])}"
    if msg.get("commit") and msg["commit"] != "-":
        head += f" · @{msg['commit']}"
    body = msg.get("message", "")
    body_indent = "  " * (level + 1)
    lines = [head]
    for line in body.splitlines() or [""]:
        lines.append(f"{body_indent}{line}")
    return "\n".join(lines)


def build_tree(msgs: list[dict]) -> list[tuple[int, dict]]:
    """按 reply_to 构建线程树，返回 [(层级, 消息)]。"""
    by_id = {m["id"]: m for m in msgs}
    children: dict[str, list[dict]] = {}
    roots: list[dict] = []
    for m in msgs:
        parent = m.get("reply_to")
        if parent and parent in by_id:
            children.setdefault(parent, []).append(m)
        else:
            roots.append(m)

    out: list[tuple[int, dict]] = []

    def walk(node: dict, level: int) -> None:
        out.append((level, node))
        for kid in children.get(node["id"], []):
            walk(kid, level + 1)

    for r in roots:
        walk(r, 0)
    return out


def open_risks(msgs: list[dict]) -> list[dict]:
    """未关闭风险 = 还没被 fixed 直接回复的 review 消息。"""
    review_ids = {m["id"] for m in msgs if m.get("type") == "review"}
    fixed_parents = {m.get("reply_to") for m in msgs if m.get("type") == "fixed"}
    return [m for m in msgs if m.get("type") == "review" and m["id"] not in fixed_parents]


# ---------------------------------------------------------------- 命令

def cmd_init(args: argparse.Namespace) -> None:
    root = Path.cwd().resolve()
    gate = root / GATE_DIR_NAME
    gate.mkdir(parents=True, exist_ok=True)
    (gate / CHANNELS_DIR).mkdir(exist_ok=True)
    git_init(gate)
    append_gitignore(root, GATE_DIR_NAME)
    if args.author:
        cfg = load_config(gate)
        cfg["author"] = args.author
        save_config(gate, cfg)
    print(f"[gate] 已初始化 {gate}")
    print("[gate] 现在可以发第一条消息了：")
    print(f'  gate send "频道名" "内容" --type handoff --author {args.author or "<你的名字>"}')


def cmd_send(args: argparse.Namespace) -> None:
    gate = ensure_gate_dir()
    if args.message:
        content = args.message
    else:
        content = sys.stdin.read().strip()
    if not content:
        log("[gate] 没有内容：请直接传消息，或用管道喂 stdin")
        sys.exit(2)

    mtype = TYPE_ALIASES.get(args.type, args.type)
    if mtype not in VALID_TYPES:
        log(f"[gate] 类型必须是 {VALID_TYPES}（或中文 交活/挑错/处理完），收到：{args.type}")
        sys.exit(2)

    existing = load_channel(gate, args.channel)
    reply_to = args.reply
    if reply_to:
        if reply_to not in {m["id"] for m in existing}:
            log(f"[gate] 回复对象不存在：{reply_to}（当前频道只有 {len(existing)} 条消息）")
            sys.exit(2)
        # 提醒：fixed 应只回复 review，且一条 review 一条 fixed
        if mtype == "fixed":
            parent = next((m for m in existing if m["id"] == reply_to), None)
            if parent and parent.get("type") != "review":
                log(f"[gate] 警告：{reply_to} 不是挑错消息，fixed 不会关闭任何风险")

    record = {
        "author": resolve_author(gate, args.author),
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "type": mtype,
        "reply_to": reply_to,
        "commit": project_commit(),
        "message": content,
    }
    mid = append_message(gate, args.channel, record)
    print(f"[gate] 已发送 {mid} → #{args.channel}")


def cmd_chat(args: argparse.Namespace) -> None:
    gate = find_gate_dir()
    if not gate:
        log("[gate] 还没初始化：先 gate init，或直接发第一条消息")
        sys.exit(2)
    msgs = require_channel(gate, args.channel)
    print(f"# {args.channel}（共 {len(msgs)} 条）")
    for level, m in build_tree(msgs):
        print(render_message(m, level))
    print()
    risks = open_risks(msgs)
    if risks:
        print(f"❌ 还有 {len(risks)} 条风险未关闭：{', '.join(m['id'] for m in risks)}")
    else:
        print("✅ 全部风险已关闭")


def cmd_list(args: argparse.Namespace) -> None:
    gate = find_gate_dir()
    if not gate:
        print("[gate] 还没有任何频道（尚未初始化）")
        return
    for f in sorted((gate / CHANNELS_DIR).glob("*.jsonl")):
        n = len([l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()])
        risks = open_risks(load_channel(gate, f.stem))
        flag = f"❌ {len(risks)}" if risks else "✅"
        print(f"{flag}  {f.stem:20s} {n:3d} 条")


def cmd_status(args: argparse.Namespace) -> None:
    gate = find_gate_dir()
    if not gate:
        sys.exit(2)
    msgs = require_channel(gate, args.channel)
    reviews = [m for m in msgs if m.get("type") == "review"]
    fixes = [m for m in msgs if m.get("type") == "fixed"]
    risks = open_risks(msgs)
    print(f"# {args.channel}")
    print(f"消息 {len(msgs)} 条 | 交活 {sum(1 for m in msgs if m['type']=='handoff')} | "
          f"挑错 {len(reviews)} | 处理完 {len(fixes)} | 未关闭 {len(risks)}")
    if risks:
        print(f"❌ Review Risk DOWN：还有 {len(risks)} 条未处理")
        for m in risks:
            first = (m.get("message") or "").splitlines()[0][:60]
            print(f"   {m['id']} ({m['author']}): {first}")
        sys.exit(1)
    print("✅ Review Risk Down：全部风险已关闭")


def cmd_pr_summary(args: argparse.Namespace) -> None:
    gate = find_gate_dir()
    if not gate:
        sys.exit(2)
    msgs = require_channel(gate, args.channel)
    reviews = [m for m in msgs if m.get("type") == "review"]
    fixes = [m for m in msgs if m.get("type") == "fixed"]
    handoffs = [m for m in msgs if m.get("type") == "handoff"]
    risks = open_risks(msgs)

    commits = sorted({m["commit"] for m in msgs if m.get("commit") and m["commit"] != "-"})

    lines: list[str] = []
    lines.append(f"# PR 摘要：{args.channel}")
    lines.append("")
    lines.append(f"- 频道留言共 {len(msgs)} 条（交活 {len(handoffs)} / 挑错 {len(reviews)} / 处理完 {len(fixes)}）")
    if commits:
        lines.append(f"- 涉及主仓库提交：{', '.join('`' + c + '`' for c in commits)}")
    lines.append("")

    lines.append("## 一、做了什么")
    if handoffs:
        for h in handoffs:
            lines.append(f"- **{h['id']}**（{h['author']}）：")
            lines.append(textwrap.indent(h["message"], "  "))
    else:
        lines.append("（没有结构化交活留言）")
    lines.append("")

    lines.append("## 二、审查出了哪些问题")
    if reviews:
        for r in reviews:
            first = (r.get("message") or "").splitlines()[0]
            fixes_for = [f for f in fixes if f.get("reply_to") == r["id"]]
            if fixes_for:
                fix = fixes_for[0]
                vline = textwrap.shorten(fix["message"], width=80, placeholder="…")
                lines.append(f"- **{r['id']}**（{r['author']}）✅ 已处理 → {fix['id']}：{vline}")
            else:
                lines.append(f"- **{r['id']}**（{r['author']}）❌ **未关闭**：{first}")
        lines.append("")
    else:
        lines.append("- 审查未提出任何问题")
        lines.append("")

    lines.append("## 三、未关闭风险")
    if risks:
        for r in risks:
            first = (r.get("message") or "").splitlines()[0]
            lines.append(f"- {r['id']}（{r['author']}）：{first}")
    else:
        lines.append("- 无 ✅ 全部风险已关闭（Review Risk Down）")
    lines.append("")
    lines.append("---")
    lines.append("_由 gate 自动生成，仅供人工最终拍板参考_")
    print("\n".join(lines))


# ---------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gate",
        description="让两个 AI 一个写、一个审，通过独立留言仓库协作（不用复制粘贴）。",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="初始化 .gate/ 独立留言仓库并写 .gitignore").add_argument(
        "--author", help="默认发言者名字"
    )

    s = sub.add_parser("send", help="发一条消息（第一条消息自动建频道）")
    s.add_argument("channel")
    s.add_argument("message", nargs="?", default=None)
    s.add_argument("--type", default="note",
                   help="note / handoff(交活) / review(挑错) / fixed(处理完)")
    s.add_argument("--reply", default=None, help="回复哪条，如 M0001")
    s.add_argument("--author", default=None, help="发言者，默认取配置/环境变量/用户名")

    c = sub.add_parser("chat", help="看群（带线程缩进，回复关系一目了然）")
    c.add_argument("channel")

    sub.add_parser("list", help="列出所有频道和风险状态")

    st = sub.add_parser("status", help="风险统计；全部关闭退出码 0，否则 1")
    st.add_argument("channel")

    sub.add_parser("review-risk-down", help="status 的别名，对应 Review Risk Down").add_argument("channel")

    pr = sub.add_parser("pr-summary", help="生成可直接贴 PR 描述的中文 markdown")
    pr.add_argument("channel")

    return p


def reorder_send_argv(argv: list[str]) -> list[str]:
    """argparse 对 nargs='?' 的位置参数有个限制：消息放在选项后面会丢。

    这里把 send 的 channel/message 两个位置参数提到最前面，选项原样放后面，
    两种书写顺序都能用。长消息更推荐走 stdin。
    """
    rest = argv[1:]
    opts: list[str] = []
    positional: list[str] = []
    value_opts = {"--type", "--reply", "--author"}
    i = 0
    while i < len(rest):
        a = rest[i]
        if a in value_opts:
            opts.append(a)
            if i + 1 < len(rest):
                opts.append(rest[i + 1])
                i += 2
                continue
        elif a.startswith("-"):
            opts.append(a)
        else:
            positional.append(a)
        i += 1
    return ["send", *positional, *opts]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "send":
        argv = reorder_send_argv(argv)
    args = build_parser().parse_args(argv)
    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "send":
        cmd_send(args)
    elif args.cmd == "chat":
        cmd_chat(args)
    elif args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "review-risk-down":
        args.channel = getattr(args, "channel", None) or args.channel
        cmd_status(args)
    elif args.cmd == "pr-summary":
        cmd_pr_summary(args)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
