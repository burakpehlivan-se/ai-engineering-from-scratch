---
name: vllm-scheduler-reader
description: Scheduler-düzeyi ayar düğmelerini okuyarak ve PagedAttention, sürekli toplu iş ve parçalı prefill'den hangisinin darboğaz olduğunu belirleyerek bir vLLM servis yapılandırmasını teşhis et.
version: 1.0.0
phase: 17
lesson: 04
tags: [vllm, paged-attention, continuous-batching, chunked-prefill, serving, scheduler]
---

Bir vLLM servis yapılandırması (model, dtype, donanım, `--gpu-memory-utilization`, `--max-num-batched-tokens`, `--enable-chunked-prefill`, `--speculative-model` veya `--speculative-config`, azami eşzamanlılık ve gözlemlenen bir metrik kümesi: TTFT ortalama/P99, ITL ortalama/P99, verim tok/s) verildiğinde scheduler-düzeyinde bir teşhis üret.

Üretilecekler:

1. **Yapılandırma okuma.** Her bayrak için, kontrol ettiği scheduler davranışını ve 2026 varsayılanını adlandır. Varsayılan-dışı bir değere ayarlanmış herhangi bir bayrağı işaretle ve nedenini belirt.
2. **Darboğaz tanımlama.** Darboğazı şunlardan biri olarak sınıflandır: PagedAttention yetersiz-tahsisli (KV blok kıtlığı), sürekli toplu iş durması (WAITING kuyruğu büyümesi), parçalı prefill yanlış-boyutlandırılmış (TTFT kuyruk sivri ucu), decode hesap-bağlı (ITL tabanı) veya HBM-bağlı (toplu iş sığmıyor). Rapor edilen metriklerle gerekçelendir.
3. **Ayar düğmesi önerileri.** Belirli, sıralı eylemler — hangi bayrağı değiştireceğin, hangi değeri deneyeceğin ve hangi metriği izleyeceğin. Scheduler-düzeyi ayarı tüketmeden "daha fazla GPU dene" önerme.
4. **Uyumluluk kontrolü.** Özellikle vLLM v0.18.0 için: `--enable-chunked-prefill` + `--speculative-model` birleşimini sert bir uyumsuzluk olarak işaretle. İkisi de isteniyorsa V1'de belgelenmiş istisna olarak N-gram GPU spekülatif kod çözmeyi öner.
5. **Sırada ne okunacak.** Teşhisin yüzeye çıkardığına bağlı olarak vLLM v0.18.0 sürüm notlarından birine, PagedAttention makalesine veya Aleksa Gordic'in V1 scheduler yürüyüşüne yönlendir.

**Hard rejects (zorunlu redler):**
- Dört temel metrik (TTFT, ITL, verim, eşzamanlılık) olmadan teşhis koymak. Reddet ve metrik kümesini iste.
- Spekülatif-kod çözme yapılandırmasını kontrol etmeden `--enable-chunked-prefill` önermek.
- `DCGM_FI_DEV_GPU_UTIL`'i bir ölçekleme sinyali olarak değerlendirmek. vLLM KV'yi önceden tahsis eder; görev-döngüsü sayıları yanıltıcıdır.

**Reddetme kuralları:**
- Rapor edilen verim bir H100 üzerinde 100 tok/s'nin altındaysa, darboğaz büyük olasılıkla vLLM değil — istemci-tarafında tokenleştirici, Python GIL veya istek-düzeyi serileştirmeyi kontrol et.
- `--gpu-memory-utilization` 0.7'nin altına ayarlanmışsa, daha fazla ayar yapmayı reddet — operatör HBM'i masada bırakmayı seçti ve düzeltme scheduler bayraklarını değiştirmeden önce tavanı yükseltmektir.
- Operatör draft-model spekülasyonu üzerinde spekülatif-kod çözme + parçalı prefill tarifi istiyorsa, reddet ve v0.18.0 uyumsuzluğunu adlandır. Bunun yerine Phase 17 · 05'te EAGLE-3'e yönlendir.

**Çıktı:** Bayraklar, darboğaz, sıralı öneriler, uyumluluk notları ve sıradaki-okuma yönlendirmesi listeleyen tek sayfalık bir scheduler teşhisi. Tanımlanan darboğaza bağlı olarak P99 ITL, blok tahsis oranı veya WAITING kuyruğu derinliğinden birini adlandıran bir "sırada ne ölçülecek" paragrafıyla bitir.
