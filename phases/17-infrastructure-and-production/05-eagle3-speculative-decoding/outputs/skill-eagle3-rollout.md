---
name: eagle3-rollout
description: Yayınlamadan önce gerçek trafik üzerinde kabul oranı alfa'yı ölçen aşamalı bir EAGLE-3 spekülatif-kod çözme yayılım planı üret.
version: 1.0.0
phase: 17
lesson: 05
tags: [speculative-decoding, eagle-3, vllm, alpha, production-rollout]
---

Hedef model, donanım (GPU türü ve sayısı), trafik tanımı (genel sohbet / kod / özelleşmiş), eşzamanlılık hedefi ve mevcut taban çizgisi metrikleri (TTFT, ITL, verim) verildiğinde, aşamalı bir EAGLE-3 yayılım planı üret.

Üretilecekler:

1. **Taban çizgisi ölçüm planı.** Hangi kıyaslama (LLMPerf, GenAI-Perf veya üretim gölgesi), hangi istem dağılımı, hangi eşzamanlılık noktası, hangi metriklerin kaydedileceği (TTFT ortalama/P99, ITL ortalama/P99, verim, eşzamanlılık).
2. **Taslak-kafa seçimi.** Genel sohbet için ShareGPT üzerinde eğitilmiş EAGLE-3. Özelleşmiş trafik (kod, tıp, hukuk) için alana-özgü eğitilmiş EAGLE-3 veya yayınlamadan önce bir tane eğitme kararı.
3. **Yapılandırma.** Tam vLLM `speculative_config` alanları (method, model, num_speculative_tokens). v0.18.0 uyumluluğunu not et: taslak-model spekülasyonu `--enable-chunked-prefill` ile birleştirilemez; V1'de N-gram GPU spec decode istisnadır.
4. **Alfa kapısı.** Üretim eşzamanlılığında alfa >= 0.55 hedefi. Ölçüm prosedürü: 24 saat gölge trafik, vLLM `spec_decode_metrics` kaydı, kabul edilen token'ları istenen taslak uzunluğuna böl. Herhangi bir 1-saatlik pencerede alfa 0.45'in altına düşerse kill switch.
5. **Kuyruk izleme.** P99 ITL deltasını çiz (spec açık - spec kapalı). Delta pozitifse, reddedilen-taslak iki-geçiş kalıbı ısırıyor. K'yı azalt veya bu iş yükünde devre dışı bırak.
6. **Başa-baş kontrolü.** Rapor edilen eşzamanlılıkta, mevcut doğrulama yükü için başa-baş alfayı hesapla. Yalnızca ölçülen alfa başa-baş değerini en az 0.1 aştığında yayınla.

**Hard rejects (zorunlu redler):**
- Üretim trafiğinde alfa ölçmeden yayınlamak. Reddet ve 24-saatlik bir gölge ölçümü zorunlu kıl.
- Ölçülen alfayı adlandırmadan 2-3x hız iddia etmek.
- Gecikmenin kısıt olmadığı çevrimdışı toplu işler için spekülatif kod çözmeyi etkinleştirmek.
- vLLM v0.18.0 üzerinde taslak-model spekülasyonunu parçalı prefill ile birleştirmek. Sert uyumsuzluk.

**Reddetme kuralları:**
- Trafik ağırlıklı olarak çok kısa çıktılarsa (ortalama 50 token altı), reddet. Taslak yükü baskındır; düz hedefi yayınla.
- Donanım tüketiciyse (RTX 4090 / 5090) ve toplu iş boyutu 8'in altında kalıyorsa, düz hedefi öner — doğrulama yükünün toplu-iş-amortismanı donanımın sağlayamayacağı eşzamanlılığı gerektirir.
- Kullanıcı ölçüm döngüsü olmadan K'nın otomatik-ayarlanmasını istiyorsa, reddet. K, ölçülen alfa ve doğrulama yükünden seçilir; hiçbir otomatik-ayarlama ölçümün yerini tutmaz.

**Çıktı:** Taban çizgisi → yapılandırma → alfa kapısı → kuyruk izleme → başa-baş onayı listeleyen tek sayfalık aşamalı bir yayılım planı. Teşhise bağlı olarak alana-özgü EAGLE-3 eğitimi, daha düşük K veya düz hedefe dönüşten birini adlandıran bir "sırada ne ölçülecek" paragrafıyla bitir.
