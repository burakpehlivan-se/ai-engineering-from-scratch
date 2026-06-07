# LLaVA ve Görsel Talimat İnce Ayarı (Visual Instruction Tuning)

> LLaVA (Nisan 2023) gezegende en çok kopyalanan multimodal mimarisidir. BLIP-2'nin Q-Former'ını 2 katmanlı MLP ile, Flamingo'nun kapılı çapraz-dikkatini saf token birleştirme (concatenation) ile değiştirdi ve yalnızca metin açıklamalardan GPT-4 tarafından üretilen 158k görsel-talimat dönüşümü üzerinde eğitildi. 2023 ile 2026 arasında bir VLM inşa eden her uygulayıcı LLaVA'nın bir çeşidini inşa etti. LLaVA-1.5 AnyRes'i ekledi. LLaVA-NeXT çözünürlüğü artırdı. LLaVA-OneVision tek bir tarifte görüntü, çoklu görüntü ve videoyu birleştirdi. Bu ders tarifi inceler, projeksiyoncuyu uygular ve "neden daha basiti kazandığını" açıklar.

**Tür:** İnşa Et
**Diller:** Python (stdlib, projeksiyoncu + talimat şablonu oluşturucu)
**Önkoşullar:** Faz 12 · 02 (CLIP), Faz 11 (LLM Mühendisliği — talimat ince ayarı)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- ViT yama gömmelerini (dim 1024) bir LLM'in gömme boyutuna (dim 4096) haritalayan 2 katmanlı MLP projeksiyoncusu inşa etme.
- LLaVA'nın iki aşamalı tarifini izleme: (1) 558k açıklama çifti üzerinde projeksiyon hizalama, (2) 158k GPT-4 tarafından üretilen dönüşüm üzerinde görsel talimat ince ayarı.
- `<image>` yer tutucusu (placeholder), sistem istemi ve kullanıcı/asistan dönüşümleri içeren LLaVA biçemli bir istem oluşturma.
- Topluluğun Q-Former'dan MLP'ye neden geçtiğini, Q-Former'ın token bütçesi kazancına rağmen açıklama.

## Sorun

BLIP-2'nin Q-Former'ı (Ders 12.03) bir görüntüyü 32 token'a sıkıştırır. Temiz, verimli, kıyaslama testleri için iyi. Ama iki sorunu var.

Birincisi, Q-Former eğitilebilir ama kaybı nihai görev değildir. 1. aşama ITC+ITM+ITG eğitir. 2. aşama dil modeli kaybını eğitir. Sorgular bir ara temsil öğrenir ki LLM sonra bunu çözmeli. Darboğazda bilgi kaybolur.

İkincisi, Q-Former 188M parametre alır ve LLaVA'nın 2023 ölçeğinde hedef LLM'nizle birlikte tasarlamak zorundaydınız. LLM'i değiştirin, Q-Former'ı yeniden eğitin. Görüntü kodlayıcısını değiştirin, yeniden eğitin. Her kombinasyon ayrı bir Ar-Ge projesiydi.

LLaVA'nın cevabı utandırıcı kadar basitti: ViT'nin 576 yama token'ını alın, her birini 2 katmanlı MLP'den (`1024 → 4096 → 4096`) geçirin ve 576'sının tamamını LLM'in girdi dizisine dökün. Darboğaz yok. Garip hedeflerde 1. aşama ön-eğitim yok. Yalnızca MLP'yi doğrudan dil modeli kaybı üzerinde eğitin.

Veri nereden geliyor? LLaVA'nın ikinci içgörüsü: GPT-4'ü (metin-only) talimat verisi üretmek için kullanın. Bir görüntü için COCO açıklama ve sınır kutusu (bounding box) verilerini GPT-4'e besleyin, sohbetler, tanımlamalar ve karmaşık akıl yürütmesi soruları üretmesini isteyin. Ücretsiz 158k talimat-cevap dönüşümü. İnsan etiketlemesi yok.

