# ReWOO ve Plan-and-Execute: Ayrılmış Planlama

> ReAct düşünceyi ve eylemi tek bir akışta iç içe geçirir. ReWOO bunları ayırır: önce büyük bir plan, sonra yürütme. 5 kat daha az token, HotpotQA'da +4% doğruluk ve planlayıcıyı 7B bir modele damıtabilirsiniz. Plan-and-Execute bunu genelleştirdi; Plan-and-Act web navigasyonuna ölçekledi.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- ReWOO'nun Planner / Worker / Solver ayrımının ReAct'ın iç içe geçmiş döngüsüne kıyasla neden token tasarrufu sağladığını ve dayanıklılığı artırdığını açıklayın.
- Bir plan DAG'i, bağımlılık sıralı bir yürütücü ve worker çıktılarını birleştiren bir çözücü (solver) uygulayın — hepsi stdlib.
- Bir görevin plan-sonra-yürütme mi yoksa iç içe geçmiş ReAct mı olarak çalıştırılacağına 2026 "beş workflow kalıbı" çerçevesiyle (Anthropic) karar verin.
- Plan-and-Act'in sentetik plan verisinin uzun vadeli web veya mobil görevlerde ne zaman gerekli olduğunu tanıyın.

## Problem

ReAct'ın iç içe geçmiş thought-action-observation döngüsü basit ve esnektir, ancak her araç çağrısı tüm önceki bağlamı —her bir önceki thought dahil— taşımak zorundadır. Token kullanımı derinlikle quadratically büyür. Daha da kötüsü: araç döngü ortasında başarısız olduğunda, modelin hata gözleminden tüm planı yeniden türetmesi gerekir.

ReWOO (Xu ve diğerleri, arXiv:2305.18323, Mayıs 2023) bunu fark etti ve bir bahse girdi: planı baştan oluştur, kanıtları paralel olarak getir, cevabı sonunda birleştir. Planlama için bir LLM çağrısı, kanıt için N araç çağrısı (paralel olabilir), çözmek için bir LLM çağrısı. Bedel: daha az esneklik (plan statik) karşılığında çok daha iyi token verimliliği ve daha net hata modları.

## Kavram

### Üç rol

```text
Planner: user_question -> [plan_dag]
Workers: [plan_dag] -> [evidence] (araç çağrıları, muhtemelen paralel)
Solver: user_question, plan_dag, evidence -> final_answer
```

Planner bir DAG üretir. Her düğüm bir aracı, argümanlarını ve hangi önceki düğümlere bağımlı olduğunu (`#E1`, `#E2` gibi referanslarla) adlandırır. Worker'lar düğümleri topolojik sırayla çalıştırır. Solver her şeyi birleştirir.

### Neden 5 kat daha az token

ReAct prompt uzunluğunu adım sayısıyla doğrusal olarak büyütür. 10. adımda, prompt thought 1 artı action 1 artı observation 1 artı thought 2 artı action 2 artı observation 2 ve böyle devam eder içerir. Her ara adım ayrıca orijinal prompt'u yineler.

ReWOO bir planner prompt'u (büyük), N küçük worker prompt'u (her biri yalnızca araç çağrısı, zincir yok) ve bir solver prompt'u öder. HotpotQA'da makale ~5x daha az token ölçerken +4 mutlak doğruluk puanı alır.

### Neden daha dayanıklı

ReAct'ta worker 3 başarısız olursa, döngünün hata ortasında akıl yürütmesi gerekir. ReWOO'da worker 3 bir hata stringi döndürür; solver onu orijinal planla birlikte bağlamda görür ve zarifçe düşebilir. Hata yerelleştirmesi adıma değil düğüme göredür.

### Planner distillation (damıtma)

Makalenin ikinci sonucu: planner gözlemleri görmediği için, 175B'lik bir öğretmenin planner çıktıları üzerine 7B'lik bir modeli fine-tune edebilirsiniz. Küçük model planlamayı halleder; büyük oluşuqa çıkarımda gerek yoktur. Bu artık standarttır — birçok 2026 production agent'ı küçük bir planner ve büyük bir yürütücü (veya tersi) kullanır.

### Plan-and-Execute (LangChain, 2023)

LangChain ekibinin Ağustos 2023 yazısı ReWOO'yu bir kalıp adına dönüştürdü: Plan-and-Execute. Önceden belirlenmiş planner bir adım listesi üretir, yürütücü her adımı çalıştırır, isteğe bağlı bir replanner sonuçları gözlemledikten sonra revize edebilir. Bu ReWOO'dan ziyade ReAct'a daha yakındır (replanner gözlemleri planlamaya geri getirir) ancak token tasarrufunu korur.

### Plan-and-Act (Erdogan ve diğerleri, arXiv:2503.09572, ICML 2025)

Plan-and-Act kalıbını uzun vadeli web ve mobil agent'lara ölçekler. Ana katkı sentetik plan verisidir: etiketli bir trajectory üreteci, planın açıkça belirtildiği eğitim verileri üretir. WebArena benzeri görevlerde 30-50 adımdan sonra çalışmayı sürdüren planner modellerini fine-tune etmek için kullanılır; tek bir ReAct trajectory'si tutarlılığını kaybeder.

### Hangisini ne zaman seçmeli

