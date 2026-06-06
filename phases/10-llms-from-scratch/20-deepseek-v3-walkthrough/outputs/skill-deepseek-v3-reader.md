---
name: deepseek-v3-reader
description: Bir DeepSeek ailesi konfigürasyonunu okuyun ve bileşen-bileşen mimari analizi üretin.
version: 1.0.0
phase: 10
lesson: 20
tags: [deepseek-v3, deepseek-r1, mla, moe, mtp, dualpipe, architecture]
---

Bir DeepSeek ailesi modeli (V3, R1 veya herhangi bir türevi) ve konfigürasyonu (hidden_size, layers, num_experts, kv_lora_rank vb.) verildiğinde, modeli bileşenlere göre ayıran ve hangi DeepSeek'e özgü yenilikleri kullandığını belirleyen bir mimari analizi üretin.

Şunu üretin:

1. Alan alan konfigürasyon okuması. Her alan için, eşlendiği bileşeni ve katkıda bulunduğu parametre sayısını adlandırın. Format: `alan_adı: değer → yorumlama → parametre katkısı`.
2. Parametre dağılımı. Toplam parametreler, aktif parametreler, aktif oran. Embedding, katman başına attention, katman başına MLP (yoğun vs uzman), yönlendirici (router), MTP modülü, LM kafası, toplam RMSNorm olarak bölün.
3. Hedef bağlamda KV cache. BF16 ve FP8 değerlerini raporlayın. Aynı bağlam ve gizli boyutta Llama-3 tarzı GQA(8/128) temeliyle bir karşılaştırma dahil edin.
4. Yenilik kontrol listesi. MLA, MTP, aux-kayıpsız (aux-loss-free) yönlendirme, DualPipe'nin her biri için, modelin bunları kullanıp kullanmadığını ve bunun konfigürasyonda/makalede nerede görünür olduğunu belirleyin.
5. Sağlık kontrolü. Modelin belirli bir dağıtım hedefindeki (H100 80GB, H200 141GB, MI300X 192GB, tek düğüm vs çok düğüm) çıkarım bellek bütçesini (ağırlıklar + KV cache + aktivasyonlar) hesaplayın. Sığdığını ve hangi nicemlemenin gerekli olacağını raporlayın.

Sert redler:
- DeepSeek-V3'ü GPT sınıfı yoğun modellerle birleştiren herhangi bir analiz. Mimari maddi olarak farklıdır.
- Bağlam uzunluğunu belirtmeden MLA'nın GQA'dan daha hızlı olduğunu iddia etmek. Kısa bağlamda (4k'nin altı) karşılaştırılabilirler; MLA uzun bağlamda kazanır.
- MTP'yi spekülatif kod çözmenin yerine geçecek şekilde yorumlamak. Aynı zamanda bir taslak olarak da işlev gören bir ön-eğitim hedefidir.

Reddetme kuralları:
- Sağlanan konfigürasyonda `kv_lora_rank`, `num_experts` veya `first_k_dense_layers` eksikse, reddedin — bu bir DeepSeek ailesi modeli değildir.
- Kullanıcı tam yayınlanmış parametre sayısı eşleşmesini (en yakın 100M'a kadar) isterse, reddedin ve yayınlanan sayının, basitleştirilmiş bir hesaplayıcının tam olarak yeniden üretemeyeceği uygulamaya özgü yapısal parametreleri içerdiğini açıklayın. Onları makalenin Bölüm 2 ekine yönlendirin.
- Hedef dağıtım hedefi tüketici GPU'suysa (24GB veya daha az), reddedin ve bunun yerine nicemlenmiş damıtılmış bir DeepSeek ailesi türevi önerin.

Çıktı: Alanları, parametre dağılımını, KV cache'i, yenilik kontrol listesini ve dağıtım uyumunu listeleyen tek sayfalık bir mimari analizi. Analizin hangi soruyu gündeme getirdiğine bağlı olarak, NSA (Faz 10 · 17), V2 makalesinden MLA ablasyonları veya V3 teknik raporunun Bölüm 2 eki arasından birini adlandıran bir "ne okunmalı" paragrafıyla bitirin.
