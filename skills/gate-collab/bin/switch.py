#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
switch —— 多 AI 协作操作台（小白友好的一键开关）

解决的问题
- 你想开"一个导演 + 几个干活/审查的 AI"，让它们隔空留言协作，不用你复制粘贴。
- 可以是多个 Codex 窗口，也可以是 Codex + Claude Code + WorkBuddy 混搭。
- 本操作台负责：建项目、装好 gate、按角色打开 AI 窗口、以及日常的看群/风险/PR 摘要。

用法（在任意目录运行）
  python3 switch.py menu                 # 打开交互菜单（默认）
  python3 switch.py new 我的项目          # 新建项目并问你要不要开窗口
  python3 switch.py start 我的项目        # 一键：新建 + 打开 导演/写手/审查 三个窗口
  python3 switch.py launch --ai codex --role writer   # 给当前项目补开一个窗口
  python3 switch.py status | chat | pr   # 当前项目的风险/群聊/PR 摘要
  python3 switch.py open /路径/到/项目    # 把一个已有 gate 项目登记进来

支持的 AI（在终端里要有对应命令；WorkBuddy 没有命令行就自动打开 App）
  codex / claude（Claude Code）/ workbuddy / 自定义命令

角色（每个角色一个提示词文件，建项目时会复制进项目 roles/ 目录）
  导演   orchestrator.md  不写代码，负责派活、盯风险、把关
  写手   writer.md        负责改代码、跑测试、交活
  审查   reviewer.md      负责挑错，默认不改代码
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STATE_DIR = Path(os.environ.get("GATE_SWITCH_HOME", str(Path.home() / ".gate-switch")))
STATE_FILE = STATE_DIR / "config.json"

ROLE_FILES = {"director": "orchestrator.md", "writer": "writer.md", "reviewer": "reviewer.md"}
ROLE_CN = {"director": "导演", "writer": "写手", "reviewer": "审查"}
AI_CN = {"codex": "Codex", "claude": "Claude Code", "workbuddy": "WorkBuddy"}
MODEL_PRESETS = {
    "codex": ["gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-5.5", "gpt-5.2", "默认"],
    "claude": ["claude-opus-4", "claude-sonnet-4", "claude-haiku-3.5", "默认"],
    "workbuddy": ["App 内选"],
}


def role_file(fname: str) -> Path:
    """优先用操作台旁的 roles/ 目录（skill 打包布局），退回同目录。"""
    cand = HERE.parent / "roles" / fname
    if cand.exists():
        return cand
    return HERE / fname

LAUNCH_PROMPT = (
    "请先阅读 roles/{role_file} 并按其中的角色开始工作。"
    "分工和模型见 roles/AI计划.md。"
    "团队通过项目里的 gate 隔空留言协作：先用 `python3 gate.py chat <频道名>` 看消息，"
    "再用 `python3 gate.py send <频道名> <内容> --author {role_cn}` 发言。\n"
    "频道名默认用项目名，第一条消息自动建群。留言只能追加不能改。"
)


def plan_entry(ai: str, model: str = "") -> dict:
    """把 'ai' 或 'ai@模型' 归一成 {"ai": ..., "model": ...}。"""
    if "@" in ai and not model:
        ai, model = ai.split("@", 1)
    if ai == "workbuddy" and not model:
        model = "App 内选"
    return {"ai": ai, "model": model or "默认"}


# ---------------------------------------------------------------- 状态存取

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"projects": {}, "current": None}


def save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def remember_project(path: Path) -> None:
    state = load_state()
    name = path.name
    state["projects"][name] = str(path)
    state["current"] = str(path)
    save_state(state)


def current_project() -> Path | None:
    state = load_state()
    cur = state.get("current")
    if cur and Path(cur).is_dir():
        return Path(cur)
    if state.get("projects"):
        last = sorted(state["projects"].values())[-1]
        return Path(last)
    return None


