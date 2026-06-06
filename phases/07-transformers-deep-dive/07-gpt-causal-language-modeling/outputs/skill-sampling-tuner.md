---
name: sampling-tuner
description: Belirli bir üretim görevi için kod çözme (decoding) stratejisi (açgözlü / sıcaklık / top-k / top-p / min-p / spekülatif) seç
version: 1.0.0
phase: 7
lesson: 7
tags: [gpt, örnekleme, kod-çözme, çıkarım]
---

Bir üretim görevi (kod, yaratıcı yazarlık, akıl yürütme, diyalog, yapılandırılmış çıktı) ve gecikme/kalite hedefi verildiğinde, aşağıdakileri üret:

1. Örnekleme yöntemi. Şunlardan biri: açgözlü (greedy), yalnızca sıcaklık, top-k, top-p, min-p, ışın-k (beam-k), spekülatif. Tek cümlelik gerekçe.
2. Parametre değerleri. Sıcaklık, top-k, top-p, min-p, tekrar cezası — görev türüne bağlı somut sayılar. (örneğin kod için sıcaklık 0.2 + top-p 1.0; sohbet için min-p 0.1 + sıcaklık 0.7.)
3. Durdurma koşulları. `max_new_tokens`, durdurma token listesi, kalıp tabanlı durdurma (örneğin kapanış `</tool_call>`).
4. Deterministiklik anahtarı. Tekrarlanabilirlik için sabit tohum; kullanım durumunun (değerlendirme, hukuki) bunu gerektirip gerektirmediğini işaretle.
5. Kalite kontrolü. Görev hedefine karşı tek satırlık test (derleme/birim testi geçme, gerçeklik, format geçerliliği vb.).

Yapılandırılmış çıktı veya kod tamamlama için sıcaklık > 1.0 önerme — halüsinasyon riski keskin şekilde artar. Açık uçlu diyalog için saf açgözlü önerme — model döngüye girecek. Model şablonlar/araçlar üretebiliyorsa belirtilmiş durdurma token listesi olmadan örnekleme yapılandırması gönderme.
