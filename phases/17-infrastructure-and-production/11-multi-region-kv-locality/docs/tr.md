# Çok-Bölgeli LLM Sunma ve KV Cache Yerelliği

> Yuvarlak-robin (round-robin) yük dengeleme, önbellekli LLM inference için aktif olarak zararlıdır. Önekini tutan düğüme düşmeyen bir istek tam prefill maliyetini öder — uzun bir istemde ~800 ms P50'ye karşı cache hit ile ~80 ms. 2026'da üretim örüntüsü, KV-cache olaylarını tüketen ve önek-hash eşleşmesi üzerinde yönlendiren cache-farkında bir router'dır (Rust'ta vLLM Router, llm-d router). Son araştırma (GORGO), bölgeler arası ağ gecikmesini yönlendirme hedefinde açık bir terim haline getiriyor. Ticari "bölgeler arası inference" teklifleri (Bedrock cross-region inference, GKE multi-cluster gateway) inference'ı opak olarak ele alır — kullanılabilirliği yönetirler, TTFT'yi değil. JPMorgan ve Mayo Clinic, Kasım 2024'te us-east-1 yük devretmesini ~22 dakikada çalıştırdı. DR gerçeği: LLM DR başarısızlıklarının %32'si, ekiplerin ağırlıkları yedekledi ama tokenizer dosyalarını veya kuantizasyon konfigürasyonlarını unuttukları için.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak önek-cache-farkında router simülatörü)
**Önkoşullar:** Faz 17 · 04 (vLLM Sunma), Faz 17 · 06 (SGLang RadixAttention)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Yuvarlak-robin yük dengenin neden önbellekli inference'ı bozduğunu açıklayın ve TTFT cezasını nicelendirin.
- Bir cache-farkında router'ı şematize edin: girdiler (KV-cache olayları), algoritma (önek-hash eşleşmesi), bağ çözücü (GPU kullanımı).
- LLM'ler için %32 DR başarısızlık sürücüsünü (eksik tokenizer dosyaları / kuantizasyon konfigürasyonları) adlandırın ve üç-dosyalık bir DR kontrol listesi belirtin.
- Ticari bölgeler-arası teklifleri (Bedrock CRI, GKE Multi-Cluster Gateway) KV-farkında yönlendirmeden ayırt edin.

## Sorun

Servisiniz us-east-1, us-west-2 ve eu-west-1'de çalışıyor. Önüne yuvarlak-robin ile bir ALB koydunuz. Üretimde önek cache hit oranı %8'e düşüyor. TTFT P50 üçe katlanıyor. vLLM log'larınız her isteğin tam prefill maliyetini ödediğini gösteriyor.

Yuvarlak-robin durumsuz servisler için optimaldir. LLM inference, tasarım gereği durumludur — KV cache, modelin gördüğü her şeyi kodlar. Kör yönlendirme, yanlış cache'e yönlendirmektir.

Ayrı olarak, ekibinizin bir DR planı var. Model ağırlıklarını S3'e bölgeler arası yedekliyorsunuz. Bölgesel bir kesinti vuruyor; yük devretmeye çalışıyorsunuz; replika başlamayı reddediyor. Senkronize etmediğiniz ayrı bir kovada olan tokenizer.json, kuantizasyon konfigürasyonu ve RoPE ölçekleme konfigürasyonunu unuttuğunuzu fark ediyorsunuz.

Çok-bölgeli LLM sunma, bir yük dengeleyici problemi değil, bir cache problemi, bir yönlendirme problemi ve bir DR-hijyen problemidir.

## Kavram

### Cache-farkında yönlendirme

İstek bir istemle gelir. Router, öneki hash'ler (diyelim ilk 512 token); her replikaya sorar "bu öneki önbelleğe aldın mı?". Replikalar, blok tahsis ettikçe ve çıkardıkça KV-cache olaylarını bir pub/sub kanalında yayınlar. Router, eşleşmesi olan replikayı seçer, kimse yapmazsa GPU-util-temelli bağ çözücüye düşer.

