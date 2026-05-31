# Ses-Dil Modelleri — Qwen2.5-Omni, Audio Flamingo, GPT-4o Audio

> 2026 ses-dil modelleri (audio-language models) konuşma + çevresel ses + müzik üzerinde akıl yürütür. Qwen2.5-Omni-7B, MMAU-Pro'da GPT-4o Audio ile eşleşir. Audio Flamingo Next, LongAudioBench'de Gemini 2.5 Pro'yu yener. Açık ve kapalı arasındaki kapanan temelde kapandı — çoklu ses görevleri hariç, herkes rastgele seviyede.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 6 · 04 (ASR), Faz 12 · 03 (Görsel-Dil Modelleri), Faz 7 · 10 (Ses Transformer'ları)
**Süre:** ~45 dakika

## Problem

5 saniyelik sesiniz var: köpek havlıyor, biri "dur!" diye bağırıyor, ardından sessizlik. Faydalı sorular birden fazla eksende uzanır:

- **Transkripsiyon.** "Ne söylendi?" — ASR alanı.
- **Anlamsal akıl yürütme.** "Bu kişi tehlikede mi?" — havlama + bağırma + sessizliğin ortak anlaşılması gerektirir.
- **Müzik akıl yürütmesi.** "Melodiyi hangi enstrümanlar çalıyor?"
- **Uzun ses alma.** "90 dakikalık bu dersin neresinde eğitmen gradyan inişini açıkladı?"

Tüm bunlara tek bir istemle cevap veren tek bir model bir **ses-dil modelidir** (LALM / ALM). Saf ASR'den farklıdır: LAM'ler serbest biçimli doğal dil yanıtları üretir, yalnızca transkripsiyon yapmaz.

## Kavram

![Ses-dil modeli: ses kodlayıcı + projeksiyon + LLM çözümleyici](../assets/alm-architecture.svg)

### Üç bileşenli şablon

Her 2026 LALM'ı aynı iskelete sahiptir:

1. **Ses kodlayıcı (audio encoder).** Whisper kodlayıcı · BEATs · CLAP · WavLM · veya modele özel kodlayıcı.
2. **Projeksiyon (projector).** Ses kodlayıcı özelliklerini LLM'nin token gömme uzayına köprüleyen lineer veya MLP.
3. **LLM.** Llama / Qwen / Gemma tabanlı çözümleyici. İç içe metin + ses token'larını alır; metin üretir.

Eğitim:

- **1. Aşama.** Kodlayıcı + LLM dondurulur; yalnızca projeksiyon ASR/biçimlendirme verisi üzerinde eğitilir.
- **2. Aşama.** Talimat takibi ses görevlerinde (soru-cevaplama, akıl yürütme, müzik anlama) tam / LoRA ince ayar.
- **3. Aşama (isteğe bağlı).** Ses-girdi / ses-çıkıtı bir ses çözümleyici ekler. Qwen2.5-Omni ve AF3-Chat bunu yapar.

### 2026 model haritası

| Model | Omurga | Ses kodlayıcı | Çıktı modu | Erişim |
|-------|--------|---------------|------------|--------|
| Qwen2.5-Omni-7B | Qwen2.5-7B | Özel + Whisper | metin + ses | Apache-2.0 |
| Qwen3-Omni | Qwen3 | Özel | metin + ses | Apache-2.0 |
| Audio Flamingo 3 | Qwen2 | AF-CLAP | metin | NVIDIA ticari olmayan |
| Audio Flamingo Next | Qwen2 | AF-CLAP v2 | metin | NVIDIA ticari olmayan |
| SALMONN | Vicuna | Whisper + BEATs | metin | Apache-2.0 |
| LTU / LTU-AS | Llama | CAV-MAE | metin | Apache-2.0 |
| GAMA | Llama | AST + Q-Former | metin | Apache-2.0 |
| Gemini 2.5 Flash/Pro (kapalı) | Gemini | tescilli | metin + ses | API |
| GPT-4o Audio (kapalı) | GPT-4o | tescilli | metin + ses | API |

### Benchmark gerçek kontrolü (2026)

