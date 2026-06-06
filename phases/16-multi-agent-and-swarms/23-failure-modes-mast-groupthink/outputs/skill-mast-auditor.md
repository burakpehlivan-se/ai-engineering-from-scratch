---
name: mast-auditor
description: Bir çok-agent'lı sistem üzerinde MAST-stili başarısızlık-modu denetimi çalıştırın. Yürütme-izi başarısızlıklarını Specification / Coordination / Verification ve Groupthink ailelerine kategorize edin; azaltmaları beklenen başarısızlık azalmasına göre sıralayın.
version: 1.0.0
phase: 16
lesson: 23
tags: [multi-agent, failure-modes, MAST, groupthink, circuit-breaker, audit]
---

Bir çok-agent'lı sistem ve örneklenmiş yürütme izleri verildiğinde, başarısızlık-modu denetimi çalıştırın.

Üretin:

1. **Örneklem oluşturma.** Production'dan en az 200 iz, görev türleri ve zaman pencereleri boyunca tekdüze örneklenmiş. Örnekleme yöntemini ve yanlılık risklerini belgelendirin.
2. **Sınıflandırma geçişi.** Her iz için, `success | failure` işaretleyin. Başarısızlıklar için, bir MAST kategorisi (spec / coord / verify) ve geçerli olduğunda, bir veya daha fazla Groupthink aile etiketi (monoculture / conformity / tom / mixed-motive / cascade) atayın.
3. **Dağılım tablosu.** MAST kategorisine ve Groupthink etiketine göre sayımlar ve yüzdeler. Cemri 2025'in referans dağılımıyla (41.77 / 36.94 / 21.30) karşılaştırın. Referanstan ağır şekilde sapan sistemlerin genellikle spesifik bir zayıf katmanı vardır.
4. **En iyi başarısızlık örüntüleri.** En sık 3 spesifik örüntüyü tanımlayın (örn. "iki agent de inceleme yapıyor"). Yeniden üretim adımlarını belgelendirin.
5. **Azaltma sıralaması.** Her en iyi örüntü için, standart kütüphaneden bir azaltma önerin: açık rol sözleşmeleri, versiyonlanmış paylaşılan durum, bağımsız doğrulayıcı, circuit breaker, tespit-teşhis-doğrulama (STRATUS) üçlüsü. Örüntünün sıklığı göz önüne alınarak beklenen başarısızlık azalmasına göre sıralayın.
6. **Sessiz başarısızlık riski.** Kaç başarısızlık makul-ama-yanlış çıktılar üretir vs gürültülü hatalar? Sessiz oran, doğrulama-katmanı yatırımını yönlendirir.
7. **Yavaş başarısızlık vekilleri.** Loud (gürültülü) bir hatadan önce sürüklenmeyi yüzeye çıkaracak 2-3 canlı metrik önerin: anlaşma oranı, yeniden deneme oranı, çıktı-uzunluk dağılımı, agent-arası düzenleme mesafesi.

Keskin redler:

- Rastgele veya katmanlı örneklem olmadan denetimler. Elle seçilmiş başarısızlıklar dramatik vakaları fazla temsil eder ve yavaş başarısızlık sürüklenmesini kaçırır.
- Temel ölçüm olmadan azaltma önerileri. Mevcut başarısızlık oranı bilinmeden "doğrulayıcı ekle" bir şey ifade etmez.
- MAST-bilinmeyen olayların göz ardı edilmesi. Bir iz bir kategoriye uymuyorsa, taksonomi eksiktir; bir kategori zorlamak yerine bir uzantı önerin.
- Çeyreklik denetimin operasyonel yavaş başarısızlık izlemesi olmadan yeterli olduğunu iddia etmek. Çeyreklik denetimler, denetimler arasındaki sürüklenmeyi kaçırır.

Ret kuralları:

- İzler agent başına atfı eksikse (kim neyi yazdı, kim neyi okudu), denetim koordinasyon başarısızlıklarını rol çakışmalarından ayırt edemez. Yeniden denetlemeden önce yapılandırılmış agent-başına loglama eklenmesini önerin.
- Sistemin toplamda 50'den az başarısız izi varsa, örneklem dağılım tahminleri üretmek için çok küçüktür. Daha uzun gözlem penceresi önerin.
- İzler PII (Kişisel Tanımlayıcı Bilgi) içeriyorsa, analizden önce maskeleyin.

Çıktı: Üç sayfalık rapor. Tek cümlelik bir özetle başlayın ("%41 spec başarısızlıkları, %12 koordinasyon, %39 doğrulama boşlukları, %8 bilinmeyen; en iyi örüntü çift-incelemeci çakışması; en yüksek-ROI azaltma açık rol sözleşmeleridir."), sonra yukarıdaki yedi bölüm. Önceliklendirilmiş bir eylem listesiyle bitirin: tahmini uygulama maliyeti ve beklenen başarısızlık-oranı azalması ile üç azaltma.
