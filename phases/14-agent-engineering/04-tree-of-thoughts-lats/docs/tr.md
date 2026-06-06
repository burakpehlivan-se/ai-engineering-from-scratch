# Tree of Thoughts ve LATS: Bilinçli Arama

> Tek bir thought zinciri (chain-of-thought) trajectory'sinde geri adım atma alanı yoktur. ToT (Yao ve diğerleri, 2023) akıl yürütmeyi her düğümde öz-değerlendirmeli bir ağaça dönüştürür. LATS (Zhou ve diğerleri, 2024) ToT'yu ReAct ve Reflexion ile Monte Carlo Tree Search (MCTS) altında birleştirir. Game of 24, %4'ten (CoT) %74'e (ToT) çıkar; LATS HumanEval'da %92.7 pass@1'e ulaşır.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 03 (Reflexion)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Aklı yürütmeyi arama olarak çerçeveleyin: düğümler "düşünceler", kenarlar "genişlemeler", değer "ne kadar umut verici".
- Öz-değerlendirme puanlamasıyla stdlib ToT tarzı BFS ağaç araması uygulayın.
- Seç / genişle / simüle et / geri yay (backpropagate) ile toy bir LATS MCTS döngüsüne genişletin.
- Aramanın token çarpanına değip değmediğine (Game of 24, kod üretimi) ve tek bir trajectory'nin yeterli olup olmadığına (basit SSS) karar verin.

## Problem

Thought zinciri (chain-of-thought) doğrusal bir yürüyüştür. İlk adım yanlışsa, sonraki her adım yanlış bir varsayım üzerine çalışır. Game of 24'te (dört rakamı + − × ÷ kullanarak 24 yapma), GPT-4 CoT %4 doğruluk elde eder. Model erken bir alt ifadeyi seçer ve kurtulamaz.

Akıl yürütmeye ihtiyaç duyulan şey, birden fazla aday önerme, onları değerlendirme, umut verici olanları seçme ve çıkmaz sokaklar ortaya çıktığında geri adım atma yeteneğidir. Bu aramadır. Tree of Thoughts ve LATS iki kanonik formülasyondur.

## Kavram

### Tree of Thoughts (Yao ve diğerleri, NeurIPS 2023)

Her düğüm tutarlı bir ara adımdır ("bir düşünce"). Her düğüm K çocuk düşüncesine genişleyebilir. LLM her düğümü bir puanlama prompt'uyla öz-değerlendirir. Arama ağacı keşfeder — BFS, DFS veya beam.

```text
                      (kök: "4 6 4 1'den 24 bul")
                     /               |            \
           ("6 - 4 = 2")    ("4 + 1 = 5")    ("4 * 6 = 24")  <- Puan: YÜKSEK
              /   \              |                  |
          ...    ...          ...                bitir
```

Öz-değerlendirme kritik parçadır. Makale üç varyant gösterir: `sure / likely / impossible` sınıflandırması, `1..10` sayısal puanı ve adaylar arası oylama. Üçü de Game of 24'te CoT'u önemli ölçüde yener (%4 -> %74, GPT-4 ile).

### LATS (Zhou ve diğerleri, ICML 2024)

LATS, ToT, ReAct ve Reflexion'ı MCTS altında birleştirir. LLM üç rol oynar:

- **Policy (Politika):** aday sonraki eylemleri önerir (ReAct tarzı).
- **Value function (Değer fonksiyonu):** kısmi bir trajectory'yi puanlar (ToT tarzı öz-değerlendirme).
- **Self-reflector (Öz-yansıtıcı):** başarısızlıkta, doğal dilde bir yansıma yazar (Reflexion tarzı) ve gelecek denemeleri yeniden tohumlandırmak için kullanır.