# ---------------------------------------------------------------- 项目创建

def copy_file(src: Path, dst: Path) -> None:
    shutil.copy2(src, dst)
    print(f"  ✓ {dst.name} → {dst.parent}")


def create_project(name: str, base_dir: str | None, ai_plan: dict, launch_now: bool,
                   dry_run: bool) -> Path:
    base = Path(base_dir or os.path.expanduser("~/Projects"))
    base.mkdir(parents=True, exist_ok=True)
    project = base / name
    if project.exists() and any(project.iterdir()):
        print(f"[switch] 目录已存在且非空：{project}")
        print("[switch] 直接复用，继续装协作工具。")
    project.mkdir(parents=True, exist_ok=True)

    # 1) git 仓库
    if not (project / ".git").exists():
        subprocess.run(["git", "init", "-q"], cwd=project)

    # 2) gate + 角色提示词（复制到项目里，保证项目自包含）
    roles_dir = project / "roles"
    roles_dir.mkdir(exist_ok=True)
    print(f"[switch] 正在把协作工具装进 {project} …")
    if not (project / "gate.py").exists():
        copy_file(HERE / "gate.py", project / "gate.py")
    for key, fname in ROLE_FILES.items():
        copy_file(role_file(fname), roles_dir / fname)

    # 3) 项目级说明 AGENTS.md（AI 会自动读到）
    agents = project / "AGENTS.md"
    if not agents.exists():
        agents.write_text(
            "# 多 AI 协作说明（gate）\n"
            "\n"
            "- 团队通过本项目里的 gate 隔空留言协作，不用互相复制粘贴。\n"
            "- 工具：`python3 gate.py`（子命令 init/send/chat/list/status/review-risk-down/pr-summary）\n"
            "- 消息类型：handoff(交活) / review(挑错) / fixed(处理完)，fixed 回复 review 即关闭风险。\n"
            "- 发言：`python3 gate.py send <频道> <内容> --type <类型> --reply M0001 --author <角色名>`\n"
            "- 看消息：`python3 gate.py chat <频道>`；风险：`python3 gate.py status <频道>`\n"
            "- 频道名默认用项目名，第一条消息自动建频道。\n"
            "- 你的角色见 roles/ 对应文件，开工前先读。\n",
            encoding="utf-8",
        )
        print(f"  ✓ AGENTS.md → {project}")

    # 4) 分工与模型记录（每个窗口开工前都会读到）
    plan = {r: (v if isinstance(v, dict) else plan_entry(v))
            for r, v in ai_plan.items()}
    write_plan(project, plan)

    # 5) gate 初始化（写 .gitignore + 独立留言仓库）
    subprocess.run([sys.executable, "gate.py", "init"], cwd=project)

    remember_project(project)

    # 6) 开窗口
    if launch_now:
        for role, entry in plan.items():
            launch_window(project, entry["ai"], role, entry["model"], dry_run=dry_run)

    print()
    print(f"[switch] 完成！当前项目：{project}")
    print("[switch] 接下来：每个 AI 窗口按自己角色干活；你在操作台菜单里按 4/5/6 看进度。")
    return project


# ---------------------------------------------------------------- 开窗口

def osa_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def ai_command(ai: str) -> str | None:
    if ai in ("codex", "claude", "workbuddy"):
        return shutil.which(ai)
    return None  # 自定义等


def write_plan(project: Path, plan: dict) -> None:
    lines = ["# 角色分工（谁用什么 AI、什么模型）", ""]
    for role in ("director", "writer", "reviewer"):
        entry = plan.get(role, {})
        ai = entry.get("ai", "codex") if isinstance(entry, dict) else entry
        model = entry.get("model", "默认") if isinstance(entry, dict) else "默认"
        lines.append(f"- {ROLE_CN.get(role, role)}：{AI_CN.get(ai, ai)} · {model}")
    lines += ["", "模型写\"默认\"表示用该 AI 自己的默认设置；WorkBuddy 在 App 内选模型。"]
    dest = project / "roles" / "AI计划.md"
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✓ AI计划.md → {project}/roles")


