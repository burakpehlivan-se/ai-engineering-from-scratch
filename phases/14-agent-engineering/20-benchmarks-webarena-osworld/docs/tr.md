# Benchmark'lar: WebArena ve OSWorld

> WebArena dört self-hosted uygulama genelinde web-agent yeteneğini test eder. OSWorld Ubuntu, Windows, macOS genelinde masaüstü-agent yeteneğini test eder.

**Tür:** Öğren
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 19 (SWE-bench, GAIA)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- WebArena'nın dört self-hosted uygulamasını ve neden çalıştırma tabanlı değerlendirmenin önemli olduğunu tanımlayın.
- OSWorld'ın neden erişilebilirlik API'leri yerine gerçek OS ekran görüntülerini kullandığını açıklayın.
- İki birincil OSWorld başarısızlık modunu adlandırın: GUI grounding ve operational knowledge.
- OSWorld-G ve OSWorld-Human'ın temel benchmark üzerine ne eklediğini özetleyin.

## Problem

Genel amaçlı agent'lar araç çağırabilir. 20 tıklama boyunca bir alışveriş checkout'unu tamamlayabilirler mi? Yalnızca klavye ve fare ile bir Linux kutusunu yapılandırabilirler mi? WebArena ve OSWorld'ın cevapladığı sorular bunlardır.

## Kavram

### WebArena (Zhou ve diğerleri, ICLR 2024)

- Dört self-hosted web uygulamasında 812 uzun vadeli görev.
- Değerlendirme gym API'leri aracılığıyla çalıştırma tabanlıdır.
- Yayınlanma: en iyi GPT-4 agent'ı %14.41 vs insan %78.24.

### OSWorld (Xie ve diğerleri, NeurIPS 2024)

- Ubuntu, Windows, macOS genelinde 369 gerçek bilgisayar görevi.
- Serbest formsuz klavye ve fare kontrolü.
- 1920×1080 ekran görüntüleri gözlem olarak.
- Yayınlanma: en iyi model %12.24 vs insan %72.36.

### Temel başarısızlık modları

1. **GUI grounding.** Piksel → element eşleme.
2. **Operational knowledge.** Hangi menü, hangi kısayol, hangi tercih paneli.

## İnşa Et

`code/main.py` bir oyuncak web-agent harness uygular: minimal 'alışveriş uygulaması' durum makinesi, 3 görev için altın trajectory'ler, betiklenmiş bir agent, çalıştırma tabanlı değerlendirici ve trajectory verimlilik metriği.

```bash
python3 code/main.py
```

## Kullan

WebArena Verified dahili kümelerde sürekli değerlendirme için. OSWorld masaüstü agent'ları için bir VM filosunda. Computer-use agent'ları (Ders 21) — Claude, OpenAI CUA, Gemini — hepsi bu tür iş yüklerinde eğitilmiş.

## Teslim Et

`outputs/skill-web-desktop-harness.md` çalıştırma tabanlı eval ve trajectory verimlilik metriğiyle bir web/masaüstü agent harness'ı oluşturur.

## Alıştırmalar

1. Toy harness'ı ikinci bir uygulama (bir forum) ile genişletin. 3 görev artı altın trajectory yazın.
2. Görev başına trajectory-verimlilik raporu ekleyin.
3. Altın trajectory'nin asla kullanmadığı bir 'dikkat dağıtıcı' araç uygulayın.
4. OSWorld-G'yi okuyun. Kendi eval'larınızda grounding hatalarını planlama hatalarından nasıl ayırırsınız?
5. WebArena'nın uygulama README'sini okuyun. Sabitlenmiş uygulama sürümlerinden birini yükselttiğinizde ne kırılır?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| WebArena | Web agent benchmark'ı | 4 self-hosted uygulamada 812 görev; gym tarzı değerlendirme |
| VisualWebArena | Görsel WebArena | Görsel olarak temellendirilmiş WebArena; ekran görüntüleri gözlemlerdir |
| OSWorld | Masaüstü agent benchmark'ı | Gerçek Ubuntu/Windows/macOS'ta 369 görev |
| GUI grounding | Pikselden-elemente eşleme | Modelin 1920x1080'de UI elementlerini konumlandırması |
| Operational knowledge | OS bilgisi | Hangi menü, hangi kısayol, hangi tercih paneli |
| Trajectory efficiency | Altın üzerindeki adım | Agent adım sayısının insan minimumuna oranı |

## İleri Okuma

- [Zhou ve diğerleri, WebArena (arXiv:2307.13854)](https://arxiv.org/abs/2307.13854) — dört uygulamalı web benchmark'ı
- [Xie ve diğerleri, OSWorld (arXiv:2404.07972)](https://arxiv.org/abs/2404.07972) — çapraz-OS masaüstü benchmark'ı
- [Anthropic, Introducing computer use](https://www.anthropic.com/news/3-5-models-and-computer-use) — Claude'un benchmark şekilli yeteneği
