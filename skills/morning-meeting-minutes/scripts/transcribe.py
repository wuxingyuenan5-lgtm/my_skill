#!/usr/bin/env python3
"""
晨会音频通用转录脚本 — morning-meeting-minutes skill
用法: python transcribe.py <audio_path> [--output output_path]
实测：base 模型 ~1.4x 实时（17 分钟音频约 13 分钟完成）
"""
import argparse
import time
import os
from faster_whisper import WhisperModel

# 默认参数（经过基准测试优化）
DEFAULT_MODEL = "base"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE = "int8"
DEFAULT_BEAM = 3  # base 模型下 beam_size=5 无增益


def main():
    parser = argparse.ArgumentParser(description="晨会音频转录")
    parser.add_argument("audio", help="音频文件路径")
    parser.add_argument("--output", "-o", help="输出文本路径", default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型 (default: {DEFAULT_MODEL})")
    parser.add_argument("--beam", type=int, default=DEFAULT_BEAM, help=f"beam_size (default: {DEFAULT_BEAM})")
    args = parser.parse_args()

    audio_path = args.audio
    if not os.path.exists(audio_path):
        print(f"错误: 文件不存在 {audio_path}", flush=True)
        return 1

    if args.output is None:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        args.output = os.path.join(os.path.dirname(audio_path) or ".", f"{base_name}_transcript.txt")

    print(f"模型: {args.model} | beam={args.beam}", flush=True)
    print(f"输入: {audio_path}", flush=True)
    print(f"输出: {args.output}", flush=True)

    t0 = time.time()
    model = WhisperModel(args.model, device=DEFAULT_DEVICE, compute_type=DEFAULT_COMPUTE)
    segments, info = model.transcribe(
        audio_path,
        language="zh",
        beam_size=args.beam,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    load_time = time.time() - t0
    print(f"模型加载 + VAD: {load_time:.1f}s | 音频时长: {info.duration:.1f}s ({info.duration/60:.1f}min)", flush=True)

    seg_count = 0
    with open(args.output, "w") as f:
        for seg in segments:
            line = f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text}\n"
            f.write(line)
            seg_count += 1

    elapsed = time.time() - t0
    ratio = info.duration / elapsed if elapsed > 0 else 0
    print(f"完成: {seg_count} 片段 | 总耗时: {elapsed:.1f}s ({elapsed/60:.1f}min) | 速度: {ratio:.1f}x 实时", flush=True)
    print(args.output, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
