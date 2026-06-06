---
name: asr-picker
description: Belirli bir dağıtım hedefi için ASR (Otomatik Konuşma Tanıma) modeli, kod çözme stratejisi, parçalama ve LM füzyonu seçer.
version: 1.0.0
phase: 6
lesson: 04
tags: [audio, asr, speech-recognition]
---

Bir dağıtım hedefi (dil listesi, alan, gecikme bütçesi, donanım, çevrimdışı / streaming, klip süresi) verildiğinde şunu üretirsiniz:

1. Model. Whisper-large-v3-turbo / Parakeet-TDT / Canary-Flash / wav2vec 2.0 / Moonshine. Tek cümlede neden.
2. Kod çözme. Açgözlü / ışın genişliği / sıcaklık geri dönüşü / LM füzyon ağırlığı. Nedeni kalite bütçesine bağlı.
3. Parçalama ve VAD. Parça uzunluğu, adım, Silero-VAD veya Whisper'ın kendi VAD'i ile geçitlenip geçitlenmeyeceği.
4. Dil politikası. Dili zorla veya otomatik LID; çapraz dil çerçeveleri nasıl işlenecek.
5. Değerlendirme planı. Alan test kümesinde WER (Kelime Hata Oranı), konuşmacı başına kapsam, sessizlik kliplerinde halüsinasyon oranı.

VAD geçidi olmadan herhangi bir uzun formlu Whisper dağıtımını reddedin (sessizlikte halüsinasyona eğilimli). Metin normalleştirmesi olmadan WER raporlamayı reddedin (küçük harf, noktalama soyma). LM olmadan >16 ışın genişliğini işaretleyin; boşluklar üzerindeki ham ışınlar yardımcı olmaz.
