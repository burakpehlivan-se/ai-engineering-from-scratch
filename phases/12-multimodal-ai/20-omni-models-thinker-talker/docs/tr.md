# Omni Modeller: Qwen2.5-Omni ve Düşünce-Konuşma Bölünmesi

> GPT-4o'nun Mayıs 2024'teki ürün demonstrasyonu, temel modelden ziyade ürün şekli nedeniyle yıkıcıydı — konuştuğunuz, modelin kameranın gördüğünü gördüğü ve 250ms'nin altında size geri konuştuğu bir ses arayüzü. Açık ekosistem 2024'ün geri kalanını ve 2025'i o ürün yüzeyine ulaşmak için yarışarak geçirdi. Qwen2.5-Omni (Mart 2025) referans açık tasarımıdır: büyük bir metin üreten Thinker (Düşünen) artı paralel ses üreten bir Talker (Konuşan), akışlı ses token'larıyla bağlı. Mini-Omni basitleştirdi, Moshi gecikmesine eşleşti, GLM-4-Voice'ı Çince'ye genişletti. Bu ders Thinker-Talker mimarisini ve gerçek zamanlı konuşma diyalogunu mümkün kılan gecikme bütçesini (latency budget) okur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, akışlı boru hattı gecikme simülatörü + VAD döngüsü)
**Ön koşullar:** Faz 12 · 19 (ses-LLM'ler), Faz 12 · 16 (her şeyden her şey)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Çıkarım boru hattını Thinker (metin çıkarma) ve Talker (ses sentezi) olarak bölün ve paralel akışın neden çalıştığını açıklayın.
- Bir konuşma etkileşimi için time-to-first-audio-byte (TTFAB) bütçesini bileşen bileşen hesaplayın.
- Thinker içinde görüntü, ses ve metin genelinde zaman hizalı (time-aligned) konum kodlaması olan TMRoPE'yi tanımlayın.
- Üç gerçek zamanlı konuşma paternini adlandırın: half-duplex, turn-taking (sıra alma), full-duplex.

## Problem

Bir gerçek zamanlı ses asistanı çok şeyi hızlı yapmalıdır:

1. Kullanıcıyı duy. Gerçek zamanlı ses tokenize etme, konuşma etkinliği algılama (VAD) ile ne zaman konuştuğunu bitirdiğini anlama.
2. İsteğe bağlı olarak gör. 2-4 FPS'de kamera girdisi, sesle birlikte Thinker'e akar.
3. Düşün. Geçmiş konuşmaya koşullu bir yanıt birleştir.
4. Konuş. Ses token'larını sentezle, dalga formuna çözümle, kullanıcının hoparlörlerine akar.

Her adım gecikme ekler. Konuşma hissi için toplam round-trip < 500ms olmalıdır — bunun altında kullanıcı gecikmeyi fark etmeyi bırakır. GPT-4o ~250ms iddia ediyor. Moshi ~160ms. Qwen2.5-Omni ~350-500ms.

Her bileşenin akması gerekir. Hiçbir şey "her şeyi topla sonra çözümle" olamaz.

## Kavram

### Thinker ve Talker

Qwen2.5-Omni'nun ayrıştırması:

- Thinker: 7B-80B arası metin üreten bir transformer. İç içe geçmiş metin + görüntü + ses token'larını tüketir. Söyleyecek şeyi temsil eden metin token'ları üretir.
- Talker: daha küçük bir ses üreten transformer (200M-1B). Thinker'ın metin çıktı token'larını artı son ses bağlamı token'larını tüketir. Ayrık ses token'ları (residual-VQ indisleri) üretir.
- Ses decoder'ı: ses token'larını gerçek zamanlı ses örneklerine dönüştüren akışlı bir dalga formu decoder'ı (SNAC, MoVQGAN ailesi).

Ayrışma önemlidir. İyi çıkarma için Thinker büyük olmalıdır. Talker küçük olabilir çünkü görevi yereldir — metni ses token'larına dönüştürmek. Daha büyük Talker daha expresif değildir; daha yavaştır.

Her ikisini paralel çalıştırma:

1. Thinker metin token t_i'yi üretir.
2. Talker t_i'yi (akış yoluyla) tüketir ve ses token'ları s_i, s_{i+1}, ..., s_{i+k} üretir.
3. Ses decoder'ı gelen ses token'larını tüketir ve ses örnekleri üretir.
4. Thinker metin token t_{i+3}'teyken, Talker zaten t_0..t_{i+2} için sesi akıtmıştır.

### TMRoPE — zaman hizalı multimodal konumlar

Thinker, görüntü karelerini (örneğin 4 FPS'de gelen), ses karelerini (saniyede 50 kare hızında gelen) ve konuşma geçmişinden gelen metni bütünleştirmelidir. Naïf dizi sırası (tüm görüntüler, sonra tüm ses, sonra metin) zamansal hizalamayı kaybeder.

TMRoPE her token'a mutlak zaman damgası atar. t=2.3s'de görüntü token'ı. t=2.32s'de ses token'ı. t=2.35s'de kullanıcı "dur" metin token'ı. RoPE attention'ı zaman damgasına göre döndürür; model bunları zamansal olarak eşanlı看到r.

Bu, "el sallarken merhaba dedi"nin çalışması için altyapıdır — model video karesini ve sesi kavramsal olarak aynı anda看到r.

### Akışlı ses sentezi

Ses token'ları akmalıdır. Mini-Omni (Xie & Wu, 2024) "dil modelleri akışlı olarak düşünürken duyabilir, konuşabilir" tanıttı: Thinker çıktı token'ları ve Talker çıktı token'ları aynı dizi içinde iç içe geçer. Talker, Thinker bir sonraki metin token'ını onayladığı anda ateş eder. Toplu iş (batch) sınırları yoktur.

Moshi (Défossez ve ark., Ekim 2024) en hızlı açık uygulamadır. Tek bir A100'de 160ms TTFAB. Mimari: metin ve ses token'larını sıralı konumlarında üreten tek bir 7B transformer, düşünme akışını konuşma akışından ayıran bir "iç monolog" (inner monologue). Bu, dikkatli eğitimle Thinker + Talker'ın tek bir modelde birleşimidir.

### VAD ve sıra alma (turn-taking)

Konuşma etkinliği algılama (VAD) girdi tarafında çalışır. İki patern:

- Half-duplex: kullanıcı konuşur, model dinler. Model konuşur, kullanıcı dinler. VAD sessizlik algılama ile net teslim (~200ms).
- Full-duplex: her ikisi aynı anda konuşabilir. Model onaylayabilir ("uh-huh") veya araya girebilir. Çok daha zordur. Moshi bunu destekler.

Qwen2.5-Omni varsayılan olarak half-duplex'i destekler, sessizlik eşiğiyle sıra alma ile. Full-duplex uygulama katmanı işlemselliği gerektirir.

### Qwen3-Omni (Kasım 2025)

Halefi. Qwen3-80B Thinker, daha büyük Talker, geliştirilmiş TMRoPE-v2. Gecikme GPT-4o'nun 250ms'sine yakın. Açık ağırlıklar. OmniBench benchmark'larında Gemini 2.0 Live ile rekabetçi.

### Üretim gecikme bütçesi

Tipik bir akışlı etkileşim için:

- Mikrofon -> ses token'ları: 40-80ms.
- Doldurma (prompt + geçmiş): 7B'de 100-200ms, 70B'de çok daha fazla.
- İlk Thinker metin token'ı: 40ms.
- Talker ilk metin token'ını işler: 20ms.
- İlk ses token'ları onaylanır: 40ms.
- Residual-VQ çözümleme: 30ms.
- Ses dalga formu çözümleme: 50-80ms.

Toplam TTFAB: 7B'de 320-510ms, 70B'de 600-900ms. Sınır kalitesi genellikle 70B+ demektir; dolayısıyla sınır gecikme farkı.

### Token hızı (token-rate) matematiği

50 Hz temel ses token'ıyla 16kHz konuşmada, çıktı saniyesi başına 50 ses token'ı gerekir. Talker ayak uydurmak için ≥50 tok/s üretmelidir. H100'de tipik LLM throughput'u 30-80 tok/s ile küçük (200-300M) bir Talker yeterince hızlıdır; 7B bir Talker geride kalır.

Bu yüzden "ana modeli kullanmak" yerine küçük özel Talker modelleri vardır.

## Kullan

`code/main.py`:

- Sahte token üretim hızlarıyla bir Thinker-Talker boru hattını simüle eder.
- Yapılandırılabilir model boyutları ve mikrofon örnek hızları için TTFAB hesaplar.
- VAD sessizlik eşiğiyle half-duplex sıra almayı gösterir.

## Teslim Et

Bu ders `outputs/skill-omni-streaming-budget.md` dosyasını üretir. Bir gerçek zamanlı ses ürününün hedef TTFAB'ı ve özellik kümesi (görüş dahil, iki dilli, full-duplex) verildiğinde Qwen2.5-Omni, Qwen3-Omni, Moshi veya Mini-Omni'yi seçer ve Thinker/Talker boyutlandırmasını yapar.

## Alıştırmalar

1. Hedef TTFAB'ınız 300ms. 7B Thinker ve 300M Talker ile her bileşenin gecikmesini yazın.

2. Qwen2.5-Omni TMRoPE kullanır. Kullanıcın t=1s'de konuşmaya başladığı ve kameranın t=1.2s'de bir jest yakaladığı bir prompt için modelin ne看到rını tanımlayın.

3. Full-duplex desteği, modelin dinlerken ses üretmesini gerektirir. Bunu öğreten bir eğitim veri formatı önerin.

4. Moshi'nin makalesinin Bölüm 4'ünü okuyun. "İç monolog" ayrılmasını ve Thinker-Talker bölünmesini neden engellediğini tanımlayın.

5. Throughput bütçesini hesaplayın: Talker'ın 16kHz konuşmada 50 temel katman token/sn ile ayak uydurması için ne kadar hızlı token üretmesi gerekir?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Thinker | "Düşünme beyni" | Ne söyleneceğini üreten büyük metin üreten transformer |
| Talker | "Ses üreten ağız" | Thinker'ın metninden ayrık ses token'ları üreten küçük transformer |
| TTFAB | "Gecikme bütçesi" | Time-to-first-audio-byte: kullanıcı ses bitişinden ilk ses örneğine kadar |
| TMRoPE | "Zaman hizalı RoPE" | Görüntü, ses, metin genelinde mutlak zaman damgaları kullanan konum kodlaması |
| Half-duplex | "Sıra alma" | Kullanıcı ve model dönüşümlü; VAD sessizliği kullanıcının bitirdiğini algılar |
| Full-duplex | "Eşzamanlı" | Model aynı anda hem konuşabilir hem dinleyebilir; backchannel yeteneği |
| İç monolog | "Moshi ayrımı" | Düşünme akışı ve konuşma akışının iç içe geçtiği tek model tasarımı |

## Daha Fazla Kaynak

- [Xu ve ark. — Qwen2.5-Omni (arXiv:2503.20215)](https://arxiv.org/abs/2503.20215)
- [Qwen Takımı — Qwen3-Omni (arXiv:2509.17765)](https://arxiv.org/html/2509.17765v1)
- [Xie & Wu — Mini-Omni (arXiv:2408.16725)](https://arxiv.org/abs/2408.16725)
- [Défossez ve ark. — Moshi (arXiv:2410.00037)](https://arxiv.org/abs/2410.00037)
- [Zeng ve ark. — GLM-4-Voice (arXiv:2412.02612)](https://arxiv.org/abs/2412.02612)
