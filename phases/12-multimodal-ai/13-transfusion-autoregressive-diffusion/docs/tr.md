# Transfusion: Tek Transformer'da Otoregresif Metin + Difüzyon Görüntüsü

> Chameleon ve Emu3 disket token'lara her şeyini bahse girdi. Çalışıyorlar ama nicelleştirme darboğazı görünür — görüntü kalitesi sürekli uzay difüzyon modellerinin altında platoya ulaşır. Transfusion (Meta, Zhou ve diğerleri, Ağustos 2024) ters bahsi yapar: görüntüleri sürekli tutun, VQ-VAE'yi tamamen bırakın ve iki kayıpla tek bir transformer eğitin. Metin token'ları sonraki-token tahmini alır. Görüntü yamaları akış eşleme (flow-matching) / difüzyon kaybı alır. Her iki hedef de aynı ağırlıkları optimize eder. Stable Diffusion 3'ün (MMDiT) arkasındaki mimari yakın bir akrabadır. Bu ders Transfusion tezini inceler, oyuncu iki-kayıplı bir eğitici inşa eder ve tek bir transformera her iki işi de yaptıran dikkat maskesini izler.

**Tür:** İnstra Et
**Diller:** Python (stdlib, MNIST ölçeğinde oyuncu iki-kayıplı eğitici)
**Önkoşullar:** Faz 12 · 11 (Chameleon), Faz 8 (Generatif Yapay Zeka)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Tek bir omurga üzerinde iki kayıp (metin token'larında NTP, görüntü yamalarında difüzyon MSE) çalıştıran bir transformer bağlama.
- Neden görüntü yamaları üzerinde çift yönlü dikkat (bidirectional attention) artı metin token'ları üzerinde nedensel dikkatin doğru maske seçimi olduğunu açıklama.
- Transfusion tarzını (sürekli görüntüler, difüzyon kaybı) Chameleon tarzıyla (disket görüntüler, NTP) karşılaştırma: hesaplama, kalite, kod karmaşıklığı.
- MMDiT'nin katkısını adlandırma: her blokta modaliteye özel ağırlıklar, artıklık akışında ortak dikkat.

## Sorun

Disket vs sürekli görüntü token'ları tartışması LLM'lerden eskidir. Sürekli temsiller (ham pikseller, VAE gizli katmanları) ayrıntıyı korur. Disket token'lar (VQ indeksleri) transformer'ın doğal sözlüğüne uyar ama nicelleştirme adımında ayrıntıyı kaybeder.

Chameleon / Emu3 diskete gitti: tek kayıp, tek mimari ama görüntü sadakati tokenize edici kalitesiyle sınırlı.

Difüzyon modelleri sürekli gitti: olağanüstü görüntü kalitesi ama LLM'den ayrı bir model, karmaşık gürültü-takvimi mühendisliği ve metin üretimiyle temiz entegrasyon yok.

Transfusion soruyor: ikisini birden alabilir miyiz? Görümleri sürekli tutun, hâlâ tek model eğitin, iki kaybı tek gradyan adımında birleştirin.

## Kavram

### İki-kayıplı mimari

Tek bir yalnızca-çözümleyici transformer, şu dizileri işler:

- Metin token'ları (disket, BPE sözlüğünden).
- Görüntü yamaları (sürekli, 16x16 piksel blokları doğrusal gömme aracılığıyla gizli boyuta projekte edilmiş — ViT kodlayıcısının girdisiyle aynı).
- Sürekli yamaların yaşadığı yeri işaretleyen `<image>` ve `</image>` etiketleri.

İleri geçiş bir kez çalışır. Kayıp token başına iki kafadan birini seçer:

- Metin token'ları için: sözlük logit'leri kafasında standart çapraz entropi.
- Görüntü yamaları için: sürekli yamalar üzerinde difüzyon kaybı — her yamaya eklenen gürültüyü tahmin etme.

Gradyan paylaşımlı transformer gövdesi üzerinden akar. Her iki kayıp da paylaşımlı ağırlıkları aynı anda geliştirir.

### Dikkat maskesi: nedensel metin + çift yönlü görüntü

Metin token'ları nedensel olmalıdır — bir metin token'ının gelecekteki metne dikkat etmesine izin veremezsiniz, aksi halde öğretmen zorlaması bozulur. Ancak görüntü yamaları bir görüntü bloğu içinde birbirine çift yönlü dikkat etmelidir.

Maske:

```
M[i, j] = 1 if:
 (i is text and j is text and j <= i) # metin için nedensel
 OR (i is image and j is image and same_image_block(i, j)) # görüntü içinde çift yönlü
 OR (i is text and j is image and j < i_image_end) # metin önceki görüntülere dikkat eder
 OR (i is image and j is text and j < i_image_start) # görüntü önceki metne dikkat eder
```

Eğitim ve çıkarımda blok-üçgensel (block-triangular) maske olarak uygulanır.

### Transformer içindeki difüzyon kaybı

Difüzyon kaybı standarttır: görüntü yamasına gürültü ekleyin, modelden gürörtüyü (veya eşdeğer olarak temiz yamayı) tahmin etmesini isteyin. Transfusion'un versiyonu akış eşlemesi kullanır — gürültülüden temize hız alanını (velocity field) tahmin etme.

Eğitim sırasında:
1. Her görüntü yaması x0 için rastgele bir zaman adımı t örnekleyin.
2. Gürültü ε örnekleyin, xt = (1-t) * x0 + t * ε hesaplayın (akış eşlemesi için doğrusal enterpolasyon).
3. Transformer v_theta(xt, t) tahmin eder; kayıp = MSE(v_theta(xt, t), ε - x0).
4. Aynı dizideki metin NTP kayıplarıyla birlikte geri yayılım.

Çıkarımda üretim:
- Metin token'ları: standart otoregresif örnekleme.
- Görüntü yamaları: difüzyon örnekleme döngüsü (tipik 10-30 adım), önceki metin token'ları koşullu.

### MMDiT: Stable Diffusion 3'ün çeşidi

Stable Diffusion 3 (Esser ve diğerleri, Mart 2024), Transfusion ile aynı anda MMDiT (Çoklu Difüzyon Transformer) sunmuştu. Mimariler kardeşlerdir.

MMDiT'nin temel farkları:

- Her blokta modaliteye özel ağırlıklar. Her transformer bloğunun metin token'ları için ayrı Q, K, V ve MLP ağırlıkları, görüntü yamaları için ayrı ağırlıkları vardır. Dikkat ortaktır (çapraz-modalite); diğer her şey modaliteye özeldür.
- Düzleştirilmiş akış eğitimi. DDPM'den daha basit matematikli, bilinen örneklemeyle belirli bir akış-eşlemesi çeşidi.
- Ölçek. MMDiT SD3'ün (2B ve 8B parametre çeşitleri) omurgasıdır. Transfusion makalesi 7B'ye kadar ölçeklenir.

Her ikisi de aynı çekirdek fikirde birleşir: tek bir transformer metin üzerinde NTP ve sürekli görüntü temsilleri üzerinde difüzyon çalıştırır.

### Neden Chameleon tarzından daha iyi

Sürekli-difüzyon ile disket-NTP arasındaki görüntü üretimi kalitesi farkı ölçülebilir. Transfusion makalesi rapor eder:

- 7B parametrede, aynı büyüklükteki Chameleon tarzı modeli FID'de 3-5 puan yener.
- Tokenize edici eğitimi gerekmez — görüntü kodlayıcısı daha basittir (gizli boyuta doğrusal projeksiyon, ViT'nin girdi katmanıyla aynı).
- Çıkarım görüntü yaması gürültü temizleme过程ini paralelleştirebilir, otoregresif görüntü token'larının aksine.

 dezavantajı: Transfusion iki-kayıplı bir model olduğundan eğitim dinamikleri daha zordur. Kayıp ağırlıklarının ayarlanması gerekir. NTP ile difüzyon arasındaki takvim uyuşmazlığı bir kafanın baskın hale gelmesine neden olabilir.

### Alt akımda ne var

Janus-Pro (Ders 12.15), Transfusion'un fikrini görüntü kodlayıcısını anlama ve üretim için ayırarak (anlama için SigLIP, üretim için VQ) inceltir, transformer gövdesini paylaşarak. Show-o (Ders 12.14) difüzyonu disket-difüzyonla (maske tahmini) değiştirir. Birleşik-üretim ailesi Transfusion'dan sonra hızla dallanır.

2026 üretim VLM'leri — Gemini 3 Pro, GPT-5, Claude Opus 4.7'nin görüntü üretimi yolu — neredeyse kesinlikle bu ailenin bir soyundanını kullanır. Detaylar özeldir.

## Kullan

`code/main.py` küçük bir MNIST benzeri problem üzerinde oyuncu bir Transfusion inşa eder:

- Metin açıklamaları bir rakamı (0-9) tanımlayan kısa tamsayı dizileridir.
- Görüntüler 4x4 piksel ızgaralarıdır.
- Paylaşımlı ağırlıklı iki doğrusal projeksiyon çifti transformer vekili olarak görev yapar; metin üzerinde NTP kaybı, gürültülü yamalar üzerinde MSE kaybı.
- Eğitim döngüsü iki kaybı alternatif çalıştırır, dikkat maskesi açıktır.
- Üretim bir metin açıklaması ve 4x4 görüntüyü tek ileri geçişte üretir.

Transformer oyuncudur. İki-kayıplı boru (plumbing), dikkat maskesi oluşturma ve çıkarım döngüsü gerçek ürünlerdir.

## Teslimat

Bu ders `outputs/skill-two-loss-trainer-designer.md` dosyasını üretir. Yeni bir multimodal eğitim görevi (metin + görüntü, metin + ses, metin + video) verildiğinde iki-kayıplı takvimi (kayıp ağırlıkları, maske şekli, paylaşımlı vs modaliteye özel bloklar) tasarlar ve uygulama risklerini işaretler.

## Alıştırmalar

1. Transfusion tarzı bir model %70 metin token'ı ve %30 görüntü yamasıyla eğitiliyor. Görüntü difüzyon kaybı, metin NTP kaybından büyüklük olarak ~10x daha büyük. Hangi kayıp ağırlıkları bunları dengeler?

2. `[T, T, <image>, P, P, P, P, </image>, T]` dizisi için blok-üçgensel maskeyi uygulayın. Her girdiyi 0 veya 1 olarak işaretleyin.

3. MMDiT modaliteye özel QKV ağırlıklarına sahip. Bu Transfusion'un tamamen paylaşımlı transformer'ına kıyasla ne kadar parametre overhead'i ekler? 7B parametrede buna değer mi?

4. Üretim: metin istemi verildiğinde model 50 token NTP çalıştırır, `<image>`'a ulaşır, ardından 20 gürültü temizleme adımında 256 yama üzerinde difüzyon çalıştırır. Toplam kaç ileri geçiş vardır?

5. SD3 makalesinin Bölüm 3'ünü okuyun. Düzleştirilmiş akışı (rectified flow) açıklayın ve neden DDPM'den daha az çıkarım adımında yakınsadığını açıklayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| İki-kayıplı eğitim | "NTP + difüzyon" | Tek bir transformer metin token'larında çapraz entropi ve sürekli görüntü yamalarında MSE'yi aynı gradyan adımında optimize eder |
| Akış eşleme | "Düzeltilmiş akış" | Gürültüden temiz veriye hız alanını tahmin eden difüzyon çeşidi; DDPM'den daha basit matematik |
| MMDiT | "Çoklu Difüzyon Transformer" | Stable Diffusion 3'ün mimarisi: ortak dikkat, modaliteye özel MLP'ler ve normlar |
| Blok-üçgensel maske | "Nedensel metin + çift yönlü görüntü" | Metin boyunca nedensel ama görüntü bölgeleri içinde çift yönlü dikkat maskesi |
| Sürekli görüntü temsili | "VQ yok" | Görüntü yamaları tamsayı sözlük indeksleri yerine gerçek değerli vektörlerdir |
| Hız tahmini | "v-parametrizasyonu" | Ağ çıktısı gürültüyle veri arasındaki hız alanıdır, gürültünün kendisi değil |

## İleri Okuma

- [Zhou ve diğerleri — Transfusion (arXiv:2408.11039)](https://arxiv.org/abs/2408.11039)
- [Esser ve diğerleri — Stable Diffusion 3 / MMDiT (arXiv:2403.03206)](https://arxiv.org/abs/2403.03206)
- [Peebles & Xie — DiT (arXiv:2212.09748)](https://arxiv.org/abs/2212.09748)
- [Zhao ve diğerleri — MonoFormer (arXiv:2409.16280)](https://arxiv.org/abs/2409.16280)
- [Xie ve diğerleri — Show-o (arXiv:2408.12528)](https://arxiv.org/abs/2408.12528)
