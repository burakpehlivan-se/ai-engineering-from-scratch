---
name: var-tokenizer-designer
description: Sonraki-ölçek görsel otoregresif görüntü üretimi için çok-ölçekli artıklı VQ tokenlayıcı tasarla
version: 1.0.0
phase: 8
lesson: 19
tags: [var, sonraki-ölçek-tahmini, vq-vae, artıklı-vq, görüntü-üretimi, tokenlayıcı]
---

Hedef görüntü (çözünürlük, kanallar, renkli vs gri tonlama, veri kümesi boyutu, alt akış LM hesaplama bütçesi, hedef FID) verildiğinde, aşağıdakileri üret:

1. Ölçek zamanlaması. K çözünürlük seviyelerini 1x1'den (H/p) x (W/p)'ye kadar listele. 256x256 için varsayılan 10 ölçek, 512x512 için 14. K'yı LM'nin etkin dizi uzunluğuna (ölçek alanlarının toplamı) ve ölçek-içi paralel bütçeye göre gerekçelendir.
2. Kod defteri. Tüm ölçeklerde tek paylaşılan kod defteri boyutu V (tipik 4096 / 8192 / 16384). V'yi veri kümesi boyutu ve kodçözücü kapasitesinden seç. Kod defteri kullanımının kalibrasyon partisinde %50'nin üzerinde kaldığını doğrula veya V'yi küçült.
3. Artık paylaşımı. 1..K ölçeklerinin toplanmış yukarı örneklenmiş gömmeleri (artıklı VQ) ile gizliyi birlikte yeniden yapılandırdığını doğrula. Yama boyutu p'yi ve VAE omurgasını (VQGAN tarzı ayrımcı açık/kapalı, algısal kayıp ağırlığı) belirt.
4. Kodçözücü. Toplanmış gizliyi piksellere geri eşleyen VAE kodçözücü. VQGAN kodçözücü, VAR-kağıdı kodçözücü veya daha hafif MAGVIT tarzı kodçözücü arasından seç. FID hedefi ve kodçözücü VRAM'ına göre gerekçelendir.
5. Konum gömme. Ölçek başına öğrenilmiş gömme ve ölçek içinde 2D sin-cos ile (scale_index, satır, sütun) üçlüsünü doğrula. Düz 1D konumları reddet; LM doğru koşulluyu uygulamak için ölçek etiketine ihtiyaç duyar.

VAR için artıklı olmayan çok-ölçekli tokenlayıcı reddet. Toplanmış artıklar olmadan sonraki-ölçek koşullusu belirsiz hale gelir ve LM, kağıdın kanıtladığından farklı bir amacı optimize eder. Kod defteri çöküşü hafifletilmedikçe V daha küçük ölçeğin piksel sayısına kalibre edilmedikçe ayrı ölçek başına kod defterlerini reddet. K x ortalama-ölçek-alanı, metin koşullaması için başlık eksi LM'nin maks dizi uzunluğunu aştığında hiçbir ölçekte sonraki-ölçek tahminini reddet.

Örnek girdi: "ImageNet sınıf-koşullu 256x256, veri kümesi 1.2M, LM bütçesi 1.5B parametre, hedef FID 5.0 altında."

Örnek çıktı:
- Ölçek zamanlaması: K=10, boyutlar 1, 2, 3, 4, 5, 6, 8, 10, 13, 16. Toplam token 671.
- Kod defteri: paylaşılan, V=4096. ImageNet'te 256'da %70-80 kullanım bekleniyor.
- Artık paylaşımı: doğrulandı; p=16, algısal + çekişmeli kayıplarla VQGAN omurgası, artık toplamı f'yi yeniden yapılandırır.
- Kodçözücü: VQGAN kodçözücü, 4 yukarı örnekleme bloğu, ekstra iyileştirici yok.
- Konum gömme: (ölçek, satır, sütun) üçlüsü, öğrenilmiş ölçek tokeni + ölçek içinde 2D sin-cos.
