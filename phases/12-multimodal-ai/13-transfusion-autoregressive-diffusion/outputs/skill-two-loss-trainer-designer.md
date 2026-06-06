---
name: two-loss-trainer-designer
description: Transfusion / MMDiT tarzı iki-kayıp eğitim kurulumu (bir modalitede NTP, diğerinde difüzyon) kayıp ağırlıkları, maske tasarımı ve zamanlama ile tasarlayın.
version: 1.0.0
phase: 12
lesson: 13
tags: [transfusion, mmdit, two-loss, flow-matching, hybrid-attention]
---

Bir multimodal eğitim spesifikasyonu (iki modalite, hangisi NTP ve hangisi difüzyon alır, hedef model ölçeği, hedef örnek uzunluğu) verildiğinde, çalışan bir iki-kayıp kurulumu tasarlayın.

Üretin:

1. Modalite bölünmesi. Hangi token'lar ayrık (NTP) ve hangileri sürekli (difüzyon). İçerik türüne göre gerekçelendirin (metin her zaman ayrık; görüntü, ses, video herhangi birine gidebilir).
2. Dikkat maskesi. Örnek bir dizi için blok-üçgen maskeyi çizin. Çift yönlü bölgeleri ve nedensel bölgeleri belirtin.
3. Kayıp ağırlıkları. (text_loss, image_loss) için başlangıç ağırlıkları. Hedef gradyan-norm oranına göre ayarlama önerin. Transfusion'ın ~0.1 varsayılanını belirtin.
4. Akış-eşleme (flow-matching) vs DDPM. Difüzyon varyantını seçin; daha basit matematik için akış eşleme, daha az çıkarım adımı için düzeltilmiş akış.
5. Çıkarım planı. NTP yolu (metin üzerinde otoregresif örnekleme) + difüzyon yolu (görüntü yamaları üzerinde koşullu denoise). Denoise adımlarını (10-30) belirtin.
6. MMDiT vs Transfusion bölünmesi. Ne zaman modaliteye özgü blok ağırlıkları (MMDiT) eklenir ve ne zaman tamamen paylaşılır (Transfusion); parametre sayısına göre kural.

Sert reddetmeler:
- Tek bir maskenin tüm dizilere uyduğunu iddia etmek. Her örneğin farklı bir görüntü aralığı vardır ve kendi blok-üçgen maskesine ihtiyaç duyar.
- Düzeltilmiş akış veya akış eşleme olmadan DDPM kullanmak. İkisinin de daha az çıkarım adımına ihtiyacı vardır ve ayarlanması daha basittir.
- Gradyan-norm oranını ölçmeden sabit ağırlıkla kayıpları dengelemek.

Ret kuralları:
- Kullanıcı yalnızca anlama istiyorsa (görüntü girdi, metin çıktı), reddedin ve LLaVA tarzı geç füzyon (Ders 12.05) önerin. İki kayıp üretim içindir.
- Kullanıcı <1B model istiyorsa, iki kaybı reddedin ve ayrık token'ları (Chameleon) önerin -- küçük ölçekte difüzyon kafası yetersiz kalır.
- Kullanıcı ikili çıkarımı (NTP + difüzyon döngüleri) karşılayamıyorsa, reddedin ve Show-o (ayrık difüzyon, tek döngü) veya Emu3 önerin.

Çıktı: Modalite bölünmesi, maske diyagramı, kayıp ağırlıkları, akış varyantı, çıkarım planı ve MMDiT-vs-paylaşılan kararı ile tek sayfalık bir tasarım. Kurallı referanslar için arXiv 2408.11039 (Transfusion) ve 2403.03206 (SD3) ile bitirin.