def model_flag(ai: str, model: str | None) -> str:
    if not model or model in ("默认", "App 内选"):
        return ""
    if ai == "codex":
        return f" -m {model}"
    if ai == "claude":
        return f" --model {model}"
    return ""


def launch_window(project: Path, ai: str, role: str, model: str | None = None,
                  dry_run: bool = False) -> None:
    role_cn = ROLE_CN.get(role, role)
    role_file = ROLE_FILES.get(role, "writer.md")
    prompt = LAUNCH_PROMPT.format(role_file=role_file, role_cn=role_cn)
    full_cmd = f'{ai}{model_flag(ai, model)} "{prompt}"'
    label = AI_CN.get(ai, ai)
    if model and model not in ("默认", "App 内选"):
        label += f" · {model}"

    if ai == "workbuddy" and not ai_command("workbuddy"):
        if dry_run:
            print(f"  [dry-run] 打开 WorkBuddy App（无命令行时自动回退，模型在 App 内选）")
            return
        subprocess.Popen(["open", "-a", "WorkBuddy"])
        print(f"[switch] WorkBuddy 没有命令行，已帮你打开 App。")
        print(f"[switch] 请在 App 里打开项目 {project}，并把 roles/{role_file} 内容告诉它。")
        return

    if not ai_command(ai):
        print(f"[switch] 提示：没找到 {ai} 命令，窗口打开后请手动确认命令可用。")

    shell = f"cd {osa_escape(str(project))} && {full_cmd}"
    script = (
        'tell application "Terminal"\n'
        "  activate\n"
        f'  do script "{osa_escape(shell)}"\n'
        f'  set title of front window to "{osa_escape(f"{project.name} · {role_cn} ({ai})")}"\n'
        "end tell"
    )
    if dry_run:
        print(f"  [dry-run] 角色：{role_cn} | AI：{label} | 将执行：")
        print(f"    {full_cmd}")
        print(f"    工作目录：{project}")
        return
    subprocess.run(["osascript", "-e", script], check=False)
    print(f"[switch] 已打开 {role_cn} 窗口（{label}）")


# ---------------------------------------------------------------- gate 封装

def run_gate(project: Path, *args: str, channel: str | None = None) -> None:
    gate = project / "gate.py"
    if not gate.exists():
        gate = HERE / "gate.py"  # 项目没复制 gate.py 时，用操作台自带的
    if not gate.exists():
        print(f"[switch] 找不到 gate.py（项目里和操作台旁边都没有）：{project}")
        sys.exit(2)
    cmd = [sys.executable, str(gate), *args]
    if channel:
        cmd.append(channel)
    subprocess.run(cmd, cwd=project)


def pick_channel(project: Path) -> str | None:
    ch = project / ".gate" / "channels"
    if not ch.is_dir():
        return None
    channels = [f.stem for f in ch.glob("*.jsonl")]
    if len(channels) == 1:
        return channels[0]
    if not channels:
        return None
    print("有多个频道，选一个：")
    for i, c in enumerate(channels, 1):
        print(f"  {i}) {c}")
    try:
        idx = int(input("输入编号: ").strip())
        return channels[idx - 1]
    except (ValueError, IndexError):
        return None


# ---------------------------------------------------------------- 交互菜单

def ask(text: str, default: str = "") -> str:
    suffix = f"（默认 {default}）" if default else ""
    try:
        v = input(f"{text}{suffix}: ").strip()
    except EOFError:
        return default
    return v or default


def ask_ai(role_cn: str, default: str = "codex") -> str:
    v = ask(f"{role_cn} 用哪个 AI（codex / claude / workbuddy / 自定义命令）", default)
    if v == "自定义命令" or v == "custom":
        return ask("输入自定义启动命令（如 /path/to/agent）", default)
    return v


