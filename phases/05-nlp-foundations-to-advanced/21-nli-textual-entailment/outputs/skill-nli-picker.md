---
name: nli-picker
description: Sınıflandırma / sadakat (faithfulness) / sıfır-atış (zero-shot) görevi için NLI (Doğal Dil Çıkarımı) modeli, etiket şablonu ve değerlendirme kurulumu seçer.
version: 1.0.0
phase: 5
lesson: 21
tags: [nlp, nli, zero-shot]
---

Bir kullanım senaryosu (sadakat kontrolü, sıfır-atış sınıflandırma, belge düzeyinde çıkarım) verildiğinde şunu üretirsiniz:

1. Model. Adlandırılmış NLI kontrol noktası. Nedeni alana, uzunluğa ve dile bağlı.
2. Şablon (sıfır-atış ise). Sözlelleştirme örüntüsü. Örnek.
3. Eşik. Karar kuralı için entailment (içerim) kesme noktası. Kalibrasyona dayalı neden.
4. Değerlendirme. Held-out etiketli kümede doğruluk, yalnızca hipotez baseline'ı, adversarial alt küme.

100 örneklik etiketli sağlık kontrolü olmadan sıfır-atış sınıflandırmayı yayınlamayı reddedin. Belge uzunluğundaki öncüllerde cümle düzeyinde NLI modeli kullanmayı reddedin. NLI'nın halüsinasyonu çözdüğü yönündeki herhangi bir iddiayı işaretleyin — onu azaltır, ortadan kaldırmaz.
