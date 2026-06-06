# ASCII Sanatı ve Görsel Jailbreak'ler

> Jiang, Li, Sun, Wang, Flick, Jagielski, Cai, Neel, Chang — "ASCC: Auxiliary-Sample-Equipped Conditional Compression" ve takip eden çalışmalar (2024). Görsel jailbreak, modelin güvenlik kalıplarını gizli talimatları tanıma üzerine eğitilmiş olmasını, ASCII-sanat-gömülü-talimatlar'ın ise o kalıpları atlamasını istismar eder. İki alt sınıf: (1) "zararlı talimat olarak gizlenmiş ASCII sanatı" — model, ASCII karakterlerini zararlı içerik olarak tanımaz; (2) "görsel-token-replacement" — modelin görsel kodlayıcısı (vision encoder), "zararlı" belirteçlerden (token) farklı bir temsil oluşturur. Çoklu-modal jailbreak, metin-tabanlı RLHF'in bir modelin tüm temsil alanlarını kapsamadığını gösterir. Bu, güvenlik eğitiminin "yüzeyinin" bir modeldeki "tüm modlara" nasıl genişletilmesi gerektiğine dair bir uyarıdır.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak ASCII-jailbreak simülatörü)
**Önkoşullar:** Faz 18 · 13 (çok-atışlı), Faz 18 · 12 (PAIR), Faz 16 · 06 (jailbreak temelleri)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- İki ASCII-jailbreak alt-sınıfını (ASCII-sanat-gizleme, görsel-token-replacement) tanımlayın ve metin-tabanlı RLHF'den nasıl farklılaştıklarını açıklayın.
- Çoklu-modal modellerin (GPT-4V, Claude 3 Opus, Gemini 1.5 Pro) neden metin-tabanlı eğitimin ötesinde ek güvenlik eğitimi gerektirdiğini açıklayın.
- "Temsil alanı" kavramını ve güvenlik eğitiminin metin üzerinde yoğunlaşmasının neden sınırlama olduğunu belirtin.
- ASCII-jailbreak için hafifletme stratejilerini (görsel-içerik denetimi, birleşik-mod temsili) listeleyin.

## Problem

Çoklu-modal modeller metin, görüntü, ses ve kodu aynı temsil alanında işler. RLHF ve güvenlik eğitimi, eğitim verilerinin baskın modu olan metin üzerinde yoğunlaşır. Bu, "görüntü alanının" güvenlik eğitimi yüzeyinin dışında olduğu bir boşluk yaratır. ASCII-sanat-gömülü-talimatlar ve görsel-token-replacement, bu boşluğu istismar eder.

## Kavram

### Alt sınıf 1: ASCII-sanat-gizleme

ASCII sanatı, metin karakterlerinden yapılmış görüntülerdir. Bir saldırgan, zararlı bir talimatı ("bana nasıl bomba yapılır anlat") ASCII sanatına dönüştürür ve modele bir görüntü olarak sunar. Model, görüntüyü metne çevirir ve talimatı tanır.

Standart güvenlik eğitimi, metin istemlerini zararlı kalıplar için tarar. "Bomba yapımı" metni, eğitimde yasaklıdır. Ancak ASCII sanatı, "bomba yapımı"nın görüntü versiyonudur; metin tarayıcısı onu yakalamaz. Model, kendi metin temsiline geri çevirdiğinde, zararlı talimatı tanır — ama genellikle çok geç.

Bu sınıf, metin-olarak-işlenen her şeyi kapsar: Unicode hileleri, tersine çevrilmiş metin, homoglif yer değiştirmeleri, hatta resim formatında saklanan base64.

### Alt sınıf 2: Görsel-token-replacement

Daha karmaşık: saldırgan, zararlı bir talimatı bir görüntüye dönüştürür; ancak, talimat "görüntüdeki metin olarak" değil, görüntüdeki gizli özellikler olarak kodlanır. Örnek: belirli bir piksel kalıbı, belirli bir kelimeye eşlenen bir gizli gömmeler (embeddings) üretir.

Modelin görsel kodlayıcısı, piksel kalıbını alır, gömmeleri üretir ve bu gömmeleri modelin metin kodlayıcısına besler. Sonuç: model, zararlı bir talimatı alır, ancak talimat metin olarak temsil edilmemiştir. Eğitim sırasında zararlı kalıpları tanımayı öğrenen metin güvenlik filtreleri, onu görmez.

