---
name: provenance-audit
description: Bir içerik dağıtımının kaynak-doğrulama zincirini damgalama ve C2PA meta verileri boyunca denetle
version: 1.0.0
phase: 18
lesson: 23
tags: [watermarking, synthid, stable-signature, c2pa, provenance]
---

Kaynak-doğrulama (provenance) iddiası olan bir içerik dağıtımı verildiğinde, kaynak-doğrulama zincirini denetle.

Çıktı:

1. Damga envanteri. Her modaliteyi (metin, görüntü, ses, video) ve her birinde uygulanan damgayı listele. Damga yok = tespit yolu yok.
2. Damga sağlamlığı. Her damga için, hayatta kaldığı karşıt sınıfı adlandır (sıkıştırma, kırpma, parafraz, ince ayar). Kirchenbauer 2023 Bölüm 6 (parafraz) ve "Stable Signature is Unstable" 2024 (ince ayar) başına sınırlamaları işaretle.
3. C2PA kapsamı. C2PA meta verileri eklenmiş mi? İmzalama zinciri güvenilir bir kimlikten mi? Meta veriler çıkarılabilir; varlığı yeterli değildir.
4. Çapraz-modal dedektör. Modaliteler arasında birleşik bir dedektör var mı (SynthID 2025) yoksa yalnızca modaliteye özgü mü?
5. Düzenleyici uyum. Dağıtım, AB Yapay Zeka Yasası Madde 50 şeffaflık yükümlülüklerini (Ağustos 2026'da yürürlüğe girer) karşılıyor mu? Şeffaflık Kodu'na (Haziran 2026 son sürüm) uyuyor mu?

Kesin redler:

- Adlandırılmış bir mekanizma ve dedektör olmadan herhangi bir "damga" iddiası.
- Yalnızca damga yokluğuna dayanan herhangi bir "özgünlük" iddiası (model-damgalanmamış ≠ özgün).
- Fernandez 2024 kaldırma saldırısının değerlendirmesi olmadan herhangi bir görüntü kaynak-doğrulama iddiası.

Ret kuralları:

- Kullanıcı "bu tüm yapay zeka içeriğini tespit edecek mi" diye sorarsa, ikili iddiayı reddet; damgalama modele özgüdür.
- Kullanıcı evrensel bir kaynak-doğrulama çözümü isterse, reddet ve damga + C2PA katmanlı yaklaşımına yönlendir.

Çıktı: Beş bölümü dolduran, modalite başına sağlamlık boşluklarını işaretleyen ve en yüksek değerli ek denetimi adlandıran tek sayfalık bir denetim. SynthID'yi (Google DeepMind), Stable Signature'ı (Fernandez ve diğerleri 2023) ve C2PA'yı her birini bir kez alıntıla.
