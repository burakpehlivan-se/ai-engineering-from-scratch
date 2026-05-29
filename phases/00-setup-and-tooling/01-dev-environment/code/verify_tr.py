# Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/01-dev-environment/code/verify.py
# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import sys
import shutil
import subprocess

CHECKS = [
    ("Python 3.10+", lambda: sys.version_info >= (3, 10), f"Python {sys.version}"),
    ("NumPy", lambda: __import__("numpy"), None),
    ("Matplotlib", lambda: __import__("matplotlib"), None),
    ("Jupyter", lambda: __import__("jupyter"), None),
    ("Git", lambda: shutil.which("git") is not None, None),
    ("Node.js", lambda: shutil.which("node") is not None, None),
    ("Rust (cargo)", lambda: shutil.which("cargo") is not None, None),
]

GPU_CHECKS = [
    ("PyTorch", lambda: __import__("torch"), None),
    (
        "CUDA",
        lambda: __import__("torch").cuda.is_available(),
        lambda: __import__("torch").cuda.get_device_name(0) if __import__("torch").cuda.is_available() else "Mevcut değil",
    ),
]


def run_check(name, check_fn, detail_fn=None):
    try:
        result = check_fn()
        if result is False:
            raise Exception("Check returned False")
        detail = ""
        if detail_fn:
            if callable(detail_fn):
                detail = f" ({detail_fn()})"
            else:
                detail = f" ({detail_fn})"
        print(f"  [GEÇTİ] {name}{detail}")
        return True
    except Exception:
        print(f"  [KALDI] {name}")
        return False


def main():
    print("\n=== Sıfırdan Yapay Zeka Mühendisliği — Ortam Kontrolü ===\n")

    print("Temel:")
    passed = sum(run_check(name, fn, detail) for name, fn, detail in CHECKS)
    total = len(CHECKS)

    print("\nGPU (isteğe bağlı):")
    gpu_passed = sum(run_check(name, fn, detail) for name, fn, detail in GPU_CHECKS)
    gpu_total = len(GPU_CHECKS)

    print(f"\nSonuç: {passed}/{total} temel kontrol geçildi", end="")
    if gpu_passed > 0:
        print(f", {gpu_passed}/{gpu_total} GPU kontrolü geçildi")
    else:
        print(" (GPU yok — sorun değil, çoğu ders CPU'da çalışır)")

    if passed == total:
        print("\nHazırsınız. Faz 1 ile başlayın.\n")
    else:
        print("\nYukarıdaki başarısız kontrolleri düzeltin, sonra bu betiği tekrar çalıştırın.\n")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