Sonuç: 8 A100'de bir gün çalışan, MMMU'da Flamingo'yu yenen ve topluluğun genişletebileceği açık bir kontrol noktası sunan bir VLM. 2023 sonuna kadar 50+ çatal (fork) doğurmuştu.

## Kavram

### Mimari

13B LLaVA-1.5:
- Görüntü kodlayıcısı: CLIP ViT-L/14 @ 336 (1. aşamada donmuş, isteğe bağlı olarak 2. aşamada serbest).
- Projeksiyoncu: GELU aktivasyonlu 2 katmanlı MLP, `1024 → 4096 → 4096`.
- LLM: Vicuna-13B (sonra Llama-3.1-8B).

Görüntü + metin istemi üzerinde ileri geçiş:

```
img -> ViT -> 576 patches of dim 1024
patches -> MLP -> 576 tokens of dim 4096
prompt: system + "<image>" placeholder + user question
replace <image> token with the 576 projected tokens
feed the full sequence to the LLM
decode response
```

#### Açıklama
Görüntü LLM bağlamının 576 tokenını kaplar. 2048 bağlamda metin için 1472 token kalır. 32k bağlamda yuvarlama hatasıdır.

### 1. Aşama: projeksiyoncu hizalaması

ViT donmuş. LLM donmuş. Yalnızca 2 katmanlı MLP eğitilir. Veri seti: 558k görüntü-açıklama çifti (LAION-CC-SBU). Kayıp: görüntü token'ları koşullu olarak açıklama üzerinde dil modellemesi.

128 toplu iş boyutuyla tek bir epokta birkaç saatte tamamlanır. Projeksiyoncu ViT uzayını LLM uzayına haritalamayı öğrenir. Göreve özel denetim yok.

### 2. Aşama: görsel talimat ince ayarı

Projeksiyoncu serbest (hâlâ eğitilebilir). LLM serbest (genellikle tamamen, bazen LoRA). 158k görsel-talimat dönüşümü üzerinde eğitilir.

Talimat verisi hilesidir. Liu ve diğerleri bunu şöyle üretti:
1. Bir COCO görüntüsü alın.
2. Metin açıklamasını çıkarın (5 insan açıklaması + sınır kutusu listesi).
3. Üç istem şablonuyla GPT-4'e gönderin:
 - Sohbet: "Bu görüntü hakkında kullanıcı ve asistan arasında gidip gelen bir diyalog üretin."
 - Detaylı açıklama: "Görüntünün zengin, detaylı bir tanımını verin."
 - Karmaşık akıl yürütmesi: "Görüntü hakkında akıl yürütmeyi gerektiren bir soru sorun, sonra cevaplayın."
4. GPT-4 çıktısını (talimat, cevap) çiftlerine ayrıştırın.

Bunların hiçbiri görüntüye doğrudan dokunmaz — yalnızca metin açıklaması. GPT-4 ikna edici görüntü içeriği hayal eder. Biraz gürültü var ama işe yaradı: 158k dönüşüm diyaloğun kilidini açmak için yeterliydi.

### Neden topluluk bunu kopyaladı

- 1. aşamaya özgü kayıp yok. Boyunca dil modeli kaybı.
- Projeksiyoncu saatlerce, günlerce değil, eğitilir.
- LLM değiştirilebilir (LLaVA-Llama2, LLaVA-Mistral, LLaVA-Llama3) yalnızca projeksiyoncuyu yeniden eğiterek.
- Görsel-talimat veri hattı GPT-4 kullanır ve yeni bir alan için yeniden üretmesi ucuzdur.

### LLaVA-1.5 ve LLaVA-NeXT

LLaVA-1.5 (Ekim 2023) şunları ekledi:
- Akademik görev verileri (VQA, OKVQA, RefCOCO) talimat ince ayarına karıştırıldı.
- Daha iyi sistem istemi.
- 2048 → 32k bağlam.