**MMAU-Pro.** Konuşma / ses / müzik / karışık dahil 1800 soru-cevap çifti. Çoklu ses alt kümesi dahildir.

| Model | Genel | Konuşma | Ses | Müzik | Çoklu ses |
|-------|-------|---------|-----|-------|----------|
| Gemini 2.5 Pro | ~%60 | %73.4 | %51.9 | %64.9 | ~%22 |
| Gemini 2.5 Flash | ~%57 | %73.4 | %50.5 | %64.9 | %21.2 |
| GPT-4o Audio | %52.5 | — | — | — | %26.5 |
| Qwen2.5-Omni-7B | %52.2 | %57.4 | %47.6 | %61.5 | ~%20 |
| Audio Flamingo 3 | ~%54 | — | — | — | — |
| Audio Flamingo Next | LongAudioBench'de SOTA | — | — | — | — |

**Çoklu ses sütunu herkes içindamaging.** 4 seçenekli çoktan seçmeli testte rastgele şans = %25; çoğu model civarında puan alır. LALM'ler hala iki klibi karşılaştırmakta zorlanır.

### 2026'da LALM'lerin yararlı olduğu yerler

- **Çağrı merkezi kayıtlarının uyum denetimi.** "Temsilci gerekli beyanı andırdı mı?"
- **Erişilebilirlik.** Kullanıcılara ses olaylarını betimleyin (yalnızca transkripsiyon değil).
- **İçerik denetimi.** Şiddetli dil + tehditkar ton + arka plan bağlamını algılama.
- **Podcast / toplantı bölümlendirme.** Anlamsal özet, yalnızca konuşmacı sıraları değil.
- **Müzik kataloğu analizi.** "Bölüm anahtarı değişikliği olan tüm parçaları bulun."

### Henüz yararlı olmadıkları yerler

- İnce düzeyli müzik teorisi (akor düzeyinin altında).
- Uzun konuşmalarda konuşmacı atıflı akıl yürütme (10 dakika sonrası bozulur).
- Çoklu ses karşılaştırma (%22-26 rastgele seviyenin çok az üstünde).
- Gerçek zamanlı akışlı akıl yürütme (çoğu çevrimdışı toplu çıkarım).

## İnşa Et

### Adım 1: Qwen2.5-Omni'ya sorgulama

```python
from transformers import AutoModelForCausalLM, AutoProcessor

processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-Omni-7B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-Omni-7B", torch_dtype="auto")

audio, sr = load_wav("clip.wav", sr=16000)
messages = [{
    "role": "user",
    "content": [
        {"type": "audio", "audio": audio},
        {"type": "text", "text": "What sounds do you hear, and what's happening?"},
    ],
}]
inputs = processor.apply_chat_template(messages, tokenize=True, return_tensors="pt")
output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0], skip_special_tokens=True))
```

#### Açıklama
Qwen2.5-Omni'ya bir ses klibi ve soru besleyerek ses anlama çıktısını alır.

### Adım 2: projeksiyon modeli

```python
import torch.nn as nn

class AudioProjector(nn.Module):
    def __init__(self, audio_dim=1280, llm_dim=4096):
        super().__init__()
        self.down = nn.Linear(audio_dim, llm_dim)
        self.act = nn.GELU()
        self.up = nn.Linear(llm_dim, llm_dim)

    def forward(self, audio_features):
        return self.up(self.act(self.down(audio_features)))
```

#### Açıklama
Bu kadar basit. Projeksiyon genellikle 1-3 lineer katmandan oluşur. ASR çiftleri (audio → transkripsiyon) üzerinde eğitilmesi 1. Aşama ön görevi (pretext task)dir.

### Adım 3: MMAU / LongAudioBench benchmark'ı

```python
from datasets import load_dataset
mmau = load_dataset("MMAU/MMAU-Pro")

correct = 0
for item in mmau["test"]:
    answer = call_model(item["audio"], item["question"], item["choices"])
    if answer == item["correct_choice"]:
        correct += 1
print(f"Accuracy: {correct / len(mmau['test']):.3f}")
```

#### Açıklama
Kategoriye göre (konuşma / ses / müzik / çoklu ses) ayrı ayrı raporlayın. Toplam sayılar modelin nerede başarısız olduğunu gizler.

