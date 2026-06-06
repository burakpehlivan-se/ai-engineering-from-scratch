# LLM'ler için Gölge Trafiği, Kanarya Yayılım ve Kademeli Dağıtım

> LLM yayılımları, yazılım dağıtımının en zor kısımlarını birleştirir: birim testi yok, dağınık arıza modları, gecikmeli sinyaller. Sıra: (1) gölge modu (shadow mode) — aday modele üretim isteklerini çoğaltın, kaydedin, sıfır kullanıcı etkisiyle karşılaştırın; belirgin dağılım sorunlarını yakalar ama kalite garantisi değildir; (2) kanarya yayılımı (canary rollout) — her adımda geçitlerle %10 → %25 → %50 → %75 → %100 kademeli trafik kaydırma; gecikme yüzdelerini, istek başına maliyeti, hata/red oranını, çıktı uzunluğu dağılımını ve kullanıcı geri bildirim oranını izleyin; (3) kararlılık onaylandıktan sonra farklı alternatifler için A/B testi. Determinizm-olmama (non-determinism) indirgenemez — aynı girdilerle %15'e kadar doğruluk oynaması, GPU FP (kayan nokta) birleşmemesinin yanı sıra toplu-iş boyutu oynaklığından kaynaklanır. Maliyet sabit değil, değişkendir — %20 daha iyi bir model, çağrı başına 3 kat pahalı olabilir. Geri alma (rollback) hızı belirleyicidir: geri alma yeniden dağıtım gerektiriyorsa, çok yavaşsınız. Politika yapılandırma/flag'lerde yaşar; model, sabitlenmiş özetlerle (digest) kayıt defterinde (registry) yaşar; geri alma = politikayı çevirmek + eşiği geri almak + eski modeli saniyeler içinde sabitlemek.

