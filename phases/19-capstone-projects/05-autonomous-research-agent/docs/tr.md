# Capstone 05 — Otonom Araştırma Ajanı (AI-Scientist Sınıfı)

> Sakana'nın AI-Scientist-v2'si tam makaleler yayınladı. Agent Laboratory deneyleri çalıştırdı. Allen AI izleri paylaştı. 2026 şekli, deneyler üzerinde planla-çalıştır-doğrula ağaç araması, bütçelenmiş maliyet, korumalı alanda kod yürütme, görüntü-geri-bildirimli LaTeX yazarı ve otomatik bir NeurIPS tarzı hakem topluluğudur. Capstone bir tane inşa etmek, makale başına $30 maliyetle uçtan uca çalıştırmak ve Sakana'nın belgelediği korumalı alan kaçışı red-team'inde hayatta kalmaktır.

**Type:** Capstone
**Languages:** Python (agent + sandbox), LaTeX (çıktı)
**Prerequisites:** Phase 2 (ML), Phase 3 (deep learning), Phase 7 (transformers), Phase 10 (LLMs from scratch), Phase 14 (agents), Phase 15 (autonomous), Phase 16 (multi-agent), Phase 18 (safety)
**Phases exercised:** P0 · P2 · P3 · P7 · P10 · P14 · P15 · P16 · P18
**Time:** 40 saat

## Problem

Otonom araştırma ajanları 2026'da bir eşiği geçti. Sakana AI'ın AI-Scientist-v2'si, atölye hakem değerlendirmesini geçen üretilmiş makalelerle Nature'da yayınlandı. ShinkaEvolve (ICLR 2026) çizgiyi hipotezlerin evrimine kadar genişletti. AMD'nin Agent Laboratory'si tekrarlanabilir izleri yayınladı. Ajanlar sihir değil — aday deneyler ağacı, maliyet sınırları, tohum-bağlı korumalı alanlar ve otomatik inceleme üzerinde çalışan bir planla-çalıştır-doğrula döngüsü. Zanaat döngüde, bütçede ve güvenlik hikâyesindedir.

Döngüyü, dar bir alanda (örneğin, 100M-parametreli bir transformerda attention-sparsity (dikkat seyrekliği) ablasyonları) bir tohum fikre karşı uygulayarak öğrenirsiniz. Değer, ilk çalıştırmada yeni bir şey keşfetmek değil. Değer altyapıdadır: ağaç-arama, deney korumalı alanı, yazar-inceleme döngüsü, red-team raporu. Sakana ekibi korumalı alan kaçışı başarısızlıklarını belgeledi; sizin ajanınız aynı red-team'i geçmeli.

## Concept

Ajan, en-iyi-önce (best-first) bir ağaç aramasıdır. Düğümler deney belirtimleridir: (hipotez, konfigürasyon, kod, beklenen sonuç). Bir genişletme adımı, küçük düzenlemelerle (optimizer değiştir, parti boyutunu kaydır, bir bileşeni ablate et) çocuklar önerir. Her çocuk, sert bir kaynak sınırıyla taze bir korumalı alanda çalışır. Sonuçlar, düğümleri (yenilik × kalite × kalan bütçe) ile sıralayan bir skor fonksiyonuna geri beslenir. Ağaç, bütçe tükenene kadar büyür, sonra en iyi dal yazılır.

Yazar çok modludur. Bir LaTeX taslağı oluşturur, derler, şekilleri işler ve işlenmiş PDF'i, düzen, şekil okunabilirliği ve iddia-kanıt uyumu konusunda eleştiri için Claude Opus 4.7'nin görü moduna geri besler. Beş LLM hakemden oluşan bir topluluk, NeurIPS tarzı puanlar (yenilik, titizlik, netlik, tekrarlanabilirlik, etki) yayar; ortalama eşiğin altına düşerse, makale eleştiri ile yazara döner.

