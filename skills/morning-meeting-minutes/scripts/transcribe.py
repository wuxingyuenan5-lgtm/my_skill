#!/usr/bin/env python3
"""
晨会音频通用转录脚本 — morning-meeting-minutes skill
用法: python transcribe.py <audio_path> [-o output.txt] [--beam 1] [--model base]

设计原则（2026-08-13 用户反馈）:
  - 流程简单, 不做复杂质检, 不拖慢正常纪要速度
  - 失败尽快暴露: 任何异常在 1-2 分钟内告知用户, 绝不长时间空跑
  - 默认 beam=1 (贪心解码) 提速, 质量对中文晨会够用
"""
import argparse
import time
import os
import tempfile
import numpy as np
from faster_whisper import WhisperModel

DEFAULT_MODEL = "base"
DEFAULT_DEVICE = "cpu"
DEFAULT_COMPUTE = "int8"
DEFAULT_BEAM = 1  # 贪心解码, 比 beam=3 快约 1.5x


def to_16k_wav(path):
    """解码并统一为 16kHz 单声道 wav; 顺带返回时长/音量(仅用于失败诊断)"""
    import av
    import wave
    container = av.open(path)
    stream = container.streams[0]
    resampler = av.AudioResampler(format='s16', layout='mono', rate=16000)
    pcm_all = []
    for frame in container.decode(stream):
        for out_frame in resampler.resample(frame):
            pcm_all.append(out_frame.to_ndarray().ravel())
    for out_frame in resampler.resample(None):
        pcm_all.append(out_frame.to_ndarray().ravel())
    container.close()
    pcm = np.concatenate(pcm_all)
    pcm_f = pcm.astype(np.float32) / 32768.0
    rms = float(np.sqrt((pcm_f ** 2).mean())) if len(pcm_f) else 0.0
    duration = len(pcm) / 16000.0
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()
    with wave.open(tmp.name, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(pcm.tobytes())
    return tmp.name, duration, rms


def run_transcribe(model, wav, out_path, beam, vad):
    segments, info = model.transcribe(
        wav, language="zh", beam_size=beam, vad_filter=vad,
        condition_on_previous_text=False,
    )
    count = 0
    with open(out_path, "w") as f:
        for seg in segments:
            f.write(f"[{seg.start:.1f}s -> {seg.end:.1f}s] {seg.text}\n")
            count += 1
    return count, info.duration


def main():
    parser = argparse.ArgumentParser(description="晨会音频转录（简单流程 + 快速失败）")
    parser.add_argument("audio", help="音频文件路径")
    parser.add_argument("--output", "-o", help="输出文本路径", default=None)
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"模型 (default: {DEFAULT_MODEL})")
    parser.add_argument("--beam", type=int, default=DEFAULT_BEAM, help=f"beam_size (default: {DEFAULT_BEAM})")
    args = parser.parse_args()

    if not os.path.exists(args.audio):
        print(f"ERROR: 文件不存在 {args.audio}", flush=True)
        return 1
    if args.output is None:
        base = os.path.splitext(os.path.basename(args.audio))[0]
        args.output = os.path.join(os.path.dirname(args.audio) or ".", f"{base}_transcript.txt")

    print(f"模型: {args.model} | beam={args.beam}", flush=True)
    print(f"输入: {args.audio}", flush=True)

    # 1. 预处理: 转 16kHz wav (约 5-10 秒)
    try:
        wav_path, duration, rms = to_16k_wav(args.audio)
    except Exception as e:
        print(f"ERROR: 音频解码失败 ({e})", flush=True)
        print("  建议: 检查音频文件是否损坏, 或重新录音", flush=True)
        return 2
    print(f"预处理完成: 时长 {duration:.0f}s | RMS={rms:.4f}", flush=True)

    # 2. 音量极低 → 立刻失败并提示 (不等转录空跑)
    if rms < 0.005:
        print("ERROR: 音量极低 (RMS<0.005), 录音被遮挡或损坏", flush=True)
        print("  建议: 重新录音 (麦克风贴近说话人), 或改用手记文本", flush=True)
        os.unlink(wav_path)
        return 2

    # 3. 转录 (带 VAD)
    t0 = time.time()
    model = WhisperModel(args.model, device=DEFAULT_DEVICE, compute_type=DEFAULT_COMPUTE)
    print(f"模型加载: {time.time()-t0:.1f}s | 开始转录 (VAD)...", flush=True)
    count, _ = run_transcribe(model, wav_path, args.output, args.beam, vad=True)
    print(f"VAD 轮: {count} 片段 | {time.time()-t0:.1f}s", flush=True)

    # 4. VAD 空 → 关 VAD 重试一次 (仍是快速路径, 但可能较久; 失败即报)
    if count == 0:
        print("VAD 结果为空, 关 VAD 重试...", flush=True)
        count, _ = run_transcribe(model, wav_path, args.output, args.beam, vad=False)

    os.unlink(wav_path)

    if count == 0:
        print("ERROR: 无法识别到任何有效语音", flush=True)
        print("  可能: 录音被遮挡/太远/噪声大/文件损坏", flush=True)
        print("  建议: 重新录音或改用手记文本", flush=True)
        return 2

    ratio = duration / (time.time() - t0) if (time.time() - t0) > 0 else 0
    print(f"DONE: {count} 片段 | 总耗时 {time.time()-t0:.0f}s | {ratio:.1f}x 实时", flush=True)
    print(args.output, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
