---
name: text-encoder-picker
description: Belirli bir kısıt kümesi için metin kodlayıcı mimarisi seçer.
phase: 5
lesson: 08
---

Kısıtlar (görev, veri hacmi, gecikme bütçesi, dağıtım hedefi, hesaplama bütçesi) verildiğinde şunu üretirsiniz:

1. Kodlayıcı mimarisi: TextCNN, BiLSTM, BiLSTM-CRF, transformer ince ayar veya "önceden eğitilmiş transformer'ı donmuş kodlayıcı + küçük başlık (head) olarak kullanma".
2. Embedding girişi: rastgele başlatma, GloVe veya fastText dondurulmuş, ya da bağlamsal transformer embedding'leri.
3. 5 satırda eğitim reçetesi: optimizer (optimize edici), öğrenme oranı, toplu iş boyutu, epok sayısı, düzenlileştirme (regularization).
4. Bir izleme sinyali. RNN/CNN modelleri: uzun bağımlılık başarısızlıkları için dizi başına-dizi uzunluğu doğruluğunu kontrol edin. Transformer ince ayarları: LR çok yüksekse ince ayar çöküşünü (fine-tuning collapse) izleyin; ilk 100 adımda eğitim kaybını kontrol edin.

Önce bir TextCNN / BiLSTM baseline'ının plato yapmadığını göstermeden, kullanıcının ~500'ün altında etiketli örneği varsa transformer ince ayarı önermeyi reddedin. Uç (edge) dağıtımı (telefon, mikrodenetleyici, tarayıcı) mimari kararları her şeyden önce gerektiriyor olarak işaretleyin.
