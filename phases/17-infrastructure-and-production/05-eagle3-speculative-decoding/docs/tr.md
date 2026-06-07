# Üretimde EAGLE-3 Spekülatif Decode

> Spekülatif decode, hızlı bir draft modelini hedef modelle eşleştirir. Draft K token önerir; hedef tek bir forward'da doğrular; kabul edilen token'lar bedavadır. 2026'da EAGLE-3 üretim kalitesinde varyanttır — draft head'ı ham token'lar yerine hedef modelin gizli durumları (hidden state) üzerinde eğitir, kabul oranı alpha'yı genel sohbette 0,6-0,8 bandına iter. Doğru soru "draft ne kadar hızlı" değil, "benim trafikte alpha ne?" Eğer alpha ~0,55'in altına düşerse, spekülatif decode yüksek eşzamanlılıkta net negatiftir çünkü her reddedilen draft ikinci bir hedef forward pass'a mal olur. Bu ders, önce alpha'yı ölçmeyi ve sonra bayrağı çevirmeyi öğretir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak kabul oranı simülatörü)
**Önkoşullar:** Faz 17 · 04 (vLLM Serving Internals), Faz 10 · 18 (Multi-Token Prediction)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Spekülatif decode'un üç neslini adlandırın ve EAGLE-3'ün EAGLE-2'den ve klasik draft modelden neyi değiştirdiğini açıklayın.
- Kabul oranı alpha'yı tanımlayın, alpha ve K'dan (draft uzunluğu) beklenen hızlanmayı hesaplayın ve hedef eşzamanlılığınız için başabaş alpha'yı belirleyin.
- Spekülatif decode'un vLLM 2026'da neden varsayılan olmayıp opt-in olduğunu ve alpha'yı ölçmeden açmanın neden bir üretim anti-örüntüsü olduğunu açıklayın.
- Bir ölçüm planı yazın: hangi kıyaslama, hangi istem dağılımı, hangi eşzamanlılık noktası, hangi metrik üzerinde geçit.

## Sorun

Decode bellek-bağlıdır (memory-bound). H100 üzerinde Llama 3.3 70B FP8 çalıştırırken, her decode edilmiş token ağırlıkların ~140 GB/s'sini okur ve bir token yayar. Decode sırasında GPU hesaplaması neredeyse boştadır — darboğaz HBM bant genişliğidir, matmul verimi değil.

