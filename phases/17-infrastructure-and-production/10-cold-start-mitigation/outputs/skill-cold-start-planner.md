---
name: cold-start-planner
description: Serverless LLM dağıtımları için soğuk başlangıç hafifletmelerini seç ve yığ. Aşamaları bütçele (düğüm, imaj, ağırlıklar, motor, ilk ileri) ve hafifletmeleri SLA ile eşle.
version: 1.0.0
phase: 17
lesson: 10
tags: [cold-start, serverless, bottlerocket, model-streamer, gpu-snapshot, warm-pool, serverlessllm]
---

Model boyutu, SLA (TTFT P99), trafik şekli (sabit vs patlamalı) ve bütçe duruşu verildiğinde bir soğuk başlangıç hafifletme planı üret.

Üretilecekler:

1. **Soğuk başlangıç bütçesi.** Ham soğuk başlangıç yolunu ayır (düğüm sağlama, imaj çekme, ağırlıkları HBM'e getirme, motor başlatma, ilk ileri geçiş). Belirtilen model boyutu için 2026 nominal saniyeleri kullan.
2. **Katman seçimi.** Toplamı SLA'nın altına getiren asgari katman sayısını seç: önceden-ekilmiş imaj (L1), model streamer (L2), GPU snapshot (L3), sıcak havuz (L4), kademeli yükleme (L5). Her katmanı, saldırdığı belirli aşamaya karşı gerekçelendir.
3. **Sıcak havuz boyutlandırması.** Birincil yol için `min_workers` belirt. SLA 70B+ modelde TTFT P99 < 60s ise, maliyetten bağımsız olarak sıcak havuzu zorunlu kıl.
4. **Maliyet tahmini.** Seçilen sıcak havuz için aylık GPU maliyeti ve günde beklenen soğuk başlangıç sayısı.
5. **Kuyruk politikası.** Taze bir kopyadaki ilk kullanıcıya ne olur — sıcak bir kopyaya mı kuyruğa alınır yoksa soğuk başlangıç vergisini mi öder? Belirli bir politika adlandır (ör. "ilk isteği 10s içinde herhangi bir sıcak kopyaya yönlendir; soğuğa düş").
6. **Başarısızlık modu.** Bir sıcak kopya oturum ortasında ölürse ne olur. Kurtarma otomatik mi (canlı geçiş) yoksa sonraki istekte soğuk başlangıç mı?

**Hard rejects (zorunlu redler):**
- Aylık maliyeti hesaplamadan "sadece sıcak havuz ekle" önermek.
- Saldırdığı belirli bir aşamayı belirtmeden bir hafifletme iddia etmek (ör. "180s imaj çekmeyi ortadan kaldırdığını söylemeden Bottlerocket kullan").
- GPU snapshot'ları üzerindeki per-GPU-topolojisi kısıtını yok saymak — platform SKU'yu taşırsa, snapshot'lar geçersiz olur.

**Reddetme kuralları:**
- SLA taze 70B soğuk başlangıçta TTFT P99 < 5s ise ve sıcak havuz yoksa, reddet — 2026 altyapı hızlarında matematiksel olarak imkânsız.
- Bütçe sıcak havuzu yasaklıyorsa ancak SLA 30s altında soğuk başlangıç gerektiriyorsa, platforma-özgü düzeltmeyi adlandır (Modal GPU snapshot'ları, Baseten ön-ısıtma) ve onu olmadan farklı bir platformda SLA vaat etmeyi reddet.
- Operatör patlamalı trafikle ve 70B modelle sıfıra-kadar-ölçekleme istiyorsa, SLA vaat etmeyi reddet — matematik snapshot'lar veya sıcak havuzlar olmadan çalışmaz.

**Çıktı:** Aşamalar, katmanlar, `min_workers`, aylık maliyet, kuyruk politikası, başarısızlık modu listeleyen tek sayfalık bir plan. Uyarı verilecek tek metrikle bitir: son kayan saat üzerinden P99 soğuk başlangıç süresi.
