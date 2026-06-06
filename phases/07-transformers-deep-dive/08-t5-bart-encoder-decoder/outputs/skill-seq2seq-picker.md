---
name: seq2seq-picker
description: Yeni bir diziden-diziye (sequence-to-sequence) görev için kodlayıcı-kodçözücü veya yalnızca kodçözücü arasında seç
version: 1.0.0
phase: 7
lesson: 8
tags: [transformers, t5, bart, diziden-diziye]
---

Bir diziden-diziye görevi (çeviri / özetleme / konuşmadan-metne / yapılandırılmış çıkarma / yeniden yazma), girdi ve çıktı uzunluk dağılımları ve kalite ve gecikme öncelikleri verildiğinde, aşağıdakileri üret:

1. Mimari. Şunlardan biri: kodlayıcı-kodçözücü (T5 / BART / Whisper tarzı), yalnızca kodçözücü talimat-ince-ayarlı, yalnızca kodlayıcı + istem şablonu. Tek cümlelik gerekçe.
2. Ön eğitim amacı. Açıklı bozma (T5), gürültü giderme (BART), sonraki-token (yalnızca kodçözücü) veya "ön eğitimi atla, mevcut kontrol noktasını ince-ayar yap." Kontrol noktasını adlandır.
3. Girdi biçimlendirme. Görev öneki dizesi (T5 tarzı) veya sistem istemi (yalnızca kodçözücü) veya ham tokenler (BART). BOS/EOS işlemeyi dahil et.
4. Kod çözme stratejisi. Işın arama genişliği ve uzunluk cezası (çeviri/özet) veya çekirdek/min-p (sohbet benzeri görevler). Görev için hangisi olduğunu belirt.
5. Değerlendirme. Göreve uygun metrik: BLEU / ROUGE / WER / F1 / tam eşleşme. Test bölütü boyutunu dahil et.

Üretken çıktılar için yalnızca kodlayıcı önerme. Girdi zaten bir konuşma olduğunda kodlayıcı-kodçözücü önerme — yalnızca kodçözücü konuşma belleğine doğal olarak uyar. Whisper'ı temel alınacak değer olarak anmadan konuşmadan-metne için yalnızca kodçözücü seçimini işaretle.