Güvenlik yük taşıyıcıdır (load-bearing). Her deney, ağ çıkışı olmayan, sınırlı duvar-saati ve sabitlenmiş kaynak sınırları olan bir E2B veya Daytona korumalı alanında çalışır. Ajanın kod üretim adımı, korumalı alandan kaçan sistem çağrılarını engelleyen bir politika katmanından geçer. Red-team raporu, Sakana tarafından belgelenen saldırı yüzeyini (fork bombaları, dosya sistemi kaçışları, LLM yazımı ağ çağrıları) yeniden üretir.

## Architecture

```
seed idea + domain
 |
 v
 literature search (Semantic Scholar + OpenAlex + FAISS cache)
 |
 v
 LangGraph plan-execute-verify tree
 |
 v
 +--- expand node ----+ per-node sandbox
 | | (E2B / Daytona)
 v v resource caps
 child_1 child_k no network egress
 | | deterministic seeds
 v v
 run experiment run experiment
 | |
 v v
 score nodes by (novelty, quality, budget)
 |
 v
 best branch -> LaTeX writer
 |
 v
 compile + vision critique (Opus 4.7 vision)
 |
 v
 reviewer ensemble (5 LLM judges, NeurIPS rubric)
 |
 v
 paper.pdf + review.md + trace.json
```

#### Açıklama

Bu mimari bir araştırma fikrinden yayınlanmış bir makaleye kadar tam boru hattını gösterir. Başlangıçta tohum fikri + alan kapsamı vardır. Ajan, Semantic Scholar ve OpenAlex'ten 50 makalenin özetlerini çeker ve bir alan özeti oluşturur. LangGraph üzerinde bir planla-çalıştır-doğrula ağacı kurulur: her genişletme adımı yeni çocuk düğümler önerir, her çocuk kendi E2B/Daytona korumalı alanında çalıştırılır. Sonuçlar yenilik, kalite ve bütçe kullanımına göre puanlanır. En iyi dal seçildikten sonra LaTeX yazarı devreye girer, derlenmiş PDF Opus 4.7 görüntü modunda eleştirilir ve beş hakemden oluşan bir topluluk NeurIPS rubriği ile puanlar. Sonunda paper.pdf, review.md ve trace.json üretilir.

## Stack

