# Hizalama Araştırması Ekosistemi — MATS, Redwood, Apollo, METR

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/28-alignment-research-ecosystem/docs/en.md)

> Beş organizasyon 2026 laboratuvar-dışı hizalama araştırması katmanını tanımlar. MATS (ML Alignment & Theory Scholars): 2021 sonundan beri 527+ araştırmacı, 180+ makale, 10K+ atıf, h-endeksi 47; 2024 yaz dönemi 501(c)(3) olarak ~90 öğrenci ve 40 mentor ile dahil edildi; 2025 öncesi mezunların %80'i güvenlik/emniyet üzerinde çalışıyor, 200+'si Anthropic, DeepMind, OpenAI, BK AISI, RAND, Redwood, METR, Apollo'da. Redwood Research: Buck Shlegeris tarafından kurulan uygulamalı hizalama laboratuvarı; AI Control'ü (Ders 10) tanıttı; kontrol güvenlik davaları üzerinde BK AISI ile işbirliği yapar. Apollo Research: sınır laboratuvarları için dağıtım-öncesi plan (scheming) değerlendirmeleri; In-Context Scheming'in (Ders 8) ve Towards Safety Cases for AI Scheming'in yazarı. METR (Model Evaluation and Threat Research): görev-tabanlı yetenek değerlendirmeleri, otonom-görev zaman-ufku çalışmaları; "Common Elements of Frontier AI Safety Policies" laboratuvar çerçevelerini karşılaştırır. Eleos AI Research: model-refahı dağıtım-öncesi değerlendirmeleri (Ders 19); Claude Opus 4 refah değerlendirmesini yürüttü.

**Tür:** Öğren
**Diller:** yok
**Ön Koşullar:** Faz 18 · 01-27 (önceki Faz 18 dersleri)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Laboratuvar-dışı hizalama araştırması ekosisteminin beş organizasyonunu ve onların temel çıktısını tanımlayın.
- MATS'ın ölçeğini (öğrenciler, makaleler, h-endeksi) ve yetenek boru hattı olarak rolünü açıklayın.
- Redwood'ın AI Control gündemini ve BK AISI ile ortaklığını açıklayın.
- METR'ın görev-tabanlı değerlendirme metodolojisini açıklayın.

## Sorun

Sınır laboratuvarları (Ders 18) güvenlik değerlendirmelerini dahili olarak üretir ve seçilmiş sonuçları yayınlar. Laboratuvarların dışındaki ekosistem, değerlendirmelerin doğrulandığı, yeni başarısızlık modlarının ilk keşfedildiği ve yeteneğin eğitildiği yerdir. Ekosistemi anlamak, hangi araştırma bulgularının kim tarafından güvenildiğini yorumlamaya yardımcı olur.

## Kavram

### MATS (ML Alignment & Theory Scholars)

2021 sonunda başladı. Araştırma mentorluk programı; öğrenciler 10-12 haftayı belirli bir hizalama problemi üzerinde kıdemli bir araştırmacıyla geçirir.

Ölçek (2026):
- Kuruluşundan beri 527+ araştırmacı.
- 180+ yayınlanmış makale.
- 10K+ atıf.
- h-endeksi 47.
- 2024 yazı: 90 öğrenci + 40 mentor; 501(c)(3) olarak dahil edildi.

Kariyer sonuçları: 2025 öncesi mezunların ~%80'i güvenlik/emniyet üzerinde çalışıyor. 200+'si Anthropic, DeepMind, OpenAI, BK AISI, RAND, Redwood, METR, Apollo'da.

### Redwood Research

Uygulamalı hizalama laboratuvarı. Buck Shlegeris tarafından kuruldu. AI Control gündemini (Ders 10) tanıttı. Kontrol güvenlik davaları üzerinde BK AISI ile işbirliği yapar. Değerlendirme tasarımında DeepMind ve Anthropic'e danışmanlık yapar.

Kanonik makaleler: Greenblatt, Shlegeris ve ark., "AI Control" (arXiv:2312.06942, ICML 2024); Alignment Faking (Greenblatt, Denison, Wright ve ark., arXiv:2412.14093, Anthropic ile ortak).

Stil: belirli tehdit modelleri, en kötü durum rakipleri, stres-test edilebilen somut protokoller.

### Apollo Research

Sınır laboratuvarları için dağıtım-öncesi plan (scheming) değerlendirmeleri. In-Context Scheming'in (Ders 8, arXiv:2412.04984) yazarı. 2025 OpenAI anti-scheming eğitim işbirliğinde ortak. Towards Safety Cases for AI Scheming (2024) üretir.

Stil: aldatmanın ortaya çıkabileceği agentic-ayarlama değerlendirmeleri; üç-sütun ayrıştırması (yanlış hizalama, hedef-yönelimlilik, durumsal farkındalık).

### METR (Model Evaluation and Threat Research)

Görev-tabanlı yetenek değerlendirmeleri. Otonom-görev tamamlama zaman-ufku çalışmaları. "Common Elements of Frontier AI Safety Policies" (metr.org/common-elements, 2025) laboratuvar çerçevelerini karşılaştırır.

Apollo ile AI Scheming güvenlik-davası taslağında ortak yazar.

