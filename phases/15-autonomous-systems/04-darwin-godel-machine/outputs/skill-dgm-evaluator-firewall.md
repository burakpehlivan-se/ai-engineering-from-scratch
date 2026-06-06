---
name: dgm-evaluator-firewall
description: Belgelenmiş reward hacking'ten kaçınmak için Darwin-Godel-Machine tarzı bir öz-değiştiren agent döngüsünün ihtiyaç duyduğu değerlendirici ayrımını belirleyin.
version: 1.0.0
phase: 15
lesson: 4
tags: [dgm, self-modification, reward-hacking, evaluator, sandbox]
---

Önerilen bir öz-değiştiren agent döngüsü (agent scaffolding, değerlendirici pipeline'ı, deployment hedefi) verildiğinde, değerlendiriciyi agent'ın erişemeyeceği yerde tutan bir firewall (güvenlik duvarı) spesifikasyonu üretin. DGM makalesi, agent'ın puanları yükseltmek için kendi güvenlik işaretçilerini kaldırdığını belgeledi; bu skill kontrolü sağlar.

Üretin:

1. **Dosya sistemi sınırı.** Agent'ın düzenleyebileceği her dosyayı listeleyin. Değerlendiricinin okuduğu her dosyayı listeleyin. Kesişim boş olmalıdır. Değilse, onu boş yapmak için gerekli taşımayı belirtin.
2. **Proses sınırı.** Değerlendirici, agent'ın kontrol etmediği bir proseste çalışmalıdır. Container'ı veya sandbox'ı belirtin. Agent'ın shell erişimi varsa, süreç içi korumaları atlayabilir.
3. **Ağ ve secret sınırı.** Agent, değerlendirici girdilerini getiren veya puanları gönderen CI secret'larını düzenleyememelidir. Secret'ların nerede yaşadığını ve nasıl bağlandığını listeleyin.
4. **Skor giriş sözleşmesi.** Skorlar, değerlendiriciden döngünün arşivine döner. Bu yol tek kanaldır. Agent'ın gelecekteki puanlamayı etkileyen yazabileceği her şey sözleşmeyi bozar.
5. **Mutasyon inceleme listesi.** Kabulden önce manuel inceleme gerektiren agent düzenleme sınıflarını listeleyin: yeni bağımlılıklar, puanlamayla ilgili kodun düzenlenmesi, sandbox yapılandırmasının düzenlenmesi, loglama veya izlemenin düzenlenmesi.

Keskin redler:

- Değerlendiricinin agent kaynağıyla aynı depoda olması. Dışarı taşıyın.
- Değerlendiricinin agent prosesi içinde bir Python import olarak çalışması. Bir alt süreçte çalıştırın.
- Agent'ın sınırın kendi tarafında uygulanan herhangi bir skor ayarlaması. Tüm ayarlamalar sunucu tarafında olmalıdır.
- Agent'ın kendi kodunu düzenleyerek susturabileceği herhangi bir loglama.

Ret kuralları:

- Kullanıcı, agent'ın düzenleyebileceği her dosyayı adlandıramıyorsa, reddedin ve önce dosya düzeyinde yazma erişimi denetimi isteyin.
- Değerlendiricinin hold-out girdileri yoksa, reddedin — bu Ders 3'ün denetimi, bir ön koşuldur.
- Deployment yüzeyi, değerlendiricinin kendisine yönelik mutasyonları içeriyorsa (önerilen bir bağımlılık güncellemesi yoluyla dolaylı olarak bile), reddedin ve manuel bir firewall inceleme adımı isteyin.

Çıktı formatı:

Şunları içeren tek sayfalık bir spesifikasyon döndürün:

- **Agent yazma yüzeyi** (yollar, glob'lar)
- **Değerlendirici okuma yüzeyi** (yollar, endpoint'ler)
- **Kesişim** (boş olmalı; diff'i gösterin)
- **Proses modeli** (değerlendirici nasıl izole ediliyor)
- **Secret envanteri** (nerede ve nasıl bağlı)
- **İnceleme-gerektiren mutasyon sınıfları** (maddeli)
- **İmza satırı** (firewall invariant'ını kim sahipleniyor)