def ask_model(ai: str, role_cn: str) -> str:
    if ai == "workbuddy":
        return "App 内选"
    presets = MODEL_PRESETS.get(ai, ["默认"])
    v = ask(f"{role_cn} 用哪个模型（{' / '.join(presets)}，直接输入自定义模型名也行；回车=默认）", "默认")
    return v or "默认"


def menu() -> None:
    while True:
        proj = current_project()
        print("\n" + "=" * 46)
        print("  多 AI 协作操作台（switch）")
        print("=" * 46)
        if proj:
            print(f"  当前项目：{proj.name}（{proj}）")
        else:
            print("  当前项目：（还没有，先按 1 新建）")
        print("=" * 46)
        print("  1) 新建协作项目（自定义 AI 搭配）")
        print("  2) 一键开始：导演+写手+审查 三个 Codex 窗口")
        print("  3) 打开已有项目 / 切换项目")
        print("  4) 启动 AI 窗口（补开某个角色）")
        print("  5) 看群聊       6) 风险状态")
        print("  7) PR 摘要       8) 发一条消息")
        print("  9) 帮助          0) 退出")
        print("=" * 46)

        choice = ask("按数字选", "")
        if not choice or choice == "0":
            print("再见 👋")
            return

        if choice == "1":
            name = ask("项目名字（会建在 ~/Projects/ 下）")
            if not name:
                print("名字不能为空。")
                continue
            plan = {}
            for role, cn in ROLE_CN.items():
                ai = ask_ai(cn)
                plan[role] = {"ai": ai, "model": ask_model(ai, cn)}
            create_project(name, None, plan, launch_now=True)
        elif choice == "2":
            name = ask("项目名字（会建在 ~/Projects/ 下）")
            if not name:
                print("名字不能为空。")
                continue
            create_project(name, None, {"director": "codex", "writer": "codex", "reviewer": "codex"},
                           launch_now=True)
        elif choice == "3":
            p = ask("项目路径")
            path = Path(p).expanduser()
            if not path.is_dir():
                print(f"目录不存在：{path}")
                continue
            remember_project(path)
            print(f"[switch] 当前项目已切换：{path}")
        elif choice == "4":
            if not proj:
                print("先按 1 或 2 新建项目。")
                continue
            print("补开哪个角色：1) 导演  2) 写手  3) 审查")
            r = ask("按数字选", "1")
            role = {"1": "director", "2": "writer", "3": "reviewer"}.get(r, "director")
            ai = ask_ai(ROLE_CN[role])
            launch_window(proj, ai, role, ask_model(ai, ROLE_CN[role]))
        elif choice == "5":
            if proj and (ch := pick_channel(proj)):
                run_gate(proj, "chat", channel=ch)
            else:
                print("还没有频道，让任意一个 AI 先发第一条消息。")
        elif choice == "6":
            if proj and (ch := pick_channel(proj)):
                run_gate(proj, "status", channel=ch)
            else:
                print("还没有频道。")
        elif choice == "7":
            if proj and (ch := pick_channel(proj)):
                run_gate(proj, "pr-summary", channel=ch)
            else:
                print("还没有频道。")
        elif choice == "8":
            if not proj:
                print("先按 1 或 2 新建项目。")
                continue
            ch = pick_channel(proj)
            if not ch:
                print("还没有频道。")
                continue
            print("消息类型：1) note  2) handoff 交活  3) review 挑错  4) fixed 处理完")
            t = ask("按数字选", "1")
            mtype = {"1": "note", "2": "handoff", "3": "review", "4": "fixed"}.get(t, "note")
            reply = ask("回复哪条（没有就回车跳过）", "")
            content = ask("内容")
            cmd = ["send", ch, "--type", mtype, "--author", "人"]
            if reply:
                cmd += ["--reply", reply]
            cmd.append(content)
            run_gate(proj, *cmd)
        elif choice == "9":
            print(__doc__)
        else:
            print("没看懂，再选一次。")


