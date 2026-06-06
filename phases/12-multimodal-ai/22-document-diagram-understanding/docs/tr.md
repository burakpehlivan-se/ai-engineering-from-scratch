# Belge ve Diyagram Anlama

> Belgeler fotoğraflar değildir. Bir PDF, bilimsel makale, fatura veya el yazısı form, düz görüntü anlayışının yakalayamadığı düzen (layout), tablolar, diyagramlar, dipnotlar, başlıklar ve semantik yapıya sahiptir. Öncesi VLM yığını bir boru hattıydı (pipeline): Tesseract OCR + LayoutLMv3 + tablo çıkarma sezgisel yöntemleri. VLM dalgası bunu OCR'sız modellerle değiştirdi — Donut (2022), Nougat (2023), DocLLM (2023) — doğrudan yapılandırılmış markup üreten. 2026'ya kadar sınır "sayfa görüntüsünü 2576px doğal çözünürlükte Claude Opus 4.7'ye besleyin" haline geldi ve yapılandırılmış markup çıktısı bedavaya geldi. Bu ders belge YZ'nin üç dönemi boyunca yolculuğunu okur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, düzen farkında belge ayrıştırıcı iskeleti)
**Ön koşullar:** Faz 12 · 05 (LLaVA), Faz 5 (NLP)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Belge YZ'nin üç dönemini açıklayın: OCR boru hattı, OCR'sız, VLM-doğal.
- LayoutLMv3'nün üç girdi akışını tanımlayın: metin, düzen (bbox), görüntü yamaları (patches), birleşik maskeleme ile.
- Donut'u (OCR'sız, görüntü → markup), Nougat'ı (bilimsel makale → LaTeX), DocLLM'yi (düzey-farkında üreteç), PaliGemma 2'yi (VLM-doğal) karşılaştırın.
- Yeni bir görev için bir belge modeli seçin (faturalar, bilimsel makaleler, el yazısı formlar, Çince makbuzlar).

## Problem

"Bu PDF'i anla" aldatıcı derecede zordur. Bilgi şu yerlerde oturur:

