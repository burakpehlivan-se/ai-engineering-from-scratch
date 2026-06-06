---
name: horizon-interpretation
description: Bir satıcının zaman-ufku (time-horizon) iddiasını inceleyin ve benchmark iddiası ile deployment gerçekliği arasında bir boşluk analizi üretin.
version: 1.0.0
phase: 15
lesson: 21
tags: [metr, time-horizon, hcast, re-bench, eval-vs-deploy, external-evaluation]
---

Bir satıcının yayınlanmış zaman-ufku (time-horizon) iddiası (örn. "modelimiz %50 güvenilirlikle 14 saatlik görevleri tamamlıyor") verildiğinde, deployment-gerçeklik deltasını nicelendiren ve herhangi bir metodolojik zayıflığı işaretleyen bir boşluk analizi üretin.

Üretin:

1. **Metodoloji denetimi.** Görev setini tanımlayın (HCAST, RE-Bench, SWAA veya özel). Lojistik uyumun açıklandığını (eğim, örneklem büyüklüğü, güven aralığı) doğrulayın. Metodoloji açıklaması olmayan bir ufk (horizon) bir pazarlama iddiasıdır.
2. **Görev dağılımı uyumu.** Satıcının benchmark görev dağılımını kullanıcının production görev dağılımına eşleyin. Maddi olarak ayrılıyorlarsa (satıcı SWE görevlerini ölçüyor, production müşteri-destek akışları), sayı transfer olmaz.
3. **Eval-bağlam boşluğu.** Benchmark horizon'u ile deployment gerçekliği arasında %10-40'lık bir boşluk uygulayın. Eval-bağlam oyunu (gaming) üzerine Anthropic 2024 alignment-faking çalışmasını ve 2026 Uluslararası AI Güvenliği Raporu'nu kaynak gösterin. Gerçek boşluk eval protokolüne bağlıdır; oyun yapılandırılmamış görevlerde daha yüksektir.
4. **Araç boşluğu.** Benchmark araçları temiz ve iyi-instrümanlıdır. Production araçları daha dağınıktır. Ek bir %5-30 güvenilirlik indirimi tahmin edin.
5. **Human-in-the-loop varsayımı.** Benchmark'lar HITL olmadığını varsayar. HITL'li production agent'ları daha yüksek güvenilirlikte ama daha düşük otonomide çalışır. Horizon yorumunu buna göre ayarlayın.

Keskin redler:

- Kaynak metodolojisi veya örneklem büyüklüğü olmayan ufk iddiaları.
- Bir benchmark horizon'unun deployment güvenilirliğini tahmin ettiği iddiaları.
- Satıcıların 2025-veya-daha-erken bir ufk sayısını mevcut olarak göstermesi (ikiye katlanma süresi ~7 aydır; 2025 sayıları bir yıl içinde eskimiştir).
- %50 horizon'unu "çoğu zaman çalışacak" olarak ele almak — %50 güvenilirlik bir yazı tura atmaktır.

Ret kuralları:

- Satıcı metodolojiyi açıklamıyorsa, reddedin ve kaynak makale veya blog gönderisini isteyin.
- Benchmark dağılımı production dağılımıyla örtüşmüyorsa, reddedin ve iç değerlendirme isteyin.
- Satıcı, spesifik eval pipeline'larında oyun denetimi olmadan ufukları gösteriyorsa, sayıyı güvenilirlik tahmini olarak alıntılamayı reddedin.

Çıktı formatı:

Şunları içeren bir ufk-yorumlama memo'su döndürün:

- **Kaynak metodoloji** (suite, uyum yöntemi, örneklem büyüklüğü, GA)
- **Dağılım örtüşmesi** (benchmark vs production; % eşleme)
- **Eval-bağlam boşluğu tahmini** (düşük / orta / yüksek, gerekçeyle)
- **Araç boşluğu tahmini** (düşük / orta / yüksek)
- **HITL varsayımı** (benchmark-tarzı otonom vs production HITL)
- **Deployment-ayarlı ufk** (boşluk ve araç indirimlerinden sonra ufk)
- **Hazırlık kararı** (production / staging / yalnızca-araştırma)
