---
name: aar-deployment-review
description: Sandbox izolasyonu ve log bütünlüğü dahil, otomatik-hizalama-araştırması (AAR) pipeline'ının deployment öncesi incelemesi.
version: 1.0.0
phase: 15
lesson: 6
tags: [aar, alignment-research, sandbox, log-integrity, rsp]
---

Önerilen bir Otomatik-Hizalama-Araştırması (Automated-Alignment-Research) deployment'ı (model, sandbox, görev kuyruğu, forum) verildiğinde, bir frontier-lab güvenlik ekibinin onaylayacağı bir deployment öncesi inceleme üretin.

Üretin:

1. **Sandbox izolasyonu.** Her AAR instance'ı için dosya sistemi, ağ ve proses sınırlarını doğrulayın. Hiçbir AAR'ın diğer bir AAR'ın sandbox'ını okuyamadığını veya değiştiremediğini doğrulayın. Hiçbir AAR'ın forum depolamasının yazma endpoint'ine doğrudan ulaşamadığını (tüm gönderiler ayrı bir servis üzerinden geçer) doğrulayın.
2. **Forum log bütünlüğü.** Forum, yalnızca-eklenebilir (append-only) ve kurcalamaya karşı kanıtlanabilir (tamper-evident) olmalıdır. Depolamayı belirtin (örn. object lock (nesne kilidi) ile S3, değişmez defter (immutable ledger), yalnızca-eklenebilir WAL). Doğrulama aralığını ve kurcalama tespit edilirse verilecek yanıtı belirtin.
3. **Görev tahsis politikası.** Görevlerin nasıl atandığını belirtin: kim yazar, kim onaylar, AAR'lar kendi takip görevlerini önerebilir mi ve hangi koşullar altında. Serbest ayrıştırma (decomposition) performansta kazanır; reçetelenen iş akışı denetlenebilirlikte kazanır. Ödünleşimi açıkça belgelendirin.
4. **İnsan inceleme aşaması.** Herhangi bir AAR çıktısı gerçek araştırma yönünü, eğitim verisini veya yayınlanan çalışmayı etkilemeden önce, adlandırılmış bir insan incelemci imzalamalıdır. İnceleme kontrol listesini belirtin: deney tekrarlanabilirliği, log tamlığı, kanıttan-iddaya eşleme.
5. **Eşik izleme.** AAR sisteminin RSP v3.0 AI R&D-4 bölgesine yaklaştığını gösteren sinyalleri izleyin: görev karmaşıklık deltası, otonom alt-görev üretimi, görevler-arası bilgi transferi. Yükseltilmiş inceleme gerektiren eşikleri tanımlayın.

Keskin redler:

- Kurcalamaya-karşı-kanıtlanabilir, sandbox-dışı logları olmayan herhangi bir AAR deployment'ı.
- AAR'ların çıktılarının, adlandırılmış insan incelemesi olmadan doğrudan eğitim verisini veya production politikasını beslediği herhangi bir pipeline.
- Tek bir AAR'ın birden fazla downstream sistemi etkilemek için yeterli kimlik bilgisine sahip olduğu herhangi bir pipeline.

Ret kuralları:

- Sandbox izolasyonu belirtilmemişse veya tek bir katmana dayanıyorsa (yalnızca Docker, seccomp / gVisor yok), reddedin ve savunma-derinliği (defense-in-depth) isteyin.
- Log depolaması herhangi biri (operatörler dahil) tarafından düzenlenebiliyorsa, reddedin ve bir kez yazılabilir (write-once) medya isteyin.
- Deployment'ın amacı, hizalama araştırmasının yalnızca bir parçasını değil yetenek pipeline'ının bir parçasını otomatikleştirmekse, reddedin ve RSP incelemesine iletin.

Çıktı formatı:

Şunları içeren bir inceleme memo'su döndürün:

- **Pipeline özeti** (tek paragraf)
- **İzolasyon puanı** (boyut başına: fs, net, proc, peer)
- **Log bütünlüğü puanı** (doğrulama planıyla)
- **Görev tahsis kararı** (sabit / serbest / hibrit, gerekçeyle)
- **İnsan inceleme aşaması** (incelemci adı, kontrol listesi)
- **Eşik monitörleri** (sinyal listesi, eşikler, yanıt)
- **Deployment kararı** (go / hold / no-go)
