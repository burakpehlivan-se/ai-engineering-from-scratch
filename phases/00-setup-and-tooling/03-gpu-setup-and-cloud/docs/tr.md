> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/00-setup-and-tooling/03-gpu-setup-and-cloud/docs/en.md)

# GPU Kurulumu ve Bulut

> CPU'da eğitim öğrenmek için iyidir. Gerçek eğitim için GPU gerekir.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 0, Ders 01
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- `nvidia-smi` ve PyTorch'un CUDA API'si ile yerel GPU kullanılabilirliğini doğrulama
- Ücretsiz bulut tabanlı deneyler için T4 GPU'lu Google Colab'ı yapılandırma
- CPU vs GPU'da matris çarpımı benchmark'ı yapma ve hızlanmayı ölçme
- fp16 kuralına göre VRAM'inize sığan en büyük modeli tahmin etme

## Sorun

1-3. fazlardaki derslerin çoğu CPU'da sorunsuz çalışır. Ama CNN'leri, transformer'ları veya LLM'leri (4+. fazlar) eğitmeye başladığınızda GPU hızlandırmasına ihtiyacınız vardır. CPU'da 8 saat süren bir eğitim, GPU'da 10 dakika sürer.

Üç seçeneğiniz var: yerel GPU, bulut GPU veya Google Colab (ücretsiz).

## Kavram

```
Seçenekleriniz:

1. Yerel NVIDIA GPU
   Maliyet: $0 (zaten sahipsiniz)
   Kurulum: CUDA + cuDNN yükleme
   En iyi: Düzenli kullanım, büyük veri setleri

2. Google Colab (ücretsiz katman)
   Maliyet: $0
   Kurulum: Yok
   En iyi: Hızlı deneyler, evde GPU yoksa

3. Bulut GPU (Lambda, RunPod, Vast.ai)
   Maliyet: $0.20-2.00/saat
   Kurulum: SSH + kurulum
   En iyi: Ciddi eğitim, büyük modeller
```

## Uygulama

### Seçenek 1: Yerel NVIDIA GPU

Bir tane olup olmadığını kontrol edin:

```bash
nvidia-smi
```

#### Açıklama
Bu komut, GPU'nuzun görünüp görünmediğini ve mevcut bellek durumunu gösterir.

CUDA ile PyTorch'u kurun:

```python
import torch

print(f"CUDA mevcut: {torch.cuda.is_available()}")
print(f"CUDA sürümü: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Bellek: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

#### Açıklama
Bu kod, CUDA'nın kullanılıp kullanılamadığını, sürümünü ve GPU adını/bellek boyutunu kontrol eder.

### Seçenek 2: Google Colab

1. [colab.research.google.com](https://colab.research.google.com) adresine gidin
2. Çalışma Zamanı > Çalışma Zamanı Türünü Değiştir > T4 GPU
3. Doğrulamak için `!nvidia-smi` çalıştırın

Bu kurstaki defterleri doğrudan Colab'a yükleyebilirsiniz.

### Seçenek 3: Bulut GPU

Lambda Labs, RunPod veya Vast.ai için:

```bash
ssh kullanici@gpu-ornek-makinesi

pip install torch torchvision torchaudio
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

#### Açıklama
Uzak GPU makinesine SSH ile bağlanıp PyTorch'u kurabilirsiniz.

GPU'nuz yok mu? Sorun değil. Çoğu ders CPU'da çalışır. GPU gerektiren dersler bunu belirtir ve Colab bağlantıları içerir.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Kullanılan: {device}")
```

#### Açıklama
Bu kod, mevcut cihazı (GPU veya CPU) otomatik olarak algılar ve kullanır.

## Uygulama: GPU vs CPU benchmark'ı

```python
import torch
import time

size = 5000

a_cpu = torch.randn(size, size)
b_cpu = torch.randn(size, size)

start = time.time()
c_cpu = a_cpu @ b_cpu
cpu_time = time.time() - start
print(f"CPU: {cpu_time:.3f}s")

if torch.cuda.is_available():
    a_gpu = a_cpu.to("cuda")
    b_gpu = b_cpu.to("cuda")

    torch.cuda.synchronize()
    start = time.time()
    c_gpu = a_gpu @ b_gpu
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"GPU: {gpu_time:.3f}s")
    print(f"Hızlanma: {cpu_time / gpu_time:.0f}x")
```

#### Açıklama
Bu benchmark, aynı matris çarpımı işlemini CPU ve GPU'da çalıştırarak hız farkını gösterir. GPU'nun paralel hesaplama gücü sayesinde büyük hızlanmalar elde edilir.

## Alıştırmalar

1. Yukarıdaki benchmark'ı çalıştırın ve CPU vs GPU sürelerini karşılaştırın
2. GPU'nuz yoksa Google Colab'da çalıştırın ve karşılaştırın
3. Ne kadar GPU belleğiniz olduğunu kontrol edin ve sığabilecek en büyük modeli tahmin edin (kural: fp16 için parametre başına 2 bayt)

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| CUDA | "GPU programlama" | Kodun GPU'da çalıştırılmasını sağlayan NVIDIA'nın paralel hesaplama platformu |
| VRAM | "GPU belleği" | GPU üzerindeki Video RAM, sistem RAM'inden ayrıdır. Model boyutunu sınırlar. |
| fp16 | "Yarı hassasiyet" | 16 bit kayan nokta, fp32'nin yarısı kadar bellek kullanır, minimum hassasiyet kaybıyla |
| Tensor Core | "Hızlı matris donanımı" | Matris çarpımı için özelleştirilmiş GPU çekirdekleri, sıradan çekirdeklerden 4-8 kat hızlı |
