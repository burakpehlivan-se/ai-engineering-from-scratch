# Capstone 04 — Çok Modlu (Multimodal) Belge Soru-Cevap (Görüntü-Öncelikli PDF, Tablolar, Grafikler)

> 2026'nın belge-Sorucevap sınırı OCR-sonra-metin yaklaşımından uzaklaşıp görüntü-öncelikli geç etkileşime (late interaction) doğru ilerledi. ColPali, ColQwen2.5 ve ColQwen3-omni her PDF sayfasını bir görüntü olarak ele alır, çok-vektörlü geç etkileşimle gömer ve sorgunun yamalara (patch) doğrudan dikkat etmesine izin verir. Finansal 10-K'lar, bilimsel makaleler ve el yazısı notlarda bu desen OCR-önce-yi büyük bir farkla geçer. Uçtan uca boru hattını 10k sayfada inşa edin ve OCR-sonra-metin karşısında yan yana karşılaştırmayı yayınlayın.

**Type:** Capstone
**Languages:** Python (pipeline), TypeScript (viewer UI)
**Prerequisites:** Phase 4 (computer vision), Phase 5 (NLP), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 12 (multimodal), Phase 17 (infrastructure)
**Phases exercised:** P4 · P5 · P7 · P11 · P12 · P17
**Time:** 30 saat

## Problem

Kuruluşlar OCR boru hatlarının bozduğu PDF'lerle dolu: döndürülmüş tabloları olan taranmış 10-K'lar, denklemlerle yoğun bilimsel makaleler, yalnızca görüntü olarak anlamlı grafikler, el yazısı ek açıklamalar. Bunları metin-öncelikli olarak ele almak, sinyalin yarısını kaybetmek demektir. 2026 yanıtı, ham sayfa görüntüleri üzerinde geç etkileşimli çok-vektörlü geri getirmedir. ColPali (Illuin Tech) bunu tanıttı; ColQwen2.5-v0.2 ve ColQwen3-omni doğruluğu yükseltti. ViDoRe v3'te görüntü-öncelikli geri getirme, OCR-sonra-metinden anlamlı marjlarla daha yüksek puan alır — ve grafiklerde, tablolarda ve el yazısında fark genişler.

Takas, depolama ve gecikmedir. Bir ColQwen gömmesi sayfa başına ~2048 yama vektörüdür, tek bir 1024-boyutlu vektör değil. Ham depolama şişer. DocPruner (2026), ölçülebilir doğruluk kaybı olmadan %50 budama sağlar. 10k sayfayı indeksleyecek, ViDoRe v3 nDCG@5'i ölçecek, 2 saniyenin altında yanıtlar sunacak ve doğrudan bir OCR-sonra-metin temel çizgisiyle karşılaştıracaksınız.

## Concept

Geç etkileşim, her sorgu tokenının her yama tokenına karşı puanlanması ve sorgu tokenı başına maksimum puanın toplanması anlamına gelir. Tek bir havuzlanmış vektöre ihtiyaç duymadan ince taneli eşleştirme elde edersiniz. Çok-vektörlü bir endeks (Vespa, Qdrant çok-vektörlü veya AstraDB) yama başına gömmeleri saklar ve geri getirme zamanında MaxSim çalıştırır.

Yanıtlayıcı, sorgu ve ilk k geri getirilen sayfaları görüntü olarak alan ve kanıt bölgeleri (sınırlayıcı kutular veya sayfa referansları) ile yanıt yazan bir görüntü-dil modelidir. Qwen3-VL-30B, Gemini 2.5 Pro ve InternVL3 2026'nın frontier seçimleridir. Denklemler ve bilimsel gösterim için, isteğe bağlı bir metin kanalı olarak bir OCR yedek (Nougat, dots.ocr) eklenir.

Değerlendirme iki boyutlu bir matristir. Bir eksen: içerik türü (düz metin paragrafları, yoğun tablolar, çubuk/çizgi grafikler, el yazısı notlar, denklemler). Diğer eksen: geri getirme yaklaşımı (görüntü-öncelikli geç etkileşim vs OCR-sonra-metin vs hibrit). Her hücre nDCG@5 ve yanıt doğruluğu alır. Rapor teslim edilen şeydir.

## Architecture

```
PDFs -> page renderer (PyMuPDF, 180 DPI)
           |
           v
  ColQwen2.5-v0.2 embed (multi-vector per page, ~2048 patches)
           |
           +------> DocPruner 50% compression
           |
           v
   multi-vector index (Vespa or Qdrant multi-vector)
           |
query ----+----> retrieve top-k pages (MaxSim)
           |
           v
  VLM answerer: Qwen3-VL-30B | Gemini 2.5 Pro | InternVL3
    inputs: query + top-k page images + optional OCR text
           |
           v
  answer with cited page numbers + evidence regions
           |
           v
  Streamlit / Next.js viewer: highlighted boxes on source page
```

#### Açıklama

