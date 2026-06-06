---
name: clip-zero-shot
description: Bir CLIP / SigLIP kontrol noktasıyla sıfır-atış (zero-shot) görüntü sınıflandırması çalıştırın ve benzerlik puanlarıyla sıralanmış tahminler üretin.
version: 1.0.0
phase: 12
lesson: 02
tags: [clip, siglip, zero-shot, vision-language]
---

Bir görüntü listesi (dosya yolları veya URL'ler) ve aday sınıf adları listesi verildiğinde, beyan edilen bir CLIP veya SigLIP kontrol noktası kullanarak sıralanmış bir sıfır-atış sınıflandırması üretin. Beceri salt tahmindir; eğitmez veya ince ayar yapmaz.

Üretin:

1. Prompt oluşturma. Her sınıf için N metin şablonu oluşturun (varsayılan: `a photo of a {class}`, `a picture of a {class}`, `an image of a {class}`). Her prompt'u metin kodlayıcısıyla gömün ve sınıf prototipini oluşturmak için ortalamasını alın.
2. Görüntü gömme. Her girdi görüntüsünü belirtilen görüntü kodlayıcısıyla gömün. Her iki tarafı da birim uzunluğa normalleştirin.
3. Sıralanmış tahminler. Her görüntü gömme vektörü ile her sınıf prototipi arasındaki kosinüs benzerliğini hesaplayın. Puanlarla birlikte top-1 ve top-5'i döndürün.
4. Kontrol noktası meta verileri. Kullanılan tam Hugging Face kontrol noktasının adını (ör. `openai/clip-vit-large-patch14` veya `google/siglip2-so400m-patch14-384`) ve beklediği çözünürlüğü belirtin.
5. Dürüstlük bildirimi. Önceden eğitim dağılımının dışındaki sınıflarda sıfır-atışın güvenilmez olduğunu belirtin; top-1 puanını bir güven vekili olarak gösterin ve 0.2'nin altında olduğunda uyarın.

Sert reddetmeler:
- Çıktıyı, arayanın sağladığı listede olmayan sınıflar için kesin bir etiket olarak çerçeveleyen herhangi bir kullanım.
- Farklı kontrol noktalarındaki puanların karşılaştırılabilir olduğuna dair iddialar; SigLIP ve CLIP farklı ölçeklerde puan alır.
- Bir aşağı akış onay politikası olmadan insan içerdiği bilinen görüntüler üzerinde çalıştırmak.

Ret kuralları:
- Arayan tıbbi, hukuki veya güvenlik-kritik kategorilere (tanı, kimlik, korunan özellikler) sınıflandırma istiyorsa, reddedin ve denetim izleri olan denetimli modellere yönlendirin.
- Arayan tek bir sınıf adı sağlıyorsa (alternatifi olmayan tek yönlü sınıflandırma), reddedin -- sıfır-atış, anlamlı olmak için en az iki adaya ihtiyaç duyar.
- Kontrol noktası belirtilmemişse, reddedin ve (CLIP, OpenCLIP, SigLIP, SigLIP 2) artı hangi ölçek olduğunu sorun.

Çıktı: Kosinüs benzerlik puanları, kontrol noktası adı, kullanılan prompt şablonları ve bir güven bayrağı ile görüntü başına en iyi 5 tahminin sıralanmış listesi. Değişken en boy oranlarını işleme (NaFlex) için Ders 12.06'ya veya daha derin bir dalış için SigLIP 2 makalesine işaret eden bir "sırada ne okunmalı" paragrafı ile bitirin.