**Tür:** Öğren
**Diller:** Python (stdlib, basit kanarya-ilerleme simülatörü)
**Önkoşullar:** Phase 17 · 13 (Gözlemlenebilirlik), Phase 17 · 21 (A/B Testi)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Gölge modunu (sıfır-etki karşılaştırma), kanarya'yı (canlı trafik kademeli) ve A/B'yi (kararlılık onaylı karşılaştırma) ayırt edin.
- Beş LLM'ye özgü kanarya metriğini (gecikme, istek başına maliyet, hata/red, çıktı uzunluğu dağılımı, kullanıcı geri bildirimi) sıralayın.
- LLM determinizm-olmamasının (%15'e kadar) bir yayılımda "kararlı"nın ne anlama geldiğini neden değiştirdiğini açıklayın.
- Saniyeler (politika çevirme) değil saatler (yeniden dağıtım) süren bir geri alma yolu tasarlayın.

## Problem

Yeni bir model gönderiyorsunuz. Çevrimdışı değerlendirmeler %3 doğruluk kazancı gösteriyor. Üretimde açıyorsunuz. 24 saat içinde maliyet %40 artıyor, kullanıcı başparmak-aşağı %8 artıyor, üç müşteri bileti "garip yanıtlar" rapor ediyor. Geri alıyorsunuz. Yeniden dağıtım 3 saat sürüyor. Hafta sonunuz mahvoldu.

Bunun her parçası önlenebilirdi. Gölge modu, herhangi bir kullanıcı görmeden önce %40'lık maliyet artışını yakalardı. Kanarya, başparmak-aşağı hareket ettiğinde %10'da dururdu. Politika-flag geri alma 30 saniye sürerdi. Disiplin, "çevrimdışı değerlendirmeler iyi görünüyor" ile "gerçek kullanıcılar mutlu" arasındaki boşluğu doldurur.

## Kavram

### Gölge modu

Aday, üretimle aynı istekleri alır; çıktılar günlüğe kaydedilir, kullanıcılara döndürülmez. Sıfır kullanıcı etkisi. Günlüğe kaydedin:

- Çıktı içeriği (üretime karşı farkı).
- Token sayıları (maliyet deltası).
- Gecikme.
- Red ve hata.

Yakalananlar: maliyet patlamaları, uzunluk gerilemeleri, belirgin red değişiklikleri, sert hatalar. Yakalanmayan: kullanıcıların algılayacağı kalite deltası. Gölge bir duman testidir, kalite testi değil.

### Kanarya yayılımı

Geçitlerle kademeli trafik kaydırma. Tipik ilerleme: %1 → %10 → %25 → %50 → %75 → %100. Her adımda 5 metrik üzerinde geçit:

1. **Gecikme yüzdeleri** — P50, P95, P99. İhlal: kanarya P99 taban çizgisinin 1,5 katı.
2. **İstek başına maliyet** — harmanlanmış $. İhlal: taban çizgisinin %20 üstü.
3. **Hata / red oranı** — 5xx artı açık redler. İhlal: taban çizgisinin 2 katı.
4. **Çıktı uzunluğu dağılımı** — ortalama + P99. İhlal: dağılımsal kayma.
5. **Kullanıcı geri bildirim oranı** — başparmak-aşağı / bilet açılışları. İhlal: taban çizgisinin 1,5 katı.

### Determinizm-olmama yeni oynaklıktır

Özdeş girdiler özdeş-olmayan çıktılar üretir. Sebepler:

- GPU FP birleşmemesi (kayan nokta indirgeme sırası toplu iş başına değişir).
- Toplu-iş boyutu oynaklığı (aynı prompt toplu-iş 128'de vs toplu-iş 16'da).
- Örnekleme (sıcaklık > 0).

Ölçüldü: özdeş değerlendirme setlerinde çalıştırma-arası %15'e kadar doğruluk oynaması. Bir yayılımda "kararlı" demek, metriklerin beklenen oynaklık dahilinde olduğu anlamına gelir, taban çizgisiyle özdeş değil. Geçitleri gürültü tabanının üstüne ayarlayın.

### Maliyet bir değişkendir

%20 daha iyi bir model, çağrı başına 3 kat pahalı olabilir. İstek başına maliyet beş geçitten biridir. Birim ekonomisini bozan "daha iyi" bir modeli göndermek, geri alma durumudur.

### Geri alma silahtır

- Politika flag'i (özellik flag sistemi): yüzdeyi yapılandırmada çevirin; saniyeler sürer.
- Model sabitleme (kayıt defteri özeti): sabitlenmiş model otomatik yükseltmez.
- Geri alma = flag'i geri çevir + sabitlenmiş özeti öncekine ayarla. Saatler değil saniyeler.

Yığınınız geri alma için yeniden dağıtım gerektiriyorsa, yaymadan önce bunu düzeltin.

### Araçlar

**Argo Rollouts** / **Flagger** — Kubernetes kademeli teslim denetleyicileri. Istio/Linkerd ağırlıklı yönlendirmesiyle bütünleşir.

**Istio ağırlıklı yönlendirme** — servis-ağı düzeyinde trafik bölme.

**KServe / Seldon Core** — yerleşik kanaryalı model sunma.

**Özellik flag'leri** — LaunchDarkly, Flagsmith, Unleash. Yeniden dağıtım olmadan politika düzeyinde çevirme.

### Metrik ritmi

Kanarya geçitleri, trafik hacmine bağlı olarak her 5-15 dakikada bir kontrol eder. Dakikada 10 istek ile %1 trafik 50-150 veri noktası verir — gecikme için yeterli ama kullanıcı geri bildirimi için gürültülü. %10, ~10 kat daha fazla verir. İlerlemeler, her adımda yeterli örnek toplamak için yeterince uzun duraklamalıdır.

### A/B adımı isteğe bağlıdır

Yeni model belirgin şekilde farklıysa (farklı davranış, farklı maliyet eğrisi, farklı ton), kanarya geçtikten sonra %50'de A/B testi yapın. Yalnızca geliştirilmiş bir versiyonsa, kanarya geçitleri geçtiğinde %100'e atlayın.

### Hatırlamanız gereken sayılar

- Kanarya ilerlemesi: %1 → %10 → %25 → %50 → %75 → %100.
- Determinizm-olmama tavanı: özdeş girdilerde çalıştırma-arası %15'e kadar oynaklık.
- Beş kanarya metriği: gecikme, maliyet, hata/red, çıktı uzunluğu, kullanıcı geri bildirimi.
- Maliyet geçidi: taban çizgisinin %20 üstü ihlaldir.
- Geri alma: saatler değil saniyeler.

## Kullanım

`code/main.py`, enjekte edilmiş gerilemelerle bir kanarya yayılımını simüle eder. Yayılımın hangi aşamada durduğunu ve hangi geçidin tetiklendiğini raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-rollout-runbook.md` üretir. Aday model, taban çizgisi ve risk toleransı verildiğinde, gölge→kanarya→%100 planı tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. %25 maliyet gerilemesi enjekte edin. Kanarya hangi aşamada durur?
2. Yeni modeliniz çevrimdışı %3 doğruluk kazancına sahip ama istek başına maliyet +%18. Gönderilir mi? Politikaya bağlıdır — her iki yolu da yazın.
3. Uçtan uca 60 saniyenin altında bir geri alma tasarlayın. Gerekli altyapıyı listeleyin.
4. Determinizm-olmama değerlendirmenizde ±%7 gösteriyor. Yanlış alarm vermemek için kanarya geçitlerini ayarlayın. Hangi çarpanları kullanıyorsunuz?
5. Gölge modu, kanaryadan önce %40'lık bir maliyet artışını yakalar. Gölgede ateşlenen uyarı kuralını yazın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Gölge modu | "yenisine çoğalt" | Kayıt için sıfır-etki adaya gönder |
| Kanarya | "kademeli trafik" | Geçitlerle kademeli kullanıcıya maruz yayılım |
| Geçitler | "yayılım kontrolleri" | İlerlemeyi engelleyen metrik eşikleri |
| Determinizm-olmama | "LLM oynaklığı" | İndirgenemez çalıştırma-arası farklılıklar |
| Politika flag'i | "flag çevirme geri alma" | Yapılandırma düzeyinde geri alma, saatler değil saniyeler |
| Model sabitleme | "kayıt defteri özeti" | Bir model versiyonuna değişmez referans |
| Argo Rollouts | "K8s kademeli" | Kubernetes-native kanarya/geri alma denetleyicisi |
| KServe | "çıkarım K8s" | Kanarya temelleriyle model sunma |
| Istio ağırlıklı | "ağ bölme" | Servis-ağı trafik bölücü |

## Ek Okuma

- [TianPan — Üretimi Kırmadan AI Özellikleri Yayınlama](https://tianpan.co/blog/2026-04-09-llm-gradual-rollout-shadow-canary-ab-testing)
- [MarkTechPost — ML Modellerini Güvenle Dağıtma](https://www.marktechpost.com/2026/03/21/safely-deploying-ml-models-to-production-four-controlled-strategies-a-b-canary-interleaved-shadow-testing/)
- [APXML — Gelişmiş LLM Dağıtım Kalıpları](https://apxml.com/courses/mlops-for-large-models-llmops/chapter-4-llm-deployment-serving-optimization/advanced-llm-deployment-patterns)
- [Argo Rollouts docs](https://argo-rollouts.readthedocs.io/)
- [Flagger docs](https://docs.flagger.app/)