LLaVA-NeXT (Ocak 2024) şunları ekledi:
- AnyRes: yüksek çözünürlüklü görüntüleri 2x2 veya 1x3 336x336 kırpma ızgarasına böler, bir de küresel düşük çözünürlüklü küçük resim. Her kırpma 576 token olur; görüntü başına toplam yaklaşık 2880 görsel token. OCR ve grafik görevlerinde sıçrama.
- ShareGPT4V (yüksek kaliteli GPT-4V açıklamaları) ile daha iyi talimat verisi karışımı.
- Daha güçlü temel LLM'ler (Mistral-7B, Yi-34B).

### LLaVA-OneVision

Ders 12.08 OneVision'ı derinlemesine ele alır. Kısa versiyon: aynı projeksiyoncu, ama tek bir modelde tekli görüntü, çoklu görüntü ve videoyu kapsayan bir müfredat (curriculum) ile eğitilmiş, paylaşımlı görsel-token bütçesiyle.

### Q-Former ile karşılaştırma

| | Q-Former (BLIP-2) | MLP (LLaVA) |
|---|---|---|
| Görüntü başına görsel token | 32 | 576 (temel) veya 2880 (AnyRes) |
| Eğitilebilir parametre | 188M + LM | 40M + LM |
| 1. aşama kaybı | ITC+ITM+ITG | Yalnızca LM |
| LLM ekleme-kullan | Yeniden eğitim gerektirir | Minimum yeniden eğitimle değiştirme |
| Çoklu görüntü | Beceriksiz | Doğal (birleştirme) |
| Video | Beceriksiz | Doğal (kare başına birleştirme) |
| Token bütçesi | Küçük | Büyük |

