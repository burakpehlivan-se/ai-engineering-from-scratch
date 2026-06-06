# Yönetilen LLM Platformları — Bedrock, Vertex AI, Azure OpenAI

> Üç hiper ölçekleyici (hyperscaler), üç farklı strateji. AWS Bedrock bir model pazar yeri — Claude, Llama, Titan, Stability, Cohere tek bir API'nin arkasında. Azure OpenAI, OpenAI ile özel bir ortaklık ve ayrılmış kapasite için Provisioned Throughput Units (PTU'lar). Vertex AI Gemini-odaklı, en iyi uzun bağlam ve multimodal hikâyeye sahip. 2026'da Artificial Analysis, Llama 3.1 405B eşdeğerleri üzerinde Azure OpenAI'yi medyan ~50 ms ve Bedrock'u ~75 ms olarak ölçüyor — fark PTU'larla açıklanır çünkü ayrılmış kapasite paylaşılan on-demand'i yener. Karar kuralı "hangisi en hızlı" değil, "hangi model kataloğu ve FinOps yüzeyi ürünüme uyuyor." Bu ders, seçimi belgelenmiş ödünleşimlerle — sezgilerle değil — yapmayı öğretir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak maliyet-ve-gecikme karşılaştırıcısı)
**Önkoşullar:** Faz 11 (LLM Mühendisliği), Faz 13 (Araçlar ve Protokoller)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Üç platform stratejisini (pazar yeri vs özel vs Gemini-odaklı) adlandırın ve her birini bir ürün kullanım senaryosuyla eşleştirin.
- Azure OpenAI'de Provisioned Throughput Units (PTU'lar)'ın ne satın aldığını ve neden on-demand Bedrock'un 405B ölçeğinde tipik olarak ~25 ms daha yavaş okuduğunu açıklayın.
- Her platform için FinOps atıf yüzeyini şematize edin (Bedrock Application Inference Profile'ları vs Vertex proje-başına-ekip vs Azure kapsamları + PTU rezervasyonları).
- "İki sağlayıcı minimumu" politikasını yazılı olarak belirtin ve 2026'da tek satıcıya bağlanmanın (lock-in) neden pahalı bir hata olduğunu açıklayın.

## Sorun

Ürününüz için Claude 3.7 Sonnet'ı seçtiniz. Şimdi onu sunmanız gerekiyor. Anthropic API'sini doğrudan çağırabilirsiniz, AWS Bedrock üzerinden çağırabilirsiniz veya bir ağ geçidi (gateway) üzerinden gidebilirsiniz. Doğrudan API en basit olanıdır; Bedrock BAA'lar, VPC endpoint'leri, IAM ve CloudWatch atfını ekler. Ağ geçidi, sağlayıcılar arasında yük devretme (failover), birleşik faturalama ve hız limitleri ekler.

Daha derin soru katalogdur. Aynı üründe Claude, Llama ve Gemini'ye ihtiyacınız varsa, bunların hepsini Bedrock artı Vertex artı Azure OpenAI aynı anda olmadıkça tek bir yerden satın alamazsınız. Hiper ölçekleyiciler birbirinin yerine geçemez — her biri model katmanına kimin sahip olduğuna dair farklı bir bahis yaptı.

Bu ders üç bahsi, gecikme farkını, FinOps farkını ve lock-in (sağlayıcıya bağlanma) riskini haritalandırır.

## Kavram

### Üç strateji

**AWS Bedrock** — pazar yeri. Claude (Anthropic), Llama (Meta), Titan (AWS birinci taraf), Stability (görüntü), Cohere (embedding'ler), Mistral, artı görüntü ve embedding alt katalogları. Tek API, tek IAM yüzeyi, tek CloudWatch dışa aktarımı. Bedrock'un bahsi, müşterilerin tek bir modelden çok seçenek (optionality) istediğidir.

**Azure OpenAI** — özel ortaklık. Azure veri merkezlerinde GPT-4 / 4o / 5 / o-serisi, DALL·E, Whisper ve OpenAI modellerinin ince ayarını (fine-tuning) alırsınız. "Azure OpenAI Service" kataloğunda OpenAI dışı model yoktur — bunlar Azure AI Foundry'ye (ayrı ürün) gider. Azure'un bahsi, OpenAI'nin sınırda (frontier) kalmaya devam edeceği ve müşterilerin bu belirli ilişki üzerinde kurumsal kontroller istediğidir.

**Vertex AI** — önce Gemini, her şey sonra. Gemini 1.5 / 2.0 / 2.5 Flash ve Pro, artı Model Garden (üçüncü taraf). Vertex'in bahsi multimodal uzun bağlam — 1M-token Gemini bağlamı farklılaştırıcıdır.

### Ölçekte gecikme farkı

Artificial Analysis sürekli kıyaslamalar yürütür. Eşdeğer Llama 3.1 405B dağıtımlarında (paylaşılan on-demand), Azure OpenAI medyan ilk-token gecikmesi yaklaşık 50 ms; Bedrock yaklaşık 75 ms. Fark bir AWS başarısızlığı değil — bir kapasite modeli farkıdır. Azure, sizin kiracınız için GPU kapasitesi ayıran PTU'lar (Provisioned Throughput Units) satar. Bedrock'un eşdeğeri (Provisioned Throughput) vardır ancak birim başına saatte yaklaşık 21$'dan başlar ve çoğu müşteri paylaşılan on-demand'de kalır.

On-demand paylaşılan kapasite, diğer tüm müşterilerin trafiğiyle rekabet eder. Ayrılmış kapasite rekabet etmez. Ürününüzün SLA'sı P99'da TTFT < 100 ms ise, ya Azure'da PTU satın alırsınız, ya Bedrock Provisioned Throughput satın alırsınız, ya da varsayılan varyansı kabul edersiniz.

### Provisioned Throughput ekonomisi

Azure PTU'lar: ayrılmış bir inference (çıkarım) hesaplama bloğu. Öngörülebilir iş yükleri için on-demand'e kıyasla %70'e kadar tasarruf. Trafikten bağımsız olarak saat başına sabit maliyet — boştayken bile rezervasyon için ödeme yaparsınız. Başabaş noktası genellikle sürekli kullanımın (utilization) %40-60'ı civarındadır.

Bedrock Provisioned Throughput: modele ve bölgeye bağlı olarak saatte 21-50$. Benzer matematik — başabaş noktası en yüksek kullanımın yaklaşık yarısı civarındadır. Aylık taahhüt gereklidir.

Vertex ayrılmış kapasitesi Gemini SKU'su başına satılır; fiyatlandırma modele ve bölgeye göre değişir ve kamuya daha az açıktır.

### FinOps yüzeyi — gerçek farklılaştırıcı

**Bedrock Application Inference Profile'ları** pazar yerindeki en temiz atıf sistemidir. Bir profile `team`, `product`, `feature` etiketleri koyun; tüm model çağrılarını onun üzerinden yönlendirin; CloudWatch profiller başına maliyeti sonradan işleme olmadan ayırır. 2025'te eklendi, hâlâ en granüler hiper ölçekleyici-yerlisi.

**Vertex** atfı proje-başına-ekip artı her yerde etiket'tir. Her ekibi bir GCP projesi olarak modellersiniz, her kaynağa etiket koyarsınız ve toplamlar için BigQuery Billing Export + DataStudio kullanırsınız. Daha fazla iş, ancak BigQuery maliyet verileri üzerinde isteğe bağlı SQL sağlar.

**Azure** atfı, abonelik/kaynak grubu (resource-group) kapsamları artı etiketlere ve birinci sınıf maliyet nesnesi olarak PTU rezervasyonlarına dayanır. Etiketler kaynak gruplarından miras alınır, isteklerden değil; dolayısıyla istek başına atıf için Application Insights özel metrikleri veya başlıkları damgalayan bir ağ geçidi gerekir.

Örüntü: Bedrock en temiz yerli, Vertex BigQuery üzerinden en esnek, Azure siz işaretleme (instrument) yapmadıkça en opak.

### 2026'da lock-in risk

Tek hiper ölçekleyiciye bağlanma, bir model hâkim olduğunda sorun değildi. 2026'da sınır her ay hareket ediyor — bir çeyrekte Claude 3.7, sonrakinde Gemini 2.5, bir sonrakinde GPT-5. Tek bir platforma kilitlenmek sizi sınırın üçte ikisinin dışında bırakır.

Çalışan ekiplerin benimsediği örüntü: herhangi bir ürün-kritik LLM çağrısı için iki sağlayıcı minimumu. Bedrock artı Azure OpenAI yaygın çifttir — birinden Claude, diğerinden GPT, aralarında yük devretme, aynı ağ geçidi. Maliyet artışı göz ardı edilebilir düzeydedir çünkü ağ geçidi optimal yönlendirme yapar; kesintiler sırasındaki kullanılabilirlik artışı (Azure OpenAI Ocak 2025 olayı, AWS us-east-1 kesintisi gibi) belirleyicidir.

### Veri yerleşimi, BAA'lar ve düzenlenmiş endüstriler

Bedrock: Çoğu bölgede BAA'lar; VPC endpoint'leri; guardrail'ler. Yaygın fintech varsayılanı.

Azure OpenAI: HIPAA, SOC 2, ISO 27001; AB veri yerleşimi; kurumsal-düzenlenmiş varsayılan.

Vertex: HIPAA, GDPR, bölge başına veri yerleşimi; Google Cloud'un uyumluluk yığını.

Üçü de temel kontrol listesini karşılar. Farklılıklar veri saklama politikalarında, log'ların nasıl işlendiğinde ve kötüye kullanım izlemenin (abuse monitoring) trafiğinizi okuyup okumadığındadır (çoğunda varsayılan opt-in; kurumsalda opt-out mevcut).

### Hatırlamanız gereken sayılar

- Llama 3.1 405B eşdeğerlerinde Azure OpenAI medyan TTFT: ~50 ms (PTU'larla).
- Bedrock on-demand medyan TTFT: ~75 ms.
- Bedrock Provisioned Throughput: birim başına 21-50$/saat.
- Azure PTU başabaş noktası: sürekli kullanımın %40-60'ı.
- Yüksek kullanımda PTU tasarrufu vs on-demand: %70'e kadar.

## Kullan

`code/main.py`, üç platformu sentetik bir iş yükü üzerinde karşılaştırır — on-demand vs PTU ekonomisini, TTFT varyansını ve maliyet atfı sadakatini modeller. PTU'ların nerede kârlı olduğunu ve pazar yerinin model genişliğinin TTFT farkını nerede aştığını görmek için çalıştırın.

## Üret

Bu ders `outputs/skill-managed-platform-picker.md` üretir. Bir iş yükü profili (gerekli modeller, TTFT SLA'sı, günlük hacim, uyumluluk gereksinimleri) verildiğinde, bir birincil platform, bir yedek ve bir FinOps işaretleme planı önerir.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Azure PTU, 70B sınıfı bir model için hangi sürekli kullanım oranında on-demand'i yener? Başabaş noktasını hesaplayın ve reklamı yapılan %40-60 bandıyla karşılaştırın.
2. Ürününüz Claude 3.7 Sonnet ve GPT-4o'ya ihtiyaç duyuyor. İki sağlayıcılı bir dağıtım tasarlayın — hangisi hangi hiper ölçekleyiciye gider, önüne hangi ağ geçidi oturur, yük devretme (failover) politikası nedir?
3. Düzenlenmiş bir sağlık müşterisi BAA'lar, US-East veri yerleşimi ve 100ms altı P99 TTFT gerektiriyor. Bir platform seçin ve üç spesifik özellikle gerekçelendirin.
4. Bedrock faturanızın bu ay trafik değişikliği olmadan 4x arttığını keşfettiniz. Application Inference Profile'ları olmadan, suçluyu nasıl bulurdunuz? Profile'larla ne kadar sürer?
5. Azure OpenAI ve Bedrock fiyatlandırma sayfalarını okuyun. 100M-token/ay'lık bir Claude iş yükü için hangisi daha ucuz — doğrudan Anthropic API, Bedrock on-demand veya Bedrock Provisioned Throughput?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Bedrock | "AWS LLM servisi" | Claude, Llama, Titan, Mistral, Cohere'yi kapsayan model pazar yeri |
| Azure OpenAI | "Azure'un ChatGPT'si" | Kurumsal kontrollerle Azure veri merkezlerinde özel OpenAI modelleri |
| Vertex AI | "Google'ın LLM'i" | Üçüncü taraf modeller için Model Garden ile Gemini-odaklı platform |
| PTU | "ayrılmış kapasite" | Provisioned Throughput Unit — ayrılmış inference (çıkarım) GPU'ları, saat başına fiyatlandırılır |
| Application Inference Profile | "Bedrock etiketleme" | Etiketli, CloudWatch-yerlisi ürün başına maliyet/kullanım profili |
| Model Garden | "Vertex kataloğu" | Vertex AI'ın Gemini'den ayrı üçüncü taraf model bölümü |
| İki sağlayıcı minimumu | "LLM yedekliliği" | Her kritik LLM yolunu ≥2 hiper ölçekleyici üzerinde çalıştırma politikası |
| BAA | "HIPAA kâğıt işleri" | Business Associate Agreement; PHI için gerekli; üçü tarafından sağlanır |
| Kötüye kullanım izleme | "log izleyici" | Sağlayıcı tarafı güvenlik taraması; kurumsalda opt-out |

## İleri Okuma

- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) — yetkili fiyat kartı ve Provisioned Throughput fiyatlandırması.
- [Azure OpenAI Service Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/) — PTU ekonomisi ve fiyat kartları.
- [Vertex AI Generative AI Pricing](https://cloud.google.com/vertex-ai/generative-ai/pricing) — Gemini katmanları ve Model Garden ek ücretleri.
- [Artificial Analysis LLM Leaderboard](https://artificialanalysis.ai/) — sağlayıcılar arasında sürekli gecikme ve verim kıyaslamaları.
- [The AI Journal — AWS Bedrock vs Azure OpenAI CTO Guide 2026](https://theaijournal.co/2026/03/aws-bedrock-vs-azure-openai/) — kurumsal karar çerçevesi.
- [Finout — Bedrock vs Vertex vs Azure FinOps](https://www.finout.io/blog/bedrock-vs.-vertex-vs.-azure-cognitive-a-finops-comparison-for-ai-spend) — atıf mekanikleri yan yana.
