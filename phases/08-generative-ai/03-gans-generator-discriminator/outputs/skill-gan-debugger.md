---
name: gan-debugger
description: Başarısız GAN eğitimini kayıp eğrileri ve örnek ızgaralarından teşhis et; tek satırlık düzeltmeler yaz
version: 1.0.0
phase: 8
lesson: 03
tags: [gan, çekişmeli, hata-ayıklama]
---

Başarısız bir GAN çalıştırması (D ve G kayıp eğrileri, örnek ızgarası, veri kümesi boyutu, optimizer yapılandırması) verildiğinde, aşağıdakileri üret:

1. Teşhis. Kök neden: mod çöküşü, D çok güçlü, D çok zayıf, kaybolan gradyan, parti-normalizasyon sızıntısı, D aşırı öğrenmesi, öğrenme oranı uyumsuzluğu, kötü başlatma.
2. Kanıt. Kayıp eğrilerinde veya örneklerde belirtici göstergeye işaretçi (ör. "500. adımda D(fake) < 0.05 = D çok güçlü").
3. Düzeltme. Somut bir değişiklik. Örnekler: `lr_D = lr_G / 2`, BN'yi IN ile değiştir, D'ye spektral norm ekle, WGAN-GP'ye lambda=10 ile geç, parti boyutunu 2 kes, D girdilerine 0.1 Gauss gürültüsü ekle.
4. Yeniden çalıştırma protokolü. Denenecek tohumlar, yeniden değerlendirmeden önceki adım sayısı, kabul kriteri (ör. "20k adımda FID temel çizgisinin altına düşer").
5. Geri dönüş. Düzeltme bir yeniden çalıştırmada tutmazsa sırada ne denenir. Genellikle: mimari değiştir (StyleGAN, R3GAN) veya veri kümesi çok çeşitliyse paradigma değiştir (difüzyon, akış eşleme).

D zaten doygun olduğunda G öğrenme oranını artırmayı önerme. Gerçek başarısızlık D olduğunda G'ye düzenlileştirme ekleme — önce D'yi düzelt. 100 adım içinde eğitim çöküşü gösteren herhangi bir çalıştırmayı derin algoritmik bir sorun değil, muhtemelen kötü başlatma veya lr patlaması olarak işaretle.
