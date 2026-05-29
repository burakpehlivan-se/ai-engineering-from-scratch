# Orijinal: https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/05-jupyter-notebooks/code/notebook_tips.py
# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.

import time
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def timing_comparison():
    print("=== Zamanlama: Liste vs NumPy ===\n")

    size = 1_000_000

    start = time.perf_counter()
    python_list = [x ** 2 for x in range(size)]
    list_time = time.perf_counter() - start
    print(f"Liste kavraması: {list_time:.4f}s")

    start = time.perf_counter()
    numpy_array = np.arange(size) ** 2
    numpy_time = time.perf_counter() - start
    print(f"NumPy:              {numpy_time:.4f}s")
    print(f"Hızlanma:            {list_time / numpy_time:.1f}x")


def inline_plotting():
    print("\n=== Satır İçi Grafik ===\n")

    np.random.seed(42)
    x = np.linspace(0, 10, 200)
    y_sin = np.sin(x)
    y_noisy = y_sin + np.random.normal(0, 0.2, 200)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].plot(x, y_sin, label="sin(x)")
    axes[0].plot(x, y_noisy, alpha=0.5, label="gürültülü")
    axes[0].set_title("Sinyal vs Gürültü")
    axes[0].legend()

    axes[1].hist(y_noisy - y_sin, bins=30, edgecolor="black")
    axes[1].set_title("Gürültü Dağılımı")

    plt.tight_layout()
    plt.savefig("notebook_plot.png", dpi=100)
    print("Grafik notebook_plot.png olarak kaydedildi")
    print("Bir defterde, plt.show() bunu satır içi görüntüler.")


def dataframe_display():
    print("\n=== DataFrame Görüntüleme ===\n")

    df = pd.DataFrame({
        "model": ["Doğrusal Regresyon", "Rastgele Orman", "Sinir Ağı", "XGBoost"],
        "dogruluk": [0.72, 0.89, 0.94, 0.91],
        "egitim_suresi_sn": [0.1, 2.3, 45.6, 8.2],
        "parametreler": [102, 50_000, 1_200_000, 25_000],
    })

    print("Bir defterde sadece 'df' yazarak zengin bir HTML tablosu görüntülenir:\n")
    print(df.to_string(index=False))

    print(f"\nEn iyi model: {df.loc[df['dogruluk'].idxmax(), 'model']}")
    print(f"En hızlı model: {df.loc[df['egitim_suresi_sn'].idxmin(), 'model']}")


def memory_check():
    print("\n=== Bellek Kullanımı ===\n")

    small = np.random.randn(1000)
    medium = np.random.randn(100_000)
    large = np.random.randn(10_000_000)

    for name, arr in [("1K", small), ("100K", medium), ("10M", large)]:
        size_mb = arr.nbytes / 1e6
        print(f"Dizi {name:>4s} eleman: {size_mb:>8.2f} MB")

    print(f"\nPython süreci belleği: ~{sys.getsizeof(large) / 1e6:.1f} MB (büyük dizi için)")
    print("Defterlerde bellek hücreler arasında birikir. Serbest bırakmak için çekirdeği yeniden başlatın.")


def magic_command_equivalents():
    print("\n=== Sihirli Komut Eşdeğerleri ===\n")
    print("Bir defterde sihirli komutlar kullanırsınız:")
    print("  %timeit np.random.randn(10000)    -> mikro karşılaştırma")
    print("  %%time uzun_islem()              -> duvar saati zamanı")
    print("  %matplotlib inline               -> grafikleri hücrelerde göster")
    print("  !pip install paket               -> defterden yükle")
    print("  %env DEGISKEN                    -> ortam değişkenini kontrol et")
    print()

    iterations = 1000
    start = time.perf_counter()
    for _ in range(iterations):
        np.random.randn(10000)
    elapsed = time.perf_counter() - start
    per_call = elapsed / iterations * 1e6

    print(f"Manuel zamanlama (%%timeit gibi): np.random.randn(10000)")
    print(f"  {per_call:.1f} us/chagri ({iterations} iterasyon)")


if __name__ == "__main__":
    print("Defter İpuçları - Temel Kalıplar\n")
    print("Bunları Jupyter defterinde çalıştırarak zengin çıktıyı görün.\n")

    timing_comparison()
    inline_plotting()
    dataframe_display()
    memory_check()
    magic_command_equivalents()
