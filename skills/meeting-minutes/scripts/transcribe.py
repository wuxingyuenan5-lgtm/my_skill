# -*- coding: utf-8 -*-
"""faster-whisper 会议录音转写脚本（GPU 版，large-v3）。

用法：
    python transcribe.py <音频路径> [-o 输出.txt] [--model 模型目录] [--cpu]

关键环境（Windows + 仅显卡驱动、未装 CUDA Toolkit）：
    - 先 `pip install faster-whisper nvidia-cublas-cu12`
    - 用 ctypes.CDLL() 预加载 cuBLAS DLL（os.add_dll_directory / PATH 对
      ctranslate2 均无效，只有 ctypes 预加载可行）
    - 模型走本地目录，不要每次重新下载（large-v3 model.bin 约 3.09GB）
"""
import sys, io, time, os, argparse, ctypes

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 绕过代理（国内镜像/本地模型无需代理；Clash 会把 hf-mirror 绕到海外卡死）
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'

# ---- 预加载 cuBLAS DLL（GPU 必需） ----
# 把下面路径改成你 venv 的 site-packages 目录
SITE_PACKAGES = r'C:/Users/YOUR_USER/.workbuddy/binaries/python/envs/meeting/Lib/site-packages'
for _sub in ('cublas', 'cuda_nvrtc', 'cuda_runtime'):
    _d = os.path.join(SITE_PACKAGES, 'nvidia', _sub, 'bin')
    if os.path.isdir(_d):
        try:
            os.add_dll_directory(_d)
        except Exception:
            pass
        for _f in ('cublas64_12.dll', 'cublasLt64_12.dll', 'nvrtc64_120_0.dll'):
            _p = os.path.join(_d, _f)
            if os.path.exists(_p):
                try:
                    ctypes.CDLL(_p)
                    print('preloaded', _f, flush=True)
                except Exception as _e:
                    print('preload fail', _f, _e, flush=True)

from faster_whisper import WhisperModel

# 模型本地目录（首次下载后固定此处，勿重复下载）
DEFAULT_MODEL = r'C:/Users/YOUR_USER/.../models/large-v3'

# 领域术语提示，提升专有名词识别率
INITIAL_PROMPT = (
    '以下是私募基金投资相关的会议录音，涉及基金、净值、回撤、超额收益、量化、'
    'CTA、套利、期权、股指期货、转债、贴水、基差、仓位、风控、募资、客户、产品等术语。'
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('audio')
    ap.add_argument('-o', '--out', default=None)
    ap.add_argument('--model', default=DEFAULT_MODEL)
    ap.add_argument('--cpu', action='store_true', help='强制 CPU（无 GPU 时）')
    ap.add_argument('--beam', type=int, default=5)
    args = ap.parse_args()

    out = args.out or (os.path.splitext(args.audio)[0] + '.txt')
    device = 'cpu' if args.cpu else 'cuda'
    compute = 'int8' if args.cpu else 'float16'

    t0 = time.time()
    print('loading model...', flush=True)
    model = WhisperModel(args.model, device=device, compute_type=compute)
    print('model loaded in', round(time.time() - t0, 1), 's', flush=True)

    segments, info = model.transcribe(
        args.audio,
        language='zh',
        beam_size=args.beam,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        initial_prompt=INITIAL_PROMPT,
    )
    print('duration:', round(info.duration, 1), 's', flush=True)

    lines = []
    for i, seg in enumerate(segments, 1):
        lines.append(f'[{seg.start:7.1f} -> {seg.end:7.1f}] {seg.text.strip()}')
        if i % 100 == 0:
            print(f'progress {i} segs, {seg.end:.0f}s / {info.duration:.0f}s '
                  f'({seg.end / info.duration * 100:.0f}%)', flush=True)

    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print('DONE', len(lines), 'segments in', round(time.time() - t0, 1), 's', flush=True)
    print('OUTPUT:', out, flush=True)


if __name__ == '__main__':
    main()