Spekülatif decode boşluğu sömürür. Ucuz bir draft modeliyle K aday token üretin, sonra hedef modelden tüm K'yı tek bir forward pass'ta doğrulamasını isteyin. Doğrulanan her token etkili olarak bedavadır (hedefin zaten yapmak zorunda olduğu K'lı bir batch'in forward'una amorti edilir).

Klasik draft-model yaklaşımı, aynı ailenin daha küçük bir modelini kullanır (Llama 3.3 70B için Llama 3.2 1B taslak). Çalışır, ancak kabul oranı ortadır — daha küçük modelin dağılımı hedeften sapar. EAGLE, sonra EAGLE-2, sonra EAGLE-3, hafif bir draft head'ını doğrudan hedef modelin dahili durumları üzerinde eğitir, böylece draft'ın dağılımı hedefi çok daha yakından izler. Bu yüzden alpha draft-model ile 0,4'ten EAGLE-3 ile 0,6-0,8'e gider.

Yakalama: EAGLE-3, vLLM 2026'da opt-in'dir. `speculative_config` açıkça ayarlanmalıdır. Bayrak yok, hızlanma yok. Gerçek trafikte alpha'yı ölçmeden açan ekipler genellikle kuyruk gecikmesinin daha iyi değil daha kötü olduğunu görür.

## Kavram

### Spekülatif decode gerçekte ne satın alır

Spec decode olmadan, token başına maliyet bir hedef forward'tur. K draft uzunluğunda ve alpha kabul oranında spec decode ile, hedef forward başına beklenen token `1 + K * alpha`'dır. Hızlanma, `(1 + K * alpha) / (1 + epsilon)`'dur; burada epsilon draft-artı-doğrulama ek yüküdür. K=5, alpha=0,7 için: `(1 + 5*0,7) / (1 + 0,1) = 4,5 / 1,1 = 4,1x`. Gerçek dünya sayıları 2-3x çevresinde kümelenir çünkü alpha üretim trafikte nadiren o kadar yüksektir ve epsilon yüksek batch boyutunda büyür.

### Alpha neden tek önemli metriktir

Reddedilen token'lar yok olmaz — ilk reddedilen token için ikinci bir hedef forward zorlar. Alpha'nın 0,4'e düştüğü bir iş yükünde, draft ek yükü artı doğrulama artı yeniden atış ödersiniz. Yüksek eşzamanlılıkta (diyelim 256 eşzamanlı), decode batch'i "yalnız hedef" ile "doğrulamayla hedef" arasındaki bellek bant genişliği farkını daraltacak kadar zaten büyüktür. Çoğu 2026 donanımında 0,55 alpha'nın altında, spec decode net negatiftir.

Alpha iş yüküne göre değişir. ShareGPT-tarzı genel sohbette, ShareGPT üzerinde eğitilmiş EAGLE-3 0,6-0,8'e ulaşır. Alana özgü trafikte (kod, tıbbi, hukuki) genel veri üzerinde eğitilmiş draft head 0,4-0,6'ya düşer. Alana özgü bir draft head eğitmek alpha'yı kurtarır — hedef ince ayarına kıyasla hafif, hızlı bir eğitim işidir.

### EAGLE nesilleri bir bakışta

- **Klasik draft modeli**: aynı ailenin küçük modeli. Alpha 0,3-0,5. Altyapı basit — iki model yüklü, draft hedef forward başına K forward çalıştırır.
- **EAGLE-1 (2024)**: hedefin gizli durumları (son katman) üzerinde eğitilmiş tek draft head. Alpha ~0,5-0,6. Hedef üzerinde küçük parametre ek yükü.
- **EAGLE-2 (2025)**: uyarlanabilir draft uzunluğu ve ağaç-temelli draftlar (tek bir hedef geçişinde birden çok dalı doğrula). Alpha ~0,6-0,7. Daha karmaşık draft zamanlayıcı.
- **EAGLE-3 (2025-2026)**: draft head birden çok hedef katmanı (yalnızca son değil) üzerinde eğitilmiş, daha iyi hizalama. Genel sohbette alpha ~0,6-0,8.

### 2026 üretim reçetesi

1. Hedef modeli düz olarak gönderin. Hedef eşzamanlılıkta taban TTFT, ITL, verimi ölçün.
2. EAGLE-3 draft'ı vLLM `speculative_config` üzerinden etkinleştirin. Kıyaslamayı yeniden çalıştırın.
3. Kabul oranı alpha'yı loglayın. vLLM V1 bunu `spec_decode_metrics.accepted_tokens_per_request` olarak raporlar. Alpha'yı elde etmek için istenen draft uzunluğuna bölün.
4. Üretim trafik dağılımında alpha < 0,55 ise, spec decode'u devre dışı bırakın veya alana özgü bir EAGLE-3 draft eğitin.
5. Üretim eşzamanlılığında yeniden çalıştırın. P99 ITL'nin kötüleşmediğini doğrulayın.

### Üretim tuzağı: P99 kuyruğu

Ortalama ITL spec decode ile düşer. P50 değil, P99'u izleyin. Prediş ayarlamazsanız daha kötü olabilir. Reddedilen draftlar iki geçişli bir diziyi tetikler (draft + doğrulama-başarısız + yeniden atış). Tam batch altında, bu iki geçiş sıralıdır.

### EAGLE-3'ün zaten dağıtıldığı yerler

Google, 2025'te AI Overviews'da spekülatif decode'u dağıttı (aynı kalite, daha hızlı yanıt). vLLM V1, `speculative_config`'i belgelenen arayüz olarak gönderir; V1'deki N-gram GPU spekülatif decode chunked prefill ile uyumlu varyanttır. SGLang, prefix-ağırlıklı iş yükleri için önerilen draft yolu olarak EAGLE-3'ü destekler.

### Başabaş matematiği tek satırda

Beklenen hızlanma: `S(alpha, K) = (1 + K*alpha) / (1 + verify_overhead)`. `S = 1` ayarı, alpha için çözer: `alpha_breakeven = verify_overhead / K`. Tipik verify_overhead ~0,15 ve K=5 için: `alpha_breakeven = 0,03`. Ama bu ham decode matematiğidir. Yüksek eşzamanlılıkta doğrulama ek yükü artar ve decode batch'i zaten bellek okumalarını diziler arasında amorti eder, dolayısıyla etkin alpha_breakeven pratikte ~0,45-0,55'e tırmanır.

### Spekülatif decode ne zaman kullanılmaz

- Gecikmenin önemli olmadığı Batch-1 çevrimdışı üretim. Düz hedef kullanın.
- Çok kısa çıktılar (50 token altı). Draft ek yükü ve doğrulama maliyeti baskın.
- Alana eğitilmiş draft head'i olmayan uzmanlaşmış alanlar. Alpha çok düşük.
- vLLM v0.18.0 artı draft-model spec decode artı `--enable-chunked-prefill`. Bu kombinasyon derlenmez. Belgelenen istisna, V1'de N-gram GPU spec decode'dur.

## Kullan

`code/main.py`, bir dizi alpha değeri ve draft uzunluğu K boyunca spekülatif decode'lu ve decode'suz bir decode döngüsü simüle eder. Başabaş alpha'yı, ölçülen hızlanmayı ve kuyruk davranışını yazdırır. Spekülatif decode'un ödemeyi nerede bıraktığını tam olarak görmek için birkaç (alpha, K) kombinasyonunda çalıştırın.

## Üret

Bu ders `outputs/skill-eagle3-rollout.md` üretir. Hedef model, trafik dağılımı açıklaması ve eşzamanlılık hedefi verildiğinde, aşamalı bir EAGLE-3 devreye alma planı üretir — taban kıyaslaması, konfigürasyonu etkinleştirme, alpha'yı ölçme, alpha >= 0,55 üzerinde geçit, P99 ITL'yi izleme.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. K=5'te, 2x hızlanma için hangi alpha gerekir? 3x için? Bu, verify_overhead'e ne kadar duyarlı?
2. Üretim trafiğinin %70'i genel sohbet, %30'u kod olarak bölündüğünü hayal edin. Genel sohbet, ShareGPT üzerinde eğitilmiş EAGLE-3 ile alpha 0,7'ye ulaşır; kod, 0,4'e ulaşır. Karışık alpha nedir ve spec decode net-pozitif mi?
3. vLLM `speculative_config` dokümantasyonunu okuyun. Üç modu (draft model, EAGLE, N-gram) adlandırın ve hangisinin chunked prefill ile uyumlu olduğunu belirtin.
4. EAGLE-3'ü etkinleştirdikten sonra ortalama ITL'nin %25 düştüğünü ancak P99 ITL'nin %15 arttığını görüyorsunuz. Tanı koyun ve bir azaltma önerin.
5. Llama 3.3 70B için EAGLE-3 draft head'inin bellek maliyetini hesaplayın. Llama 3.2 1B'yi klasik draft olarak çalıştırmakla nasıl karşılaştırılır?

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Spekülatif decode | "draft artı doğrulama" | K token'ı ucuz bir modelle öner, tüm K'yı tek bir hedef forward'ta doğrula |
| Kabul oranı alpha | "spec kabul oranı" | Draft token'larının hedef tarafından kabul edilen kesri; tek önemli metrik |
| Draft uzunluğu K | "spec k" | Draft'ın hedef forward başına kaç token önerdiği; tipik 4-8 |
| Doğrulama ek yükü epsilon | "spec ek yükü" | Düz hedef forward'a kıyasla doğrulama-ve-yeniden atış ekstra maliyeti; batch ile büyür |
| EAGLE-3 | "en son EAGLE" | 2025-2026 varyantı; draft head'ı birden çok hedef katmanı üzerinde eğitir; genel sohbette alpha 0,6-0,8 |
| `speculative_config` | "vLLM spec konfig" | vLLM V1'deki açık opt-in; varsayılan yok, hızlanma yok demektir |
| N-gram spec decode | "N-gram draft" | İstemdeki N-gram aramalarını kullanan GPU tarafı draft; chunked-prefill-uyumlu |
| Başabaş alpha | "no-op alpha" | Spec decode'un sıfır hızlanma verdiği alpha; üretim eşzamanlılığında bunu izleyin |
| Reddedilen-draft iki geçiş | "yeniden atış maliyeti" | Draftlar reddedildiğinde iki hedef forward; P99 kuyruğunu yönlendirir |

## İleri Okuma

- [vLLM — Speculative Decoding docs](https://docs.vllm.ai/en/latest/features/spec_decode/) — `speculative_config` ve V1'de chunked-prefill uyumluluğu üzerine yetkili kaynak.
- [vLLM Speculative Config API](https://docs.vllm.ai/en/latest/api/vllm/config/speculative/) — tam alan kümesi.
- [EAGLE paper (arXiv:2401.15077)](https://arxiv.org/abs/2401.15077) — orijinal EAGLE draft-head formülasyonu.
- [EAGLE-2 paper (arXiv:2406.16858)](https://arxiv.org/abs/2406.16858) — uyarlanabilir draftlar ve ağaçlar.
- [UC Berkeley EECS-2025-224](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2025/EECS-2025-224.html) — spekülatif decode ile verimli LLM sistemi.
- [BentoML — Speculative Decoding](https://bentoml.com/llm/inference-optimization/speculative-decoding) — üretim devreye alma kontrol listesi.
