---
name: load-test-plan
description: Gerçekçi bir LLM yük testi tasarla — aracı (LLMPerf, k6, GenAI-Perf, guidellm) seç, dört kalıp (sabit, rampa, ani, ıslatma) kur ve CI'da kapı koy.
version: 1.0.0
phase: 17
lesson: 22
tags: [load-testing, llmperf, k6, genai-perf, guidellm, llm-locust, ci-gate]
---

İş yükü (uç nokta, TTFT/TPOT/hata için SLA), hedef ölçek (eşzamanlılık, RPS) ve CI duruşu (PR kapısı veya yalnızca sürüm) verildiğinde bir yük testi planı üret.

Üretilecekler:

1. **Araç.** Taban çizgisi çalıştırmaları için LLMPerf; CI kapıları için k6 + streaming uzantısı; NVIDIA referans çalıştırmaları için GenAI-Perf; büyük sentetik için guidellm. Yalnızca zaten Locust'taysan LLM-Locust.
2. **İstem dağılımı.** Gerçek trafikten (varsa) veya yayınlanmış dağılımdan (ShareGPT / HumanEval) ortalama + standart sapma girdi token'ı. Tek-istemli-döngüyü yasakla.
3. **Dört kalıp.** Sabit, rampa, ani, ıslatma. Her biri için: hedef RPS, süre, beklenen başarısızlık modu.
4. **CI kapısı.** Belirli eşikler: TTFT P95 < X, 5xx < %5, TPOT < Y. PR başına çalışma süresi: 3-5 dk.
5. **Metrik hizalaması.** Raporlama aracının GenAI-Perf tarzı (ITL TTFT'yi dışlar) mı yoksa LLMPerf tarzı (ITL TTFT'yi içerir) mı olduğunu not et. Birini seç ve tutarlı kal.
6. **Çıktı.** Repo'ya eklenmiş bir betik dosyası (k6 JS, LLMPerf CLI).

**Hard rejects (zorunlu redler):**
- Tek biçimli istemlerle yük testi. Reddet — sayılar yalan söyler.
- Akış (streaming) desteği olmadan yük testi. Reddet — LLM uç noktaları varsayılan olarak akış yapar.
- Metrik-tanım farklarını kabul etmeden araçlar arasında sayıları karşılaştırmak. Reddet.

**Reddetme kuralları:**
- Ekip Locust stok'unu LLM-Locust uzantısı olmadan çalıştırmayı düşünüyorsa, reddet — GIL tuzağı.
- CI kapı bütçesi PR başına <60 saniye ise, tam ıslatmayı reddet — hızlı bir sabit-durum ve ayrı bir gecelik ıslatma öner.
- İstem dağılımı verisi yoksa, belgelenmiş yayınlanmış bir dağılım (ShareGPT) zorunlu kıl ve varsayımı not et.

**Çıktı:** Araç, istem dağılımı, hedefleri olan dört kalıp, CI kapı eşikleri, metrik hizalaması içeren tek sayfalık bir plan. Tek CI çıktısıyla bitir: PR yalnızca tüm eşikler karşılandığında yeşil, 3-çalıştırma kararlılığı.
