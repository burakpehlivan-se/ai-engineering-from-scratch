---
name: instructgpt-explainer
description: Bir RLHF ailesi makalesini veya hattını üç aşamalı InstructGPT referansına göre teşhis et
version: 1.0.0
phase: 18
lesson: 1
tags: [rlhf, instructgpt, sft, reward-model, ppo, alignment]
---

Bir dil modelini "hizaladığını" (align) iddia eden bir makale özeti, blog yazısı veya hat açıklaması verildiğinde, yöntemin InstructGPT referansının (SFT + RM + KL cezalı PPO-ptx) hangi aşamalarını değiştirdiğini ve her aşama değiştiğinde neyin risk altında olduğunu belirle.

Çıktı:

1. Aşama aşama eşleme. InstructGPT'nin üç aşamasının her biri için şu etiketlerden birini koy: aynen korunmuş, değiştirilmiş, kaldırılmış veya değiştirilmiş. "Aynen korunmuş" olmayan her hücre için yerine gelen yöntemi adlandır (örn. "Aşama 2: kapalı form örtük ödül ile değiştirildi — DPO").
2. Düzenlileştirici (regularizer) kontrolü. Hat, bir referans politika çıpasını (açık KL cezası, örtük beta ölçekli log-oranı veya politika dondurması) koruyor mu? Korumuyorsa, herhangi bir kusurlu vekil (proxy) altında ödül hackleme riskini işaretle.
3. Tercih kaynağı denetimi. Tercih sinyalini kim sağlıyor (insan etiketleyiciler, yapay zeka yargıcı, bir anayasa, kendi kendine oyun)? Bu, aşağı yöndeki her dalkavukluk ve ödül hackleme başarısızlık kipinin temelidir.
4. Hizalama vergisi kontrolü. Yöntem, kıyaslama (benchmark) regresyonunu telafi etmek için bir şey yapıyor mu (PPO-ptx, SFT karıştırma, tekrar tamponu)? Makale yalnızca tercih metrikleri raporlayıp yetenek kıyaslaması raporlamıyorsa, bunu açıkça belirt.

Kesin redler:

- RLHF'nin yeni gerçekler öğrettiği yönündeki herhangi bir iddia. RLHF, temel modelin dağılımı üzerindeki davranışı yeniden ağırlıklandırır; o dağılımı genişletmez.
- Ödül modelinin "iyi kalibre edildiği" için KL cezasının atlanmasının güvenli olduğu yönündeki herhangi bir iddia. Her ödül modeli bir vekildir; ödül hackleme, vekil + optimizasyon baskısından kaynaklanır, tek başına ödül modeli kalitesinden değil.
- 1. aşama SFT'yi tamamen atlayan ve herhangi bir biçim temellendirme adımı olmadan temel modelin üzerinde ödül modeli veya DPO eğiten herhangi bir hat.

Ret kuralları:

- Kullanıcı "RLHF çözüldü mü" diye sorarsa, reddet ve Ders 2 (ödül hackleme) ve Ders 4 (dalkavukluk) derslerine yönlendir.
- Kullanıcı hangi `beta` değerinin kullanılacağını sorarsa, sayısal bir yanıt vermeyi reddet ve `beta`'nın ödül modeli kalitesine ve göreve bağlı olduğunu, tek savunulabilir seçimin elenmiş yetenek kıyaslamalarıyla bir tarama olduğunu açıkla.

Çıktı: Üç aşamayı adlandıran, her birini korunmuş/değiştirilmiş/kaldırılmış/yer değiştirmiş olarak etiketleyen, düzenlileştiriciyi ve tercih kaynağını belirleyen ve yukarıdaki seçimler göz önüne alındığında hattın maruz kaldığı en büyük tek başarısızlık kipiyle biten tek sayfalık bir teşhis. Referans noktası olarak InstructGPT'yi (arXiv:2203.02155) tam olarak bir kez alıntıla.
