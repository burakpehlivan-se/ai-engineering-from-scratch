---
name: embedding-picker
description: Belirli bir derlem ve dağıtım için embedding modeli, boyut ve erişim modu seçer.
version: 1.0.0
phase: 5
lesson: 22
tags: [nlp, embeddings, retrieval]
---

Bir derlem (boyut, diller, alan, ortalama uzunluk), dağıtım hedefi (bulut / uç / şirket içi), gecikme bütçesi ve depolama bütçesi verildiğinde şunu üretirsiniz:

1. Model. Adlandırılmış kontrol noktası veya API. Tek cümlelik neden.
2. Boyut. Tam / Matryoshka-kırpılmış / int8 nicellenmiş. Depolama bütçesine bağlı neden.
3. Mod. Yoğun / seyrek / çok-vektörlü / hibrit. Neden.
4. Model kartı gerektiriyorsa sorgu öneki / şablonu.
5. Değerlendirme planı. Alana uygun MTEB görevleri + nDCG@10 ile held-out alan değerlendirmesi.

Alan doğrulaması olmadan Matryoshka'yı <64 boyuta kırpan önerileri reddedin. 10k pasajın altındaki derlemler için ColBERTv2'yi reddedin (ek yük haklı çıkmaz). 512 token pencereli modellere yönlendirilen uzun-belge derlemlerini (>8k token) işaretleyin.