## Kullan

| Görev | 2026 seçimi |
|-------|-------------|
| Serbest biçimli ses soru-cevaplama (açık) | Qwen2.5-Omni-7B |
| Uzun seste en iyi açık model | Audio Flamingo Next |
| En iyi kapalı model | Gemini 2.5 Pro |
| Ses-girdi / ses-çıkıtı ajanı | Qwen2.5-Omni veya GPT-4o Audio |
| Müzik akıl yürütmesi | Audio Flamingo 3 veya 2 (müzik-uzmanı AF-CLAP) |
| Çağrı merkezi denetimi | Gemini 2.5 Pro API üzerinden, politika belgelerinizle RAG |

## Tuzaklar

- **Çoklu seste aşırı güven.** Göreviniz "hangi klibe X var" diyorsa, rastgele şans seviyesinde performans gerçektir.
- **Uzun ses bozulması.** 10 dakika sonrası çoğu modelin konuşmacı atıfı bozulur. Önce diyarize edin (Ders 6), sonra özetleyin.
- **Sessizlikte hayal görmeler.** Whisper kodlayıcısı kullanan LALM'lerde aynı Whisper tarzı sorun miras alınır. VAD-kapısı kullanın.
- **Benchmark kiraz seçimi.** Satıcı blogları en iyi durum kategorilerini vurgular. MMAU-Pro çoklu ses alt kümesini kendiniz çalıştırın.

## Gönder

`outputs/skill-alm-picker.md` olarak kaydedin. Verilen bir ses anlama görevi için LALM + benchmark alt kümesi + çıktı modu (metin vs ses) seçin.

## Alıştırmalar

1. **Kolay.** `code/main.py`'yi çalıştırın. Oyuncak bir projeksiyon modeli + sahte LALM yönlendirmesi (ses-gömme, metin-token'ları) → çıktı token'larını görün.
2. **Orta.** Qwen2.5-Omni-7B'yi 100 MMAU-Pro konuşma maddesi üzerinde puanlayın. Makaledeki bildirilen sayı ile karşılaştırın.
3. **Zor.** Minimal bir ses biçimlendirme referansı (baseline) oluşturun: BEATs kodlayıcı + 2 katmanlı projeksiyon + dondurulmuş Llama-3.2-1B. Yalnızca projeksiyonu AudioCaps üzerinde ince ayar yapın. Clotho-AQA'da SALMONN ile karşılaştırın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|---------------------|------------------------|
| LALM | Ses ChatGPT'si | Ses kodlayıcı + projeksiyon + LLM çözümleyici. |
| Projeksiyon | Adaptör | Ses özelliklerini LLM gömme uzayına eşleyen küçük MLP. |
| MMAU | Benchmark | Konuşma, ses, müzik genelinde 10k ses-soru-cevap çifti. |
| MMAU-Pro | Daha zor MMAU | 1800 çoklu ses / akıl yürütme ağırlıklı soru. |
| LongAudioBench | Uzun biçimli değerlendirme | Anlamsal sorgularla çok dakikalık klipler. |
| Ses-girdi / ses-çıkıtı | Spektral yerli | Model metin devresi olmadan sesi alır ve ses çıkarır. |

## İleri Okuma

- [Chu et al. (2024). Qwen2-Audio](https://arxiv.org/abs/2407.10759) — referans mimarisi.
- [Alibaba (2025). Qwen2.5-Omni](https://huggingface.co/Qwen/Qwen2.5-Omni-7B) — spektral-giriş-spektral-çıkış.
- [NVIDIA (2025). Audio Flamingo 3](https://arxiv.org/abs/2507.08128) — açık uzun ses lideri.
- [NVIDIA (2026). Audio Flamingo Next](https://arxiv.org/abs/2604.10905) — LongAudioBench SOTA.
- [Tang et al. (2023). SALMONN](https://arxiv.org/abs/2310.13289) — çift kodlayıcı öncüsü.
- [MMAU-Pro liderlik tablosu](https://mmaubenchmark.github.io/) — canlı 2026 sıralamaları.
