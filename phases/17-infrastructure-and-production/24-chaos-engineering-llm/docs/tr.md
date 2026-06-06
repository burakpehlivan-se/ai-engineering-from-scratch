# LLM Üretimi için Kaos Mühendisliği

> LLM'ler için kaos mühendisliği 2026'da kendi disiplinidir. Üretimde deney çalıştırmadan önce önkoşullar: tanımlanmış SLI/SLO (Hizmet Düzeyi Göstergesi/Hedefi), iz+metrik+günlük gözlemlenebilirliği, otomatik geri alma, runbook'lar, nöbetçi. Mimari dört düzleme sahiptir: kontrol (deney zamanlayıcı), hedef (servisler, altyapı, veri depoları), güvenlik (koruyucular + iptal + trafik filtreleri), gözlemlenebilirlik (metrikler + izler + günlükler), geri bildirim (SLO ayarlamalarına). Koruyucular zorunludur: yakma hızı (burn-rate) uyarıları, günlük hata bütçesi yanması beklenenin 2 katını aşarsa deneyleri duraklatır; bastırma pencereleri + iz-ID korelasyonu uyarı gürültüsünü tekilleştirir. Ritim: haftalık küçük kanarya + SLO gözden geçirmesi; aylık oyun günü + post-mortem; çeyreklik ekipler-arası dayanıklılık denetimi + bağımlılık haritalama. LLM'ye özgü deneyler: bellek aşırı yüklemesi, ağ arızaları, sağlayıcı kesintileri, hatalı biçimlenmiş prompt'lar, KV cache çıkarma fırtınaları. Araçlar: Harness Chaos Engineering (LLM-türetilmiş öneriler, patlama yarıçapı küçültme, MCP araç entegrasyonu); LitmusChaos (CNCF); Chaos Mesh (CNCF Kubernetes-native).