**vLLM Router** (Rust, 2026 production-stack): `kv.cache.block_added` olaylarına abone olur, bir önek-hash → replika indeksi tutar, O(1) aramayla yönlendirir. Eşleşme olmadığında en az kuyruk derinliğine düşer.

**llm-d router**: aynı örüntü, Kubernetes-yerel. Olayları ControlPlane API'si aracılığıyla yayınlar.

**SGLang RadixAttention** (Faz 17 · 06) replika-içi eşdeğerdir. Çapraz-replika yönlendirme kesinlikle yukarı akıştır.

### Sayılar

H100'de Llama 3.3 70B FP8, 2K-token istemde TTFT P50:

- Cache hit (aynı replika, önek yerleşik): ~80 ms.
- Cache miss (soğuk prefill): ~800 ms.

10x fark. Router, replikalar arasında önek cache'inin %60-80'ine isabet ediyorsa, N-replika kapasitesinde tek-replika performansını yaklaşıklandırırsınız. %10'una isabet ediyorsa, naif ölçeklendirmeyi yaklaşıklandırırsınız.

### Bölgeler arasının yeni bir kısıtı var — ağ gecikmesi

Bölgeler arası RTT:

- us-east-1 ↔ us-west-2: ~65 ms.
- us-east-1 ↔ eu-west-1: ~75 ms.
- us-east-1 ↔ ap-southeast-1: ~220 ms.

Yönlendirme bir isteği us-east-1'den ap-southeast-1'deki sıcak bir öneke alırsa, tasarruf edilen prefill (800 → 80 ms) 440 ms'lik gidiş-dönüş tarafından gölgelenir. GORGO (2026 araştırması) bunu açık hale getiriyor — yalnızca prefill yerine `prefill_time + network_latency` ortaklaşa minimize edin. Çoğu zaman cevap, büyük multi-MB öneklerin prefill'in baskın olduğu durumlar dışında, yönlendirmeyi bölgesel tutmaktır.

### Ticari "bölgeler arası inference" burada yardımcı olmaz

AWS Bedrock cross-region inference, kapasite baskısı sırasında istekleri otomatik olarak diğer bölgelere yönlendirir. Kullanılabilirliği optimize eder, TTFT'yi değil, ve inference'ı opak olarak ele alır. GKE Multi-Cluster Gateway aynıdır — servis-düzeyinde yük devretme, KV cache farkındalığı yok.

Bunları kullanırken bile hâlâ bir uygulama-katmanı cache-farkında router'a ihtiyacınız var. "us-east-1 yanıyor" durumunu onlar yönetir. Cache-farkında yönlendirme TTFT durumunu yönetir.

### DR hijyeni — %32 eksik-dosyalar problemi

Yaygın olarak alıntılanan 2026 istatistiği: LLM DR başarısızlıklarının %32'si, ekipler ağırlıkları yedekledi ama şunları unuttuğu için olur:

- `tokenizer.json` veya `tokenizer.model`
- Kuantizasyon konfigürasyonları (`quantize_config.json`, AWQ ölçekleri, GPTQ sıfır-noktaları)
- Modele özgü konfigürasyonlar (RoPE ölçekleme, attention maskeleri, sohbet şablonları)
- Motor konfigürasyonu (`vllm_config.yaml`, örnekleme varsayılanları, LoRA adaptör manifestoları)

Düzeltme, üç-dosyalık minimum DR manifestidir:

1. HF model reposu altındaki tüm dosyalar (ağırlıklar + konfigürasyonlar + tokenizer).
2. Motor-a-özgü sunma konfigürasyonu.
3. Dağıtım manifesti (K8s YAML, Dockerfile, bağımlılık kilidi).

Artı: üç ayda bir bir DR tatbikatı çalıştırın. JPMorgan'ın us-east-1 tatbikatı, yalnızca oyun kitabı prova edildiği için Kasım 2024'te 22 dakikalık kurtarmaya ulaştı.

### Veri yerleşimi ortogonal