# ---------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="switch", description="多 AI 协作操作台")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("menu", help="打开交互菜单（默认）")

    n = sub.add_parser("new", help="新建协作项目")
    n.add_argument("name")
    n.add_argument("--dir", help="项目放哪（默认 ~/Projects）")
    n.add_argument("--director-ai", default="codex")
    n.add_argument("--writer-ai", default="codex")
    n.add_argument("--reviewer-ai", default="codex")
    n.add_argument("--director-model", default="", help="模型名，或 ai 参数里写 ai@模型")
    n.add_argument("--writer-model", default="")
    n.add_argument("--reviewer-model", default="")
    n.add_argument("--no-launch", action="store_true", help="只建项目，不开窗口")
    n.add_argument("--dry-run", action="store_true", help="只打印将打开什么，不真开")

    s = sub.add_parser("start", help="一键：新建 + 开三个 Codex 窗口")
    s.add_argument("name")
    s.add_argument("--dir")
    s.add_argument("--no-launch", action="store_true")
    s.add_argument("--dry-run", action="store_true")

    o = sub.add_parser("open", help="登记一个已有项目")
    o.add_argument("path")

    l = sub.add_parser("launch", help="给当前项目补开一个 AI 窗口")
    l.add_argument("--ai", default="codex", help="codex / claude / workbuddy / 自定义命令")
    l.add_argument("--role", default="writer", help="director / writer / reviewer")
    l.add_argument("--model", default="默认", help="模型名；默认/App 内选 表示用 AI 自带默认")
    l.add_argument("--dry-run", action="store_true")

    for name, desc in (("status", "看风险"), ("chat", "看群聊"), ("pr", "PR 摘要")):
        c = sub.add_parser(name, help=desc)
        c.add_argument("--channel", default=None)

    sub.add_parser("projects", help="列出登记过的项目")
    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        argv = ["menu"]
    args = build_parser().parse_args(argv)

    if args.cmd == "menu":
        menu()
    elif args.cmd == "new":
        create_project(
            args.name, args.dir,
            {
                "director": plan_entry(args.director_ai, args.director_model),
                "writer": plan_entry(args.writer_ai, args.writer_model),
                "reviewer": plan_entry(args.reviewer_ai, args.reviewer_model),
            },
            launch_now=not args.no_launch, dry_run=args.dry_run,
        )
    elif args.cmd == "start":
        create_project(
            args.name, args.dir,
            {"director": "codex", "writer": "codex", "reviewer": "codex"},
            launch_now=not args.no_launch, dry_run=args.dry_run,
        )
    elif args.cmd == "open":
        path = Path(args.path).expanduser()
        if not (path / ".gate").is_dir():
            print(f"[switch] 该目录还没有 gate 协作仓库：{path}")
            return 1
        remember_project(path)
        print(f"[switch] 已登记：{path}")
    elif args.cmd == "launch":
        proj = current_project()
        if not proj:
            print("[switch] 还没有当前项目，先 switch new 或 switch open")
            return 1
        launch_window(proj, args.ai, args.role, args.model, dry_run=args.dry_run)
    elif args.cmd in ("status", "chat", "pr"):
        proj = current_project()
        if not proj:
            print("[switch] 还没有当前项目，先 switch new 或 switch open")
            return 1
        ch = args.channel or pick_channel(proj)
        if not ch:
            print("[switch] 还没有频道，让任意一个 AI 先发第一条消息")
            return 1
        run_gate(proj, {"status": "status", "chat": "chat", "pr": "pr-summary"}[args.cmd], channel=ch)
    elif args.cmd == "projects":
        state = load_state()
        for name, path in state.get("projects", {}).items():
            mark = " ← 当前" if path == state.get("current") else ""
            print(f"  {name:20s} {path}{mark}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n再见 👋")
        sys.exit(130)
