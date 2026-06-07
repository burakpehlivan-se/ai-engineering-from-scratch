# Capstone 08 — Düzenlenmiş Bir Dikey İçin Üretim RAG Sohbet Botu

> Harvey, Glean, Mendable ve LlamaCloud 2026'da aynı üretim şeklini çalıştırıyor. Docling veya Unstructured ve görseller için ColPali ile hazmedin. Hibrit arayın. bge-reranker-v2-gemma ile yeniden sıralayın. %60-80 isabet oranıyla prompt önbelleği kullanarak Claude Sonnet 4.7 ile sentezleyin. Llama Guard 4 ve NeMo Guardrails ile koruyun. Langfuse ve Phoenix ile izleyin. 200-soruluk altın küme üzerinde RAGAS ile puanlayın. Düzenlenmiş bir alanda (yasal, klinik, sigorta) bir tane inşa edin ve capstone altın kümeyi, red-team'i ve drift panosunu geçmektir.

**Type:** Capstone
**Languages:** Python (pipeline + API), TypeScript (chat UI)
**Prerequisites:** Phase 5 (NLP), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 12 (multimodal), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:** P5 · P7 · P11 · P12 · P17 · P18
**Time:** 30 saat

## Problem

Düzenlenmiş-alana özgü RAG (yasal sözleşmeler, klinik araştırma protokolleri, sigorta poliçeleri) 2026'nın en çok yayınlanan üretim şeklidir çünkü yatırım getirisi açıktır ve bahisler somuttur. Harvey (Allen & Overy) bunu yasal için inşa etti. Mendable geliştirici-belgelendirme çeşidini yayınladı. Glean kurumsal aramayı kapsar. Desen şudur: yüksek-doğrulukla hazmedin, hibrit arama ile yeniden sıralayın, alıntı zorunluluğu ve prompt önbelleği ile sentezleyin, birden çok güvenlik katmanıyla koruyun ve sürekli olarak drift'i izleyin.

Zor kısımlar model değil. Yargı alanına duyarlı uyum (HIPAA, GDPR, SOC2), alıntı-düzey denetlenebilirlik, maliyet kontrolü (yüksek isabet oranında prompt önbelleği %60-90 indirim sağlar), RAGAS sadakati üzerinden halüsinasyon tespiti ve endeksin yetişemediği güncellemeler olduğunda drift tespitidir. Bu capstone, yanında bir red-team paketiyle birlikte 200-soruluk altın küme üzerinde tüm bunları yayınlamanızı ister.

## Concept

Boru hattının iki tarafı var. **Hazmetme**: docling veya Unstructured yapılandırılmış belgeleri ayrıştırır; ColPali görsel olarak zengin olanları yönetir; parçalar özetler, etiketler ve rol-tabanlı erişim etiketleri alır. Vektörler pgvector + pgvectorscale'a (50M vektörün altında) veya Qdrant Cloud'a gider; seyrek BM25 yanında çalışır. **Konuşma**: LangGraph belleği ve çok-dönüşlülüğü yönetir; her sorgu hibrit geri getirme çalıştırır, bge-reranker-v2-gemma-2b ile yeniden sıralar, Claude Sonnet 4.7 (prompt önbellekli) ile sentezler, çıktıyı Llama Guard 4 ve NeMo Guardrails'ten geçirir ve alıntı-çıpalı bir yanıt yayar.

