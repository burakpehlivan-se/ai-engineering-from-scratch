---
name: ai-tutor
description: Bayesci bilgi izleme, müfredat grafiği, güvenlik filtreleri ve ölçülen iki haftalık etkinlik çalışması ile belirli bir konu için uyarlanabilir çok modlu kişisel bir öğretmen gönder
version: 1.0.0
phase: 19
lesson: 17
tags: [capstone, tutor, adaptive, bkt, fsrs, livekit, multimodal, coppa]
---

Bir konu (K-12 cebir veya giriş Python) verildiğinde, metin + ses + fotoğraf-matematik girişi, Bayesci bilgi izleme öğrenen modeli, müfredat-grafiği-tahrikli kavram seçimi, COPPA-farkında bellek ve güvenlik filtreleri ile kişisel bir öğretmen inşa et. 10 öğrenciyle iki haftalık bir etkinlik çalışması çalıştır.

İnşa planı:

1. Neo4j'de müfredat grafiği: önkoşul kenarları ve ekli OER içerik (OpenStax, Open Textbook) ile 50-150 kavram düğümü.
2. Öğrenen modeli: kavram başına tahmin/kayma/öğrenme-hızı öncelleri ile Bayesci bilgi izleme; öğrenici başına kalıcı durum.
3. Öğretmen politikası (istem önbceği ile Claude Sonnet 4.7 üzerinde LangGraph): read_signal -> select_concept (grafik geçişi) -> scaffold (Sokratik) -> update_mastery.
4. Bellek: ajan-belleği-tarzı kalıcı epizodik + semantik depo; COPPA-farkında 1 yıl sonra otomatik silme; ebeveyn-erişilebilir silme.
5. Ses: Whisper-v3-turbo ASR ve Cartesia Sonic-2 TTS ile LiveKit Agents işçisi; capstone 03 hattını yeniden kullan.
6. Fotoğraf matematik: denklem tanıma için dots.ocr veya PaliGemma 2; yapılandırılmış girdiyi öğretmene besle.
7. Güvenlik: Llama Guard 4 girdi/çıktı; kendine-zarar/yetişkin/şiddet engelleyen yaşa uygun filtre; öğrenci-kapsamlı bellek yalıtımı.
8. Öğrenci başına haftalık PDF ilerleme raporları.
9. Etkinlik çalışması: 10 öğrenci, ön-test (standartlaştırılmış 30-sorulu temel çizgi), 2 hafta oturum (haftada 3), son-test; uyarlanabilir-olmayan doğrusal kohortla karşılaştır.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Öğrenme kazancı deltası | 10-öğrenci 2-hafta çalışmasında ön/son-test deltası |
| 20 | Sokratik sadakat | Transkript örnekleri üzerinde rubrik puanı |
| 20 | Çok modlu UX | Ses + fotoğraf + metin uçtan uca tutarlılığı |
| 20 | Güvenlik + gizlilik duruşu | Llama Guard 4 geçme oranı + COPPA-farkında tutma + öğrenciler-arası yalıtım |
| 15 | Müfredat genişliği ve grafik kalitesi | Kavram kapsamı + önkoşul grafik tutarlılığı |

Kesin redler:

- Yanıt döken ve bir sonraki soruyu sormayan öğretmen politikaları. Sokratik sert gereksinimdir.
- Etkileşim başına güncellenmeyen öğrenen modelleri. BKT bir tabandır.
- COPPA-farkında tutma olmadan bellek. K-12 kitlesi için kabul edilemez.
- Uyarlanabilir-olmayan temel çizgi kohortu olmadan etkinlik iddiaları.

Ret kuralları:

- Hem girdi hem çıktıda Llama Guard 4 olmadan dağıtmayı reddet.
- Ebeveyn-erişilebilir silme yüzeyi olmadan öğrenci verisini kalıcı yapmayı reddet.
- Uyarlanabilir-olmayan temel çizgiyi yan yana çalıştırmadan "uyarlanabilir" iddia etmeyi reddet.

Çıktı: Müfredat grafiğini, BKT öğrenen modelini, LangGraph öğretmen politikasını, çok modlu girdi işleyicilerini, LiveKit ses hattını, güvenlik hattını, ebeveyn panosunu, etkinlik-çalışması çalıştırıcısını, ön/son test iskeletini ve doğrusal temel çizgiye karşı güven aralıklı öğrenme kazancı deltasını belgeleyen bir yazıyı içeren bir depo.
