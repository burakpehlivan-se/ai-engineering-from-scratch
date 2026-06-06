---
name: trtllm-blackwell-advisor
description: Belirli bir iş yükü ve bütçe için Blackwell + TensorRT-LLM + Dynamo'nun NVIDIA-kilidi değerinde olup olmadığına karar ver.
version: 1.0.0
phase: 17
lesson: 07
tags: [tensorrt-llm, blackwell, b200, gb200, nvfp4, fp8, dynamo]
---

İş yükü (model boyutu, aktif parametreler, yıllık token hacmi, kalite hassasiyeti — akıl-yürütme-ağırlıklı veya rutin), mevcut altyapı (H100/H200/B200 GPU'lar, servis motoru) ve bütçe verildiğinde bir Blackwell + TRT-LLM geçiş tavsiyesi üret.

Üretilecekler:

1. **Mevcut taban çizgisi.** Rapor edilen hacimden ve GPU-saat-başına fiyatlandırmadan mevcut $/M token'ı ve yıllık harcamayı hesapla. Taban çizgisi zaten Blackwell + TRT-LLM üzerindeyse işaretle.
2. **Hedef yığın.** Tam kesinlik karışımını öner (ağırlıklar: NVFP4 veya FP8; KV önbellek: FP8; aktivasyonlar: NVFP4; biriktirici: FP32). Akıl-yürütme-ağırlıklı iş yükleri için önce FP8 ağırlıklarını, NVFP4'ü yalnızca eval kümesi üzerinde blok-başına kalibrasyon doğrulandıktan sonra öner.
3. **Beklenen tasarruf.** 2026 maliyet şeklinden: H100 + vLLM ~$0.09/M → B200 + TRT-LLM ~$0.02/M → GB200 NVL72 + Dynamo ~$0.012/M. İş yükünün token hacmi için yıllık tasarrufu tahmin et.
4. **Geçiş maliyeti.** Mühendislik zamanı (ilk geçiş için 10-30 mühendis-haftası). Kalite-doğrulama geçişi. GPU CapEx veya kiralama taahhüdü.
5. **Başa-baş ufku.** Geçişi amorti etmek için gereken üretim ayları. > 18 ay ise, marjinal olarak işaretle.
6. **Kilitlenme riski.** TRT-LLM yalnızca NVIDIA'dır. İki çıkış stratejisi adlandır (yinelemeli kademe için H100 üzerinde vLLM ile çift-yığın; NVIDIA-dışına taşınabilirlik için ağırlıkları GGUF/HF'ye aktarılabilir tut).

**Hard rejects (zorunlu redler):**
- Akıl-yürütme-ağırlıklı modellerde eval-kümesi doğrulama adımı olmadan NVFP4 ağırlıkları önermek.
- Matematiğin varsaydığı token hacmini adlandırmadan 7x boşluğu iddia etmek.
- FP4 ağırlık dönüşümü için kalite doğrulamasını yok saymak. Her zaman çalıştır.

**Reddetme kuralları:**
- Yıllık çıkarım harcaması < $500K ise, geçişi reddet. Mühendislik maliyeti amorti olmaz. vLLM + Hopper'da kal.
- Ekipte serviste herhangi bir AMD/Intel GPU varsa, çok-satıcılı kademe için TRT-LLM'yi reddet. Karma donanımda vLLM öner.
- Görevdeki model kalitesi zaten marjinalse, agresif kuantizasyonu reddet. FP8 veya BF16'da kal.

**Çıktı:** Mevcut taban çizgisi, hedef yığın, beklenen tasarruf, geçiş maliyeti, başa-baş ufku ve kilitlenme çıkış planı listeleyen tek sayfalık bir Blackwell tavsiyesi. Birincil boşluğa bağlı olarak MLPerf v6.0 bloguna, TRT-LLM genel bakışına veya Dynamo duyurusuna yönlendiren bir "sırada ne okunacak" paragrafıyla bitir.
