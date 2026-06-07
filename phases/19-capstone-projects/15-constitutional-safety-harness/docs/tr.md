# Capstone 15 — Anayasal Güvenlik Çatısı (Harness) + Red-Team Atış Poligonu

> Anthropic'in Anayasal Sınıflandırıcıları, Meta'nın Llama Guard 4'ü, Google'ın ShieldGemma-2'si, NVIDIA'nın Nemotron 3 İçerik Güvenliği ve çok dilli kapsam için X-Guard, 2026 güvenlik-sınıflandırıcı yığınını tanımladı. garak, PyRIT, NVIDIA Aegis ve promptfoo standart düşmanca değerlendirme araçları oldu. NeMo Guardrails v0.12 bunları bir üretim boru hattına bağlar. Bu capstone tüm bunları birbirine bağlar: bir hedef uygulama etrafında katmanlı bir güvenlik çatısı, 6+ saldırı ailesi çalıştıran otonom bir red-team ajanı ve ölçülebilir bir zararsızlık deltası üreten anayasal bir öz-eleştiri çalıştırması.

**Type:** Capstone
**Languages:** Python (güvenlik boru hattı, red team), YAML (politika konfigürasyonları)
**Prerequisites:** Phase 10 (LLMs from scratch), Phase 11 (LLM engineering), Phase 13 (tools), Phase 14 (agents), Phase 18 (ethics, safety, alignment)
**Phases exercised:** P10 · P11 · P13 · P14 · P18
**Time:** 25 saat

## Problem

2026'da LLM güvenliğinin sınırı, sınıflandırıcıların çalışıp çalışmadığı (kabaca çalışıyor) değil, fazla-reddetmeden veya bariz boşluklar bırakmadan bir üretim uygulamasının etrafına nasıl doğru bir şekilde oluşturulacağıdır. Llama Guard 4 İngilizce politika ihlallerini yönetir. X-Guard (132 dil) çok dilli jailbreak'leri yönetir. ShieldGemma-2 görüntü-tabanlı istem enjeksiyonunu yakalar. NVIDIA Nemotron 3 İçerik Güvenliği kurumsal kategorileri kapsar. Anthropic'in Anayasal Sınıflandırıcıları, servis etmekten çok eğitim sırasında kullanılan ayrı bir yaklaşımdır.

Saldırı evrimi de önemlidir. PAIR ve TAP jailbreak keşfini otomatikleştirir. GCG gradyan-tabanlı sonek saldırıları çalıştırır. Çok-dönüşlü ve kod-değiştirme saldırıları ajan belleğini istismar eder. Dağıtılan her LLM'nin bir red-team atış poligonuna ihtiyacı vardır — garak ve PyRIT kanonik sürücülerdir — artı belgelenmiş azaltmalar ve CVSS-puanlı bulgular.

Bir hedef uygulamayı (ya 8B talimat-ayarlı bir model ya da diğer capstone'lardan birinin RAG sohbet botları) sertleştirecek, 6+ saldırı ailesine karşı çalıştıracak ve önce/sonra bir zararsızlık ölçümü üreteceksiniz.

## Concept

Güvenlik boru hattı beş katmandır. **Girdi temizleme**: sıfır-genişlik karakterleri çıkar, base64/rot13 çöz, Unicode normalleştir. **Politika katmanı**: NeMo Guardrails v0.12 rayları (alan-dışı, toksiklik, PII çıkarma). **Sınıflandırıcı kapısı**: Girdi üzerinde Llama Guard 4, İngilizce-dışı üzerinde X-Guard, görüntü girdileri üzerinde ShieldGemma-2. **Model**: hedef LLM. **Çıktı süzgeci**: Çıktı üzerinde Llama Guard 4, Presidio PII temizleme, uygulanabilir olduğu yerde alıntı zorunluluğu. **HITL katmanı**: Yüksek-riskli olarak işaretlenen çıktılar bir Slack kuyruğuna gider.

Red-team atış poligonu bir zamanlayıcıda çalışır. PAIR ve TAP otonom olarak jailbreak'leri keşfeder. GCG gradyan-tabanlı sonek saldırıları çalıştırır. ASCII / base64 / rot13 kodlama saldırıları. Çok-dönüşlü saldırılar (persona benimseme, bellek istismarı). Kod-değiştirme saldırıları (İngilizce'yi Svahili veya Tayca ile karıştırır). Her çalıştırma, CVSS puanlaması ve açıklama zaman çizelgesi ile yapılandırılmış bir bulgular dosyası üretir.

