---
name: dualpipe-planner
description: Bir eğitim kümesi için pipeline paralellik stratejisi (1F1B, Zero Bubble, DualPipe, DualPipeV) planlayın.
version: 1.0.0
phase: 10
lesson: 19
tags: [pipeline-parallelism, dualpipe, dualpipev, zero-bubble, expert-parallelism, distributed-training]
---

Bir eğitim kümesi belirtimi (toplam GPU sayısı, ara bağlantı topolojisi, hızlandırıcı modeli, GPU başına bellek), bir model şekli (toplam parametreler, aktif parametreler, MoE veya yoğun, beklenen katman sayısı) ve bir hedef eğitim verisi hacmi verildiğinde, bir pipeline paralellik stratejisi önerin ve beklenen baloncuk (bubble) oranını doğrulayın.

Şunu üretin:

1. Pipeline derinliği P. GPU bellek bütçesine (her sıralama için bir pipeline aşaması sığmalı), MoE vs yoğun ve ara bağlantı bant genişliğine göre seçin. Aralık: küçük kümeler için 4, sınır (frontier) MoE eğitimi için 16-32.
2. Mikro-parti sayısı M. DualPipe ve DualPipeV için 2'ye bölünebilir olmalıdır. Tipik M/P oranı 8 ile 16 arasında. Gradyan birikim hedeflerine ve hedef dizi uzunluğundaki aktivasyon belleğine karşı gerekçelendirin.
3. Zamanlama (schedule) seçimi. 1F1B, Zero Bubble, DualPipe, DualPipeV arasından seçin. Karar tablosu: 500 GPU'nun altında yoğun eğitim -> Zero Bubble. Uzman paralelliği ile MoE -> DualPipe. Ağır tümünden-tümüne (all-to-all) olmadan 500 GPU'nun üzerinde yoğun eğitim -> DualPipeV. 100 GPU'nun altındaki küçük çalıştırmalar -> 1F1B yeterlidir.
4. Beklenen baloncuk oranı. Hedef P ve M'de seçilen zamanlama için hesaplayın. Yüzde olarak ve toplam eğitim bütçesinde 1F1B'ye kıyasla mutlak GPU-saat tasarrufu olarak raporlayın.
5. Parametre çoğaltma planı (yalnızca DualPipe). 2x parametre çoğaltmanın mevcut VRAM'a sığdığını doğrulayın. Seçilen P'ye göre GPU başına etkin parametre yoğunluğunu raporlayın.

Sert redler:
- Uzman Paralelliği olmadan DualPipe. EP-ağır iletişimleri gizlemeden 2x çoğaltma gerekçelendirilmez.
- Herhangi bir eğitim çalıştırmasında P > 64. Baloncuk oranı, zamana bakılmaksızın P ile doğrusal olarak büyür.
- DualPipe/DualPipeV için 2'ye bölünemeyen mikro-parti sayısı. Zamanlama kapanmaz.
- Model tek bir GPU'nun belleğine sığdığında herhangi bir pipeline paralelliği. Yalnızca veri paralelliği kullanın.

Reddetme kuralları:
- Ara bağlantı GPU başına 200 Gbps veya daha yavaşsa, DualPipe'ı reddedin ve DualPipeV'yi önerin. Tümünden-tümüne örtüşme penceresi, çoğaltmayı gerekçelendirmek için çok dardır.
- Kullanıcı küme topolojileri için uygun özel bir tümünden-tümüne çekirdeği sağlayamıyorsa, DualPipe yerine Zero Bubble'ı önerin.
- Eğitim çalıştırması 1B tokenin altındaysa, pipeline paralelliği planlamasını tamamen reddedin ve veri paralelliği artı tensör paralelliği önerin.

Çıktı: P, M, zamanlama, beklenen baloncuk oranı, parametre çoğaltma maliyetini (DualPipe ise) ve bir tümünden-tümüne çekirdek önerisini listeleyen tek sayfalık bir plan. Hedef sayıya ulaşılmazsa daha basit bir zamanlamaya geçişi gerekçelendirecek belirli kullanım metriğini (ilk 1000 adımda ölçülen toplam GPU kullanım yüzdesi) adlandıran bir "geri dönüş tetikleyicisi" paragrafıyla bitirin.
