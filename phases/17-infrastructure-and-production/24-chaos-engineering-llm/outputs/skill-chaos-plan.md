---
name: chaos-plan
description: Bir LLM kaos mühendisliği planı tasarla — ön koşulları doğrula, dört düzlemi kur, aracı seç, üç güvenli deneyle başla ve güvenlik-düzlemi kapılarını uygula.
version: 1.0.0
phase: 17
lesson: 24
tags: [chaos-engineering, litmuschaos, chaosmesh, harness, llm-chaos, game-day]
---

Yığın (Kubernetes / VM'ler / yönetilen), SLI/SLO olgunluğu, gözlemlenebilirlik kalitesi ve ekip nöbet olgunluğu verildiğinde bir kaos planı üret.

Üretilecekler:

1. **Ön koşul kontrolü.** SLI/SLO tanımlı, gözlemlenebilirlik bağlı, geri alma otomatik, runbook'lar yapılandırılmış, nöbet rotasyonu olduğunu doğrula. Eksik olan varsa, üretim kaosu çalıştırmayı reddet.
2. **Dört düzlem.** Her düzlem için araçları adlandır (kontrol, hedef, güvenlik, gözlemlenebilirlik). Gözlemlenebilirlik için Phase 17 · 13'e yönlendir.
3. **Üç ilk deney.** Pod öldürmeyle başla. Sonra sağlayıcı 429. Sonra bellek aşırı yüklemesi. Her biri patlama-yarıçapı sınırı, süre, başarı ölçütü ile.
4. **Güvenlik kapıları.** Yanma oranı (beklenenin >2 katı), patlama yarıçapı (filonun <%30), trace-ID etiketlemesi, bastırma pencereleri.
5. **Kadans.** Haftalık küçük kanarya. Aylık oyun günü (ekipler-arası). Üç aylık dayanıklılık denetimi.
6. **Araçlar.** LitmusChaos (OSS, CNCF mezunu), Chaos Mesh (OSS, CNCF sandbox), Harness Chaos (ticari AI-destekli), AWS FIS / Azure Chaos Studio (yönetilen bulut-native).

**Hard rejects (zorunlu redler):**
- Beş ön koşul olmadan üretimde kaos çalıştırmak. Reddet — gerçek bir olaya dönüşür.
- Patlama-yarıçapı sınırları olmayan deneyler. Reddet.
- Trace-ID etiketlemesi olmayan deneyler. Reddet — uyarıları ayıklamak imkânsız.

**Reddetme kuralları:**
- Ekip staging'de hiçbir başarılı deney çalıştırmadıysa, staging'de bir tane yeşil olana kadar üretim kaosunu reddet.
- Olay hacmi zaten yüksekse (>2/hafta), eklenen kaosu reddet — önce stabilize et.
- Ekipte SLO yoksa, herhangi bir deneyden önce SLO zorunlu kıl.

**Çıktı:** Ön koşul kontrolü, dört-düzlem araçları, üç ilk deney, güvenlik kapıları, kadans içeren tek sayfalık bir plan. Üç aylık bağımlılık-haritası güncelleme taahhüdüyle bitir.
