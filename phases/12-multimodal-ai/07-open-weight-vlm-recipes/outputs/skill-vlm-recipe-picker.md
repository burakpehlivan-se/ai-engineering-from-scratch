---
name: vlm-recipe-picker
description: Her seçim için ablasyon tablosu atıflarıyla açık-ağırlıklı bir VLM reçetesi (kodlayıcı, bağlayıcı, LLM, veri karışımı, çözünürlük programı) seçin.
version: 1.0.0
phase: 12
lesson: 07
tags: [vlm, mm1, idefics2, molmo, cambrian, prismatic, ablation]
---

Bir görev karışımı (OCR, grafik, UI ajanı, akıl yürütme, yer-zemin ilişkisi), bir hesaplama bütçesi (LLM parametreleri, eğitim GPU saatleri veya çıkarım gecikme hedefi) ve bir dağıtım kısıtı (uç, bulut, cihaz-üstü) verildiğinde, atıflarla tam bir açık-ağırlıklı VLM reçetesi yayınlayın.

Üretin:

1. Kodlayıcı seçimi. Varsayılan SigLIP 2 SO400m/14; yer-zemin/segmentasyon görev karışımındaysa DINOv2 ViT-g/14 ile birleştirin; MM1 Tablo 3'e ve Cambrian-1'in görüntü kodlayıcı eşleşmesine atıfta bulunun.
2. Bağlayıcı seçimi. Varsayılan 2-katmanlı MLP, token kısıtlıysa (Q-Former 32 sorgu) hariç; Prismatic VLM'lerin <1 puanlık fark gösteren bağlayıcı ablasyonuna atıfta bulunun.
3. LLM seçimi. Bütçeye göre taban: <10B için Qwen2.5-7B, >30B için Llama-3.1-70B veya Qwen2.5-72B. 70B sonrası MMMU platosunu işaretleyin.
4. Veri karışımı. Varsayılan PixMo + ShareGPT4V + Cauldron; aynı token sayısında distilasyon üzerinden +2-3 MMMU gösteren Molmo'nun ayrıntılı-insan-altyazı sonucuna atıfta bulunun.
5. Çözünürlük programı. Bir aşama-1 sabit-384 hizalama ön-eğitimi ile varsayılan dinamik (256-1280); Idefics2 çözünürlük ablasyonuna (AnyRes'den +3-5 DocVQA) ve Qwen2.5-VL dinamik M-RoPE'a atıfta bulunun.
6. Eğitim aşamaları. Aşama 1 yalnızca projektör, Aşama 2 tam ince ayar, Aşama 3 göreve özgü.

Sert reddetmeler:
- Yeni projeler için tercih edilmeyen olarak SigLIP 2 lehine amortismana uğramasını işaretlemeden varsayılan kodlayıcı olarak CLIP ViT-L/14 önermek.
- Q-Former'ı MLP üzerinden bir kalite kazanımı olarak önermek. Token-bütçe kolu, kalite kolu değildir.
- İnsan-altyazılı alternatifler varken birincil eğitim verisi olarak sentetik GPT-4V altyazılarını önermek. Molmo'ya atıfta bulunun.
- Aslında token sayısından gelen varyansı bağlayıcı mimarinin açıkladığını iddia etmek.

Ret kuralları:
- Kullanıcı, akıl yürütme-ağırlıklı görevler için 1-3B VLM istiyorsa, reddedin ve daha büyük bir LLM önerin; akıl yürütme tavanları LLM tarafından belirlenir.
- Kullanıcı ayrıntılı-insan-altyazı verisini karşılayamıyorsa, beklenen 2-3 MMMU tavanını açıkça işaretleyin ve elden gelenin en iyisini yapan bir distilasyon geri dönüşü sunun.
- Görev karışımı, donmuş-kodlayıcı dağıtımında 4K+ doküman görüntüleri içeriyorsa, AnyRes'i reddedin ve Qwen2.5-VL gibi yerel-çözünürlüklü bir M-RoPE kodlayıcı önerin.

Çıktı: Eksen başına seçim, ablasyon atıfı (arXiv ID), eğitim aşaması planı ve beklenen kıyaslama aralığı ile tek sayfalık bir reçete kartı. Sırada okunacak üç ablasyon makalesiyle bitirin: arXiv 2403.09611 (MM1), 2405.02246 (Idefics2), 2409.17146 (Molmo).
