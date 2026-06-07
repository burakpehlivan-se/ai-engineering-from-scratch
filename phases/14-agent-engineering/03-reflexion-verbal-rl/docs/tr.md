# Reflexion: Sözel Güçlendirme Öğrenmesi

> Gradient tabanlı RL binlerce deneme ve bir hata modunu düzeltmek için bir GPU kümesi gerektirir. Reflexion (Shinn ve diğerleri, NeurIPS 2023) bunu doğal dil ile yapar: her başarısız denemeden sonra, agent bir yansıma (reflection) yazar, epizodik hafızada (episodic memory) saklar ve bir sonraki denemeyi o hafızaya koşullandırır. Bu, Letta'nın sleep-time compute (uyku zamanı hesaplama), Claude Code'un CLAUDE.md learnings ve pro-workflow'nun learn-rule'unun arkasındaki kalıptır.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 02 (ReWOO)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Reflexion'ın üç bileşenini (Actor, Evaluator, Self-Reflector) ve epizodik hafızanın rolünü adlandırın.
- İkili (binary) değerlendirici, yansıma tamponu (reflection buffer) ve taze yeniden denemelerle stdlib bir Reflexion döngüsü uygulayın.
- Verilen bir görev için skaler, sezgisel (heuristic) ve öz-değerlendirmeli (self-evaluated) geri besleme kaynakları arasında seçim yapın.
- Neden sözel güçlendirmenin gradient tabanlı RL'in binlerce denemeyle düzeltmesi gereken hataları yakaladığını açıklayın.

## Problem

Bir agent bir görevde başarısız olur. Standart RL'de binlerce deneme daha çalıştırırdınız, gradyan hesaplardınız, ağırlıkları güncellerdiniz. Pahalı, yavaş ve çoğu production agent'ın her başarısızlık için bir eğitim bütçesi yoktur.

Reflexion (Shinn ve diğerleri, arXiv:2303.11366) farklı bir soru sorar: ya agent neden başarısız olduğunu düşünseydi ve o düşünceyle tekrar denese? Ağırlık güncellemesi yok. Gradyan yok. Yalnızca denemeler arasında saklanan doğal dil.

Sonuç: ALFWorld'da ReAct ve diğer fine-tune edilmemiş temelleri yener. HotpotQA'da ReAct'ı geliştirir. Kod üretiminde (HumanEval/MBPP) o zamanki en iyi durumu (state of the art) belirler. Tek bir gradyan adımı olmadan.

## Kavram

### Üç bileşen

```text
Actor : bir trajectory üretir (ReAct tarzı döngü)
Evaluator : trajectory'yi puanlar — ikili, sezgisel veya öz-değerlendirmeli
Self-Reflector: başarısızlık üzerine doğal dilde bir yansıma yazar
```

Artı bir veri yapısı:

```text
Episodik hafıza: önceki yansımalardan oluşan liste, bir sonraki denemenin prompt'unun başına eklenir
```

Bir deneme Actor'u çalıştırır. Evaluator puanlar. Puan düşükse, Self-Reflector bir yansıma üretir ("Soru Y'yi soruyorken X olarak yanlış okuduğum için yanlış aracı seçtim"). Yansıma epizodik hafızaya girer. Sonraki deneme taze başlar ancak yansımayı görür.

### Üç değerlendirici türü

1. **Skaler** — harici bir ikili sinyal. ALFWorld başarılı ya da başarısız. HumanEval testleri geçer ya da geçemez. En basit, en yüksek sinyal.
2. **Sezgisel** — önceden tanımlanmış hata imzaları. "Agent aynı eylemi arka arkaya iki kez yaptıysa, sıkışmış olarak işaretle." "Trajectory 50 adımı aşarsa, verimsiz olarak işaretle."
3. **Öz-değerlendirmeli** — LLM kendi trajectory'sini puanlar. Ground truth (temel gerçek) mevcut olmadığında gereklidir. Daha düşük sinyal; araç destekli doğrulamayla (Ders 05 — CRITIC) iyi eşleşir.

2026 varsayılanı bir karışımdır: mevcut olduğunda skaler, olmadığında öz-değerlendirme, güvenlik bariyerleri olarak sezgiseller.

### Neden genelleşir

Reflexion yeni bir algoritmadan ziyade adlandırılmış bir kalıptır. Üretimdeki neredeyse her "kendini iyileştiren" agent bir varyant çalıştırır:

- Letta'nın sleep-time compute'i (Ders 08): ayrı bir agent geçmiş konuşmaları yansıtır ve hafıza bloklarına yazar.
- Claude Code'un `CLAUDE.md` / "save memory" kalıbı: yansımalarlearnings olarak yakalanır, gelecek oturumların başına eklenir.
- pro-workflow'nun `/learn-rule` komutu: düzeltmeler açık kurallar olarak yakalanır.
- LangGraph'ın yansıma düğümleri: çıktıyı puanlayan ve gerekirse refine'a yönlendiren bir düğüm.

Hepsi aynı içgöruden türemiştir: doğal dil, "başarısızlıktan ne öğrendiğimi" çalıştırmalar arasında taşımak için yeterince zengin bir ortamdır.

### Ne zaman işe yarar ne zaman yaramaz

Reflexion şu durumlarda işe yarar:

- Açık bir başarısızlık sinyali vardır (test hatası, araç hatası, yanlış cevap).
- Görev sınıfı tekrarlanabilir (aynı tür soru tekrar sorulabilir).
- Yansımanın trajectory'yi iyileştirmek için yeri vardır (yeterli eylem bütçesi).

Reflexion şu durumlarda yardımcı olmaz:

