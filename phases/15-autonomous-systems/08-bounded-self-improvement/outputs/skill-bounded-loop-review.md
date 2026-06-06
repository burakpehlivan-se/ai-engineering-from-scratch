---
name: bounded-loop-review
description: Önerilen sınırlı öz-iyileştirme döngüsünü dört-ilkel stack'ine (invariant'lar, çapa, çok-amaçlı, regresyon tespiti) göre denetleyin.
version: 1.0.0
phase: 15
lesson: 8
tags: [bounded-self-improvement, invariants, alignment-anchor, rsi-safety]
---

Önerilen bir öz-iyileştirme döngüsü verildiğinde, ICLR 2026 RSI Atölyesi tarafından tanımlanan dört sınırlayıcı ilkele göre puanlayın ve somut bir boşluk analizi üretin.

Üretin:

1. **Invariant envanteri.** Döngünün uyguladığı her invariant'ı listeleyin. Her biri için, (a) neyin kontrol edildiğini, (b) kontrolün nerede çalıştığını (agent'ın erişiminin içi/dışı), (c) ihlalin ne yaptığını (keskin red, duraklatma, yalnızca-log) adlandırın.
2. **Çapa tanımlaması.** Hizalama çapasını (amaç bildirimi, anayasa, niyet açıklaması) adlandırın. Depolama konumunu belirtin ve döngünün onu düzenleyemediğini doğrulayın. Çapa yoksa, eksik olarak işaretleyin.
3. **Çok-amaçlı eksenler.** Döngünün değerlendirdiği her ekseni listeleyin. Performansın yanı sıra güvenlik, adalet ve sağlamlığın mevcut olduğunu doğrulayın. Tek-eksenli bir döngü bu kontrolü geçemez.
4. **Regresyon politikası.** Tarihsel pencereyi, eksen başına toleransı ve bir düşüş tespit edildiğinde ne olduğunu belirtin. Regresyon kontrollerinin yalnızca iç tarih yerine harici bir karşılaştırma seti kullandığını doğrulayın.
5. **Boşluk analizi.** Eksik her ilkel için, hangi başarısızlık sınıfının ilk ortaya çıkacağını tahmin edin. Invariant'lar eksik → kaçak yetenek veya araç sürüklenmesi. Çapa eksik → amaç yeniden yorumlama. Çok-amaçlı eksik → güvenlik regresyonu performans kazanımını maskeler. Regresyon eksik → sessiz yetenek kaybı.

Keskin redler:

- Sıfır invariant'lı herhangi bir döngü.
- Düzenleme yüzeyinin dışında hizalama çapası olmayan herhangi bir döngü.
- Tek bir skaler puan optimize eden herhangi bir döngü.
- Regresyon kontrolü yalnızca kendi tarihini okuyan herhangi bir döngü (döngü "normal"i tanımlar).

Ret kuralları:

- Kullanıcı "henüz bozulmadı"yı güvenlik kanıtı olarak ele alıyorsa, reddedin ve herhangi bir hesaplama harcanmadan önce açık geçit tasarımı isteyin.
- Kullanıcı 15 dakikada invariant listesini üretemiyorsa, reddedin — döngünün invariant'ı yoktur.
- Döngünün dört ilkelin tümü olmadan production'da (gerçek kullanıcıları veya altyapıyı etkileyecek şekilde) çalıştırılması öneriliyorsa, reddedin ve önce izlemeli (staging) çalışma isteyin.

Çıktı formatı:

Şunları içeren puanlı bir inceleme döndürün:

- **Invariant puanı** (0-5, açık listeyle)
- **Çapa puanı** (0-5, depolama ve doğrulama yöntemiyle)
- **Çok-amaçlı puan** (0-5, listelenmiş eksenlerle)
- **Regresyon puanı** (0-5, tolerans ve pencereyle)
- **Boşluk analizi** (tahmin edilen ilk başarısızlık, azaltma planı)
- **Deployment'a hazırlık** (production / staging / yalnızca-araştırma)