Değerlendirme yığınının dört katmanı var. **Altın küme** (200 etiketli Soru-Cevap alıntılarla) doğruluk için. **Red team** (jailbreak'ler, PII çıkarma denemeleri, alan-dışı sorular) güvenlik için. **RAGAS** dönüş başına otomatik olarak sadakat / yanıt alakalılığı / bağlam kesinliği için. **Drift panosu** (Arize Phoenix) haftalık olarak geri getirme kalitesini ve halüsinasyon puanını izler.

Prompt önbelleği maliyet koludur. Claude 4.5+ ve GPT-5+ sistem istemlerini + geri getirilen bağlamı önbelleğe almayı destekler. %60-80 isabet oranında, sorgu başına maliyet 3-5x düşer. Boru hattı, yüksek önbellek isabet oranlarına ulaşmak için kararlı önekler (sistem istemi + yeniden sıralanmış bağlam önce) için tasarlanmalıdır.

## Architecture

```
documents (contracts, protocols, policies)
 |
 v
docling / Unstructured parse + ColPali for visuals
 |
 v
chunks + summaries + role-labels + jurisdiction tags
 |
 v
pgvector + pgvectorscale + BM25 (Tantivy)
 |
query + role + jurisdiction
 |
 v
LangGraph conversational agent
 +--- retrieve (hybrid)
 +--- filter by role + jurisdiction
 +--- rerank (bge-reranker-v2-gemma-2b or Voyage rerank-2)
 +--- synthesize (Claude Sonnet 4.7, prompt cached)
 +--- guard (Llama Guard 4 + NeMo Guardrails + Presidio output PII scrub)
 +--- cite + return
 |
 v
eval:
 RAGAS faithfulness / answer_relevance / context_precision (online)
 Langfuse annotation queue (sampled)
 Arize Phoenix drift (weekly)
 red team suite (pre-release)
```

#### Açıklama

Bu mimari düzenlenmiş bir dikey için üretim RAG boru hattını gösterir. Belgeler docling veya Unstructured ile ayrıştırılır, görsel ağırlıklı sayfalar ColPali'ye yönlendirilir. Parçalar özetler, rol-etiketleri ve yargı alanı etiketleri ile zenginleştirilir; hem pgvector (yoğun) hem Tantivy (seyrek) endekslerine yazılır. Sorgu zamanında LangGraph konuşma ajanı rol ve yargı alanına göre filtreler, hibrit geri getirme yapar, yeniden sıralar, prompt önbellekli sentezleme yapar ve çok katmanlı koruma uygular. Sürekli değerlendirme RAGAS çevrimiçi puanları, Langfuse örnekleme, Arize Phoenix haftalık drift ve sürüm-öncesi red team paketi ile yapılır.

## Stack

- Hazmetme: Yapısalı belgeler için Unstructured.io veya docling; görsel-ağırlıklı PDF'ler için ColPali
- Vektör veritabanı: 50M vektörün altında pgvector + pgvectorscale; aksi halde Qdrant Cloud
- Seyrek: Alan ağırlıklı Tantivy BM25
- Orkestrasyon: LlamaIndex Workflows (hazmetme) + LangGraph (konuşma)
- Yeniden sıralayıcı: bge-reranker-v2-gemma-2b self-hosted veya Voyage rerank-2 hosted
- LLM: Prompt önbelleği ile Claude Sonnet 4.7; yedek Llama 3.3 70B self-hosted
- Değerlendirme: RAGAS 0.2 çevrimiçi, halüsinasyon ve jailbreak paketleri için DeepEval
- Gözlemlenebilirlik: Ek açıklama kuyruğu ile self-hosted Langfuse; drift için Arize Phoenix
- Koruma rayları: Llama Guard 4 girdi/çıktı sınıflandırıcısı, NeMo Guardrails v0.12 politikası, Presidio PII temizleme
- Uyum: Parçalarda rol-tabanlı erişim etiketleri; GDPR/HIPAA için yargı alanı etiketleri

## Build It

1. **Hazmetme.** Korpusu (ciddi bir inşa için 1000-10000 belge) Unstructured veya docling ile ayrıştırın. Taranmış / görsel-ağırlıklı sayfalar için, ColPali üzerinden yönlendirin. Özetler, rol-etiketleri, yargı alanı etiketleri ile parçalar üretin.

2. **Endeks.** (Voyage-3 veya Nomic-embed-v2) yoğun gömmelerini pgvector + pgvectorscale'a. Tantivy aracılığıyla BM25 yan endeksi. Yük olarak rol ve yargı alanı süzgeçleri.

3. **Hibrit geri getirme.** Önce rol+yargı alanına göre filtreleyin; sonra paralel yoğun + BM25; resiprok sıra füzyonu ile birleştirin; ilk 20'yi yeniden sıralayıcıya; ilk 5'i sentezleyiciye.

4. **Prompt önbelleği ile sentezleme.** Önbellek başlığında sistem istemi + statik politikalar; yeniden sıralanmış bağlam önbellek uzantısı olarak; kullanıcı sorusu önbelleğe alınmamış sonek. Düzenli durumda %60-80 önbellek isabet oranını hedefleyin.

5. **Koruma rayları.** Girdi üzerinde Llama Guard 4; NeMo Guardrails rayları alan-dışı soruları veya politika-yasaklı konuları engeller; Presidio çıktıdaki kazara PII'yi temizler; alıntı zorunluluğu son-çıktı süzgeci.

6. **Altın küme.** Bir alan uzmanı tarafından (yanıt, alıntılar) ile etiketlenmiş 200 Soru-Cevap çifti. Ajanı tam-alıntı eşleşmesi, yanıt doğruluğu, sadakati (RAGAS) üzerinde puanlayın.

7. **Red team.** 50 düşmanca istem: jailbreak'ler (PAIR, TAP), PII sızdırma denemeleri, alan-dışı, yargı-ötesi sızıntılar. Geçme/başarısızlık ve önem derecesi ile puanlayın.

8. **Drift panosu.** Arize Phoenix haftalık olarak geri getirme kalitesini (nDCG, alıntı sadakati) izler. %5 düşüşte uyarı verir.

9. **Maliyet raporu.** Langfuse: prompt-önbellek isabet oranı, sorgu başına token, aşamaya göre $/sorgu dökümü.

## Use It

```
$ chat --role=analyst --jurisdiction=GDPR
> what is the data-retention obligation for EU user profiles under our contract?
[retrieve] hybrid top-20 filtered to GDPR + analyst-role
[rerank] top-5 kept
[synth] claude-sonnet-4.7, cache hit 74%, 0.8s
answer:
 The contract (Section 12.4, Master Services Agreement dated 2024-03-11)
 obligates EU user profile deletion within 30 days of termination per GDPR
 Article 17. The DPA amendment (DPA-v2.1, Section 5) extends this to 14 days
 for "restricted" category data.
 citations: [MSA-2024-03-11 s12.4, DPA-v2.1 s5]
```

#### Açıklama

Bu örnek düzenlenmiş bir RAG sorgusunun tipik akışını gösterir. Analist rolü ve GDPR yargı alanı belirtilerek bir sözleşme sorusu sorulur. Sistem 20 hibrit sonucu filtreler, yeniden sıralar ve ilk 5'i tutar. Sentez aşaması %74 önbellek isabet oranıyla 0.8 saniyede çalışır. Yanıt, sözleşme bölümüne ve DPA değişikliğine dosya:satır alıntılarıyla birlikte iki spesifik yükümlülüğü belirtir. Kullanıcı herhangi bir iddiayı tek tıklamayla kaynak belgede doğrulayabilir.

## Ship It

`outputs/skill-production-rag.md` teslim edilen şeyi tanımlar. Uyum etiketleriyle dağıtılan, rubrikten geçen, canlı drift izleme ile gözlemlenen düzenlenmiş-alana özgü bir sohbet botu.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | RAGAS sadakati + yanıt alakalılığı | Altın küme üzerinde çevrimiçi puanlar (200 Soru-Cevap) |
| 20 | Alıntı doğruluğu | Doğrulanabilir kaynak bağlayıcılarına sahip yanıtların oranı |
| 20 | Koruma rayı kapsamı | Llama Guard 4 geçme oranı + jailbreak paketi sonuçları |
| 20 | Maliyet / gecikme mühendisliği | Prompt-önbellek isabet oranı, p95 gecikme, $/sorgu |
| 15 | Drift izleme panosu | Haftalık geri getirme-kalitesi trendi ile Phoenix canlı panosu |
| **100** | | |

## Exercises

1. Farklı bir yargı alanı altında ikinci bir korpus dilimi inşa edin (ör. GDPR yanında HIPAA). 20-soruluk yargı-ötesi sondada rol+yargı alanı filtrelemenin çapraz sızıntıyı engellediğini gösterin.

2. Bir haftalık üretim trafiği üzerinde prompt-önbellek isabet oranını ölçün. Önbellek önekini hangi sorguların kırdığını belirleyin. Yeniden yapılandırın.

3. 10k-token özet arabelleği ile çok-dönümlü bellek ekleyin. Konuşma büyüdükçe sadakatin düşüp düşmediğini ölçün.

4. Claude Sonnet 4.7'yi self-hosted Llama 3.3 70B ile değiştirin. $/sorgu ve sadakat deltasını ölçün.

5. Bir "emin değilim" modu ekleyin: yeniden sıralanmış en yüksek skorlar bir eşiğin altındaysa, ajan yanıt vermek yerine "güvenilir alıntılarım yok" der. Yanlış-güven azalmasını ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Prompt önbelleği | "Önbelleklenmiş sistem + bağlam" | Claude/OpenAI özelliği: önbelleklenmiş önek token'ları isabette %60-90 indirimli |
| RAGAS | "RAG değerlendiricisi" | Sadakat, yanıt alakalılığı, bağlam kesinliğinin otomatik puanlanması |
| Altın küme | "Etiketli değerlendirme" | Alıntılarla 200+ uzman-etiketli Soru-Cevap; temel gerçek |
| Yargı alanı etiketi | "Uyum etiketi" | Parçalara eklenmiş GDPR/HIPAA/SOC2 kapsamı; geri getirme süzgeci tarafından uygulanır |
| Alıntı sadakati | "Temellenmiş yanıt oranı" | Geri getirilebilir kaynak aralıklarıyla desteklenen iddiaların oranı |
| Drift | "Geri getirme kalitesi bozulması" | nDCG veya alıntı puanında haftalık değişim; uyarı eşiği %5 |
| Red team | "Düşmanca değerlendirme" | Sürüm-öncesi jailbreak, PII çıkarma, alan-dışı sondalar |

## Further Reading

- [Harvey AI](https://www.harvey.ai) — referans yasal üretim yığını
- [Glean enterprise search](https://www.glean.com) — kurumsal ölçekte referans RAG
- [Mendable documentation](https://mendable.ai) — geliştirici-belgelendirme RAG referansı
- [LlamaCloud Parse + Index](https://docs.llamaindex.ai/en/stable/examples/llama_cloud/llama_parse/) — yönetilen hazmetme
- [Anthropic prompt caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) — maliyet kolu referansı
- [RAGAS 0.2 documentation](https://docs.ragas.io/) — kanonik RAG değerlendirme çatısı
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) — referans drift gözlemlenebilirliği
- [Llama Guard 4](https://ai.meta.com/research/publications/llama-guard-4/) — 2026 güvenlik sınıflandırıcısı
- [NeMo Guardrails v0.12](https://docs.nvidia.com/nemo-guardrails/) — politika ray çatısı
