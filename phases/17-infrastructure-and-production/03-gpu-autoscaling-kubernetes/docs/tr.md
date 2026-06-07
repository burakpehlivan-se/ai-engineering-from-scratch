# Kubernetes Üzerinde GPU Otomatik Ölçekleme — Karpenter, KAI Scheduler, Gang Scheduling

> Üç katman, bir değil. Karpenter düğümleri dinamik olarak sağlar (bir dakikanın altında, Cluster Autoscaler'dan %40 daha hızlı). KAI Scheduler gang scheduling, topoloji farkındalığı ve hiyerarşik kuyrukları yönetir — yedi düğümün bir eksik GPU için bekleyip yandığı 7/8 kısmi tahsis tuzağını engeller. Uygulama düzeyinde otomatik ölçekleyiciler (NVIDIA Dynamo Planner, llm-d Workload Variant Autoscaler) inference'a özgü sinyallerde — kuyruk derinliği, KV cache kullanımı — CPU/DCGM görev döngüsünde değil ölçeklenir. Klasik HPA tuzağı, `DCGM_FI_DEV_GPU_UTIL`'in bir görev döngüsü (duty-cycle) ölçümü olmasıdır: %100, 10 istek veya 100 olabilir. vLLM, KV cache belleğini önceden tahsis eder, bu nedenle bellek asla ölçek küçültmeyi tetiklemez. Bu ders, üç katmanı birleştirmeyi ve inference sırasında çalışan GPU işlerini sonlandıran varsayılan Karpenter `WhenEmptyOrUnderutilized` politikasından kaçınmayı öğretir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak kuyruk-derinliği otomatik ölçekleyici simülatörü)
**Önkoşullar:** Faz 17 · 02 (Inference Platform Ekonomisi), Faz 17 · 04 (vLLM Serving Internals)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Üç otomatik ölçekleme katmanını (düğüm sağlama, gang scheduling, uygulama düzeyi) şematize edin ve her katmanda kullanılan aracı adlandırın.
- `DCGM_FI_DEV_GPU_UTIL`'in vLLM için neden yanlış HPA sinyali olduğunu açıklayın ve iki alternatif adlandırın (kuyruk derinliği, KV cache kullanımı).
- Gang scheduling ve KAI Scheduler'ın engellediği kısmi-tahsis hata modunu (8 GPU'dan 7'si boşta) açıklayın.
- Çalışan GPU işlerini sonlandıran Karpenter konsolidasyon politikasını (`WhenEmptyOrUnderutilized`) adlandırın ve 2026'daki güvenli alternatifi belirtin.

## Sorun

Ekibiniz Kubernetes üzerinde LLM-sunma servisi gönderdi. HPA'yı sinyal olarak `DCGM_FI_DEV_GPU_UTIL` ile kurdunuz. Servis mesai saatlerinde %100 kullanıma sabitleniyor. HPA asla ölçek büyütmez — zaten dolu olduğunuzu düşünüyor. Manuel olarak bir replika ekliyorsunuz; TTFT düşüyor. HPA yine de ölçek büyütmüyor. Sinyal size yalan söylüyor.

Ayrı olarak, düğümler için Cluster Autoscaler kullanıyorsunuz. 2'de 1M-token'lık bir istek geliyor; küme 3 dakika düğüm sağlıyor ve istek zaman aşımına uğruyor.

Yine ayrı olarak, 2 düğüm arasında 8 GPU gerektiren 70B bir model dağıtıyorsunuz. Kümenin 7 GPU'su boşta ve 1'i 3 düğüme dağılmış. Cluster Autoscaler, eksik 1 GPU için bir düğüm sağlıyor. Yedi düğüm 4 dakika para yakarken Kubernetes son GPU'yu hazırlıyor.

Üç katman, üç farklı hata modu. 2026'da GPU-farkında otomatik ölçekleme "HPA'yı aç" değil. Düğüm sağlamayı, gang scheduling'i ve uygulama-sinyalli otomatik ölçeklemeyi birleştirmektir.

## Kavram

### Katman 1 — düğüm sağlama (Karpenter)

Karpenter, bekleyen pod'ları izler ve ~45-60 saniye içinde düğüm sağlar (Cluster Autoscaler, GPU düğümleri için tipik olarak 90-120 saniye sürer). `NodePool` kısıtına göre instance türlerini dinamik olarak seçer — pod'unuz 8 H100'e ihtiyaç duyuyorsa ve kümenin eşleşen düğümü yoksa, Karpenter mevcut grubu ölçeklemek yerine doğrudan bir tane sağlar.

**Konsolidasyon tuzağı**: Karpenter'ın varsayılan `consolidationPolicy: WhenEmptyOrUnderutilized` politikası GPU havuzları için tehlikelidir. Çalışan bir GPU düğümünü, pod'ları daha ucuz, doğru boyutlu bir instance'a taşımak için sonlandırır. Inference iş yükleri için bu, çalışan istekleri çıkarmak ve yeni düğümde 70B modeli yeniden yüklemek anlamına gelir. Kayıp, dakikalarca kapasite artı istek hatalarıdır.

GPU havuzları için güvenli ayar:

```yaml
disruption:
 consolidationPolicy: WhenEmpty
 consolidateAfter: 1h
```

Karpenter'ın gerçekten boş düğümleri bir saat sonra konsolide etmesine izin verir, ancak asla çalışan bir işi çıkarmaz.

#### Açıklama

Bu YAML, Karpenter'ın kesinti (disruption) davranışını yapılandırır. `WhenEmpty` politikası yalnızca boş düğümleri hedefler, `consolidateAfter: 1h` ise konsolidasyonu tetiklemeden önce bir saatlik bir sakinlik süresi uygular — bu, GPU'larda çalışan inference işlerinin ortasında sonlandırılmasını engeller.

### Katman 2 — gang scheduling (KAI Scheduler)

KAI Scheduler (önce "Karp" projesi, sonra yeniden adlandırıldı) varsayılan kube-scheduler'ın yapmadıklarını yönetir:

**Gang scheduling** — tümü-veya-hiç. 8 GPU gerektiren dağıtık bir inference pod'u ya 8'i birden başlar ya da hiçbiri başlamaz. Bunu olmadan, kısmi-tahsis tuzağını alırsınız: 8 pod'dan 7'si başlar, süresiz olarak bekler, para yakar.

**Topoloji farkındalığı** — hangi GPU'ların NVLink'i paylaştığını, hangilerinin aynı raf üzerinde oturduğunu, hangilerinin aralarında InfiniBand olduğunu bilir. Pod'ları buna göre yerleştirir. DeepSeek-V3 67B tensor-paralel iş yükü bir NVLink alanında kalmalıdır; KAI Scheduler buna uyar.

**Hiyerarşik kuyruklar** — birden çok ekip aynı GPU havuzu için öncelik ve kota ile rekabet eder. Takım A'nın üretim darboğazı, Takım B'nin eğitim işi tarafından yalnızca öncelik kuralları izin veriyorsa öncelikli olarak ele alınır (preempt).

KAI, kube-scheduler'ın yanında ikincil bir scheduler olarak dağıtılır; iş yüklerini onu kullanmak üzere işaretlersiniz. Hem Ray hem de vLLM production-stack entegre olur.

### Katman 3 — uygulama düzeyi sinyalleri

**HPA tuzağı**: `DCGM_FI_DEV_GPU_UTIL` bir görev döngüsü (duty-cycle) metriğidir — her örnekleme aralığında GPU'nun çalışıp çalışmadığını ölçer. %100 kullanım, 10 eşzamanlı istek veya 100 anlamına gelebilir; GPU her iki durumda da meşguldü. Görev döngüsü üzerinde ölçekleme, kördöğüsü ölçeklemektir.

Daha kötüsü, vLLM ve benzer motorlar KV cache belleğini önceden tahsis eder (`--gpu-memory-utilization`'a kadar). Bellek kullanımı tek bir istekte bile %90 civarında kalır. Bellek-temelli HPA asla ölçek küçültmez.

**2026 alternatif sinyalleri**:

- Kuyruk derinliği (prefill için bekleyen isteklerin sayısı).
- KV cache kullanımı (blokların aktif dizilere tahsis edilen kesri).
- Replika başına P99 TTFT (sizin SLA sinyaliniz).
- Goodput (tüm SLO'ları karşılayan saniyedeki istekler).

NVIDIA Dynamo Planner ve llm-d Workload Variant Autoscaler bu sinyalleri tüketir ve replikaları ölçekler. LLM sunma için HPA'yı tamamen değiştirirler.

### Ne zaman neyi kullanmalı

| Ölçek kararı | Araç |
|---------------|------|
| Düğüm ekle/çıkar | Karpenter |
| Çoklu-GPU işlerini zamanla | KAI Scheduler |
| Replika ekle/çıkar | Dynamo Planner / llm-d WVA (veya kuyruk derinliğinde özel HPA) |
| GPU türü seç | Karpenter NodePool |
| Düşük önceliği önceliklendir | KAI Scheduler kuyrukları |

### Ayrıştırılmış prefill/decode her şeyi karmaşıklaştırır

Ayrıştırılmış prefill/decode (Faz 17 · 17) çalıştırırsanız, farklı ölçek tetikleyicilerine sahip iki pod sınıfınız olur: prefill pod'ları kuyruk derinliğinde, decode pod'ları KV cache baskısında ölçeklenir. llm-d bunları rol başına HPA ile ayrı `Service`'ler olarak sunar. Önlerine tek bir HPA koymaya çalışmayın.

### Burada da cold start önemli

Cold-start azaltma (Faz 17 · 10), düğüm sağlama süresinin kullanıcıya görünür hale geldiği yerdir. Karpenter'ın 45-60 saniyelik ısınması artı 20GB'lık model yüklemesi artı motor başlatması, sıfırdan bir isteğin 2-5 dakika sürmesi anlamına gelir. SLO-kritik yollar için sıcak bir havuz (`min_workers=1`) tutun veya uygulama katmanında Modal-tarzı kontrol noktası (checkpointing) kullanın.

### Hatırlamanız gereken sayılar

- Karpenter düğüm sağlama: GPU düğümleri için ~45-60s vs Cluster Autoscaler ~90-120s.
- KAI Scheduler, kısmi-tahsis israfını engeller — 7/8 tuzağı.
- HPA sinyali olarak `DCGM_FI_DEV_GPU_UTIL`: bozuk; kuyruk derinliği veya KV kullanımı kullanın.
- Karpenter `WhenEmptyOrUnderutilized`: çalışan GPU işlerini sonlandırır. Inference için `WhenEmpty + consolidateAfter: 1h` kullanın.

## Kullan

`code/main.py`, ani yüklü (bursty) bir GPU iş yükünde üç katmanlı bir otomatik ölçekleyici simüle eder. Naif HPA'yı (görev döngüsü), kuyruk-derinliği HPA'sını ve KAI-gang-zamanlı ölçeklemeyi karşılaştırır. Karşılanmayan istekleri, boş-GPU dakikalarını ve bileşik bir puanı raporlar.

## Üret

Bu ders `outputs/skill-gpu-autoscaler-plan.md` üretir. Küme topolojisi, iş yükü şekli ve SLO verildiğinde, üç katmanlı bir otomatik ölçekleme planı tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Ani yüklü bir iş yükünde, naif görev-döngüsü HPA'sı kaç isteği düşürüyor ve kuyruk-derinliği HPA'sı kaç tanesini yakalıyor? Fark nereden geliyor?
2. Llama 3.3 70B FP8'i H100 SXM5 üzerinde sunan bir küme için bir Karpenter NodePool tasarlayın. `capacity-type`, `disruption.consolidationPolicy`, `consolidateAfter` ve GPU-dışı iş yüklerini bu düğümlerden uzak tutan bir taint belirtin.
3. Ekibiniz dağıtımların Pending'de sıkıştığını çünkü "GPU'lar mevcut ama pod zamanlanmıyor" diye bildiriyor. Tanı koyun — bu Karpenter, kube-scheduler veya KAI Scheduler mı? Hangi metrikler doğruluyor?
4. Ayrıştırılmış prefill pod'larını ölçeklemek için bir sinyal ve decode pod'ları için farklı bir sinyal seçin. İkisini de gerekçelendirin.
5. 7/24 bir üretim servisinde, P99 TTFT > 10s ile günde ortalama 60 istek-düşürme olayı olan `WhenEmptyOrUnderutilized` konsolidasyon tuzağının maliyetini hesaplayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Karpenter | "düğüm sağlayıcı" | Kubernetes düğüm otomatik ölçekleyici; dakika altı sağlama |
| Cluster Autoscaler | "eski ölçekleyici" | Kubernetes düğüm otomatik ölçekleyici öncüsü; daha yavaş, grup-temelli |
| KAI Scheduler | "GPU scheduler" | Gang + topoloji + kuyruklar için ikincil scheduler |
| Gang scheduling | "tümü veya hiç" | N pod'u atomik olarak zamanla veya tümünü ertele |
| Topoloji farkındalığı | "raf-farkında" | NVLink/IB/raf yerleşimine göre pod'ları yerleştir |
| `DCGM_FI_DEV_GPU_UTIL` | "GPU kullanımı" | Görev döngüsü metriği; LLM'ler için ölçekleme sinyali DEĞİLDİR |
| Kuyruk derinliği | "bekleyen istekler" | Prefill-bağlı ölçekleme için doğru HPA sinyali |
| KV cache kullanımı | "bellek baskısı" | Decode-bağlı ölçekleme için doğru HPA sinyali |
| Konsolidasyon | "Karpenter konsolidasyonu" | Daha ucuz instance türüne düğüm sonlandırma |
| `WhenEmpty + 1h` | "güvenli konsolidasyon" | Çalışan GPU işlerini çıkarmayan politika |

## İleri Okuma

- [KAI Scheduler GitHub](https://github.com/kai-scheduler/KAI-Scheduler) — tasarım dokümanları ve konfigürasyon örnekleri.
- [Karpenter Disruption Controls](https://karpenter.sh/docs/concepts/disruption/) — konsolidasyon politikası semantiği ve GPU-güvenli varsayılanlar.
- [NVIDIA — Disaggregated LLM Inference on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — Dynamo Planner ölçekleme sinyalleri.
- [Ray docs — KAI Scheduler for RayClusters](https://docs.ray.io/en/latest/cluster/kubernetes/k8s-ecosystem/kai-scheduler.html) — Ray entegrasyon örüntüsü.
- [AWS EKS Compute and Autoscaling Best Practices](https://docs.aws.amazon.com/eks/latest/best-practices/aiml-compute.html) — yönetilen-Kubernetes'a özgü rehberlik.
- [llm-d GitHub](https://github.com/llm-d/llm-d) — Workload Variant Autoscaler tasarımı.
