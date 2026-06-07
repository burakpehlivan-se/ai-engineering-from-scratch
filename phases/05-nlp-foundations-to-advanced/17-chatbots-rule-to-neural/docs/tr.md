# Sohbet Botları — Kurallardan Sinir Ağlarına ve LLM Ajanlarına

> ELIZA kalıp eşleştirmeyle yanıt verdi. DialogFlow niyetleri eşledi. GPT ağırlıklardan cevapladı. Claude araçları çalıştırdı ve doğruladı. Her dönem bir öncekinin en büyük başarısızlığını çözdü.

**Tür:** Öğren
**Diller:** Python
**Ön koşullar:** Faz 5 · 13 (Soru-Cevap), Faz 5 · 14 (Bilgi Getirme)
**Süre:** ~75 dakika

## Problem

Bir kullanıcı "Uçuşumu değiştirmek istiyorum" der. Sistem ne istediğini, hangi bilginin eksik olduğunu, bunu nasıl elde edeceğini ve eylemi nasıl tamamlayacağını anlamalıdır. Ardından kullanıcı "Peki ya iptal edersem?" der ve sistem bağlamı hatırlamalı, görevi değiştirmeli ve durumu korumalıdır.

Bir makine öğrenmesi sistemi için konuşma zordur. Girdi serbest formdadır. Çıktı birçok tur boyunca tutarlı olmalıdır. Sistem dünyanın üzerine eylemde bulunabilir (uçuş değiştirme, kart tahsil etme). Her yanlış adım kullanıcı tarafından görünürdür.

Sohbet botu mimarileri dört paradigma üzerinden döngüsel olarak ilerlemiş, her biri bir öncekinin çok gözle görülür biçimde başarısız olmasıyla tanıtılmıştır. Bu ders bunları sırayla inceler. 2026 production manzarası son ikisinin bir karışımıdır.

## Kavram

![Sohbet botu evrimi: kurallar → retrieval → sinir ağları → ajan](../assets/chatbot.svg)

**Kurallara dayalı (ELIZA, AIML, DialogFlow).** El yazısı kalıplar kullanıcı girişini eşler ve yanıtlar üretir. Niyet sınıflandırıcıları önceden tanımlanmış akışlara yönlendirir. Slot doldurma (slot-filling) durum makineleri gerekli bilgileri toplar. Tasarlandığı dar kapsam içinde mükemmel çalışır. Dışarısında anında başarısız olur. Halüsinasyona toleratedılmayan güvenlik-kritik alanlarda (bankacılık kimlik doğrulama, havayolu rezervasyonu) hâlâ kullanılır.

**Retrieval tabanlı.** SSS benzeri bir sistem. Her (ifade, yanıt) çiftini kodlayın. Çalışma zamanında, kullanıcının mesajını kodlayın ve en yakın depolanan yanıtı getirin. Zendesk'in klasik "benzer makaleler" özelliğini düşünün. Parafrazları kurallardan daha iyi ele alır. Üretim olmadığı için halüsinasyon yoktur.

**Sinir ağı tabanlı (seq2seq).** Konuşma günlükleri üzerinde eğitilmiş encoder-decoder. Yanıtları sıfırdan üretir. Akıcıdır ancak genel çıktılar ("Bilmiyorum") ve olgusal sapmaya eğilimlidir. Hiçbir zaman güvenilir şekilde konu üzerinde kalamaz. Google, Facebook ve Microsoft'un 2016-2019 döneminde heves kırıcı sohbet botlarına sahip olmasının nedeni budur.

**LLM ajanları (agent).** Planlama yapan, araçları çağıran ve sonuçları doğrulayan bir döngüye sarılmış bir dil modeli. Uzun bir prompt'a sahip bir sohbet botu değil. Bir agent döngüsü: planla → aracı çağır → sonucu gözlemle → bir sonraki adıma karar ver. Retrieval-öncelikli temelleme (RAG) halüsinasyon yapmasını engeller. Araç çağrısı gerçekten bir şeyler yapmasını sağlar. Bu 2026 mimarisidir.

Dört paradigma sıralı değiştirme değildir. 2026 production sohbet botu dördünden de geçer: kimlik doğrulama ve yıkıcı eylemler için kurallara dayalı, SSS için retrieval, doğal ifadeler için sinir ağı üretimi, belirsiz açık uçlu sorgular için LLM ajanı.

## İnşa Et

### Adım 1: kurallara dayalı kalıp eşleştirme