Ortam geri bildirimi (gözlemler) değer fonksiyonuna karışır, böylece arama yalnızca model görüşlerinden değil gerçek araç sonuçlarından beslenir. Makale zamandaki sonuçlar: GPT-4 ile HumanEval pass@1 %92.7 (SOTA), GPT-3.5 ile WebArena ortalaması 75.9 (gradient tabanlı fine-tune'a yaklaşıyor).

### MCTS, asgari düzeyde

Her iterasyon için dört faz:

1. **Select (Seç)** — UCT (upper confidence bound for trees) kullanarak kökten yaprağa yürüyün.
2. **Expand (Genişle)** — politika aracılığıyla K çocuk üretin.
3. **Simulate (Simüle et)** — bir çocuktan politikayla rollout yapın, yaprağı değer fonksiyonuyla (veya ortam ödülüyle) puanlayın.
4. **Backpropagate (Geri yay)** — ziyaret sayılarını ve değer tahminlerini yol boyunca güncelleyin.

UCT formülü: `Q(s, a) + c * sqrt(ln N(s) / N(s, a))`. İlk terim exploitation (sömürü); ikincisi exploration (keşif). Her görev için `c`'yi ayarlayın.

### Maliyet gerçeği

Arama token'ları patlatır. Game of 24'te ToT, CoT'un 100-1000 katı token kullanır. LATS benzer. Bu ücretsiz değildir; aramayı şunlara saklayın:

- Tek bir trajectory'nin yetersiz olduğu kanıtlanmış görevler (Game of 24, karmaşık kod).
- Duvardan duvara sürenin doğruluktan daha az önemli olduğu görevler.
- Ucuz, güvenilir bir değer fonksiyonu olan görevler (kod için birim testler, matematik için açık hedef).

Görevinizin tek bir doğru cevabı ve gürültülü bir değerlendiricisi varsa, arama genellikle işleri daha kötü yapar — "yüksek puanlı" yanlış bir cevap bulur.

### 2026 konumlandırması

Çoğu production agent LATS çalıştırmaz. Araç destekli doğrulamayla (CRITIC, Ders 05) ReAct çalıştırırlar. Arama niş alanlarda ortaya çıkar:

- Testleri değer fonksiyonu olarak çalıştıran kodlama agent'ları (HumanEval tarzı).
- Çoklu sorgu yollarını keşfeden derin araştırma agent'ları.
- LangGraph subgraph'ları içinde ağırlıklı planlama workflow'ları.

AlphaEvolve (Ders 11) 2026'nın aşırı noktasıdır: kod üzerinde evrimsel arama, makine tarafından kontrol edilebilir fitness, frontier kazançları (56 yılda ilk 4x4 matmul iyileştirmesi).

## İnşa Et

`code/main.py` şunları uygular:

- Seçilmiş "aritmetik işlemleri seç" görevinde küçük bir ToT BFS.
- Aynı görevde bir toy LATS MCTS döngüsü (Select / Expand / Simulate / Backpropagate) UCT seçimiyle.
- Sembolik puan ile öz-değerlendirme puanını birleştiren bir değer fonksiyonu.

Çalıştırın:

```bash
python3 code/main.py
```

Trace, BFS ile her düğümde üç aday genişleten ToT'u, MCTS ile en iyi rollout'a yaklaşan LATS ile karşılaştırır. Her ikisi için de token sayıları yazdırılır.

## Kullan

LangGraph ToT tarzı keşfi subgraph kalıpları olarak sunar; LangChain ekibinin LATS blogu (Mayıs 2024) referans tutorial'ıdır. LlamaIndex bir `TreeOfThoughts` agent sunar. 2026 production agent'larının çoğu için bu kalıp bir `if task_complexity > threshold: use_search()` kapısının arkasında yaşar — Ders 05'teki evaluator-optimizer kalıbına bakın.

## Teslim Et

`outputs/skill-search-policy.md`, görev şekli, bütçe ve değerlendirici doğruluğuna göre doğrusal ReAct, ToT, LATS ve evrimsel arama arasında seçim yapar.

## Alıştırmalar

1. Toy LATS'i UCT c=0.1 ve c=2.0 ile çalıştırın. Trace'de ne değişir?
2. Daha gürültülü bir puanlayıcıya (rastgele titreşim ekleyerek) değer fonksiyonunu değiştirin. MCTS hâlâ en iyi yaprağı buluyor mu? Tahammül ettiği minimum sinyal-gürültü oranı nedir?
3. Beam-search ToT uygulayın (her seviyede top-k'yi koruyun) ve BFS ile karşılaştırın. Sıkı bir token bütçesinde hangisi daha iyi?
4. LATS Bölüm 5.1'i okuyun. HumanEnv trajectory sayısını yeniden üretin: raporlanan pass@1'e ulaşmak için kaç rollout gerekir?
5. LATS makalesinin "LATS ne zaman daha az yardımcı olur" tartışmasını okuyun. Görev şeklini arama stratejisiyle eşleştiren tek paragraflık bir karar kuralı yazın.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Tree of Thoughts | "Dallanmış CoT" | Yao ve diğerleri — öz-değerlendirmeli düşünce düğümleri ağacı |
| LATS | "LLM'ler için MCTS" | Zhou ve diğerleri — ToT + ReAct + Reflexion'ı MCTS altında birleştirir |
| UCT | "Upper confidence bound" | Exploitation (Q) ve exploration (ln N / n) arasındaki dengeyi seçen formül |
| Value function | "Bu durum ne kadar iyi" | Promptlanmış LLM puanı veya ortam ödülü; geri yayımı besler |
| Policy | "Eylem önerici" | ReAct tarzı üreteci; aday sonraki düşünceleri/eylemleri üretir |
| Rollout | "Simüle edilmiş trajectory" | Politikayla bir düğümden yaprağa yürüyüş, değerle puanlama |
| Backpropagate | "Ataları güncelle" | Yaprağın ödülünü yol boyunca yukarı itme, ziyaret sayılarını ve Q'yu güncelleme |
| Search cost | "Token patlaması" | Game of 24'te CoT'un 100-1000 katı; benimsemeden önce bütçele |

## İleri Okuma

- [Yao ve diğerleri, Tree of Thoughts (arXiv:2305.10601)](https://arxiv.org/abs/2305.10601) — kanonik makale
- [Zhou ve diğerleri, LATS (arXiv:2310.04406)](https://arxiv.org/abs/2310.04406) — Reflexion geri bildirimli MCTS
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — arama için subgraph kalıpları
- [AlphaEvolve (arXiv:2506.13131)](https://arxiv.org/abs/2506.13131) — programlı değerlendiricilerle evrimsel arama