**Tür:** Öğren
**Diller:** Python (stdlib, basit kaos deneyi koşucusu)
**Önkoşullar:** Phase 17 · 23 (AI için SRE), Phase 17 · 13 (Gözlemlenebilirlik)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Beş kaos mühendisliği önkoşulunu (SLI/SLO, gözlemlenebilirlik, geri alma, runbook'lar, nöbetçi) sayın ve herhangi birini atlamanın pratiği neden kırdığını açıklayın.
- Dört düzlemi (kontrol, hedef, güvenlik, gözlemlenebilirlik) ve SLO'ya geri bildirim döngüsünü şematize edin.
- Beş LLM'ye özgü deneyi (bellek aşırı yüklemesi, ağ arızası, sağlayıcı kesintisi, hatalı biçimlenmiş prompt, KV çıkarma fırtınası) sıralayın.
- Yığına göre bir araç seçin — Harness, LitmusChaos, Chaos Mesh.

## Problem

Geleneksel yığınlarda kaos testi yerleşmiştir. LLM yığınları yeni arıza modları ekler. 4K token'lık bir prompt zehirli bir karakterle tokenleştiriciyi 12 saniye durdurur. Bir yukarı akış sağlayıcısı 429'lar; ağ geçidiniz yeniden dener; servisiniz yeniden deneme-amplifiye eşzamanlılık üzerinde OOM'lar. Sıçrama yükü altında bir KV cache çıkarma fırtınası, hesaplamayı doyuran yeniden-prefill kaskadlarına neden olur.

Bunların hiçbiri birim testlerinde görünmez. Kaos mühendisliği, kullanıcılardan önce keşfetmenin yoludur.

## Kavram

### Önkoşullar

Üretimde onsuz kaos çalıştırmayın:

1. **SLI/SLO** — tanımlanmış hizmet düzeyi göstergeleri ve hedefleri.
2. **Gözlemlenebilirlik** — panolara bağlı izler, metrikler, günlükler.
3. **Otomatik geri alma** — Phase 17 · 20 politika-flag geri alma.
4. **Runbook'lar** — yapılandırılmış, Phase 17 · 23.
5. **Nöbetçi** — yanıt verecek biri.

Herhangi birinin eksikliği kaosu gerçek olaya dönüştürür.

### Dört düzlem + geri bildirim

**Kontrol düzlemi** — deney zamanlayıcı (Litmus iş akışı, Chaos Mesh zamanlaması, Harness UI).

**Hedef düzlemi** — servisler, pod'lar, düğümler, yük dengeleyiciler, veri depoları.

**Güvenlik düzlemi** — öldürme anahtarı, bastırma pencereleri, patlama-yarıçapı sınırları, hata bütçesi geçitleri.

**Gözlemlenebilirlik düzlemi** — normal metrikler + kaos-kaynaklıyı doğaldan ayırt etmek için iz-ID korelasyonu.

**Geri bildirim döngüsü** — bulgular SLO ayarlamasına, runbook güncellemelerine, kod düzeltmelerine geri beslenir.

### Koruyucular zorunludur

- **Yakma hızı uyarısı**: günlük hata bütçesi yanması beklenenin 2 katını aşarsa deneyi duraklat.
- **Bastırma pencereleri**: deney sırasında patlama yarıçapındaki deney-dışı uyarıları sustur.
- **İz-ID korelasyonu**: deney-kaynaklı tüm hatalar bir etiket taşır, böylece nöbetçi tekilleştirebilir.

### Beş LLM'ye özgü deney

1. **Bellek aşırı yüklemesi** — yüksek eşzamanlılıkla uzun-bağlam istekleri göndererek bir KV cache öneçıkarma fırtınasına zorla. Gözlemle: servis zarifçe dökülüyor mu yoksa çöküyor mu?

2. **Ağ arızası** — çıkarım ağ geçidi ile sağlayıcı arasındaki bağlantıyı kes. Gözlemle: yedek düşme SLA içinde devreye giriyor mu? (Phase 17 · 19)

3. **Sağlayıcı kesintisi simülasyonu** — OpenAI'dan %100 429. Gözlemle: yönlendirme Anthropic'e yük devrediyor mu? (Phase 17 · 16, 19)

4. **Hatalı biçimlenmiş prompt** — tokenleştiriciyi durduran yük enjekte et (ör. derin iç içe unicode, devasa UTF-8 kod noktası). Gözlemle: tek bir istek bir çalışanı kilitliyor mu?

5. **KV çıkarma fırtınası** — vLLM blok bütçesini doyurarak çıkarmaya zorla. Gözlemle: LMCache iyileşiyor mu yoksa servis kötüleşiyor mu?

### Ritim

- **Haftalık** — staging'de küçük kanarya deneyleri, belki %5 üretim.
- **Aylık** — belirli bir senaryo üzerinde zamanlanmış oyun günü; ekipler-arası katılım; post-mortem.
- **Çeyreklik** — ekipler-arası dayanıklılık denetimi; bağımlılık haritası güncellemesi.

### Araçlar

- **Harness Chaos Engineering** — ticari; AI-türetilmiş deney önerileri; patlama-yarıçapı küçültme; MCP araç entegrasyonu.
- **LitmusChaos** — CNCF mezun; Kubernetes iş-akışı tabanlı.
- **Chaos Mesh** — CNCF sandbox; Kubernetes-native CRD stili.
- **Gremlin** — ticari; geniş destek.
- **AWS FIS** / **Azure Chaos Studio** — yönetilen bulut teklifleri.

### Küçük başlamak

İlk deney: sabit trafik altında bir decode kopyasının pod-öldürmesi. Yeniden yönlendirmeyi ve iyileşmeyi gözlemleyin. Bu çalışırsa ve güvenli görünürse, ağ kaosuna geçin.

İlk LLM'ye özgü deney: 5 dakika için bir sağlayıcı 429 enjekte edin. Yedek düşmeyi gözlemleyin. Çoğu ekip, yedek düşmelerinin tam olarak test edilmediğini keşfeder.

### Hatırlamanız gereken sayılar

- Dört düzlem: kontrol, hedef, güvenlik, gözlemlenebilirlik.
- Yakma hızı duraklaması: beklenen günlük bütçe yanmasının 2 katı.
- Ritim: haftalık kanarya, aylık oyun günü, çeyreklik denetim.
- Beş LLM deneyi: bellek, ağ, sağlayıcı, hatalı biçimlenmiş prompt, KV fırtınası.

## Kullanım

`code/main.py`, güvenlik düzlemi geçitleriyle üç kaos deneyini simüle eder. Hangi deneylerin yakma hızı iptalini tetikleyeceğini raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-chaos-plan.md` üretir. Yığın ve olgunluk verildiğinde, ilk üç deneyi ve aracı seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Hangi deney yakma hızı geçidini tetikler ve neden?
2. vLLM tabanlı bir RAG servisi için ilk beş kaos deneyini tasarlayın. Başarı ölçütlerini dahil edin.
3. Yakma hızı uyarınız bir deneyi duraklattı. Kök nedeni nasıl belirlersiniz — kaos mu doğal mı?
4. Kaos'un üretimde mi yoksa yalnızca staging'de mi çalışması gerektiğini tartışın. Üretim ne zaman doğru cevaptır?
5. Genel ağ kaosunun tekrarlayamayacağı üç LLM'ye özgü arıza modunu sayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| SLI / SLO | "servis hedefleri" | Gösterge + hedef; gerekli önkoşul |
| Patlama yarıçapı | "kapsam" | Deneyden etkilenen servis / kullanıcı kümesi |
| Yakma hızı uyarısı | "bütçe geçidi" | Hata bütçesi yanma hızı > beklenenin 2 katı olduğunda ateşlenir |
| Oyun günü | "aylık tatbikat" | Zamanlanmış ekipler-arası kaos egzersizi |
| LitmusChaos | "CNCF iş akışı" | Mezun CNCF Kubernetes kaos aracı |
| Chaos Mesh | "CNCF CRD" | CNCF sandbox Kubernetes-native kaos |
| Harness CE | "ticari AI destekli" | AI önerileriyle Harness kaos |
| Hatalı biçimlenmiş prompt | "tokenleştirici bombası" | Tokenizasyonu durduran girdi |
| KV çıkarma fırtınası | "öneçıkarma kaskadı" | Yeniden prefill'leri tetikleyen toplu çıkarma |

## Ek Okuma

- [DevSecOps School — Kaos Mühendisliği 2026 Kılavuzu](https://devsecopsschool.com/blog/chaos-engineering/)
- [Ankush Sharma — LLM'ler için Gözlemlenebilirlik (kitap)](https://www.amazon.com/Observability-Large-Language-Models-Engineering-ebook/dp/B0DJSR65TR)
- [LitmusChaos (CNCF)](https://litmuschaos.io/)
- [Chaos Mesh (CNCF)](https://chaos-mesh.org/)
- [Harness Chaos Engineering](https://www.harness.io/products/chaos-engineering)
- [AWS FIS](https://aws.amazon.com/fis/)
