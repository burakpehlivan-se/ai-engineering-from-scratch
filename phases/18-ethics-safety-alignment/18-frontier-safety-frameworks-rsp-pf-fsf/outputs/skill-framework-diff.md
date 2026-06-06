---
name: framework-diff
description: Yeni bir güvenlik çerçevesini veya sürüm notunu RSP v3.0, PF v2, FSF v3.0'a karşı karşılaştır
version: 1.0.0
phase: 18
lesson: 18
tags: [rsp, pf, fsf, frontier-safety, safety-case]
---

Yeni bir güvenlik çerçevesi, politikası veya sürüm notu verildiğinde, onu Anthropic RSP v3.0, OpenAI PF v2, DeepMind FSF v3.0 boyunca beş yapısal eksen boyunca karşılaştır.

Çıktı:

1. Katman yapısı. Çerçeve ayrık yetenek eşikleri tanımlıyor mu? Alan başına mı (FSF-tarzı) yoksa küresel mi (RSP-tarzı)?
2. CBRN eşiği. Hangi CBRN değerlendirmesi gerekli? WMDP'ye (Ders 17) veya eşdeğerine başvuruyor mu? Bir çıkarma çalışması içeriyor mu?
3. Yapay zeka Ar-Ge eşiği. Model-otonom-arastırma eşiği var mı? Çıta "giriş seviyesi araştırmacı" (Anthropic AI R&D-2) mi yoksa "ölçeklendirmeyi önemli ölçüde hızlandırmak" (Anthropic AI R&D-4) mı?
4. Rakip ayarlaması. Çerçeve, rakipler karşılaştırılabilir güvenlik önlemleri olmadan sevk ederlerse gereksinimlerin azaltılmasına izin veriyor mu? Uygun şekilde yarış-dinamiği veya teşvik-uyumluluğu olarak çerçevele.
5. Güvenlik durumu yapısı. Yazılı bir güvenlik durumu gerekli mi? İzlemeyi, okunaksızlığı veya yapamazlığı mı hedefliyor? Kanıt çıtası nedir?

Kesin redler:

- Katman başına yetenek eşikleri olmayan herhangi bir güvenlik çerçevesi.
- Dış yönetişim çapraz referansını (UK AISI, US CAISI, EU AI Office) atlayan herhangi bir çerçeve.
- Spesifik eşik sayıları olmadan "yayınlanmış tüm çerçevelerle uyumluyuz" iddiasında bulunan herhangi bir çerçeve.

Ret kuralları:

- Kullanıcı hangi çerçevenin "en iyi" olduğunu sorarsa, sıralamayı reddet ve yapısal hizalamaya yönlendir.
- Kullanıcı sayısal bir eşik önerisi isterse, reddet — eşikler laboratuvara özgüdür ve ölçüm altyapılarına bağlıdır.

Çıktı: Üç çerçeveye karşı tek sayfalık yan yana karşılaştırma, işaretlenmiş boşluklar ve eklenmesi gereken spesifik bir eşik önerisi. RSP v3.0, PF v2, FSF v3.0'ı her birini bir kez alıntıla.
