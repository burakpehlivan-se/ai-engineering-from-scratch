# Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/03-gpu-setup-and-cloud/code/gpu_check.py
# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import time
import sys


def check_gpu():
    try:
        import torch
    except ImportError:
        print("PyTorch yüklü değil. Çalıştırın: pip install torch")
        return

    print("=== GPU Kontrolü ===\n")
    print(f"PyTorch sürümü: {torch.__version__}")
    print(f"CUDA mevcut: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print("\nGPU algılanamadı. Çoğu ders için sorun değil.")
        print("GPU ağırlıklı dersler için Google Colab (ücretsiz) kullanın.")
        return

    print(f"CUDA sürümü: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")

    props = torch.cuda.get_device_properties(0)
    print(f"Bellek: {props.total_memory / 1e9:.1f} GB")
    print(f"Hesaplama yeteneği: {props.major}.{props.minor}")

    print("\n=== CPU vs GPU Karşılaştırması ===\n")
    size = 4000

    a = torch.randn(size, size)
    b = torch.randn(size, size)

    start = time.time()
    _ = a @ b
    cpu_time = time.time() - start
    print(f"CPU matris çarpımı ({size}x{size}): {cpu_time:.3f}s")

    a_gpu = a.to("cuda")
    b_gpu = b.to("cuda")
    torch.cuda.synchronize()

    start = time.time()
    _ = a_gpu @ b_gpu
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"GPU matris çarpımı ({size}x{size}): {gpu_time:.3f}s")
    print(f"Hızlanma: {cpu_time / gpu_time:.0f}x")

    vram_gb = props.total_memory / 1e9
    params_fp16 = vram_gb * 1e9 / 2
    params_billions = params_fp16 / 1e9
    print(f"\nTahmini maks model boyutu (fp16): ~{params_billions:.0f}B parametre")


if __name__ == "__main__":
    check_gpu()
