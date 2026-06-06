---
name: alm-picker
description: Bir ses-anlama görevi için ses-dil modeli (audio-language model), kıyaslama alt kümesi, çıktı modu (metin vs konuşma) ve koruma setleri seçer.
version: 1.0.0
phase: 6
lesson: 10
tags: [alm, lalm, qwen-omni, audio-flamingo, gemini-audio, mmau]
---

Görev (konuşma / ses / müzik / çoklu-ses / uzun-ses, çıktı modu, gecikme, lisans) verildiğinde şunu üretirsiniz:

1. Model. Qwen2.5-Omni-7B · Qwen3-Omni · SALMONN · Audio Flamingo 3 · AF-Next · LTU · GAMA · Gemini 2.5 Pro (API) · GPT-4o Audio (API). Tek cümlelik neden.
2. Doğrulamak için kıyaslama alt kümesi. MMAU-Pro konuşma / ses / müzik / çoklu-ses · LongAudioBench · AudioCaps · ClothoAQA. Kullanıcı göreviyle eşleşen ekseni seçin.
3. Çıktı modu. Yalnızca metin · metin + konuşma (Qwen-Omni, GPT-4o Audio). Gerekirse ek bir konuşma kod çözücüyü bütçeleyin.
4. Koruma setleri. Modelinizin çoklu-ses puanı <%30 (neredeyse rastgele) olduğunda çoklu-ses karşılaştırma gerektiren istemleri reddedin. >10 dakikalık girdiler için LALM'den önce diarizasyon uygulayın.
5. Yükseltme. Bu görev özelleşmiş bir modele — transkripsiyon için Whisper, sınıflandırma için BEATs, diarizasyon için pyannote — ne zaman düşmelidir. LALM her birinin en iyisi değildir.

Modelinizin MMAU-Pro çoklu-ses alt kümesinde >%40 puan aldığını doğrulamadan çoklu-ses karşılaştırma görevlerini yayınlamayı reddedin. Yukarı akış diarizasyonu olmadan uzun-sesi (>10 dk) reddedin. Satıcının bildirdiği sayıları bağımsız yeniden doğrulama olmadan kullanan herhangi bir dağıtımı işaretleyin.

Örnek girdi: "Uyumluluk denetimi: 10 dakikalık banka araması kayıtlarını transkribe et + acente zorunlu açıklamayı okudu mu tespit et."

Örnek çıktı:
- Model: Transkripsiyon için Whisper-large-v3-turbo + açıklama-kontrol QA'sı için transkript üzerinden Gemini 2.5 Pro (API ile). Ham ses üzerinde doğrudan LALM cazip ama 10 dk sonrası uzun-ses LALM doğruluğu düşer.
- Kıyaslama alt kümesi: MMAU-Pro konuşma alt kümesi (Gemini 2.5 Pro = %73,4) — konuşma-akıl-yürütme eksenini kapsar. Ayrıca kendi 50 aramalık altın kümenizde spot kontrol.
- Çıktı modu: yalnızca metin. Denetim raporu için konuşma çıktısı gerekmiyor.
- Koruma setleri: önce pyannote 3.1 ile diarizasyon yapın; konuşmacı başına segmentleri ayrı ayrı gönderin; arama başına güven puanını günlüğe kaydedin.
- Yükseltme: bir arama açıklama kontrolünü geçemezse, otonom işaret yerine insan incelemesine yönlendirin.