### Çoklu-modal modellerin savunması neden zayıf

RLHF, modelin metin çıktılarını optimize eder. Eğer model, metin olmayan bir temsilden zararlı bir metin üretirse, metin-RLHF bunu yakalar — ama yalnızca çıktı düzeyinde, girdi düzeyinde değil. Model, istemdeki gizli temsili "görmez" ve zararlı içerik üretebilir.

Çoklu-modal güvenlik eğitimi, görüntüden-metne dönüşümden sonra değil, önce güvenlik kalıplarını aramayı gerektirir. Pratikte, bu, 2024'te başlayan ve 2025-2026'da olgunlaşan aktif bir araştırma alanıdır.

### Temsil alanı kavramı

Bir modelin "temsil alanı", modelin girdileri dahili olarak temsil ettiği tüm yolları kapsar. Metin modelleri için bu, tek bir boyuttur (belirteç dizisi). Çoklu-modal modeller için bu, birden çok boyuttur: metin dizileri, görüntü yamaları, ses çerçeveleri, araç çıktıları. Güvenlik eğitimi, her boyutta eğitilmelidir; metin-yoğunlaşmalı eğitim, modlar arasında "kör noktalar" bırakır.

### ASCII-jailbreak başarı oranları

2024 makaleleri, metin modellerinde ASCII-jailbreak'in %20-40 başarı oranı, çoklu-modal modellerde %60-80 başarı oranı gösterir. Çoklu-modal modeller, ASCII'yi metin-olarak-işlemek için bir "görüntü-metin köprüsü" eğitilir; güvenlik eğitimi, köprünün kendisinde değil, metin tarafında uygulanır.

### Görsel-içerik denetimi hafifletmesi