- Agent zaten ilk denemede başarılıdır.
- Başarısızlık dışarıdan kaynaklanmıştır (ağ çöktü, araç bozuldu) — "ağ çökmüştü" üzerine yansıma gelecek çalıştırmalara yardımcı olmaz.
- Yansıma batıl inanca dönüşür — bir kerelik kararsız bir çalıştırmaya ilişkin bir anlatı saklanır.

2026 tuzağı: hafıza çürümesi (memory rot). Yansımalardan bazıları eski veya yanlıştır; epizodik tampon büyüdükçe yeniden çalıştırmalar yavaşlar. Çözüm: periyodik sıkıştırma (Ders 06), yansımalar üzerinde TTL veya ayrı bir sleep-time temizleme agent'ı (Letta).

## İnşa Et

`code/main.py` bir oyuncak bulmaca üzerine Reflexion uygular: hedefe toplamı ulaşan 3 elemanlı bir liste üret. Actor aday listeler üretir; Evaluator toplamı kontrol eder; Self-Reflector neyin yanlış gittiğine dair bir satır yazar. Yansıma bir sonraki deneme için epizodik hafızaya girer.

Bileşenler:

- `Actor` — yansıma gördüğünde iyileşen betiklenmiş bir politika.
- `Evaluator.binary()` — hedef toplamda geçme/başarısız olma.
- `SelfReflector` — başarısızlığın tek satırlık bir tanısını üretir.
- `EpisodicMemory` — TTL semantiğiyle sınırlı bir liste.

Çalıştırın:

```bash
python3 code/main.py
```

Trace üç deneme gösterir. Deneme 1 başarısız olur, bir yansıma saklanır, deneme 2 yansımayı görür ve iyileşir ancak hâlâ başarısız olur, deneme 3 başarılı olur. Temel çalıştırmayla (yansıma olmadan) karşılaştırın — deneme 1'in cevabında sıkışıp kalır.

## Kullan

LangGraph yansımayı bir düğüm kalıbı olarak sunar. Claude Code'un `/memory` komutu ve pro-workflow'nun `/learn-rule` komutu epizodik tamponu bir markdown dosyası olarak dışsallaştırır. Letta'nın sleep-time compute'i Self-Reflector'ı boş zamanlarda çalıştırarak birincil agent'ın gecikme bağımlılığını korur. OpenAI Agents SDK doğrudan Reflexion sunmaz; bunu puanla trajectory'leri reddeden özel bir Guardrail ve çalıştırmalar arası dayanıklı bir memory `Session` ile inşa edersiniz.

## Teslim Et

`outputs/skill-reflexion-buffer.md` yansıma yakalama, TTL ve ayıklama (deduplication) ile epizodik bir tampon oluşturur ve korur. Verilen bir görev sınıfı ve bir başarısızlıkla, bir sonraki denemeye gerçekten yardımcı olan bir yansıma üretir (generic bir "daha dikkatli ol" değil).

## Alıştırmalar

1. İkili değerlendiriciyi, mesafe metriği (hedeften ne kadar uzak) döndüren skaler bir değerlendiriciye geçirin. Daha hızlı yakınsar mı?
2. Yansımalara 10 denemelik bir TTL ekleyin. Bu noktadan sonra eski yansımalar zararlı mı yoksa yardımcı mı?
3. Sezgisel değerlendirici uygulayın: aynı eylem tekrar ediyorsa denemeyi sıkışmış olarak işaretle. Bu Self-Reflector ile nasıl etkileşir?
4. Yansımalara aldırış etmeyen düşmanca (adversarial) bir Actor ile Reflexion çalıştırın. Actor'un yansımaları fark etmesini zorunlu kılan minimum yansıma prompt mühendisliği nedir?
5. Reflexion makalesinin AlfWorld ile ilgili Bölüm 4'ünü okuyun. %130 başarı oranı artışını kavramsal olarak yeniden üretin: vanilya ReAct'a kıyasla temel fark nedir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Reflexion | "Kendini düzeltme" | Shinn ve diğerleri 2023 — Actor, Evaluator, Self-Reflector artı epizodik hafıza |
| Verbal reinforcement | "Gradyanssız öğrenme" | Bir sonraki denemenin prompt'unun başına eklenen doğal dil yansıması |
| Episodic memory | "Görev bazlı yansımalar" | Bir görev sınıfı için sınırlı önceki yansıma tamponu |
| Scalar evaluator | "İkili başarı sinyali" | Ground truth'tan geçme/başarısız olma veya sayısal puan |
| Heuristic evaluator | "Kalıp tabanlı algılayıcı" | Önceden tanımlanmış hata imzaları (ör. döngüde sıkışma, çok fazla adım) |
| Self-evaluator | "Kendi izi üzerinde LLM-hakem" | Ground truth olmadığında daha düşük sinyal geri dönüşü — araç destekli doğrulamayla eşleştirin |
| Memory rot | "Eski yansımalar" | Epizodik tampon eski girişlerle dolar; sıkıştırma/TTL ile çözülür |
| Sleep-time reflection | "Asenkron öz-yansıma" | Birincil agent hızlı kalırken Self-Reflector'ı sıcak yoldan çalıştırın |

## İleri Okuma

- [Shinn ve diğerleri, Reflexion: Language Agents with Verbal Reinforcement Learning (arXiv:2303.11366)](https://arxiv.org/abs/2303.11366) — kanonik makale
- [Letta, Sleep-time Compute](https://www.letta.com/blog/sleep-time-compute) — production'da asenkron yansıma
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — epizodik tamponu bağlam parçası olarak yönetme
- [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — yansıma düğümü kalıbı