| Kalıp | Ne zaman |
|-------|----------|
| ReAct | Kısa görevler, bilinmeyen ortam, reaktif istisna yönetimi gerekli |
| ReWOO | Bilinen araçlarıyla yapılandırılmış görevler, token-hassas, paralel kanıt |
| Plan-and-Execute | ReWOO gibi ama kısmi yürütmeden sonra yeniden planlama |
| Plan-and-Act | Uzun vadeli (>30 adım), web/mobil/computer-use |
| Tree of Thoughts | Aramaya değer (Ders 04) |

Anthropic'in Aralık 2024 rehberi: en basit olanla başlayın. Görev bir araç çağrısı artı bir özetse, ReWOO inşa etmeyin. Görev 40 adımlık bir araştırma assignment'ise, yalnızca ReAct yapmayın.

## İnşa Et

`code/main.py` bir oyuncak ReWOO uygular:

- `Planner` — prompt'tan bir plan DAG üreten betiklenmiş bir politika.
- `Worker` — her düğümün araç çağrısını kayıt defteri aracılığıyla yönlendirir.
- `Solver` — kanıtı okuyan ve son cevabı üreten betiklenmiş birleştirme.
- Bağımlılık çözümleme — `#E1` gibi referanslar önceki worker çıktılarıyla ikame edilir.

Demo, "Fransa'nın başkentinin nüfusu nedir, milyonlara yuvarlanmış?" sorusunu iki adımlık bir planla cevaplar: (1) başkenti ara, (2) nüfusu ara, sonra çöz.

Çalıştırın:

```bash
python3 code/main.py
```

Trace ilk olarak tüm planı, sonra worker sonuçlarını, sonra solver birleştirmesini gösterir. Token sayısını ReAct tarzı iç içe geçmiş bir çalıştırmayla karşılaştırın — ReWOO bu tür yapılandırılmış görevlerde kazanır.

## Kullan

LangGraph Plan-and-Execute'ı bir reçete olarak sunar (ReAct için `create_react_agent`, plan-yürütme için özel graf'lar). CrewAI'nin Flows kalıbını doğrudan kodlar: görevleri baştan tanımlarsınız ve Flow DAG bunları çalıştırır. Plan-and-Act'in sentetik veri yaklaşımı hâlâ çoğunlukla araştırmadır; runtime kalıbı (açık plan DAG'i) LangGraph ve CrewAI Flows aracılığıyla production'da sunulur.

## Teslim Et

`outputs/skill-rewoo-planner.md`, bir kullanıcı isteğiyle, verilen bir araç kataloğuyla bir ReWOO plan DAG'i üretir. Planı (döngüsel olmayan, her referans çözülmüş, her araç mevcut) bir yürütücüye devretmeden önce doğrular.

## Alıştırmalar

1. Bağımsız plan düğümleri için worker çalıştırmasını paralelleştirin. 6 düğümlü bir DAG'ta 2 paralel grupla ne kazanırsınız?
2. Herhangi bir worker hata döndürdüğünde tetiklenen bir replanner düğümü ekleyin. ReWOO'yu Plan-and-Execute yapan en küçük değişiklik nedir?
3. `Planner`'ı küçük bir modelle (7B sınıfı) ve `Solver`'ı frontier bir modelle değiştirin. Uçtan uca kaliteyi karşılaştırın — ayrım nerede başarısız olur?
4. ReWOO makalesinin Bölüm 4'ünü okuyun. 175B -> 7B sonucunu kavramsal olarak yeniden üretin: hangi eğitim verilerine ihtiyacınız var ve plan kalitesini nasıl puanlarsınız?
5. Oyuncak kodu Plan-and-Act'in trajectory şekline taşıyın: plan bir DAG değil bir dizidir. Hangi tavizler değişir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| ReWOO | "Reasoning without observations" | Planla, sonra kanıtları paralel olarak getir, sonra çöz — planlama prompt'unda gözlem yok |
| Plan-and-Execute | "LangChain'in plan-execute kalıbı" | Yürütmeden sonra isteğe bağlı bir replanner düğümüyle ReWOO |
| Plan-and-Act | "Ölçeklenmiş plan-execute" | Uzun vadeli görevler için sentetik plan eğitim verileriyle açık planner/executor ayrımı |
| Evidence reference | "#E1, #E2, ..." | Gönderim sırasında önceki worker çıktısıyla ikame edilen plan-düğüm yer tutucusu |
| Planner distillation | "Küçük planner, büyük executor" | Büyük bir öğretmenin planner trace'leri üzerine küçük bir modeli fine-tune etme |
| Token efficiency | "Daha az gidip gelme" | Makalede HotpotQA'da ReAct'a göre 5x daha az token |
| DAG executor | "Topolojik yönlendirici" | Plan düğümlerini bağımlılık sırasıyla çalıştırır; her seviyede paralel |

## İleri Okuma

- [Xu ve diğerleri, ReWOO: Decoupling Reasoning from Observations (arXiv:2305.18323)](https://arxiv.org/abs/2305.18323) — kanonik makale
- [Erdogan ve diğerleri, Plan-and-Act (arXiv:2503.09572)](https://arxiv.org/abs/2503.09572) — sentetik planlarla ölçeklenmiş planner-executor
- [LangGraph Plan-and-Execute tutorial](https://docs.langchain.com/oss/python/langgraph/overview) — framework reçetesi
- [Anthropic, Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) — işe yarayan en basit kalıbı seçin