- Metin içeriği (sinyalin %90'ı).
- Düzen (başlıklar, dipnotlar, kenar çubukları, iki sütunlu format).
- Tablolar (satırlar, sütunlar, birleşik hücreler).
- Şekiller ve diyagramlar.
- El yazısı notlar.
- Fontlar ve tipografi (başlık vs gövde).

Ham OCR metni döker ve geri kalanını kaybeder. Faturalarla ilgilenen bir sistemin "$1.245: Toplam" ifadesinin dipnottan değil sağ alt köşeden geldiğini bilmesi gerekir.

## Kavram

### 1. Dönem — OCR boru hattı (2021 öncesi)

Klasik yığın:

1. PDF → sayfa başına görüntü.
2. Tesseract (veya ticari OCR) kelime başına sınırlayıcı kutu (bounding box) ile metin çıkarır.
3. Analiz düzenleyicisi blokları (başlık, tablo, paragraf) belirler.
4. Tablo yapısı tanıyıcı tabloları ayrıştırır.
5. Alan kuralları + regex alanları çıkarır.

Temiz basılmış metin için çalışır. El yazısı, eğik tarama, karmaşık tablolar, İngilizce dışı scriptlerde bozulur. Her hata modu özel bir istisna yolu gerektirir.

### TrOCR (2021)

TrOCR (Li ve ark., arXiv:2109.10282), Tesseract'ın klasik CNN-CTC'sini sentetik + gerçek metin görüntüleri üzerinde eğitilmiş bir transformer encoder-decoder ile değiştirdi. El yazısı ve çok dilli metinde temiz kazanım. Hâlâ bir boru hattı (algılayıcı sonra TrOCR sonra düzen) ancak OCR adımı dramatik olarak gelişti.

### 2. Dönem — OCR'sız (2022-2023)

İlk OCR'sız modeller şunu söyledi: algılamayı tamamen atlayın, görüntü piksellerini doğrudan yapılandırılmış çıktıya eşleyin.

Donut (Kim ve ark., arXiv:2111.15664):
- Encoder-decoder transformer, encoder Swin-B.
- Çıktı, form anlama için JSON, özetleme için markdown veya herhangi bir görev-spesifik şemadır.
- OCR yok, düzen yok, algılama yok.

Nougat (Blecher ve ark., arXiv:2308.13418):
- Özellikle bilimsel makaleler üzerinde eğitilmiş.
- Çıktı LaTeX / markdown'dır.
- Denklemleri, çok sütunlu düzeni, şekilleri işler.
- Her arXiv-parser'ın çağırdığı model.

Bunlar uzmanlardır, genelciler değil. Donut bilimsel makalede başarısız olur; Nougat faturada başarısız olur.

### LayoutLMv3 (2022)

Farklı bir iz. LayoutLMv3 (Huang ve ark., arXiv:2204.08387) OCR'ı korur ancak düzen anlayışını ekler:

- Üç girdi akışı: OCR metin token'ları, token başına 2B sınırlayıcı kutu, görüntü yamaları.
- Üç modallık genelinde masked eğitim hedefi (masked metin, masked yamalar, masked düzen).
- Aşağı akım: sınıflandırma, varlık çıkarma, tablo soru-cevap.

LayoutLMv3 OCR tabanlı belge anlamanın zirvesidir. Formlar ve faturalarda güçlü. OCR yukarı akım gerektirir. Standart belge benchmark'larında en iyi VLM-öncesi doğruluk.

### DocLLM (2023)

DocLLM (Wang ve ark., arXiv:2401.00908) LayoutLM'nin üreteç kardeşidir. Düzen token'larına koşullu serbest biçimli yanıtlar üretir. Belgeler üzerinde soru-cevap için daha iyidir; hâlâ OCR girdisine bağlıdır.

### 3. Dönem — VLM-doğal (2024+)

2024'te VLM'ler boru hattını tamamen değiştirecek kadar iyi oldu. Sayfa görüntüsünü yüksek çözünürlükte bir VLM'e besleyin, soruyu sorun, cevabı alın.

- LLaVA-NeXT 336-tile AnyRes küçük belgeler için çalışır.
- Qwen2.5-VL dinamik çözünürlüğü 2048+ pikseli doğal olarak işler.
- Claude Opus 4.7 2576px belgeleri destekler.
- PaliGemma 2 (Nisan 2025) özellikle belgeler + el yazısı için eğitilmiştir.

VLM-doğal ile OCR boru hattı arasındaki fark hızla kapandı. 2026'ya kadar VLM-doğal şunlarda kazanır:

- Sahne metni (el yazısı + basılmış, karışık scriptler).
- Birleşik hücrelere sahip karmaşık tablolar.
- Metne gömülü matematik denklemleri.
- Metin notları olan şekiller.

OCR boru hattı hâlâ şunlarda kazanır:

- Sayfa başına gecikmenin önemli olduğu devasa ölçekli saf tarama iş yükleri.
- Boru hattı güvenilirliği (deterministik hatalar vs VLM halüsinasyonları).
- Denetlenebilir OCR çıktısı gerektiren düzenlenmiş ortamlar.

### Claude 4.7 / GPT-5 sınırı

2576 piksel doğal girdide, sınır VLM'leri neredeyse insan düzeyinde doğrulukla belge anlama yapar. 2026 başındaki benchmark rakamları:

- DocVQA: Claude 4.7 ~95.1, PaliGemma 2 ~88.4, Nougat ~77.3, boru hattı LayoutLMv3 ~83.
- ChartQA: Claude 4.7 ~92.2, GPT-4V ~78.
- VisualMRC: Claude 4.7 ~94.

Kapalı model farkı çoğunlukla çözünürlük ve temel LLM ölçeğidir. 7B'deki açık modeller birkaç puan geridedir ancak yakalıyor.

### Matematik denklemleri ve LaTeX çıktısı

Bilimsel makaleler denklemler için tam LaTeX çıktısı gerektirir. Nougat bunun için eğitilmiştir. LaTeX hedefleriyle eğitilmiş VLM'ler (Qwen2.5-VL-Math, Nougat türevleri) kullanılabilir LaTeX üretir. Açık LaTeX eğitimi olmadan VLM'ler okunabilir ancak hassas olmayan transkripsiyonlar üretir.

2026'da bilimsel makale boru hatları için: PDF üzerinde Nougat'ı, ardından zorlu sayfalarda bir VLM zincirleyin.

### El yazısı

Hâlâ en zor alt görev. Karışık basılmış + el yazısı (doktor notları, doldurulmuş formlar), OCR boru hattının hâlâ VLM'leri yendiği maliyet alanıdır. Saf el yazısı VLM'leri gelişiyor (Claude 4.7, PaliGemma 2).

### 2026 reçetesi

Yeni bir belge-YZ projesi için:

- Ölçekli saf basılmış faturalar: LayoutLMv3 + kurallar, maliyet-etkin.
- Karışık belgeler (bilimsel + el yazısı + formlar): VLM-doğal (PaliGemma 2 veya Qwen2.5-VL).
- Tam alım: matematik için Nougat, şekiller için VLM.
- Düzenleyici: çapraz kontrol için OCR boru hattı + VLM doğrulayıcı.

## Kullan

`code/main.py`:

- (metin, bbox) çiftleri verildiğinde LayoutVMv3 tarzı girdi üreten oyuncak bir düzen-farkında tokenizer.
- Formlar için JSON şablonu üreten Donut tarzı bir görev şeması üreteci.
- OCR boru hattı, Donut, Nougat ve VLM-doğal arasında sayfa başına token bütçeleri karşılaştırması.

## Teslim Et

Bu ders `outputs/skill-document-ai-stack-picker.md` dosyasını üretir. Bir belge-YZ projesi (alan, ölçek, kalite, düzenleme) verildiğinde OCR boru hattı, OCR'sız uzman ve VLM-doğal arasında seçim yapar.

## Alıştırmalar

1. Projeniz günde 10M fatura. Doğruluktan ödün vermeden sayfa başına maliyeti en aza indiren yığın hangisidir?

2. LayoutVMv3 neden form soru-cevabında saf-CLIP-VLM'leri yenerken sahne metninde düşük performans gösterir? Bbox akışı neyi feda eder?

3. Nougat LaTeX üretir. VLM-doğal çıktının Nougat'ı LaTeX sadakatinde yendiği ve Nougat'ın kazandığı bir test durumu önerin.

4. PaliGemma 2 makalesini okuyun (Google, 2024). PaliGemma 1'e kıyasla belge doğruluğunu artıran temel eğitim verisi eklentisi neydi?

5. Düzenleyici-güvenli bir hibrit tasarlayın: birincil olarak OCR boru hattı, ikincil çapraz kontrol için VLM. Anlaşmazlığı nasıl çözümlersiniz?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| OCR boru hattı | "Tesseract tarzı" | Aşama aşama yığın: algıla → OCR → düzen → kurallar; deterministik, kırılgan |
| OCR'sız | "Donut tarzı" | Açık OCR'ı atlayan görüntüden-çıktıya transformer; tek model |
| Düzen-farkında | "LayoutLM" | Girdi token başına bbox koordinatları içerir; modallıklar arası birleşik maskeleme |
| VLM-doğal | "Sınır VLM" | Sayfa görüntüsünü yüksek çözünürlükte Claude/GPT/Qwen VLM'e doğrudan besle; boru hattı yok |
| DocVQA | "Belge benchmark'ı" | Belge VQA standardı; en çok atıf yapılan puan |
| Markup çıktısı | "LaTeX / MD" | Serbest biçimli metin yerine yapılandırılmış çıktı formatı; aşağı akım otomasyonu sağlar |

## Daha Fazla Kaynak

- [Li ve ark. — TrOCR (arXiv:2109.10282)](https://arxiv.org/abs/2109.10282)
- [Blecher ve ark. — Nougat (arXiv:2308.13418)](https://arxiv.org/abs/2308.13418)
- [Huang ve ark. — LayoutLMv3 (arXiv:2204.08387)](https://arxiv.org/abs/2204.08387)
- [Kim ve ark. — Donut (arXiv:2111.15664)](https://arxiv.org/abs/2111.15664)
- [Wang ve ark. — DocLLM (arXiv:2401.00908)](https://arxiv.org/abs/2401.00908)
