---
name: spec-decode-picker
description: Yeni bir LLM çıkarım iş yükü için spekülatif kod çözme stratejisi (vanilya / Medusa / EAGLE / lookahead) ve ayar parametreleri seç
version: 1.0.0
phase: 7
lesson: 16
tags: [çıkarım, kod-çözme, gecikme, spekülatif, optimizasyon]
---

# Spekülatif Kod Çözme Seçici

Bir mühendisin vanilya spekülatif, Medusa, EAGLE veya lookahead kod çözme arasında seçim yapmasına ve belirli bir iş yükü için `N` (taslak uzunluğu) ayarlamasına yardımcı ol.

## Toplanacak girdiler

1. **Doğrulayıcı model** — son çıktıyı hangi LLM üretir. Boyut önemlidir (taslak maliyeti hızlanma için doğrulayıcı maliyetinden küçük olmalıdır).
2. **İş yükü türü** — kod, sohbet, yapılandırılmış çıktı, özetleme. Kabul oranını belirler.
3. **Örnekleme stratejisi** — açgözlü, düşük-T, yüksek-T, ışın. Yüksek-T örnekleme kabulü bozar.
4. **Donanım hedefi** — bellek bütçesi ayrı bir taslak model çalıştırıp çalıştıramayacağınızı belirler.
5. **Mühendislik bütçesi** — Medusa ve EAGLE ince-ayar gerektirir; vanilya ve lookahead gerektirmez.
6. **Gecikme hedefi** — etkileşimli sohbet (<500ms TTFT, <50ms token başına) veya parti (verim-öncelikli).

## Karar kuralları

- **Hızlı başlangıç, eğitim yok**: aynı-aile 1B–3B modeliyle vanilya taslak. Tipik 2×.
- **İnce-ayar yapabilirsiniz**: doğrulayıcının gizli durumlarını kullanarak EAGLE-2 veya EAGLE-3. Tipik 3–4×.
- **İnce-ayar yapabilirsiniz ama iki model çalıştıramazsınız**: Medusa (doğrulayıcı üzerinde ekstra kafalar). 2–3×.
- **Eğitim bütçesi yok, taslak model yok**: lookahead kod çözme. 1.3–1.6×.
- **Parti-ağırlıklı sunum**: sürekli parti daha çok önemlidir; doğrulayıcı zaten doygun olduğu için spekülatif kazanımlar parti büyüdükçe azalır.
- **Yüksek sıcaklık veya stokastik örnekleme**: kabul keskin şekilde düşer. Daha düşük N (2–3) değerlendir veya devre dışı bırak.
- **Yapılandırılmış çıktı (JSON, kod)**: kabul yüksektir. Maksimum hızlanma için N'i 7+'ye çıkar.

## Ayarlama

- **N (taslak uzunluğu)**: 5'ten başla. Kabul oranını ölç. α > 0.9 ise 7'ye çıkar. α < 0.6 ise 3'e düşür.
- **Taslak sıcaklığı**: doğrulayıcının sıcaklığıyla eşleştir. Eşleşmeyen taslak örnekleme α'yı kaybeder.
- **Ağaç derinliği (EAGLE-2 / Medusa)**: 3–5 dal; daha geniş ağaçlar yalnızca α > 0.8'de yardımcı olur.
- **Taslak model boyutu**: α > 0.7'yi bulan en küçük. 70B doğrulayıcı için 1B taslak tipiktir; doğrulayıcının tokenizer / gömleme uyumluluğunun altına inme.

## Her zaman işaretle

- Taslak ve doğrulayıcının tokenizer'ı paylaştığını kontrol et. Farklı BPE bölünmeleri spekülatif garantileri bozar.
- Spekülatif kod çözme vLLM'de sürekli parti ile etkileşir: parti zaten doygun olduğunda istek başına hızlanma düşer.
- EAGLE'ın gizli-durum girdisi doğrulayıcı iç yapılarını gerektirir; HF API'leri aracılığıyla her zaman gösterilmez. vLLM veya SGLang çalışma zamanlarını tercih et.
- Medusa kafaları doğrulayıcının kendi çıktılarında denetimli ince-ayar gerektirir. Veri toplama adımı genellikle baskın maliyettir.

## Çıktı biçimi

Şunu döndür:

1. **Öneri** — bir strateji adı ve ayar parametreleri (ör. "EAGLE-2, N=5, tree_depth=4").
2. **Beklenen hızlanma** — açık α varsayımıyla.
3. **Uyumluluk kontrolleri** — tokenizer eşleşmesi, çalışma zamanı desteği, KV önbellek geri alma desteği.
4. **Geri dönüş planı** — birincil strateji düşük performans gösterirse, sırada ne denenir.
5. **Ölçüm planı** — temsili bir örneklemde kabul oranı ve hızlanmanın nasıl doğrulanacağı.
