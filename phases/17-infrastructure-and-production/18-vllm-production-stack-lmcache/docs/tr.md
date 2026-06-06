# vLLM Üretim Yığını — LMCache ile KV Offloading

> vLLM'nin üretim-yığını (production-stack) referans Kubernetes dağıtımıdır — yönlendirici, motorlar ve gözlemlenebilirlik birlikte kablolanmıştır. LMCache, KV cache'i GPU belleğinden çıkaran ve sorgular ile motorlar arasında yeniden kullanan (CPU DRAM, sonra disk/Ceph) KV-offloading (önbellek boşaltma) katmanıdır. vLLM 0.11.0 KV Offloading Connector (Ocak 2026), bunu Connector API (v0.9.0+) üzerinden asenkron ve takılabilir hale getirir. Offload gecikmesi kullanıcıya dönük değildir. LMCache, paylaşılan önekler olmadan bile değerlidir — bir GPU KV slotları tükenirse, öneçıkarılan (preempted) istekler yeniden prefill hesaplamak yerine CPU'dan geri yüklenebilir. 4 a3-highgpu-4g'ye yayılmış 16x H100 (80GB HBM) üzerinde yayınlanmış kıyaslamalar: KV cache HBM'i aştığında, hem yerel CPU offload hem de LMCache throughput'u önemli ölçüde iyileştirir; düşük KV ayakizinde, tüm yapılandırmalar küçük bir ek yükle (overhead) taban çizgisiyle eşleşir.

**Tür:** Öğren
**Diller:** Python (stdlib, basit KV-dökülme simülatörü)
**Önkoşullar:** Phase 17 · 04 (vLLM Servis İç Yapısı), Phase 17 · 06 (SGLang/RadixAttention)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- vLLM üretim-yığını katmanlarını şematize edin: yönlendirici, motorlar, KV offload, gözlemlenebilirlik.
- KV Offloading Connector API'sini (v0.9.0+) ve 0.11.0 asenkron yolunun offload gecikmesini nasıl gizlediğini açıklayın.
- LMCache CPU-DRAM'ın ne zaman yardımcı olduğunu (KV > HBM) vs ek yük eklediğini (KV HBM'e sığacak kadar küçük) nicelleştirin.
- Dağıtım kısıtlarına göre yerel vLLM CPU offload ve LMCache connector arasında seçim yapın.

## Problem

vLLM servisiniz, eşzamanlılık (concurrency) her yükseldiğinde öneçıkarma (preemption) olaylarıyla %100 HBM gösteriyor. İstekler çıkarılıyor, kuyruğa alınıyor ve aynı 2K token prompt'unu bir dakika içinde dört kez yeniden prefill ediyorsunuz. GPU hesaplama gereksiz prefill'lere harcanıyor; goodput (üretken throughput) ham throughput'un çok altında.

Daha fazla GPU eklemek doğrusal maliyetlidir. Daha fazla HBM mümkün değil. Ama CPU DRAM ucuz — bir soket HBM'den çok daha kötü ama "geçici olarak sıcak" KV cache için yeterli olan 512 GB+'a sahip.

LMCache, KV cache'i CPU DRAM'e çıkararak öneçıkarılan isteklerin hızlı kurtarılmasını sağlar ve tekrarlanan önekler motorlar arasında her motor yeniden prefill etmeden paylaşılır.

## Kavram

### vLLM üretim-yığını

`github.com/vllm-project/production-stack` referans Kubernetes dağıtımıdır:

- **Yönlendirici** — önbellek-farkında (Phase 17 · 11). KV olaylarını tüketir.
- **Motorlar** — vLLM çalışanları. GPU başına veya TP/PP (Tensor/Pipeline Paralelliği) grubu başına bir tane.
- **KV cache offload** — LMCache dağıtımı veya yerel connector.
- **Gözlemlenebilirlik** — Prometheus kazıma (scrape), Grafana panoları, OTel (OpenTelemetry) izleri.
- **Kontrol düzlemi** — servis keşfi, yapılandırma, kademeli güncellemeler.

Helm chart + operatör olarak gönderilir.

### KV Offloading Connector API (v0.9.0+)

vLLM 0.9.0, takılabilir KV cache arka uçları için bir Connector API sundu. Motorunuz blokları connector'a boşaltır; connector onları depolar (RAM, disk, nesne depolama, LMCache). İstek bir blok gerektirdiğinde, connector onu geri yükler.

vLLM 0.11.0 (Ocak 2026) asenkron bir offload yolu ekler — offload arka planda gerçekleşebilir, böylece motor yaygın durumda bloklanmaz. Uçtan uca gecikme ve throughput yine de iş yükü şekline, KV cache isabet oranına ve sistem baskısına bağlıdır; vLLM'in kendi notları, özel-çekirdek (custom-kernel) offload'un düşük isabet oranlarında throughput'u düşürebileceğini ve asenkron zamanlamanın spekülatif kod çözme (speculative decoding) ile bilinen etkileşim sorunlarına sahip olduğunu belirtir.

### Yerel CPU offload vs LMCache

**Yerel vLLM CPU offload**: motor-yerel. KV bloklarını ana bilgisayar RAM'inde depolar. Uygulaması hızlı, ağ atlaması yok. Motorlar arası geçiş yapmaz.

**LMCache connector**: küme-ölçekli. Blokları paylaşılan bir LMCache sunucusunda (CPU DRAM + Ceph/S3 katmanı) depolar. Bloklara herhangi bir motor erişebilir. 16x H100 kıyaslamaları yayınlandı.