Anayasal-öz-eleştiri çalıştırması eğitim-zamanı bir müdahaledir. 1k zararlı-deneme istemi alın, modelin bir yanıt taslağı oluşturmasını sağlayın, yazılı bir anayasaya (zarar verme, kanıt alıntıla, yasadışı istekleri reddet) göre eleştirin ve eleştiri döngüsünde yeniden eğitin. Holdout bir değerlendirme üzerinde önce/sonra zararsızlık deltasını ölçün.

## Architecture

```
request (text / image / multilingual)
 |
 v
input sanitize (strip zero-width, decode, normalize)
 |
 v
NeMo Guardrails v0.12 rails (off-domain, policy)
 |
 v
classifier gate:
 Llama Guard 4 (English)
 X-Guard (multilingual, 132 langs)
 ShieldGemma-2 (image prompts)
 Nemotron 3 Content Safety (enterprise)
 |
 v (allowed)
target LLM
 |
 v
output filter: Llama Guard 4 + Presidio PII + citation check
 |
 v
HITL tier for flagged outputs

parallel:
 red-team scheduler
 -> garak (classic attacks)
 -> PyRIT (orchestrated red team)
 -> autonomous jailbreak agent (PAIR + TAP)
 -> GCG suffix attacks
 -> multilingual / code-switch
 -> multi-turn persona adoption

output: CVSS-scored findings + disclosure timeline + before/after harmlessness delta
```

#### Açıklama

Bu mimari hedef uygulamayı çevreleyen beş katmanlı güvenlik boru hattını gösterir. Bir istek (metin, görüntü veya çok dilli) ilk olarak sıfır-genişlik karakterler temizlenir ve kodlama çözülür. NeMo Guardrails v0.12 rayları alan-dışı ve politika ihlali sorgularını filtreler. Sınıflandırıcı kapısı dile ve girdi türüne göre uygun modeli seçer: İngilizce için Llama Guard 4, çok dilli için X-Guard, görüntü istemleri için ShieldGemma-2, kurumsal kategoriler için Nemotron 3. Tüm kapılardan geçen istekler hedef LLM'ye ulaşır. Çıktı tekrar sınıflandırılır, PII temizlenir ve alıntı kontrolünden geçirilir. Yüksek-riskli olarak işaretlenenler HITL kuyruğuna yönlendirilir. Paralel olarak, red-team zamanlayıcısı garak, PyRIT, PAIR/TAP ajanları, GCG sonek, çok dilli ve çok-dönüşlü saldırganları çalıştırır. Çıktılar CVSS-puanlı bulgular, açıklama zaman çizelgesi ve zararsızlık deltasıdır.

## Stack

- Güvenlik sınıflandırıcıları: Llama Guard 4, ShieldGemma-2, NVIDIA Nemotron 3 İçerik Güvenliği, X-Guard
- Koruma rayı çatısı: NeMo Guardrails v0.12 + OPA
- Red-team sürücüleri: garak (NVIDIA), PyRIT (Microsoft Azure), NVIDIA Aegis, promptfoo
- Jailbreak ajanları: PAIR (Chao ve ark., 2023), Tree-of-Attacks (TAP), GCG sonek
- Anayasal eğitim: Anthropic tarzı öz-eleştiri döngüsü + eleştiriler üzerinde SFT
- PII temizleme: Presidio
- Hedef: 8B talimat-ayarlı bir model veya diğer capstone'ların RAG sohbet botlarından biri