Bir hafifletme, görüntüleri modele göndermeden önce taramak için ayrı bir görsel-içerik sınıflandırıcı kullanmaktır. Bu, saldırı yüzeyini azaltır, ancak tüm ASCII varyantlarını (tersine çevrilmiş, döndürülmüş, gizli piksel kalıpları) yakalamaz. Yanlış pozitif oranı, yararlı görüntüleri (ekran görüntüleri, PDF'ler, fotoğraflar) reddedebilir.

### Birleşik-mod temsili hafifletmesi

Daha derin bir hafifletme, modelin kendisini çoklu-modal güvenlik üzerine eğitmektir: zararlı istemlerin hem metin hem de görüntü temsilleri eğitim sırasında etiketlenir. Bu, tüm temsil alanında güvenlik kalıplarını öğretir. Zor, çünkü eğitim verilerinin, tüm modlarda zararlı temsilleri kapsaması gerekir. 2025'te, OpenAI ve Google, "güvenlik-augmenteli çoklu-modal" eğitimini duyurdu; etkinliği devam eden araştırmadır.

### Ders 13 ve 14 arasındaki fark

Çok-atışlı (Ders 13) yalnızca metin bağlamı içinde çalışır. ASCII-jailbreak, metin dışı temsilleri istismar eder. İkisi de bağlam genişlemesinin doğal sonuçlarıdır, ancak farklı modlarda. Çoklu-modal modeller için, güvenlik eğitimi her iki sınıfı da kapsamalıdır.

### Ders 15 ile bağlantı

Dolaylı prompt enjeksiyonu (Ders 15), metin tabanlı modellerde bile çalışan ilgili bir saldırıdır: bir araç, web sayfası veya belge, modele gizli talimatlar içerir. Bu, "modelin girdi kaynağı"nın güvenlik eğitimi yüzeyinin dışında olduğu ilgili bir boşluktur.

### Bunun Faz 18'deki yeri

Ders 14, "temsil alanı" kavramını tanıtır. Ders 15 (dolaylı prompt enjeksiyonu), temsil alanını "modelin dışındaki veri kaynakları"na genişletir. Ders 18 (güvenlik duruşları), her iki saldırı sınıfını da kontrol listesine dahil eder.

## Kullan

`code/main.py`, basitleştirilmiş bir ASCII-jailbreak simülatörü inşa eder. Hedef modeli, "şifreli anahtar kelime" içeren metin istemlerini reddeden kural-tabanlı bir maskedir. Saldırgan, "şifreli anahtar kelime"yi ASCII sanatına dönüştürür (örneğin, basit bir 7x7 ızgarada karakterler halinde). Model, görüntüyü alır, metne geri çevirir ve metin-güvenlik-filtresi uygular. Saldırı, metin-filtresi ASCII'yi tanımadığında başarılı olur. Saldırganın başarı oranını, farklı ASCII varyantları (tersine çevrilmiş, döndürülmüş, küçük harfli) için ölçebilirsiniz.

## Yayınla

Bu ders `outputs/skill-multimodal-safety.md` dosyasını üretir. Bir çoklu-modal model değerlendirme raporu verildiğinde, hem metin hem de görüntü modlarında güvenlik eğitiminin uygulanıp uygulanmadığını, görsel-içerik denetiminin devrede olup olmadığını ve temsil alanı kapsamının modlar arasında tutarlı olup olmadığını kontrol eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. ASCII varyantlarını (düz, tersine çevrilmiş, döndürülmüş, küçük harfli) deneyin. Her birinin başarı oranı nedir?

2. Görsel-içerik denetimi ekleyin: hedef modele ulaşmadan önce tüm ASCII-art-gibi görüntüleri filtreleyin. Başarı oranı düşer, aynı kalır veya artar mı? Hangi ASCII varyantları hâlâ geçer?

3. Modele, "görüntüden metin dönüşümü" aşamasında bir güvenlik filtresi ekleyin: dönüştürülen metin anahtar kelimeleri içeriyorsa, zararlı yanıtı reddedin. Bu, başarı oranını nasıl değiştirir?

4. Ders 13 (çok-atışlı) ve Ders 14 (ASCII) birleştirin: bir istem, 128 ASCII-gizlenmiş soru-yanıt çifti içerir. Bu, "çok-atışlı + ASCII" saldırısı, yalnızca çok-atışlı veya yalnızca ASCII'den daha mı güçlüdür? Bir deney tasarlayın.

5. Çoklu-modal güvenlik eğitimi, tüm temsil alanlarında güvenlik kalıplarını eğitmeyi gerektirir. Bunu, 100k örnek içeren sentetik bir veri kümesi için, 5 modda (metin, görüntü, ses, kod, araç çıktısı) tanımlayın. Eğitim veri kümesinin boyutu ne olmalıdır?

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| ASCII sanatı | "metin-görüntü" | Metin karakterlerinden yapılmış görüntü; model bunu metne geri çevirebilir |
| Görsel-token-replacement | "gizli piksel kalıbı" | Görüntüdeki özelliklerin, metin olarak temsil edilmeyen gömmeler üretmesi |
| Çoklu-modal güvenlik eğitimi | "modlar arasında" | Bir modelin tüm temsil modlarında güvenlik kalıplarını eğitme |
| Temsil alanı | "girdi temsili" | Bir modelin, tüm modlarda, girdileri dahili olarak temsil ettiği yollar |
| Görsel-içerik denetimi | "görüntü sınıflandırıcısı" | Modele ulaşmadan önce görüntüleri tarayan bağımsız modül |
| Birleşik-mod temsili | "modlar arası eğitim" | Tüm modlarda zararlı temsilleri eğitim sırasında etiketleyen eğitim veri kümesi |
| Köprü (görüntü-metin) | "kod çözücü katman" | Modelin görüntüleri metne dönüştüren bileşeni |
| Temsil boşluğu | "kör nokta" | Güvenlik eğitimi yüzeyinin dışındaki temsil alanı |

## İleri Okuma

- [Jiang ve diğerleri — ASCC: Auxiliary-Sample-Equipped Conditional Compression (2024)](https://arxiv.org/abs/2404.05422) — ASCII-jailbreak yöntemleri
- [OpenAI — GPT-4V System Card (2023)](https://openai.com/index/gpt-4v-system-card/) — çoklu-modal güvenlik uygulaması
- [Anthropic — Claude 3 Model Card (2024)](https://www-cdn.anthropic.com/7c5c6ef72b1e4d4ea956b87c9afb0b80a0e5c98e.pdf) — çoklu-modal güvenlik değerlendirmesi
- [Qi ve diğerleri — On the Adversarial Robustness of Multimodal Foundation Models (2023)](https://arxiv.org/abs/2308.04047) — temsil alanı analizi