AB müşterisi PHI AB'den ayrılamaz. Cache-farkında router'ınız Paris-kökenli bir isteği önek eşleşmesi için us-east-1'e gönderirse, TTFT kazancı ne olursa olsun GDPR'ı ihlal etmiş olursunuz. Önbellek için optimize etmeden önce router'ları yerleşim sınırına göre bölümlendirin.

### Hatırlamanız gereken sayılar

- Cache hit vs miss TTFT farkı: ~10x (2K istemde 80 ms vs 800 ms).
- Bölgeler arası RTT ABD-AB: ~75 ms.
- DR başarısızlığı: %32 tokenizer/quant konfigürasyonlarını kaçırır.
- JPMorgan us-east-1 yük devretme Kasım 2024: 22 dakika (30-dakikalık SLA).

## Kullan

`code/main.py`, çok-bölgeli bir iş yükünde üç yönlendirme stratejisini (yuvarlak-robin, cache-farkında bölgesel, cache-farkında küresel) simüle eder. Cache hit oranını, TTFT P50/P99'u ve bölgeler arası faturayı raporlar.

## Üret

Bu ders `outputs/skill-multi-region-router.md` üretir. Bölgeler, yerleşim kısıtları ve SLA verildiğinde, bir yönlendirme planı tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. 75 ms RTT verildiğinde, bölgeler arası yönlendirme yerel-yalnızca yönlendirmeyi hangi istem uzunluğunda yener?
2. Cache hit oranınız %70'ten %12'ye düşüyor. Üç olası nedeni ve her birini doğrulayacak gözlemlenebilirleri tanılayın.
3. vLLM'de sunulan 5 LoRA adaptörlü 70B AWQ- kuantaize edilmiş model için bir DR manifesti tasarlayın. Her dosyayı ve konfigürasyonu listeleyin.
4. Sıkı TTFT SLO'ları olan bir fintech için Bedrock cross-region inference'in "yeterli" olup olmadığını tartışın. Belirli davranışları alıntılayın.
5. Paris-kökenli bir istek us-east-1'deki bir önekle eşleşiyor. Yönlendirir misiniz? Politikayı yazın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Cache-farkında yönlendirme | "akıllı LB" | Önek-hash eşleşmesini KV-cache-tutan replikaya yönlendir |
| KV-cache olayları | "cache pub-sub" | Replikalar blok ekleme/çıkarma yayınlar; router indeksler |
| Önek hash | "cache anahtarı" | Router araması olarak kullanılan ilk N tokenin hash'i |
| GORGO | "bölgeler arası yönlendirme araştırması" | arXiv 2602.11688; ağ gecikmesi açık terim olarak |
| Bölgeler arası inference | "Bedrock CRI" | AWS ürünü; kullanılabilirlik yük devretme, TTFT farkındalığı değil |
| DR manifesti | "yedekleme listesi" | Kurtarmak için gereken her dosya — yalnızca ağırlıklar değil |
| Veri yerleşimi | "GDPR sınırı" | Kullanıcı verilerinin hangi bölgeyi göreceğine ilişkin yasal kısıt |
| RTT | "gidiş-dönüş süresi" | Ağ gecikmesi; ABD-AB 75 ms, ABD-APAC 220 ms |
| LLM-farkında LB | "cache-hit LB" | Bir ürün kategorisi olarak cache-farkında router |

## İleri Okuma

- [BentoML — Multi-cloud and cross-region inference](https://bentoml.com/llm/infrastructure-and-operations/multi-cloud-and-cross-region-inference)
- [arXiv — GORGO (2602.11688)](https://arxiv.org/html/2602.11688v1) — ağ gecikmesi terimiyle bölgeler arası KV-cache yeniden kullanımı.
- [TianPan — Multi-Region LLM Serving Cache Locality](https://tianpan.co/blog/2026-04-17-multi-region-llm-serving-data-residency-routing)
- [AWS Bedrock Cross-Region Inference](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html) — kullanılabilirlik yük devretme dokümantasyonu.
- [vLLM Production Stack Router](https://github.com/vllm-project/production-stack) — cache-farkında router kaynağı.
