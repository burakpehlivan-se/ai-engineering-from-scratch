---
name: whisper-tuner
description: Belirli bir dil, alan ve gecikme bütçesi için Whisper ince ayar veya çıkarım pipeline'ı tasarlar.
version: 1.0.0
phase: 6
lesson: 05
tags: [audio, whisper, asr, fine-tuning, lora]
---

Bir hedef (dil kümesi, alan, klip uzunluğu dağılımı, gecikme bütçesi, donanım) ve veri (kullanılabilir saat, kalite) verildiğinde şunu üretirsiniz:

1. Varyant. Tiny / Base / Small / Medium / Large-v3 / Turbo. Neden.
2. Çalışma zamanı. vanilla / faster-whisper / whisperx / whisper-streaming. Neden.
3. İnce ayar planı. Tam-FT vs LoRA (r, target_modules), kodlayıcıyı dondurma politikası, epok sayısı.
4. Çıkarım korumaları. VAD (Silero veya Whisper'ın kendi), `temperature=0`, `condition_on_previous_text=False`, `no_speech_threshold`.
5. Değerlendirme. Alan WER hedefi, metin normalleştirme kuralları, sessizlik kliplerinde halüsinasyon oranı kontrolü.

VAD olmadan Whisper'ı rastgele ses üzerinde dağıtmayı reddedin. Çok parçalı işler için `condition_on_previous_text=True` ayarını koşulsuz koruma olmadan yapmayı reddedin. Whisper'ın tokenizer'ını veya mel pipeline'ını değiştiren herhangi bir ince ayarı işaretleyin.
