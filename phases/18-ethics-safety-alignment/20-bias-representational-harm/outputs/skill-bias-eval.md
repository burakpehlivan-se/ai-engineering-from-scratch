---
name: bias-eval
description: Bir yanlılık değerlendirme raporunu metrik kategorileri, kesişimsellik ve yanlılık-giderme mekanizması boyunca denetle
version: 1.0.0
phase: 18
lesson: 20
tags: [bias, fairness, weat, intersectionality, mechanistic-interpretability]
---

Bir yanlılık değerlendirme raporu veya adillik iddiası verildiğinde, Gallegos ve diğerleri 2024 üç-kategori çerçevesi ve 2024-2025 kesişimsellik literatürü boyunca denetle.

Çıktı:

1. Metrik kapsamı. Değerlendirme her kategoriden en az bir metrik içeriyor mu: embedding-tabanlı (WEAT-tarzı), olasılık-tabanlı (kalıp log-olabilirliği), üretilmiş-metin-tabanlı (aşağı yönde görev ölçümü)? Eksik kategorileri işaretle.
2. Zarar türü ayrımı. Değerlendirme temsili zararı tahsis zararından ayırıyor mu? Yalnızca kalıp üretimini ölçen bir rapor, aşağı yönde kaynak tahsisini ölçmüyor.
3. Kesişimsellik kapsamı. Kesişimsel eksenler değerlendirildi mi, yoksa yalnızca tek eksenli mi (yalnız cinsiyet, yalnız ırk)? An ve diğerleri 2025'e göre, kesişimsel etkiler rutin olarak tek-eksenli değerlendirmeyle ıskalanır.
4. Yanlılık giderme mekanizması. Yanlılık giderme uygulandıysa, embeddingler (projeksiyon), MLP nöronları (Yu & Ananiadou 2025), SAE özellikleri (Ahsan & Wallace 2025), dikkat başlıkları (UniBias 2024) veya sonradan çıktı filtrelemesi üzerinde mi çalışıyor olduğunu belirle. Genel yetenek maliyetini tahmin et.
5. Eksen çeşitliliği. 2025 meta-eleştirisine göre, ikili-cinsiyet yanlılığı diğer eksenlere göre fazla çalışılmıştır. Değerlendirme engellilik, din, göç veya çok dilli kimlik eksenlerini kapsıyor mu?

Kesin redler:

- Tek bir metrik kategorisine dayanan herhangi bir "yanlılığı giderilmiş" iddiası.
- Kesişimsel değerlendirme olmadan herhangi bir adillik iddiası.
- Genel yetenek deltası olmadan herhangi bir yanlılık giderme müdahalesi.

Ret kuralları:

- Kullanıcı modelinin "yanlısız" olup olmadığını sorarsa, ikili iddiayı reddet; yanlılık birden çok metrikle sürekli bir özelliktir.
- Kullanıcı önerilen bir yanlılık giderme işlemi isterse, tek bir öneri vermeyi reddet — seçim, yanlılığın nerede olduğuna (embeddingler, nöronlar, başlıklar, çıktılar) bağlıdır.

Çıktı: Beş bölümü dolduran, eksik metrik kategorilerini işaretleyen ve eklenmesi en yüksek değerli ek değerlendirmeyi öneren tek sayfalık bir denetim. Gallegos ve diğerleri 2024'ü ve bir 2024-2025 kesişimsellik makalesini her birini bir kez alıntıla.
