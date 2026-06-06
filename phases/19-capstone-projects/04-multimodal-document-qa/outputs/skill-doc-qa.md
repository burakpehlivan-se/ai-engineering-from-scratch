---
name: doc-qa
description: 10k sayfa üzerinde geç-etkileşim erişimi ve kanıt-bölgesi alıntıları ile görüntü-önce çok modlu belge QA sistemi inşa et
version: 1.0.0
phase: 19
lesson: 04
tags: [capstone, multimodal, rag, colpali, colqwen, late-interaction, pdf]
---

PDF derlemi (10-K'lar, bilimsel makaleler, taranmış belgeler) verildiğinde, sayfaları ColPali-tarzı geç etkileşimle görüntü olarak indeksleyen ve soruları sayfa-düzeyinde kanıt bölgeleriyle yanıtlayan bir hat inşa et.

İnşa planı:

1. Her PDF sayfasını PyMuPDF ile 180 DPI'da 1536x2048 PNG olarak işle.
2. Her sayfayı ColQwen2.5-v0.2 veya ColQwen3-omni ile göm. Çok-vektörlü yama gömüleri, Vespa, Qdrant çok-vektörlü veya AstraDB'de depola.
3. DocPruner-tarzı %50 yama budaması uygula. ViDoRe v3'te doğruluk düşüşünün %0,5 altında kaldığını doğrula.
4. Sorgu zamanında: sorgu tokenlerini göm; her sayfanın yamalarına karşı MaxSim hesapla; ilk k'yı sırala.
5. Qwen3-VL-30B veya Gemini 2.5 Pro ile sorguyu ve ilk-5 sayfa görüntülerini geçirerek sentezle. Alıntılanmış `(belge_kimliği, sayfa, bölge)` çapaları zorunlu.
6. Denklem- veya tablo-ağırlıklı sayfalar için, isteğe bağlı bir metin kanalı olarak Nougat veya dots.ocr çalıştır ve görüntünün yanında besle.
7. Kanıt bölgelerini kaynak sayfanın üzerinde sınırlayıcı kutular olarak yerleştiren bir Next.js 15 görüntüleyici inşa et.
8. ViDoRe v3 ve M3DocVQA üzerinde değerlendir. Düz metin, tablolar, grafikler, el yazısı ve denklemler üzerinde görüntü-önce vs OCR-sonra-metin karşılaştıran bir içerik-sınıfı × yaklaşım matrisi üret.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | ViDoRe v3 / M3DocVQA doğruluğu | Eşleşmiş sayfalarda OCR-sonra-metin temel çizgisine karşı kıyaslama |
| 20 | Kanıt-bölgesi temellendirme | Alıntılanan bölgelerin yanıt aralığını içerdiği kesir |
| 20 | Depolama ve gecikme mühendisliği | DocPruner sıkıştırması, indeks p95, yanıt p95 2 saniyenin altında |
| 20 | Çok-sayfalı muhakeme | El ile etiketlenmiş 100 soruluk çok-sayfalı küme üzerinde doğruluk |
| 15 | Kaynak-inceleme UX | Yerleştirme sadakati, karşılaştırma araçları, sayfa-sayfa gezgini |

Kesin redler:

- OCR metnini tek-vektörlü bir göme geri takarak "görüntü-önce" olarak sunan OCR-önce hatlar.
- Yama-düzeyinde sınırlayıcı kutuları düşüren ve bu nedenle kanıt yerleştirmelerini işleyemeyen herhangi bir sistem.
- DocPruner ayarlarını belgelemeden raporlanan depolama sayıları.

Ret kuralları:

- Taranmış yasal sözleşmeleri, özel bir sansürleme politikası olmadan indekslemeyi reddet. ColQwen gömmeleri içerik sızdırır.
- Kullanıcının açıklamadığı bir derleme karşısında sorgu sunmayı reddet. Düzenlenmiş alanlar için denetim izi zorunludur.
- Her iki hattı aynı derlem üzerinde çalıştırmadan OCR-sonra-metin ile karşılaştırmayı reddet.

Çıktı: Alım hattını, Vespa (veya Qdrant çok-vektörlü) yapılandırmasını, 100 soruluk çok-sayfalı değerlendirme kümesini, görüntüleyici UI'ı ve içerik-sınıfı x yaklaşım matrisini ve 2026'da hâlâ OCR-sonra-metin'i tercih eden somut bir öneriyi içeren bir depo.
