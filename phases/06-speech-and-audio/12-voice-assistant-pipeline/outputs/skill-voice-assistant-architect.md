---
name: voice-assistant-architect
description: Belirli bir iş yükü için tam yığın bir ses asistanı spesifikasyonu üretir — bileşenler, gecikme bütçesi, gözlemlenebilirlik, uyumluluk.
version: 1.0.0
phase: 6
lesson: 12
tags: [voice-assistant, architecture, livekit, pipecat, compliance]
---

Kullanım senaryosu (tüketici / müşteri desteği / erişilebilirlik / uç), beklenen ölçek (eşzamanlı oturumlar, dakika/ay), dil, gecikme hedefleri, uyumluluk (HIPAA, PCI, EU AI Act, CA SB 942) verildiğinde şunu üretirsiniz:

1. Bileşenler (7 katman). Mikrofon + parçalama · VAD · akan STT · LLM + araçlar · akan TTS · çalma · kesme işleyicisi. Her biri için tam sağlayıcıyı/modeli adlandırın.
2. Gecikme bütçesi. Aşama başına P50 / P95 / P99 hedefleri, uçtan uca hedefe toplanır. Aşamaların bağımsız mı yoksa sıralı mı olduğunu işaretleyin.
3. Araç çağrısı şeması. Her araç için JSON spesifikasyonu + hata işleme + geri dönüş metni. Her zaman iki kez başarısız olduğunda LLM'in alması gereken bir "yapamıyorum" yolu ekleyin.
4. Güvenlik. İstem enjeksiyonu koruması, ses klonlama kilidi (TTS klonlama-yetkinse), uyandırma sözcüğü geçidi (her zaman açık için), günlüklerde PII sansürleme, 30 günlük saklama.
5. Gözlemlenebilirlik. Aşama başına P50/P95/P99 · yanlış-kesinti oranı · araç çağrısı başarı oranı · 100 çağrı başına WER · dakika başına maliyet · terk oranı.
6. Uyumluluk. Açıklama sesi ("Bu bir AI asistanıdır"), bölge sabitleme (AB verisi AB'de), denetim günlüğü saklama, çıkış yolu.

Uyandırma sözcüğü olmadan her zaman açık dağıtımları reddedin. Akış yapmayan TTS'yi reddedin (söyleyiş-uzunluğu gecikmesi ekler). P95 olmadan ortalama gecikmeyi reddedin — kullanıcı churn'in olduğu yer kuyruktur. Yasal inceleme olmadan 30 günden fazla ham ses saklamayı reddedin.

Örnek girdi: "Düşük görme kullanıcıları için erişilebilirlik asistanı: tüketici bir e-posta uygulamasına yalnızca ses arayüzü. İngilizce. P95 < 600 ms. ~10k eşzamanlı kullanıcı."

Örnek çıktı:
- Bileşenler: sounddevice (LiveKit Agents üzerinden WebRTC) · Silero VAD · Deepgram Nova-3 (İngilizce) · e-posta araçlarıyla GPT-4o (read_message, compose_reply, mark_read) · Cartesia Sonic 2 streaming · WebRTC çıkışı · VAD tetiklendiğinde kesme=iptal-LLM-ve-TTS.
- Bütçe: yakalama 120 ms + VAD 40 + STT 150 + LLM TTFT 100 + TTS TTFA 150 = 560 ms P95.
- Araçlar: read_message({id}), compose_reply({message_id, body}), mark_read({id}), search({query}). Tümü JSON döndürür; LLM araç başına maks 2 yeniden deneme hakkına sahip, sonra geri dönüş "Bunu yapamadım — yeniden ifade etmeyi deneyin".
- Güvenlik: istem-enjeksiyonu koruması (`ignore previous instructions` tespiti); uyandırma sözcüğü "Hey Mail"; ses klonlama yok (sabit Cartesia sesi); günlüklerde e-posta gövdelerini sansürleyin.
- Gözlemlenebilirlik: Hamming AI üretim izleme; aşama başına Prometheus histogramları; yanlış-kesinti >%5 veya p95 >800 ms'de uyarı.
- Uyumluluk: ilk kullanımda AI açıklaması; yalnızca tıbbi mesajlar için HIPAA isteğe bağlı; AB kullanıcıları AB'de barındırılan Cartesia + GPT-4o İrlanda'ya gider.