## Build It

1. **Hedef kurulumu.** vLLM üzerinde 8B talimat-ayarlı bir model kurun (veya başka bir capstone'tan bir RAG sohbet botunu yeniden kullanın). Bu test altındaki uygulama.

2. **Güvenlik boru hattı sarmalama.** Beş katmanlı boru hattını hedefin etrafına bağlayın. Her katmanın bireysel olarak gözlemlenebilir olduğunu doğrulayın (Langfuse'ta katman başına bir span).

3. **Sınıflandırıcı kapsamı.** Llama Guard 4, X-Guard (çok dilli), ShieldGemma-2 (görüntü) yükleyin. Temel çizgileri kurmak için her birini küçük etiketli bir küme üzerinde çalıştırın.

4. **Red-team zamanlayıcısı.** garak, PyRIT, bir PAIR ajanı, bir TAP ajanı, bir GCG çalıştırıcısı, çok-dönüşlü bir saldırgan ve kod-değiştirme bir saldırgan zamanlayın. Her biri ayrı bir kuyrukta çalışır.

5. **Saldırı paketi.** Altı saldırı ailesi: (1) PAIR otomatik jailbreak, (2) TAP ağaç-saldırıları, (3) GCG gradyan sonek, (4) ASCII / base64 / rot13 kodlama, (5) çok-dönüşlü persona, (6) çok dilli kod-değiştirme. Aile başına başarı oranını raporlayın.

6. **Anayasal öz-eleştiri.** 1k zararlı-deneme istemini bir araya getirin. Her biri için, hedef bir yanıt taslağı oluşturur. Bir eleştirmen LLM, yazılı bir anayasaya ("zarar verme," "kanıt alıntıla," "yasadışı istekleri reddet") göre puanlar. Eleştirmenin itiraz ettiği istemler yeniden yazılır; hedef, eleştiri-iyileştirilmiş çiftler üzerinde ince ayar yapar. Holdout bir değerlendirme üzerinde önce/sonra zararsızlığı ölçün.

7. **Fazla-reddetme ölçümü.** İyi huylu bir istem paketi (ör. XSTest) üzerinde yanlış-pozitif oranını izleyin. Hedef, iyi huylu sorularda yardımcı kalmalıdır.

8. **CVSS puanlaması.** Başarılı her jailbreak için, CVSS 4.0 üzerinde puanlayın (saldırı vektörü, karmaşıklık, etki). Bir açıklama zaman çizelgesi ve azaltma planı üretin.

9. **Atış poligonu otomasyonu.** Yukarıdakilerin tümü bir cron üzerinde çalışır; bulgular bir kuyruğa yazılır; fazla-reddetme regresyon uyarıları Slack'e ateşlenir.

## Use It

```
$ safety probe --model=target --family=PAIR --budget=50
[attacker] PAIR agent running on target
[attack] attempt 1/50: disguise query as academic research ... blocked
[attack] attempt 2/50: appeal to roleplay ... blocked
[attack] attempt 3/50: chain-of-thought coax ... SUCCEEDED
[finding] CVSS 4.8 medium: roleplay bypass on target
[range] 7 successes out of 50 (14% success rate)
```

#### Açıklama

Bu örnek PAIR saldırı ailesinin tek bir çalıştırmasını gösterir. PAIR ajanı hedef modele 50 deneme yapar. İlk ikisi ("akademik araştırma kisvesi" ve "rol yapma appeali") sınıflandırıcı kapıları tarafından engellenir. Üçüncüsü ("düşünce zinciri ikna") başarılı olur. Sistem bir CVSS 4.8 orta bulgu oluşturur ve 50 denemeden 7'sinin (%14) başarılı olduğunu raporlar. Operatör bu bulguyu inceler, gerekirse ek bir koruma kuralı ekler ve bir sonraki çalıştırmada başarı oranını tekrar ölçer.

## Ship It

`outputs/skill-safety-harness.md` teslim edilen şeydir. Üretim-düzeyinde katmanlı bir güvenlik boru hattı artı önce/sonra zararsızlık deltalarıyla tekrarlanabilir bir red-team atış poligonu.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Saldırı-yüzey kapsamı | 6+ saldırı ailesi çalıştırıldı, 2+ dil |
| 20 | Doğru-pozitif / yanlış-pozitif takası | XSTest iyi huylu geçme oranına karşı saldırı engelleme oranı |
| 20 | Öz-eleştiri deltası | Holdout değerlendirmede önce/sonra zararsızlık |
| 20 | Dokümantasyon ve açıklama | Zaman çizelgesi ile CVSS-puanlı bulgular |
| 15 | Otomasyon ve tekrarlanabilirlik | Her şey uyarılarla cron üzerinde çalışır |
| **100** | | |

## Exercises

1. Bir RAG sohbet botu üzerinde garak'ın istem-enjeksiyon eklentisini çalıştırın ve çıktı süzgeci katmanıyla vs olmadan saldırı başarı oranını karşılaştırın.

2. Yedinci bir saldırı ailesi ekleyin: geri getirilen belgeler aracılığıyla dolaylı istem enjeksiyonu. Gerekli ekstra savunmayı ölçün.

3. Bir "yardımla-reddet" modu uygulayın: koruma rayı engellediğinde, hedef düz bir reddetme yerine daha güvenli ilgili bir yanıt sunar. XSTest deltasını ölçün.

4. Çok dilli kapsam boşluğu: X-Guard'ın düşük performans gösterdiği bir dil bulun. Onu hedefleyen bir ince-ayar veri kümesi önerin.

5. Anayasal öz-eleştiriyi 30B bir modelde çalıştırın ve deltanın ölçeklenip ölçeklenmediğini ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Katmanlı güvenlik | "Derinlik savunması" | Girdi, kapı, çıktı, HITL'de birden çok koruma rayı |
| Llama Guard 4 | "Meta'nın güvenlik sınıflandırıcısı" | 2026 referans girdi/çıktı içerik sınıflandırıcısı |
| PAIR | "Jailbreak ajanı" | LLM-tarafından yönlendirilen jailbreak keşfi üzerine makale (Chao ve ark.) |
| TAP | "Saldırı ağacı" | PAIR'ın ağaç-arama varyantı |
| GCG | "Açgözlü koordinat gradyanı" | Gradyan-tabanlı düşmanca sonek saldırısı |
| Anayasal öz-eleştiri | "Anthropic tarzı eğitim" | Hedef taslak -> eleştirmen puan -> yeniden yaz -> yeniden eğit |
| XSTest | "İyi huylu sonda seti" | Fazla-reddetme regresyonu için kıyaslama |
| CVSS 4.0 | "Önem derecesi puanı" | Güvenlik bulguları için standart güvenlik açığı puanlaması |

## Further Reading

- [Anthropic Constitutional Classifiers](https://www.anthropic.com/research/constitutional-classifiers) — eğitim-zamanı referansı
- [Meta Llama Guard 4](https://ai.meta.com/research/publications/llama-guard-4/) — 2026 girdi/çıktı sınıflandırıcısı
- [Google ShieldGemma-2](https://huggingface.co/google/shieldgemma-2b) — görüntü + çok modlu güvenlik
- [NVIDIA Nemotron 3 Content Safety](https://developer.nvidia.com/blog/building-nvidia-nemotron-3-agents-for-reasoning-multimodal-rag-voice-and-safety/) — kurumsal referans
- [X-Guard (arXiv:2504.08848)](https://arxiv.org/abs/2504.08848) — 132-dil çok dilli güvenlik
- [garak](https://github.com/NVIDIA/garak) — NVIDIA red-team araç takımı
- [PyRIT](https://github.com/Azure/PyRIT) — Microsoft red-team çatısı
- [NeMo Guardrails v0.12](https://docs.nvidia.com/nemo-guardrails/) — ray çatısı
- [PAIR (arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — jailbreak ajan makalesi