MLP basitlik ve token esnekliğinde kazanır. Q-Former token bütçesinde kazanır. 2023 sonuna kadar token bütçesi bağlayıcı kısıt değildi (LLM bağlamı 32k-128k'ya büyüdü) ve basitlik baskın hale geldi.

### İstem biçimi

```
A chat between a curious human and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the human's questions. USER: <image> Describe this image in detail. ASSISTANT: The image shows ...
```

#### Açıklama
`<image>` bir yer tutucu token'dır. Tokenizasyondan önce 576 görsel token'la (veya AnyRes ile 2880) değiştirilir. Tokenizatör eğitimdekinden biraz daha uzun bir dizi görür ama LLM bilinmeyen girişi işler çünkü 1. aşama ona öğretti.

### Parametre ekonomisi

LLaVA-1.5-7B ayrımı:
- CLIP ViT-L/14 @ 336: 303M (1. aşamada donmuş, genellikle 2. aşamada serbest).
- Projeksiyoncu (2x doğrusal): ~22M eğitilebilir.
- Llama-7B: 7B.
- Toplam: 7.3B parametre. 2. aşamada eğitilebilir: tam 7B + 22M projeksiyoncu.

2. aşama eğitim maliyeti: 8xA100 üzerinde ~20 saat. Bu kilit sayıdır — bir gün, bir düğüm, tekrarlanabilir. Bu yüzden LLaVA yayıldı.

## Kullan

`code/main.py` şunları uygular:

1. Saf Python'da 2 katmanlı MLP projeksiyoncusu (oyuncu ölçeğinde dim 16 → 32 → 32).
2. İstem oluşturma hattı: sistem istemi + `<image>` N projekte edilmiş token'la değiştirildi + kullanıcı dönüşü + asistan üretimi yer tutucusu.
3. 576 tokenlık görsel bloğun LLM bağlamında nasıl göründüğünün görselleştiricisi (2k / 32k / 128k bağlamın yüzdesi).

## Teslimat

Bu ders `outputs/skill-llava-vibes-eval.md` dosyasını üretir. Bir LLaVA ailesi kontrol noktası verildiğinde, 10 istemlik bir hissiyat-değerlendirme (vibes-eval) paketi çalıştırır (3 açıklama, 3 VQA, 2 akıl yürütmesi, 2 reddetme) ve insan-okunabilir bir puan kartı raporlar. Kıyaslama değil; projeksiyoncu ve LLM'in iyi bağlandığını doğrulamak için bir duman testi.

## Alıştırmalar

1. `1024 → 4096 → 4096` boyutunda 2 katmanlı MLP projeksiyoncusunun eğitilebilir parametre sayısını hesaplayın. GELU ve sapmayla (bias) LLaVA-13B'nin yüzde kaçıdır?

2. "Reddetme" durumu için bir LLaVA istemi oluşturun — görüntü özel bir birey içeriyor. Beklenen asistan yanıtını yazın. LLaVA neden bunu zero-shot reddetmeli ve reddetmeyi güçlendirmek için hangi eğitim verisi gerekir?

3. LLaVA-NeXT blogunun AnyRes bölümünü okuyun. AnyRes ile 1344x672 görüntü için görsel token sayısını hesaplayın. Temel 336x336'daki 576 token ile karşılaştırın.

4. LLaVA 1. aşaması projeksiyoncusu açıklamalar üzerinde dil modeli kaybıyla eğitilir. 1. aşamayı atlayıp doğrudan 2. aşamaya (görsel talimat ince ayarı) giderseniz ne olur? Cevap için Prismatic VLMs kıyaslama deneyine (arXiv:2402.07865) atıfta bulunun.

5. LLaVA-Instruct-150k, COCO açıklamalarıyla GPT-4 kullanarak talimat üretir. Yeni bir alan için (tıbbi röntgen, uydu görüntüleri) alan talimatları üretmek için dört adımlı veri hattını açıklayın. Her adımda ne yanlış gidebilir?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Projeksiyoncu | "MLP köprüsü" | ViT boyutunu LLM boyutuna haritalayan GELU'lu 2 katmanlı MLP |
| Görüntü token'ı | "<image> yer tutucusu" | Çıkarım öncesinde N projekte edilmiş görsel token ile değiştirilen istem işareti |
| Görsel talimat ince ayarı | "LLaVA 2. aşama" | GPT-4 tarafından üretilen (görüntü, talimat, cevap) üçlüleri üzerinde eğitim |
| 1. aşama hizalaması | "Projeksiyoncu ön-eğitimi" | ViT ve LLM donmuş, projeksiyoncu açıklamalar üzerinde dil modeli kaybıyla eğitilir |
| AnyRes | "Çoklu kırpma döşeme" | Yüksek çözünürlüklü görüntüleri bir döşeme ızgarasına böler ve her döşemenin görsel token'larını birleştirir |
| LLaVA-Instruct | "GPT-4 tarafından üretilmiş" | COCO açıklamalarından + GPT-4'ten sentezlenmiş 158k talimat-cevap çifti |
| Görüntü kodlayıcısı dondurma | "Omurga kilitli" | CLIP ağırlıkları 1. aşamada güncellenmez, bazen 2. aşamada da güncellenmez |
| ShareGPT4V | "Daha iyi açıklamalar" | GPT-4V tarafından üretilen 1M yoğun açıklama, daha yüksek kaliteli hizalama için kullanılır |
| VQA | "Görsel soru cevaplama" | Bir görüntü hakkında serbest biçimli bir soruyu yanıtlama görevi |
| Prismatic VLMs | "Tasarım alanı makalesi" | Karamcheti 2024 kıyaslama deneyi, projeksiyoncu ve veri seçimlerini sistematik olarak test eder |

## İleri Okuma

- [Liu ve diğerleri — Görsel Talimat İnce Ayarı (arXiv:2304.08485)](https://arxiv.org/abs/2304.08485) — LLaVA makalesi.
- [Liu ve diğerleri — Görsel Talimat İnce Ayarıyla İyileştirilmiş Temel Modeller (arXiv:2310.03744)](https://arxiv.org/abs/2310.03744) — LLaVA-1.5.
- [Chen ve diğerleri — ShareGPT4V (arXiv:2311.12793)](https://arxiv.org/abs/2311.12793) — yoğun açıklama veri seti.
- [Karamcheti ve diğerleri — Prismatic VLMs (arXiv:2402.07865)](https://arxiv.org/abs/2402.07865) — tasarım alanı kıyaslama deneyleri.
- [Li ve diğerleri — LLaVA-OneVision (arXiv:2408.03326)](https://arxiv.org/abs/2408.03326) — birleşik tekli görüntü, çoklu görüntü, video.
