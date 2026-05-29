#!/usr/bin/env python3
"""
Kod dosyalarındaki print ifadelerini çevirmek için araç.
Kullanım: python scripts/translate_code.py <kaynak_dosya> <hedef_dosya>
"""

import re
import sys
from pathlib import Path

# Çeviri sözlüğü
TRANSLATIONS = {
    # Genel
    "=== ": "=== ",
    " ===\n": " ===\n",
    "\n=== ": "\n=== ",
    
    # Faz 01 için yaygın çeviriler
    "Vectors": "Vektörler",
    "Matrices": "Matrisler",
    "Matrix": "Matris",
    "Angle Between Vectors": "Vektörler Arası Açı",
    "Projection": "Projeksiyon",
    "Linear Independence": "Doğrusal Bağımsızlık",
    "Gram-Schmidt Orthogonalization": "Gram-Schmidt Ortoğonalleştirme",
    "Matrix Rank": "Matris Derecesi",
    "Neural Network Layer": "Sinir Ağı Katmanı",
    "normalized": "normalize edilmiş",
    "independent": "bağımsız",
    "Angle between": "Açı",
    "degrees": "derece",
    "Input": "Girdi",
    "Output": "Çıktı",
    "This is literally what a neural network layer does.": "Bu, bir sinir ağı katmanının tam olarak yaptığı şeydir.",
    
    # Faz 00 için
    "Environment Check": "Ortam Kontrolü",
    "GPU Check": "GPU Kontrolü",
    "GPU (optional)": "GPU (isteğe bağlı)",
    "Core": "Temel",
    "Result": "Sonuç",
    "core checks passed": "temel kontrol geçildi",
    "GPU checks passed": "GPU kontrolü geçildi",
    "You're ready. Start with Phase 1.": "Hazırsınız. Faz 1 ile başlayın.",
    "Fix the failed checks above": "Yukarıdaki başarısız kontrolleri düzeltin",
    "then run this script again": "sonra bu betiği tekrar çalıştırın",
    "PyTorch not installed. Run: pip install torch": "PyTorch yüklü değil. Çalıştırın: pip install torch",
    "PyTorch version": "PyTorch sürümü",
    "CUDA available": "CUDA mevcut",
    "No GPU detected. That's fine for most lessons.": "GPU algılanamadı. Çoğu ders için sorun değil.",
    "For GPU-heavy lessons, use Google Colab (free).": "GPU ağırlıklı dersler için Google Colab (ücretsiz) kullanın.",
    "CUDA version": "CUDA sürümü",
    "GPU": "GPU",
    "Memory": "Bellek",
    "Compute capability": "Hesaplama yeteneği",
    "CPU vs GPU Benchmark": "CPU vs GPU Karşılaştırması",
    "CPU matrix multiply": "CPU matris çarpımı",
    "GPU matrix multiply": "GPU matris çarpımı",
    "Speedup": "Hızlanma",
    "Estimated max model size": "Tahmini maks model boyutu",
    "Install the SDK: pip install anthropic": "SDK'ı yükleyin: pip install anthropic",
    "SDK response": "SDK yanıtı",
    "Tokens used": "Kullanılan token'lar",
    "Set ANTHROPIC_API_KEY environment variable first": "Önce ANTHROPIC_API_KEY ortam değişkenini ayarlayın",
    "Raw HTTP response": "Ham HTTP yanıtı",
    "API Calls": "API Çağrıları",
    "Using the SDK": "SDK kullanarak",
    "Using raw HTTP": "Ham HTTP kullanarak",
    "Timing: List vs NumPy": "Zamanlama: Liste vs NumPy",
    "List comprehension": "Liste kavraması",
    "Inline Plotting": "Satır İçi Grafik",
    "Signal vs Noise": "Sinyal vs Gürültü",
    "Noise Distribution": "Gürültü Dağılımı",
    "Saved plot to": "Grafik şu adrese kaydedildi",
    "In a notebook, plt.show() displays this inline.": "Bir defterde, plt.show() bunu satır içi görüntüler.",
    "DataFrame Display": "DataFrame Görüntüleme",
    "Best model": "En iyi model",
    "Fastest model": "En hızlı model",
    "Memory Usage": "Bellek Kullanımı",
    "Python process memory": "Python süreci belleği",
    "In notebooks, memory accumulates across cells. Restart the kernel to free it.": "Defterlerde bellek hücreler arasında birikir. Serbest bırakmak için çekirdeği yeniden başlatın.",
    "Magic Command Equivalents": "Sihirli Komut Eşdeğerleri",
    "Install the datasets library: pip install datasets": "datasets kütüphanesini yükleyin: pip install datasets",
    "Install huggingface_hub: pip install huggingface_hub": "huggingface_hub'ı yükleyin: pip install huggingface_hub",
    "Dataset": "Veri seti",
    "Split": "Bölüm",
    "Rows": "Satır sayısı",
    "Columns": "Sütunlar",
    "Features": "Özellikler",
    "First row": "İlk satır",
    "Streamed": "akışa alındı",
    "rows from": "satır",
    "Format comparison for": "için biçim karşılaştırması",
    "CSV": "CSV",
    "JSON": "JSON",
    "Parquet": "Parquet",
    "bytes": "bayt",
    "smaller than CSV": "CSV'den daha küçük",
    "Splits": "Bölümler",
    "Train": "Eğitim",
    "Val": "Doğrulama",
    "Test": "Test",
    "Downloaded": "indirildi",
    "Path": "Yol",
    "Size": "Boyut",
    "No HF cache found yet.": "Henüz HF önbelleği bulunamadı.",
    "HF Dataset Cache": "HF Veri Seti Önbelleği",
    "Files": "Dosya sayısı",
    "Total size": "Toplam boyut",
    "Loaded": "yüklendi",
    "from": "adresinden",
    "Dataset fingerprint": "Veri seti parmak izi",
    "first": "ilk",
    "rows": "satır",
    "All checks passed. Your data pipeline is ready.": "Tüm kontroller geçildi. Veri hatınız hazır.",
    "Data Management Utility": "Veri Yönetimi Yardımcı Aracı",
    "AI Debugging and Profiling Toolkit": "Yapay Zeka Hata Ayıklama ve Profilleme Araç Takımı",
    "Phase 0, Lesson 12": "Faz 0, Ders 12",
    "PyTorch not installed. Install with:": "PyTorch yüklü değil. Şununla yükleyin:",
    "Running non-PyTorch demos only...": "Sadece PyTorch dışı demolar çalıştırılıyor...",
    "All demos complete.": "Tüm demolar tamamlandı.",
    "Next: introduce bugs intentionally and practice catching them.": "Sıradaki adım: kasıtlı olarak hatalar ekleyin ve yakalamayı çalışın.",
    "Print Debugging for Tensors": "Tensörler İçin Yazdırma Hata Ayıklaması",
    "input batch": "girdi toplu işi",
    "after matmul": "matmul sonrası",
    "with injected NaN": "enjekte edilmiş NaN ile",
    "Timing Code Sections": "Kod Bölümlerini Zamanlama",
    "matrix multiply": "matris çarpımı",
    "Memory Tracking": "Bellek İzleme",
    "Top 5 memory allocations": "En büyük 5 bellek tahsisi",
    "Shape Checking Through Model": "Model Üzerinde Şekil Kontrolü",
    "NaN Detection": "NaN Tespiti",
    "Normal loss": "Normal kayıp",
    "NaN detected": "NaN algılandı",
    "Simulated NaN loss": "Simüle edilmiş NaN kaybı",
    "Device Checking": "Cihaz Kontrolü",
    "Model device": "Model cihazı",
    "With mixed devices": "Karışık cihazlarla",
    "Gradient Health Check": "Gradyan Sağlığı Kontrolü",
    "Total gradient norm": "Toplam gradyan normu",
    "GPU Memory Summary": "GPU Bellek Özeti",
    "No GPU available. Skipping GPU memory demo.": "GPU mevcut değil. GPU bellek demosu atlanıyor.",
    "On a GPU machine": "GPU makinesinde",
    "Allocated": "Tahsis",
    "Cached": "Önbellek",
    "After": "sonrası",
    "After cleanup": "Temizlik sonrası",
    "Structured Logging": "Yapılandırılmış Günlükleme",
    "Training started": "Eğitim başladı",
    "Loss spike detected": "Kayıp sıçraması algılandı",
    "Training complete": "Eğitim tamamlandı",
    "Conditional Breakpoint Pattern": "Koşullu Kesme Noktası Kalıbı",
    "In real code, use this pattern:": "Gerçek kodda bu kalıbı kullanın:",
    "Useful pdb commands once inside:": "İçeri girdikten sonra faydalı pdb komutları:",
    "print shape": "şekli yazdır",
    "check device": "cihazı kontrol et",
    "inspect gradients": "gradyanları incele",
    "count NaNs": "NaN'ları say",
    "continue execution": "çalıştırmaya devam et",
    "quit debugger": "hata ayıklayıcıdan çık",
    "WARNING: large gradient in": "UYARI: büyük gradyan",
    "WARNING: zero gradient in": "UYARI: sıfır gradyan",
}


def translate_file(source_path: str, target_path: str):
    """Dosyayı çevir."""
    source = Path(source_path)
    target = Path(target_path)
    
    content = source.read_text(encoding="utf-8")
    
    # GitHub linki ekle
    repo_url = "https://github.com/rohitg00/ai-engineering-from-scratch/blob/main"
    relative_path = str(source).replace("source/", "")
    header = f"# Orijinal: {repo_url}/{relative_path}\n# Bu dosya, orijinal kodun Türkçe çevrilmiş versiyonudur.\n\n"
    
    # Çevirileri uygula
    translated = content
    for eng, tur in TRANSLATIONS.items():
        translated = translated.replace(eng, tur)
    
    # Hedef dizini oluştur
    target.parent.mkdir(parents=True, exist_ok=True)
    
    # Yaz
    target.write_text(header + translated, encoding="utf-8")
    print(f"✓ {target.name}")


def main():
    if len(sys.argv) < 3:
        print("Kullanım: python translate_code.py <kaynak_dosya> <hedef_dosya>")
        sys.exit(1)
    
    translate_file(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