Stil: uzun-ufuk görev değerlendirmeleri, ampirik yetenek ölçümü, çerçeve sentezi.

### Eleos AI Research

Model-refahı dağıtım-öncesi değerlendirmeleri. Sistem kartının 5.3 bölümünde belgelenen Claude Opus 4 refah değerlendirmesini yürüttü. Ders 19'un refahla-ilgili iddiaları için dış metodoloji kontrolünü sağlar.

### Akış

MATS araştırmacıları eğitir. Mezunlar Anthropic, DeepMind, OpenAI'ye (laboratuvar güvenlik ekipleri) veya Redwood, Apollo, METR, Eleos'a (dış değerlendirme) gider. Dış değerlendiriciler laboratuvarlarla ve BK AISI / CAISI ile ortaklık yapar. Yayınlar, bir sonraki dönem için MATS'a geri beslenir.

### Bu katman neden önemli

Tek-kaynak değerlendirmeler güvenilmezdir: kendi modellerini değerlendiren laboratuvarların yapısal bir çıkar çatışması vardır. Dış değerlendiriciler, laboratuvarın yetersiz bildirebileceği başarısızlık modlarını gündeme getirebilir ve doğrulayabilir. 2024 Sleeper Agents makalesi (Ders 7) Anthropic + Redwood idi; Alignment Faking Anthropic + Redwood idi; In-Context Scheming Apollo idi; Anti-Scheming Apollo + OpenAI idi. Çok-organizasyon yapısı kalite kontrolüdür.

### Bu, Faz 18'de nereye oturuyor

Dersler 7-11 Redwood ve Apollo çalışmasına referans verir; Ders 18 METR'ın çerçeve karşılaştırmasına referans verir; Ders 19 Eleos'a referans verir. Ders 28, Faz'ın geri kalanının dayandığı ekosistemin açık organizasyonel haritasıdır.

## Uygulama

Kod yok. Laboratuvar-içi politika çalışmasına dış sentezin nasıl değer eklediğinin bir örneği olarak METR'ın "Common Elements of Frontier AI Safety Policies" çalışmasını okuyun.

## Ship It

Bu ders `outputs/skill-ecosystem-map.md` üretir. Bir hizalama iddiası veya değerlendirmesi verildiğinde, organizasyonu, yayın yerini ve metodolojik stili tanımlar ve bilinen-muadil organizasyonlara karşı çapraz kontrol yapar.

## Alıştırmalar

1. Dersler 7-15'ten bir makale seçin ve dahil olan organizasyonları tanımlayın. Yazarları MATS mezunlarına ve mevcut ekosistem bağlantılarına karşı çapraz kontrol edin.

2. METR'ın "Common Elements of Frontier AI Safety Policies" çalışmasını okuyun. Vurguladıkları üç laboratuvarlar-arası yakınsamayı ve iki en büyük ayrışmayı tanımlayın.

3. MATS kariyer sonuçları ~%80 güvenlik/emniyet. Bu seçim baskısının uyumsal (alanı eğitir) mi yoksa önyargılı (hetodoks pozisyonları filtreler) mi olduğunu tartışın.

4. Redwood ve Apollo'nun her ikisi de farklı stillerle kontrol/scheming çalışması yapar. Bir başarısızlık modu seçin ve her birinin onu nasıl araştıracağını açıklayın.

5. Eleos AI saf model-refahı organizasyonu olan tek kuruluştur. Farklı bir refah-bitşık soruya (bilişsel özgürlük, robotik bedenlenme vb.) odaklanan varsayımsal ikinci bir organizasyon tasarlayın ve metodolojisini açıklayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| MATS | "mentorluk programı" | ML Alignment & Theory Scholars; 2021'den beri 527+ araştırmacı |
| Redwood Research | "kontrol laboratuvarı" | Uygulamalı hizalama; AI Control yazarları; BK AISI ortağı |
| Apollo Research | "scheming değerlendirmeleri" | Sınır laboratuvarları için dağıtım-öncesi scheming değerlendirmeleri |
| METR | "görev-ufku değerlendirmeleri" | Görev-tabanlı yetenek değerlendirmeleri; çerçeve sentezi |
| Eleos AI | "refah laboratuvarı" | Model-refahı dağıtım-öncesi değerlendirmeleri |
| Yetenek boru hattı | "MATS -> laboratuvarlar" | MATS mezunları Anthropic, DM, OpenAI, Redwood, Apollo, METR'a akar |
| Dış değerlendirme | "laboratuvar-dışı kontrol" | Modelin üreticisi tarafından yapılmayan değerlendirme; güvenilirlik katar |

## İleri Okuma

- [MATS (ML Alignment & Theory Scholars)](https://www.matsprogram.org/) — mentorluk programı
- [Redwood Research](https://www.redwoodresearch.org/) — AI Control makaleleri
- [Apollo Research](https://www.apolloresearch.ai/) — scheming değerlendirmeleri
- [METR — Common Elements of Frontier AI Safety Policies](https://metr.org/blog/2025-03-26-common-elements-of-frontier-ai-safety-policies/) — çerçeve karşılaştırması
- [Eleos AI Research](https://www.eleosai.org/research) — model refahı metodolojisi