- Orkestrasyon: Kontrol noktası alma ve insan-onay kapıları ile LangGraph
- Ağaç arama: Deney düğümleri üzerinde özel en-iyi-önce (Sakana v2'den AB-MCTS tarzı)
- Korumalı alan: Deney başına E2B, Docker-in-Docker yedek; cgroups aracılığıyla kaynak sınırları
- Literatür: Semantic Scholar Graph API + OpenAlex + özetlerin yerel FAISS önbelleği
- Yazar: LaTeX şablonu + şekil eleştirisi ve düzeni için Claude Opus 4.7 (görüntü modu)
- Hakem: 5 hakemden oluşan topluluk (Opus 4.7, GPT-5.4, Gemini 3 Pro, DeepSeek R1, Qwen3-Max) ağırlıklı toplama ile
- Deney çatısı: Fiziksel deneyler için PyTorch 2.5, günlükleme için W&B
- Gözlemlenebilirlik: Ajan izleri için Langfuse, makale başına $30 sert bütçe

## Build It

1. **Tohum ve alan kapsamı.** Bir tohum fikri alın (ör. "1B altı transformerların dikkat haritalarındaki seyreklik desenlerini araştır"). Arama uzayını tanımlayın: modeller, veri kümeleri, hesaplama bütçesi.

2. **Literatür geçişi.** Semantic Scholar + OpenAlex'ten en çok alıntı yapılan 50 ilgili makaleyi sorgulayın; özetleri yerel olarak önbelleğe alın; 1 sayfalık bir alan özeti üretin.

3. **Ağaç iskelesi.** Kökü tohum hipoteziyle başlatın. `expand(node) -> children`'ı küçük-düzenleme önerileriyle (çocuk başına bir konfig değişikliği) uygulayın. `score(node)`'u ağırlıklı yenilik × kalite × bütçe terimi olarak uygulayın.

4. **Korumalı alan sarmalama.** Her deney `docker run --network=none --memory=8g --cpus=2 --pids-limit=256 --read-only` (veya eşdeğer E2B politikası) çalıştırır. Tohumlar korumalı alana yazılır; çıktılar dışarıya salt-okunur bağlanır.

5. **Planla-çalıştır-doğrula döngüsü.** `plan` çocukları önerir. `execute` korumalı alanı çalıştırır, günlükleri ve metrikleri yakalar. `verify` metrikler üzerinde birim kontrollerini çalıştırır (kayıp azaldı mı? ablasyon etkiyi yalıttı mı?). Başarısız düğümler ağaçta bir başarısızlık nedeni saklar.

6. **Yazar.** Bütçeden sonra en iyi dalı seçin. Şekilleri matplotlib ile işleyin. Dal izini bağlamda tutan Claude Opus 4.7 ile bir LaTeX taslağı oluşturun. Derleyin. Derlenmiş PDF'i Opus 4.7 görüntüsüne eleştiri için besleyin. Yineleyin.

7. **Hakem topluluğu.** Beş hakem taslağı (yenilik, titizlik, netlik, tekrarlanabilirlik, etki) üzerinde NeurIPS tarzı rubriklerle puanlar. Ortalama < 4.0/5 ise, eleştiri ile yazara döndürün. 3 yeniden yazmadan sonra sert dur.

8. **Red team.** Korumalı alanı hedefleyen bir dizi düşmanca görev inşa edin veya entegre edin: fork bombaları, ağ sızdırma denemeleri, dosya sistemi kaçışları, LLM yazımı kabuk metakarakterleri. Tümünün engellendiğini doğrulayın. Bulguları yazın.

9. **Tekrarlanabilirlik.** Her makale, ağaç-arama iz JSON'ı, tohumları, W&B çalıştırma bağlantıları, korumalı alan konfigürasyonları ve uçtan uca yeniden üreten bir README ile gelir.

## Use It

```
$ ai-scientist run --seed "attention sparsity in sub-1B transformers" --budget 30
[lit] 50 papers, digest in 12s
[tree] expanded 8 nodes, budget 12/30
[exec] node #3 sparsity=top-8, loss=2.83 (best so far)
[exec] node #6 sparsity=top-4, loss=3.12 (worse)
[exec] ...
[tree] chose branch rooted at node #3 (novelty 0.62, quality 0.81)
[write] LaTeX draft v1 complete
[vision] critique: figure 2 legend too small, claim-evidence ok
[write] draft v2 after 3 edits
[review] mean 4.2/5 (novelty 3.9, rigor 4.3, clarity 4.1, repro 4.5, impact 4.2)
[done] paper.pdf + review.md + trace.json $28.40 spent
```

#### Açıklama

Bu terminal oturumu bir araştırma fikrinin uçtan uca işlenmesini gösterir. 30 dolarlık bütçeyle başlayan ajan 12 saniyede 50 makale özetleyerek başlar. Ağaç araması 8 düğümü genişletir, 12/30 dolar harcar. En iyi sonuç, top-8 seyreklik ile loss=2.83 veren 3. düğüm olur. LaTeX yazarı ilk taslağı üretir, Opus 4.7 görüntü modu 2. şeklin açıklama metninin çok küçük olduğunu belirtir. Üç düzenlemeden sonra hakem topluluğu ortalama 4.2/5 puan verir ve 28.40 dolarla proje tamamlanır. Çıktılar paper.pdf, review.md ve trace.json'dur.

## Ship It

`outputs/skill-ai-scientist.md` teslim edilen şeydir. Bir tohum fikri + bir alan + 30$ bütçe verildiğinde, tam boru hattını çalıştırır ve incelenebilir bir makale artı tekrarlanabilirlik demeti yayar.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Makale kalitesi | Yayınlanmış atölye makalelerine karşı kör rubrik incelemesi |
| 20 | Deneysel titizlik | Temel çizgiler, tohumlar, ablasyonlar; her iddia sonuçlar tablosundaki bir hücreyle desteklenir |
| 20 | Maliyet ve hesaplama disiplini | Makale başına $30 tavan uygulanır, Langfuse izli |
| 20 | Güvenlik | Korumalı alan red-team'i geçer; ağ politikası ve acil-durdurma anahtarı doğrulanır |
| 15 | Tekrarlanabilirlik | Tek-komut yeniden çalıştırma, aynı tohumlarla makaleyi yeniden üretir |
| **100** | | |

## Exercises

1. Boru hattını aynı alanda üç farklı tohum fikre karşı çalıştırın. Ağaç-aramanın hangi kısımlarının örtüştüğünü karşılaştırın. Yinelenen israf edilen hesaplamayı belirleyin.

2. $5 üzerinde tahmin edilen düğümler için deney yürütmeden önce bir insan-in-the-loop kapısı ekleyin. Toplam maliyetin ne kadar düştüğünü ölçün.

3. Hakem topluluğunu tek bir hakemle değiştirin. Bilinen-kötü makalelerden oluşan bir holdout kümesinde yanlış-kabul oranını ölçün.

4. Bir ağ-sızdırma red-team testi ekleyin: ajan harici bir adrese `curl` çekmeye çalışan kod yazar. `--network=none` politikasının bunu engellediğini doğrulayın. Denemeyi günlüğe kaydedin.

5. Ağaç-aramanızı düz rastgele bir temel çizgiyle karşılaştırın (aynı bütçe, genişletme stratejisi yok). Yenilik × kalite kazancını raporlayın.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Ağaç arama | "AB-MCTS tarzı genişletme" | Yenilik×kalite×bütçe skoru ile deney düğümleri üzerinde en-iyi-önce keşif |
| Korumalı alan | "Deney yalıtımı" | Ağ olmayan, sınırlı CPU/bellek, sabitlenmiş tohumlar, salt-okunur girdiler içeren konteyner |
| Görüntü eleştirisi | "İşle-sonra-oku" | Makaleyi PDF olarak derleyin, düzen ve iddia-kanıt eleştirisi için PDF'i bir görüntü-dil modeline besleyin |
| Hakem topluluğu | "Otomatik hakem incelemesi" | NeurIPS rubriği ile puanlayan birden çok LLM hakem; ağırlıklı toplam boru hattını geçitler |
| Yenilik skoru | "Bu yeni mi?" | 50 makalelik literatür önbelleğine yakınlığı cezalandıran sezgisel |
| Maliyet tavanı | "$ bütçe" | Makale başına toplam harcamaya sert sınır; Langfuse sayaçları + çalıştırma-öncesi tahminler |
| Red team | "Korumalı alan kaçışı denetimi" | Politika yanlışsa korumalı alandan kaçacak düşmanca görevler |

## Further Reading

- [Sakana AI-Scientist-v2 repository](https://github.com/SakanaAI/AI-Scientist-v2) — referans üretim araştırma ajanı
- [Sakana AI-Scientist-v1 paper (arXiv:2408.06292)](https://arxiv.org/abs/2408.06292) — orijinal metodoloji
- [ShinkaEvolve (Sakana ICLR 2026)](https://sakana.ai) — evrimsel uzantı
- [Agent Laboratory (AMD)](https://github.com/SamuelSchmidgall/AgentLaboratory) — çok-rollü araştırma-laboratuvarı çatısı
- [LangGraph documentation](https://langchain-ai.github.io/langgraph/) — referans orkestrasyon katmanı
- [Semantic Scholar Graph API](https://api.semanticscholar.org/) — literatür arama
- [E2B sandboxes](https://e2b.dev) — referans deney yalıtımı
- [NeurIPS reviewer guidelines](https://neurips.cc/Conferences/2026/Reviewer-Guidelines) — hakem topluluğunun kodladığı rubrik
