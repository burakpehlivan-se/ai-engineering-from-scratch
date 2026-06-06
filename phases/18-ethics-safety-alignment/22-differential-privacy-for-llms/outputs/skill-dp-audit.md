---
name: dp-audit
description: Bir dil modeli dağıtımı için ayrımsal gizlilik (differential privacy) iddiasını denetle
version: 1.0.0
phase: 18
lesson: 22
tags: [differential-privacy, dp-sgd, lora, mia, pmixed]
---

Bir dil modeli dağıtımı için gizlilik iddiası verildiğinde, iddiayı denetle.

Çıktı:

1. (ε, δ) değerleri. Hangi ε ve δ kullanıldı? Onları hangi muhasebeci hesapladı (Moments Accountant, Rényi DP, GDP)? Muhasebecisiz ε anlamsızdır.
2. DP hedefi. DP garantisi tam model üzerinde mi yoksa adaptörler (LoRA) üzerinde mi? LoRA ise, temel modelin ezberlemesi kapsanmaz.
3. MIA (üyelik çıkarma saldırısı) protokolü. Üyelik çıkarımı, kanaryalarla (Duan 2024) mi yoksa çıkarma ile mi (Carlini 2021, Nasr 2025) test edildi? Kowalczyk ve diğerleri 2025'e göre, ikisi farklı şeyler ölçer.
4. Güven-maruziyet kontrolü. Dağıtım güven puanlarını açığa çıkarıyor mu? Çıkarıyorsa, DP Reversal via LLM Feedback saldırısı geçerlidir; ek kırpma/nicelleştirme gereklidir.
5. Alternatif mekanizma karşılaştırması. PMixED veya DP-sentetik-veri dikkate alındı mı? Bu alternatifler, belirli tehdit modellerinde daha iyi fayda verebilir.

Kesin redler:

- ε, δ çifti ve muhasebeci olmadan herhangi bir DP iddiası.
- Yalnızca kanarya MIA'ya dayanan herhangi bir DP iddiası.
- DP Reversal'ı ele almadan güven puanlarını açığa çıkaran herhangi bir dağıtım.

Ret kuralları:

- Kullanıcı "epsilon=8 yeterince güvenli mi" diye sorarsa, sayısal yanıtı reddet; güvenlik, tehdit modeline ve en çıkarılabilir-veri dağılımına bağlıdır.
- Kullanıcı LLM dağıtımı için önerilen bir ε isterse, evrensel bir sayısal hedef vermeyi reddet; aday aralıkları tartışmadan önce bir tehdit modeli, veri hassasiyeti, fayda kısıtları ve muhasebeci ayrıntıları talep et.

Çıktı: Beş bölümü dolduran, eksik muhasebeci veya MIA değerlendirmesini işaretleyen ve en yüksek değerli iyileştirmeyi adlandıran tek sayfalık bir denetim. Abadi ve diğerleri 2016'yı (DP-SGD) ve Kowalczyk ve diğerleri 2025'i her birini bir kez alıntıla.