```python
import re


class RulePattern:
 def __init__(self, pattern, response_template):
 self.regex = re.compile(pattern, re. IGNORECASE)
 self.template = response_template


PATTERNS = [
 RulePattern(r"my name is (\w+)", "Nice to meet you, {0}."),
 RulePattern(r"i (need|want) (.+)", "Why do you {0} {1}?"),
 RulePattern(r"i feel (.+)", "Why do you feel {0}?"),
 RulePattern(r"(.*)", "Tell me more about that."),
]


def rule_based_respond(user_input):
 for pattern in PATTERNS:
 m = pattern.regex.match(user_input.strip())
 if m:
 return pattern.template.format(*m.groups())
 return "I don't understand."
```

#### Açıklama
20 satırlık bir ELIZA. Yansıtma hilesi ("Üzgünüm" → "Neden üzgünsün?") Weizenbaum 1966'dan klasik psikoterapist demosudur. Hâlâ öğreticidir.

### Adım 2: retrieval tabanlı (SSS)

Bu gösterim parçası `pip install sentence-transformers` gerektirir (torch'u çeker). Bu derste çalışan `code/main.py` dosyası dış bağımlılık olmadan çalışabilmesi için stdlib Jaccard benzerliği kullanır.

```python
from sentence_transformers import SentenceTransformer
import numpy as np


FAQ = [
 ("how do i reset my password", "Go to Settings > Security > Reset Password."),
 ("how do i cancel my order", "Go to Orders, find the order, click Cancel."),
 ("what is your return policy", "30-day returns on unused items, original packaging."),
]


encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
faq_questions = [q for q, _ in FAQ]
faq_embeddings = encoder.encode(faq_questions, normalize_embeddings=True)


def faq_respond(user_input, threshold=0.5):
 q_emb = encoder.encode([user_input], normalize_embeddings=True)[0]
 sims = faq_embeddings @ q_emb
 best = int(np.argmax(sims))
 if sims[best] < threshold:
 return None
 return FAQ[best][1]
```

#### Açıklama
Eşik tabanlı reddetme temel tasarım kararıdır. En iyi eşleşme yeterince yakın değilse `None` dönün ve sistemi yukarı aktarmasına izin verin.

### Adım 3: sinir ağı üretimi (baseline)

Küçük bir instruction-tuned encoder-decoder (FLAN-T5) veya fine-tune edilmiş konuşma modeli kullanın. 2026'da tek başına production'da kullanılamaz (çelişki, konu dışı kayma, olgusal saçmalık), ancak doğal ifadeler için hibrit sistemlerin içinde gönderilir. DialgPT tarzı sadece decoder modelleri tutarlı yanıtlar üretmek için açık tür ayracı ve EOS işleme gerektirir; FLAN-T5 text2text pipeline'ı öğretici örnek için kutudan çıkar.

```python
from transformers import pipeline

chatbot = pipeline("text2text-generation", model="google/flan-t5-small")

response = chatbot("Respond politely to: Hi there!", max_new_tokens=40)
print(response[0]["generated_text"])
```

#### Açıklama
FLAN-T5, instruction-tuning ile metin-girdi → metin-çıkıtlı pipeline'larda çalışır. Küçük model (60M) hızlıdır ancak kalitesi düşüktür; production için büyük bir instruction-tuned model gereklidir.

### Adım 4: LLM ajan döngüsü

2026 production şekli:

```python
def agent_loop(user_message, tools, llm, max_steps=5):
 history = [{"role": "user", "content": user_message}]
 for _ in range(max_steps):
 response = llm(history, tools=tools)
 tool_call = response.get("tool_call")
 if tool_call:
 tool_name = tool_call.get("name")
 args = tool_call.get("arguments")
 if not isinstance(tool_name, str) or tool_name not in tools:
 history.append({"role": "assistant", "tool_call": tool_call})
 history.append({"role": "tool", "name": str(tool_name), "content": f"error: unknown tool {tool_name!r}"})
 continue
 if not isinstance(args, dict):
 history.append({"role": "assistant", "tool_call": tool_call})
 history.append({"role": "tool", "name": tool_name, "content": f"error: arguments must be a dict, got {type(args).__name__}"})
 continue
 fn = tools[tool_name]
 result = fn(**args)
 history.append({"role": "assistant", "tool_call": tool_call})
 history.append({"role": "tool", "name": tool_name, "content": result})
 else:
 return response["content"]
 return "I could not complete the task in the step budget."
```

#### Açıklama
Üç önemli nokta. Araçlar (tool), LLM'ın çağırabileceği fonksiyonlardır. Döngü, LLM bir araç çağrısı yerine nihai cevap döndürdüğünde sona erer. Adım bütçesi (step budget) belirsiz görevlerde sonsuz döngüleri engeller.

Gerçek production ekleri: retrieval-öncelikli temelleme (her LLM çağrısından önce ilgili belgeleri enjekte etme), koruma bariyerleri (guardrails, onay olmadan yıkıcı eylemleri reddetme), gözlemlenebilirlik (her adımı loglama) ve değerlendirmeler (ajan davranışının spec'te kalmasını sağlayan otomatik kontroller).

### Adım 5: hibrit yönlendirme

```python
def hybrid_chat(user_input):
 if is_destructive_action(user_input):
 return structured_flow(user_input)

 faq_answer = faq_respond(user_input, threshold=0.6)
 if faq_answer:
 return faq_answer

 return agent_loop(user_input, tools, llm)


def is_destructive_action(text):
 danger_words = ["delete", "cancel", "charge", "refund", "transfer"]
 return any(w in text.lower() for w in danger_words)
```

#### Açıklama
Kalıp: yıkıcı her şey için deterministik kurallar, önceden hazırlanmış SSS'ler için retrieval, diğer her şey için LLM ajanları. Bu, 2026 müşteri destek sistemlerinde gönderilen şeydir.

## Kullan

2026 stacki:

| Kullanım durumu | Mimari |
|---------|---------------|
| Rezervasyon, ödeme, kimlik doğrulama | Kurallara dayalı durum makineleri + slot doldurma |
| Müşteri destek SSS'leri | Özenle hazırlanmış yanıtlar üzerinde retrieval |
| Açık uçlu yardım sohbeti | RAG + araç çağrılarıyla LLM ajanı |
| Dahili araçlar / IDE asistanları | Araç çağrılarıyla LLM ajanı (arama, okuma, yazma) |
|Arkadaş / karakter sohbet botları | Persona system prompt'lu fine-tune LLM, bilgi üzerinde retrieval |

Production'da her zaman hibrit yönlendirme kullanın. Tek bir mimari her isteği iyi ele almaz. Yönlendirme katmanı genellikle küçük bir niyet sınıflandırıcısıdır.

## Hâlâ gönderilen başarısızlık modları

- **Kendinden emin uydurma.** LLM ajanı yapmadığı bir eylemi tamamladığını iddia eder. Hafifletme: sonuçları doğrulayın, araç çağrılarını loglayın, LLM'ın başarılı bir araç dönüşü olmadan bir şey yaptığını iddia etmesine asla izin verin.
- **Prompt enjeksiyonu (prompt injection).** Kullanıcı system prompt'u geçersiz kılan metin girer. OWASP Top 10 for LLM Applications 2025'te LLM01 olarak sıralanmıştır. İki türü var: doğrudan enjeksiyon (sohbete yapıştırılan) ve dolaylı enjeksiyon (ajanın okuduğu belgelerde, e-postalarda veya araç çıktılarında gizli).

 Saldırı oranları senaryoya göre değişir. Ölçülen başarı oranları, genel araç kullanımı ve kodlama benchmark'larında öncü modeller arasında ~%0.5-8.5 arasında değişir. Belirli yüksek riskli kurulumlar (kodlama ajanlarına yönelik uyarlanabilir saldırılar, kırılgan orkestrasyon) ~%84'e ulaşmıştır. Production CVE'leri EchoLeak'i (CVE-2025-32711, CVSS 9.3) içerir — Microsoft 365 Copilot'ta saldırgan kontrollü e-posta ile tetiklenen sıfır tıklama veri sızıntısı kusuru.

 Hafifletme: kullanıcı girişini döngü boyunca güvensiz kabul edin; araç çağrısından önce temizleyin; araç çıktılarını ana prompt'tan izole edin; Planla-Doğrula-Gerçekleştir (PVE) kalıbını kullanın (ajan önce planlar, ardından gerçekleştirme önce her eylemi plana karşı doğrular — bu, araç sonuçlarının yeni planlanmamış eylemler enjekte etmesini engeller); yıkıcı eylemler için kullanıcı onayı gerektirin; araç kapsamlarına asgari ayrıcalık (least-privilege) uygulayın.

 Hiçbir mühendislik düzeyi bu riski tamamen ortadan kaldırmaz. Çalışma zamanı savunma katmanları (LLM Guard, izin listesi doğrulama, anormal algılama) gereklidir.
- **Kapsam kayması (scope creep).** Araç çağrısı yandan ilişkili bilgi döndürdüğünde ajan görevden sapar. Hafifletme: dar araç sözleşmeleri; system prompt'u odaklı tutun; görev dışı oranı için değerlendirmeler ekleyin.
- **Sonsuz döngüler.** Aynı aracı tekrar tekrar çağırır. Hafifletme: adım bütçesi, araç çağrısı tekrar kaldırma, "ilerleme kaydediyor muyuz?" üzerine LLM judge.
- **Bağlam penceresi tükenmesi (context window exhaustion).** Uzun konuşmalar en erken turları bağlam dışına iter. Hafifletme: daha eski turları özetleyin, benzerliğe göre ilgili geçmiş turları getirin veya uzun bağlam modeli kullanın.

## Ürün Olarak Kullan

`outputs/skill-chatbot-architect.md` olarak kaydedin:

```markdown
---
name: chatbot-architect
description: Design a chatbot stack for a given use case.
version: 1.0.0
phase: 5
lesson: 17
tags: [nlp, agents, chatbot]
---

Given a product context (user need, compliance constraints, available tools, data volume), output:

1. Architecture. Rule-based, retrieval, neural, LLM agent, or hybrid (specify which paths go where).
2. LLM choice if applicable. Name the model family (Claude, GPT-4, Llama-3.1, Mixtral). Match to tool-use quality and cost.
3. Grounding strategy. RAG sources, retrieval method (see lesson 14), tool contracts.
4. Evaluation plan. Task success rate, tool-call correctness, off-task rate, hallucination rate on held-out dialogs.

Refuse to recommend a pure-LLM agent for any destructive action (payments, account deletion, data modification) without a structured confirmation flow. Refuse to skip the prompt-injection audit if the agent has write access to anything.
```

#### Açıklama
Bu, verilen ürün bağlamında bir sohbet botu stacki tasarlayan bir skill tanımıdır.

## Alıştırmalar

1. **Kolay.** Yukarıdaki kurallara dayalı yanıtlama sistemini bir kahve dükkanı sipariş botu için 10 kalıpla uygulayın. Uç durumları test edin: çift siparişler, değişiklikler, iptal, belirsiz niyet.
2. **Orta.** Hibrit SSS + LLM yedeklemeli bir sistem kurun. Bir SaaS ürünü için 50 önceden hazırlanmış SSS girişi, belge sitesi üzerinde retrieval ile LLM yedekleme. 100 gerçek destek sorusu üzerinde reddetme oranını ve doğruluğu ölçün.
3. **Zor.** Yukarıdaki ajan döngüsünü üç araçla (search, read-user-data, send-email) uygulayın. Prompt enjeksiyonu denemeleri dahil 50 test senaryosuyla bir değerlendirme çalıştırın. Görev dışı oranını, başarısız görev oranını ve enjeksiyon başarılarını raporlayın.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Niyet (Intent) | Kullanıcının istediği | Kategorik etiket (book_flight, reset_password). Bir işleyiciye yönlendirilir. |
| Slot | Bir bilgi parçası | Botun gerektiği parametre (tarih, hedef). Slot doldurma, isteme dizisidir. |
| RAG | Retrieval artı üretim | İlgili belgeleri getirin, ardından LLM yanıtını temellendirin. |
| Araç çağrısı (Tool call) | Fonksiyon çağrısı | LLM, ad + argümanlarla yapılandırılmış bir çağrío üretir. Çalışma zamanı çalıştırır, sonuç döner. |
| Agent döngüsü | Planla, eyle, doğrula | LLM çağrısı ile araç çağrısı aralıklı olarak çalışan, görev tamamlanana kadar süren kontrolcü. |
| Prompt enjeksiyonu | Kullanıcı prompt'a saldırı | System prompt'u geçersiz kılmaya çalışan kötü amaçlı girdi. |

## İleri Okuma

- [Weizenbaum (1966). ELIZA — A Computer Program For the Study of Natural Language Communication](https://web.stanford.edu/class/cs124/p36-weizenabaum.pdf) — orijinal kurallara dayalı sohbet botu makalesi.
- [Thoppilan et al. (2022). LaMDA: Language Models for Dialog Applications](https://arxiv.org/abs/2201.08239) — Google'ın geç sinir ağı sohbet botu makalesi, LLM ajanlarının hâkimiyetinden hemen önce.
- [Yao et al. (2022). ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629) — agent döngüsü kalıbına isim veren makale.
- [Anthropic's guide on building effective agents](https://www.anthropic.com/research/building-effective-agents) — 2024 production rehberi, 2026'da hâlâ geçerli.
- [Greshake et al. (2023). Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection](https://arxiv.org/abs/2302.12173) — prompt enjeksiyonu makalesi.
- [OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — prompt enjeksiyonunu üst düzey güvenlik endişesi yapan sıralama.
- [AWS — Securing Amazon Bedrock Agents against Indirect Prompt Injections](https://aws.amazon.com/blogs/machine-learning/securing-amazon-bedrock-agents-a-guide-to-safeguarding-against-implicit-prompt-injections/) — Plan-Doğrula-Gerçekleştir ve kullanıcı onayı akışları dahil pratik orkestrasyon katmanı savunmaları.
- [EchoLeak (CVE-2025-32711)](https://www.vectra.ai/topics/prompt-injection) — dolaylı prompt enjeksiyonundan kaynaklanan klasik sıfır tıklama veri sızıntısı CVE'si. Yazma erişimli ajanların neden çalışma zamanı savunmalarına ihtiyaç duyduğuna referans vakası.