Bu mimari görüntü-öncelikli belge Soru-Cevap'ın tam boru hattını gösterir. PDF'ler PyMuPDF ile 180 DPI'da sayfa görüntülerine dönüştürülür. ColQwen2.5-v0.2 her sayfayı sayfa başına ~2048 yama gömmeleri olarak kodlar. DocPruner en bilgi-taşıyan yamaları tutarak depolama maliyetini yarıya indirir. Sorgu zamanında yama gömmelerine karşı MaxSim (maksimum benzerlik) hesaplanır ve en iyi k sayfa seçilir. Bir görüntü-dil modeli (Qwen3-VL-30B veya Gemini 2.5 Pro) sorgu + ilk sayfaları alıp alıntılı bir yanıt üretir. Son olarak Next.js izleyici, kaynak sayfada vurgulanan sınırlayıcı kutuları (bounding box) gösterir.

## Stack

- Sayfa oluşturma: 180 DPI'da PyMuPDF (fitz), portre-normalleştirilmiş
- Geç etkileşim modeli: ColQwen2.5-v0.2 veya ColQwen3-omni (Hugging Face'te vidore ekibi)
- Endeks: Çok-vektörlü alan ile Vespa veya Qdrant çok-vektörlü veya MaxSim ile AstraDB
- Budama: DocPruner 2026 politikası (yüksek-varyans yamaları tut, < %0.5 doğruluk kaybıyla %50 sıkıştırma)
- OCR yedek (denklemler / yoğun tablolar): dots.ocr veya Nougat
- Görüntü-dil yanıtlayıcı: Qwen3-VL-30B self-hosted veya Gemini 2.5 Pro hosted; yedek InternVL3
- Değerlendirme: ViDoRe v3 kıyaslaması, çok-sayfalı akıl yürütme için M3DocVQA
- İzleyici arayüzü: Kanvas yerleşimi ile kanıt bölgeleri için Next.js 15

## Build It

1. **Hazmetme.** 10-K'lar, bilimsel makaleler ve taranmış belgeler arasında 10k PDF sayfalık bir korpusu gezin. Her sayfayı 1536x2048 PNG'ye dönüştürün. `{doc_id, page_num, image_path}` kalıcı kılın.

2. **Gömme.** Her sayfa görüntüsünde ColQwen2.5-v0.2'yi çalıştırın. Çıktı şekli 128 boyutlu ~2048 yama gömmeleri. En yüksek-sinyalli yarıyı tutmak için DocPruner uygulayın. Vespa çok-vektörlü alanına veya Qdrant çok-vektörlüye yazın.

3. **Sorgu.** Gelen her sorgu için, sorgu kulesi (token-düzey gömmeler) ile gömün. Endekse karşı MaxSim çalıştırın: her sorgu tokenı için, sayfa yaması gömmeleri üzerinde maksimum nokta-çarpımı alın, toplayın. İlk k sayfayı döndürün.

4. **Sentezleme.** Qwen3-VL-30B'yi sorgu ve ilk 5 sayfa görüntüsüyle çağırın. İstem: "Yalnızca sağlanan sayfaları kullanarak yanıtlayın. Her iddiayı (doc_id, sayfa) ile alıntılayın ve bölgeyi adlandırın (şekil, tablo, paragraf)."

5. **Kanıt bölgeleri.** Yanıtı sonradan işleyerek alıntılanmış bölgeleri çıkarın. Görüntü-dil modeli sınırlayıcı kutular yayınlıyorsa (Qwen3-VL yapar), bunları izleyicide yerleşim olarak işleyin.

6. **OCR yedek.** Denklem-yoğun olarak tanımlanan sayfalar için (görüntü varyansına dayalı sezgisel), Nougat veya dots.ocr çalıştırın ve OCR metnini görüntünün yanında ek bir kanal olarak geçirin.

7. **Eval.** ViDoRe v3 (geri getirme nDCG@5) ve M3DocVQA (çok-sayfalı Soru-Cevap doğruluğu) çalıştırın. Aynı sentezleyiciyle aynı korpus üzerinde OCR-sonra-metin boru hattını da çalıştırın. İçerik türü × yaklaşım matrisi üretin.

8. **Arayüz.** Önce Streamlit prototipi; kanıt bölgesi yerleşimli sayfa-sayfa üretim izleyici olarak Next.js 15.

## Use It

```
$ doc-qa ask "what was the 2024 operating margin change for segment EMEA?"
[retrieve]   top-5 pages in 320ms (ColQwen2.5, MaxSim, Vespa)
[synth]      qwen3-vl-30b, 1.4s, cited (form-10k-2024, p. 88) + (..., p. 92)
answer:
  EMEA operating margin moved from 18.2% to 16.8%, a 140bp decline.
  cited: 10-K-2024.pdf p.88 (Table 4, Segment Operating Margin)
         10-K-2024.pdf p.92 (MD&A, Operating Performance)
[viewer]     open with highlighted bounding boxes overlaid on p.88 Table 4
```

#### Açıklama

Bu örnek finansal bir 10-K üzerinde tipik bir sorgu akışını gösterir. Kullanıcı EMEA bölümünün 2024 faaliyet kâr marjı değişimini sorar. Sistem 320ms'de ilk 5 sayfayı getirir, Qwen3-VL-30B 1.4 saniyede sentezler ve yanıtı her iki kaynak sayfaya sınırlayıcı kutular yerleştirilmiş şekilde döndürür. İzleyici açıldığında kullanıcı doğrudan kaynak tabloya yönlendirilir ve iddianın doğrulanması tek tıklama olur.

## Ship It

`outputs/skill-doc-qa.md` teslim edilen şeyi tanımlar: belirli bir korpusa ayarlanmış ve ViDoRe v3 üzerinde OCR-sonra-metin temel çizgisine karşı değerlendirilmiş görüntü-öncelikli çok modlu bir belge Soru-Cevap sistemi.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | ViDoRe v3 / M3DocVQA doğruluğu | OCR-metin temel çizgisine ve yayınlanmış sıralama tablosuna karşı kıyaslama sayıları |
| 20 | Kanıt bölgesi temellendirme | Gerçekten yanıt aralığını içeren alıntılanmış bölgelerin oranı |
| 20 | Depolama ve gecikme mühendisliği | DocPruner sıkıştırma oranı, endeks p95, yanıt p95 |
| 20 | Çok-sayfalı akıl yürütme | El ile etiketlenmiş 100-soruluk çok-sayfalı küme üzerinde doğruluk |
| 15 | Kaynak-inceleme UX | İzleyici netliği, yerleşim sadakati, yan yana karşılaştırma araçları |
| **100** | | |

## Exercises

1. Aynı korpus üzerinde ColQwen2.5-v0.2 ile ColQwen3-omni'yi karşılaştırın. Hangisi hangi sayfaları doğru alıp diğeri kaçırıyor? Endekse bir "içerik sınıfı" etiketi ekleyerek türe göre yönlendirin.

2. Gömmeleri agresif şekilde budayın (%75, %90). Sıkıştırma uçurumunu bulun: ViDoRe nDCG@5'in OCR temel çizgisinin altına düştüğü nokta.

3. Bir hibrit inşa edin: OCR-sonra-metin ve ColQwen'i paralel çalıştırın, RRF ile birleştirin, bir cross-encoder ile yeniden sıralayın. Hibrit tek başına olanları geçer mi? En çok nerede yardımcı olur?

4. Qwen3-VL-30B'yi daha küçük bir görüntü-dil modeliyle (Qwen2.5-VL-7B) değiştirin. Dolar başına doğruluk eğrisini ölçün.

5. El yazısı not desteği ekleyin. El yazısı korpusunu işleyin, ColQwen ile gömün, geri getirmeyi ölçün. Bir el yazısı OCR boru hattına karşı karşılaştırın.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Geç etkileşim | "ColPali tarzı geri getirme" | Sorgu tokenları sayfa yamalarına karşı bağımsız olarak puanlanır; MaxSim toplar |
| Çok-vektörlü | "Yama başına gömme" | Her belgenin bir havuzlanmış vektör değil birçok vektörü vardır |
| MaxSim | "Geç etkileşim puanlaması" | Her sorgu tokenı için, belge vektörleri üzerinde maksimum benzerlik alın; toplayın |
| DocPruner | "Yama sıkıştırma" | 2026 budaması, ihmal edilebilir doğruluk kaybıyla yamaların %50'sini tutar |
| ViDoRe v3 | "Belge geri getirme kıyaslaması" | Görsel-belge geri getirmesini ölçmek için 2026 standardı |
| Kanıt bölgesi | "Alıntılanmış sınırlayıcı kutu" | Yanıt aralığını yerelleştiren kaynak sayfadaki bir bbox |
| OCR yedek | "Denklem kanalı" | Denklem veya tablo-yoğun sayfalar için görüntünün yanında kullanılan metin boru hattı |

## Further Reading

- [ColPali (Illuin Tech) repository](https://github.com/illuin-tech/colpali) — referans geç etkileşim belge geri getirme
- [ColPali paper (arXiv:2407.01449)](https://arxiv.org/abs/2407.01449) — kurucu yöntem makalesi
- [ColQwen family on Hugging Face](https://huggingface.co/vidore) — üretime hazır kontrol noktaları
- [M3DocRAG (Adobe)](https://arxiv.org/abs/2411.04952) — çok-sayfalı çok modlu RAG temel çizgisi
- [Vespa multi-vector tutorial](https://docs.vespa.ai/en/colpali.html) — referans sunum yığını
- [Qdrant multi-vector support](https://qdrant.tech/documentation/concepts/vectors/#multivectors) — alternatif endeks
- [AstraDB multi-vector](https://docs.datastax.com/en/astra-db-serverless/databases/vector-search.html) — alternatif yönetilen endeks
- [Nougat OCR](https://github.com/facebookresearch/nougat) — denklem-yetenekli OCR yedek