Tek bir motor HBM baskısı altındayken yerel'i seçin. Birden çok motor önekleri paylaşırken (ortak sistem prompt'lu RAG, paylaşılan şablonlu çok-kiracılı) LMCache'ı seçin.

### Kıyaslama davranışı

4 a3-highgpu-4g'ye yayılmış 16x H100 (80 GB HBM) testi:

- Düşük KV ayakizi (kısa prompt'lar, düşük eşzamanlılık): tüm yapılandırmalar taban çizgisiyle eşleşir, LMCache ~%3-5 ek yük ekler.
- Orta ayakizi: LMCache, motorlar arası önek yeniden kullanımında yardımcı olmaya başlar.
- KV HBM'i aştığında: yerel CPU offload ve LMCache her ikisi de throughput'u önemli ölçüde iyileştirir; LMCache motorlar-arası paylaşım nedeniyle daha büyük kazanç sağlar.

### LMCache ne zaman belirleyicidir

- Çok-kiracılı servis, sistem prompt'ları kiracılar arasında paylaşılır.
- RAG, doküman parçaları sorgular arasında tekrarlanır.
- Aynı temel model üzerinde ince-ayarlı varyantlar (LoRA — Düşük-Rank Uyarlama), temel model KV yeniden kullanımı gereksiz işi keser.
- Öneçıkarma-ağırlıklı iş yükleri: yeniden prefill'den daha ucuza CPU'dan geri yükleme.

### Ne zaman etkinleştirilmemeli

- Küçük HBM baskısı — fayda olmadan ek yük ödersiniz.
- Kısa bağlamlar (<1K token) — aktarım süresi > yeniden prefill.
- Tek-kiracılı tek-prompt iş yükü — yakalanacak yeniden kullanım yok.

### Ayrıştırılmış servis ile bütünleşme

Phase 17 · 17 ayrıştırılmış servis + LMCache birleşir: prefill havuzundan decode havuzuna KV aktarımları, kullanılmazlarsa LMCache'e iner; sonraki sorgular LMCache'ten çeker. Phase 17 · 11 önbellek-farkında yönlendirici, yerel VEYA LMCache-paylaşılan önbelleği eşleşen motora yönlendirebilir.

### Hatırlamanız gereken sayılar

- vLLM 0.9.0: Connector API gönderildi.
- vLLM 0.11.0 (Ocak 2026): asenkron offload yolu; uçtan uca gecikme etkisi iş yüküne, KV isabet oranına ve sistem baskısına bağlıdır (mutlak garanti değil).
- 16x H100 kıyaslama: LMCache, KV ayakizi HBM'i aştığında yardımcı olur.
- Küçük HBM baskısı: fayda olmadan %3-5 ek yük.

## Kullanım

`code/main.py`, LMCache ile ve olmadan öneçıkarma-ağırlıklı bir iş yükünü simüle eder. Önlenen yeniden prefill'leri, throughput kazancını ve başabaş HBM kullanımını raporlar.

## Yaygınlaştırma

Bu ders `outputs/skill-vllm-stack-decider.md` üretir. İş yükü şekli ve vLLM dağıtımı verildiğinde, yerel vs LMCache vs hiçbiri kararını verir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. LMCache hangi HBM kullanımında ödeme yapmaya başlar?
2. Bir kiracı 6K token'lık sistem prompt'unu saatte 200 sorguda paylaşıyor. Kiracı başına beklenen LMCache tasarrufunu hesaplayın.
3. LMCache sunucusu tek bir arıza noktasıdır. HA stratejisini tasarlayın (kopyalar, yere düşme).
4. LMCache, dönen diske (spinning disk) sahip Ceph'e yazar. 4K token KV + 70B FP8 (500 MB) için, okuma süresi vs yeniden prefill nedir?
5. vLLM 0.11.0 asenkron yolunun "bedava" olup olmadığını tartışın — ek yük nereye gizlenir?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| Üretim-yığını | "referans dağıtım" | vLLM'nin Kubernetes Helm chart + operatörü |
| Connector API | "KV arka uç arayüzü" | vLLM 0.9.0+ takılabilir KV deposu arayüzü |
| Yerel CPU offload | "motor-yerel dökülme" | KV'yi aynı motorun ana bilgisayar RAM'inde depola |
| LMCache | "küme KV cache" | CPU DRAM + disk üzerinde motorlar-arası KV önbelleği |
| 0.11.0 asenkron | "bloklamayan offload" | Offload, motor akışının arkasına gizlenmiş |
| Öneçıkarma | "yer açmak için çıkar" | HBM dolu olduğunda KV cache karıştırma |
| Önek yeniden kullanımı | "aynı sistem prompt'u" | Birden çok sorgu başlangıcı paylaşır; önbellek isabeti |
| Ceph katmanı | "disk katmanı" | Önbellek hiyerarşisinde DRAM'in altında dayanıklı depolama |

## Ek Okuma

- [vLLM Blog — KV Offloading Connector (Ocak 2026)](https://blog.vllm.ai/2026/01/08/kv-offloading-connector.html)
- [vLLM Üretim Yığını GitHub](https://github.com/vllm-project/production-stack) — Helm chart + operatör.
- [LMCache for Enterprise-Scale LLM Inference (arXiv:2510.09665)](https://arxiv.org/html/2510.09665v2)
- [LMCache GitHub](https://github.com/LMCache/LMCache) — Connector uygulaması.
- [vLLM 0.11.0 sürüm notları](https://github.com/vllm-project/vllm/releases) — asenkron yol ayrıntıları.
