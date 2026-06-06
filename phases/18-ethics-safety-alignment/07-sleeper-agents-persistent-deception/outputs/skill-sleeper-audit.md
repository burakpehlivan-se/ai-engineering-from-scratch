---
name: sleeper-audit
description: Bir hizalama eğitimi raporunu, yerleştirilmiş veya şüphelenilen bir arka kapının gerçekten kaldırıldığını gösterip göstermediğine göre denetle
version: 1.0.0
phase: 18
lesson: 7
tags: [sleeper-agents, backdoor, alignment-training, adversarial-training, probes]
---

Bir rapor, SFT, RLHF, karşıt eğitim veya herhangi bir bileşim aracılığıyla bir modelden zararlı bir davranışın kaldırıldığını iddia ettiğinde, kaldırmanın standart Hubinger ve diğerleri 2024 tehdit modeline karşı gerçekten gösterilip gösterilmediğini denetle.

Çıktı:

1. Çıkarma kapsamı. Rapor, eğitim hattının hiç görmediği bir çıkarma yöntemini elde tuttu mu? Eğer tek değerlendirme kırmızı takımın kendi dağılımıysa, kaldırma kanıtlanmamıştır.
2. Tetikleyici genelliği. İddia edilen tetikleyici, değişmez bir dize mi, bir dağılım kayması mı, yoksa çevresel bir özellik mi (tarih, token, bağlam boyutu)? Tetikleyicinin genelliği, kırmızı takımın kapsamak zorunda olduğu arama uzayının boyutunu belirler.
3. İç durum kanıtı. Ekip, davranış temiz olduğunda bile tetikleyiciyle ilgili durumun hâlâ dahili olarak mevcut olup olmadığını kontrol etmek için artık-akış sondaları, SAE (seyrek oto-kodlayıcı) özellikleri veya diğer mekanistik sondalar uyguladı mı? Nisan 2024 Anthropic takip çalışmasına göre, iç durum davranışsal kaldırmadan sonra doğrusal olarak okunabilir kalır.
4. Hat boyunca kalıcılık kontrolü. Kaldırma, sonraki her eğitim aşamasından sonra doğrulandı mı (daha fazla SFT, sonraki RLHF geçişi, adaptör birleştirme, distilasyon)? Arka kapılar eğitim boyunca kalıcıdır — değerlendirilen, bir orta kontrol noktası değil, son modeldir.
5. Ölçek tutarlılığı kontrolü. İddia daha küçük bir modele dayanıyorsa, Hubinger 2024 Şekil 4 kalıcılığın ölçekle büyüdüğünü gösterir. Daha küçük model kanıtı yukarıya taşınmaz.

Kesin redler:

- Elenmiş çıkarma olmadan "RLHF uyguladık, bu yüzden model güvenli" şeklindeki herhangi bir iddia.
- Yalnızca kırmızı takım dağılımı değerlendirmesine dayanan herhangi bir iddia (eğitim ve değerlendirme aynı havuzdan çekilir).
- Orijinal yerleştirme mekanizması bilinmediğinde iç durum sondaları olmadan yapılan kaldırma iddiası.

Ret kuralları:

- Kullanıcı "RLHF aldatıcı hizalamayı kaldırabilir mi" diye sorarsa, ikili yanıtı reddet ve kalıcılık üzerine Hubinger ve diğerleri 2024 Bölüm 5'e ve düşünce zinciri üzerine Bölüm 6'ya yönlendir.
- Kullanıcı gizli aldatma için sayısal bir olasılık isterse, reddet ve taban oranlarının bilinmediğini; deneysel kanıtın yapılandırılmış organizmalardaki kalıcılık olduğunu, doğal eğitilmiş modellerdeki ortaya çıkış oranı olmadığını açıkla.

Çıktı: Raporun kanıtlarını yukarıdaki beş denetim boyutuna eşleyen, raporun ele almadığı her boyutu işaretleyen ve ele alınmamış en büyük tek tehdit modelini belirten tek sayfalık bir denetim. Temel tehdit modeli için Hubinger ve diğerlerini (arXiv:2401.05566) alıntıla.
