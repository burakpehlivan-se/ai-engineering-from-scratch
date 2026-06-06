---
name: duplex-pipeline
description: Bir ses-ajan iş yükü için tam çift yönlü (full-duplex, Moshi) veya pipeline (VAD + STT + LLM + TTS) mimarisi seçer.
version: 1.0.0
phase: 6
lesson: 15
tags: [moshi, hibiki, full-duplex, voice-agent, streaming]
---

İş yükü (gecikme hedefi, araç çağrısı ihtiyaçları, dil kapsamı, donanım bütçesi, bulut vs uç) verildiğinde şunu üretirsiniz:

1. Mimari. Tam çift yönlü (Moshi / GPT-4o Realtime / Gemini Live) vs pipeline (LiveKit + STT + LLM + TTS, Ders 12). Tek cümlelik neden.
2. Model. Moshi · Hibiki · Hibiki-Zero · Sesame CSM · GPT-4o Realtime · Gemini 2.5 Live · geleneksel pipeline. Neden.
3. Ölçek. Oturum başına GPU maliyeti (Moshi bir yuva tutar), maks eşzamanlı oturum, soğuk başlangıç etkisi.
4. Araç çağrısı yolu. Gerekirse — hibrit pipeline (çift yönlü + araç çağrıları için harici LLM) veya salt pipeline. Takas açıklaması.
5. Dil kapsamı. Tam çift yönlü modellerin dar dil desteği vardır; pipeline'lar LLM'nin çok dilli yeteneğini devralır.

Araç çağrısı / erişim gerektiren kurumsal ajanlar için salt tam çift yönlü mimariyi reddedin — Moshi bir diyalog modelidir, ajan çatısı değil. 250 ms'nin altında konuşma ajanları için salt pipeline'ı reddedin — aşamalar birikir. Tek GPU'da >4 eşzamanlı oturum için Moshi'yi reddedin — çakışmaya girer.

Örnek girdi: "Dil öğrenimi için ses arkadaşı — konuşma akıcılığı pratiği. İngilizce + Fransızca. < 250 ms duyarlılık. 10k günlük aktif."

Örnek çıktı:
- Mimari: tam çift yönlü (Moshi). 250 ms'nin altı gecikme gereksinimi + konuşma akıcılığı, Moshi'nin güçlü yönlerine uyuyor.
- Model: Moshi. EN + FR'nin ikisi de iyi destekleniyor. CC-BY 4.0 lisans.
- Ölçek: 4-6 eşzamanlı oturum başına bir L4 GPU → %10 eşzamanlılıkta 10k DAU için pik ~1500 GPU. Kyutai Pocket TTS + yerel Whisper kullanan cihaz-üstü hafif mod için plan yapın.
- Araç çağrısı: minimal — "dilbilgisi ipucunu göster" ve "bu ifadeyi çevir" küçük bir LLM yan kolu ile yönlendirilebilir; etkileşimin çoğu açık uçlu diyalogdur, Moshi'nin parladığı yer.
- Dil kapsamı: EN + FR (yerel); Hibiki-Zero adaptasyonu ile ES / DE / JP (yeni dil başına 1000 saat ses gerekli).
