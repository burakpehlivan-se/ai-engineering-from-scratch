# STaR, V-STaR, Quiet-STaR — Kendi Kendine Öğrenen Akıl Yürütme

> En küçük öz-iyileştirme döngüsü (self-improvement loop), mantıksal gerekçenin (rationale) içine oturur. Bir model bir düşünce zinciri (chain of thought) üretir, doğru cevaba ulaşanları tutar ve bunlar üzerinde fine-tuning yapar. Bu STaR'dır. V-STaR, çıkarım sırasındaki seçimi iyileştirmek için bir doğrulayıcı (verifier) ekler. Quiet-STaR, mantıksal gerekçeyi her token'a indirger. Üçü de çalışır. Hiçbiri sihir değildir — döngü, doğru cevaba tesadüfen ulaşan her türlü kısayolu korur.

**Tür:** Öğrenme
**Diller:** Python (stdlib, bootstrap döngüsü simülatörü)
**Önkoşullar:** Faz 13 · 01-03 (Akıl Yürütme ve CoT), Faz 15 · 01 (uzun vadeli çerçeve)
**Süre:** ~60 dakika

## Sorun

Bir modele akıl yürütmeyi öğretmenin basit yolu, insan tarafından yazılmış akıl yürütme izlerini (reasoning traces) toplamaktır. Bu pahalı, yavaştır ve insanların ne kadar yüksek kaliteli düşünce zinciri yazmaya istekli olduğuna bağlıdır.

STaR (Kendi Kendine Öğrenen Akıl Yürütücü, Zelikman ve ark., 2022) şunu sorar: peki ya model kendi gerekçelerini yazsa ve bunları bilinen cevaplara göre değerlendirse? Döngü şöyledir:

1. Bir akıl yürütme izi ve cevap örnekle.
2. Son cevap doğruysa, izi tut.
3. Tutulan izler üzerinde fine-tuning yap.
4. Tekrarla.

Çalışır. GSM8K ve CommonsenseQA, yeni insan etiketlemesi olmadan iyileşti. Ancak döngünün yerleşik bir önyargısı var: doğru cevabı üreten her gerekçe, mantığın kendisi tutarlı olsun ya da olmasın korunur. V-STaR (Hosseini ve ark., 2024) bunu öğrenilmiş bir doğrulayıcı ile düzeltir; Quiet-STaR (Zelikman ve ark., 2024) fikri her token内部 gerekçeye kadar genelleştirir.

## Kavram

### STaR: işe yarayan üzerinde bootstrap

Biraz zayıf akıl yürütme yeteneğine sahip bir temel modelle (base model) başlayın. Her eğitim probleminde bir gerekçe ve cevap örnekle. Cevap etiketle eşleşirse, (sorun, gerekçe, cevap) üçlüsünü tutun. Tutulan küme üzerinde modeli fine-tune edin. Tekrarlayın.

Bir detay önemlidir: model bir soruyu hiçbir zaman doğru yapamazsa, döngü onun üzerinde öğrenemez. STaR **rasyonalizasyon** (rationalization) ekler: modelin başarısız olduğu sorularda doğru cevabı ipucu olarak enjekte edin ve modele o cevaba götüren bir gerekçe üretmesi için tekrar sorun. Rasyonelize edilmiş gerekçeler eğitim kümesine eklenir.

Orijinal makaledeki sonuç (Zelikman ve ark., 2022): bir GPT-J temel modeli, rasyonalizasyonla tekrarlanan STaR turları sayesinde GSM8K'da %5,8'den %10,7'ye yükseldi — yaklaşık 5 puanlık mutlak artış. CommonsenseQA'da STaR eğitimi görmüş GPT-J 6B, %72,5'e ulaştı; bu, elle etiketlenmiş gerekçelerle eğitilmiş, yaklaşık 30 kat daha büyük bir model olan fine-tune edilmiş GPT-3 175B (~%73) ile karşılaştırılabilir.

### V-STaR: DPO ile bir doğrulayıcı eğitin

STaR yanlış gerekçeleri atar. Hosseini ve ark. (2024) şunu gözlemledi: bunlar da veri; her (gerekçe, "bu doğru mu" çifti) bir doğrulayıcı eğitebilir. Doğru ve yanlış çözümler üzerinde Doğrudan Tercih Optimizasyonu (Direct Preference Optimization — DPO) kullanarak bir sıralayıcı (ranker) oluştururlar. Çıkarım sırasımda N gerekçe örnekleme yapılır ve doğrulayıcının en yüksek tercihini seçersiniz.

Raporlanan fark: GSM8K ve MATH'ta önceki öz-iyileştirme temellerine göre +4 ile +17 puan; kazançların çoğu, ek generator fine-tuning'inden değil, çıkarım sırasındaki seçim için doğrulayıcıdan gelir.

### Quiet-STaR: her token için iç gerekçe

Zelikman ve ark. (2024) şunu sordu: ya model her token pozisyonunda, yalnızca soru ve cevap arasında değil, kısa bir iç gerekçe üretmeyi öğrenirse? Quiet-STaR, her tahmin edilen token'dan önce gizli bir "düşünce" üretmeyi eğitir ve ardından düşünce-farkındalıklı tahmini temel tahminle öğrenilmiş bir ağırlıkla karıştırır.

Sonuç: Mistral 7B, GSM8K'da %5,9'dan %10,9'a ve CommonsenseQA'da %36,3'ten %47,2'ye görev-başlı fine-tuning olmadan mutlak sıfır-shot (zero-shot) iyileşmeler elde etti. Model "ne zaman düşüneceğini" öğrendi; zor token'lar daha uzun iç gerekçe alır, kolay olanlar neredeyse hiç almaz.

### Neden üçü de aynı güvenlik endişesini paylaşıyor

Üç yöntem de nihai cevabı gradyan sinyali olarak kullanır. Kusurlu bir mantıkla — bir kısayolu istismar ederek, tahminde bulunarak veya genelleşmeyen bir kalıp kullanarak — doğru cevaba ulaşan bir gerekçe olumlu olarak güçlendirilir. Dağıtım-içindeki (in-distribution) sorunlarda kısayol işe yarar. Dağıtım-dışındaki (out-of-distribution) sorunlarda sessizce bozulur.

V-STaR'ın doğrulayıcısı, gerekçeleri sıralamayı öğrenerek bunu hafifletir, ancak doğrulayıcı aynı etiket kümesi üzerinde eğitilir. Düzgün biçimlendirilmiş yanlış mantığı dürüst belirsizlikten (uncertainty) tercih etmeyi öğrenebilir. Daha güvenli tasarım, STaR tarzı veriyi (a) süreç denetimli ödül modelleriyle (process-supervised reward models — yalnızca ara adımları ödüllendiren, yalnızca cevapları değil) ve (b) basit kısayolları bozan tutulmuş OOD değerlendirmesiyle birleştirmektir.

### Karşılaştırma

| Yöntem | Eğitim sinyali | Çıkarım maliyeti | Veri israfı | Bilinen hata modu |
|---|---|---|---|---|
| STaR | (gerekçe, cevap) doğruysa tut | 1x | tüm yanlış gerekçeleri atar | kısayol gerekçeleri |
| STaR + rasyonalizasyon | yukarıdakine + doğru cevap ipucuyla yeniden deneme | 1x | daha az | rasyonelize gerekçeler tutarsız olabilir |
| V-STaR | STaR + her iki sınıftan DPO doğrulayıcısı | Nx (N'den en iyi) | minimal | doğrulayıcı kendinden emin yanlışlığı pekiştirebilir |
| Quiet-STaR | her token gerekçesi + karıştırma ağırlığı | 1,5-3x | minimal | hâlâ cevaba koşullu gradyan |

### 2026 yığınında nerede duruyor

STaR eskidir. Ancak kalıp 2025-2026'da her yerde tekrar ortaya çıkıyor. Doğrulanabilir matematik problemleri üzerindeki RL (DeepSeek-R1, Kimi-k1.5, o1), STaR'ın cevaba koşullu gradyan sinyalinin ölçeklendirilmiş halidir. Süreç ödül modelleri (process reward models — Lightman ve ark., 2023; OpenAI'ın "Let's verify step by step" çalışması), süreç denetimli alternatiftir. AlphaEvolve (Ders 3), etiket yerine bir program değerlendiricisi kullanan, kod için STaR'dır. Darwin Godel Machine (Ders 4), agent iskeletinin (scaffolding) kendisi için STaR'dır.

STaR'ı anlamak hepsini birbirine bağlar. Bu, asgari düzeyde çalışabilir öz-iyileştirme döngüsüdür (minimum viable self-improvement loop).

## Kullan

`code/main.py`, basit bir aritmetik görevi üzerinde simüle edilmiş bir STaR döngüsü çalıştırır. Şunları görebilirsiniz:

- Doğruluk, bootstrap turları boyunca nasıl yükselir.
- Kısayollar nasıl sızar: simülatör, zamanın %40'ında doğru cevaba ulaşan ancak kötü genelleşen "tembel" bir gerekçe sınıfı içerir. STaR'ın bunları tutup tutmadığına bakın.
- Bir doğrulayıcı (V-STaR tarzı) çıkarım sırasında nasıl yardımcı olur, ancak eğitim sırasında tanıtılan kısayolları tam olarak nasıl budayamaz.

## Üret

`outputs/skill-star-loop-reviewer.md`, önerilen bir kendi-kendine-öğrenen akıl yürütme boru hattını (pipeline) eğitimden önce denetlemenize yardımcı olur.

## Alıştırmalar

1. Simülatörü çalıştırın. Kısayol sıklığını sıfıra, ardından 0,4'e ayarlayın. Her iki çalışma da eğitim dağıtımında %90'ın üzerine çıksa bile, nihai doğruluk ne kadar farklılaşır?

2. Simülatöre tutulmuş bir OOD testi ekleyin. Farklı bir dağıtımdan sorular çizin ve bootstrap edilmiş modeli hem dağıtım-içinde hem de OOD kümeleri üzerinde değerlendirin. Farkı nicelleştirin.

3. Quiet-STaR makalesini okuyun (arXiv:2403.09629) Bölüm 3. "Düşünce sonu" (end-of-thought) token'ını ve karıştırma-ağırlığı başlığını (mixing-weight head) her biri üç cümleyle açıklayın.

4. STaR'ın doğruysa-tut filtresini, her gerekçe adımını bağımsız olarak ödüllendiren süreç denetimli bir alternatifle karşılaştırın. Etiketleme maliyeti farkını ve olası kalite farkını belirleyin.

5. Dağıtılmış bir modelde kısayol gerekçelerini yakalayacak bir değerlendirme tasarlayın. Mükemmel olmasına gerek yok; STaR döngüsünün pekiştireceği en basit kısayolları bozması yeterli.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| STaR | "Kendi Kendine Öğrenen Akıl Yürütücü" | Model tarafından üretilen, doğru cevaba ulaşan gerekçeler üzerinde fine-tune et; tekrarla |
| Rasyonalizasyon (Rationalization) | "İpucu eklenmiş yeniden deneme" | Doğru cevabı enjekte edin ve temel modelin başarısız olduğu sorularda gerekçe üretmesi için tekrar sorun |
| V-STaR | "Doğrulayıcı STaR" | Doğru ve yanlış gerekçeler üzerinde DPO ile doğrulayıcı eğitin, çıkarım sırasındaki seçim için kullanın |
| Quiet-STaR | "Her token için gerekçeler" | Her token pozisyonunda gizli düşünceler üretin; temel tahminle karıştırın |
| Cevaba koşullu gradyan (Answer-conditioned gradient) | "Sonuca dayalı sinyal" | Eğitim döngüsü yalnızca nihai cevapları ödüllendirir, akıl yürütme adımlarını değil |
| Süreç ödül modeli (Process reward model) | "Adım düzeyinde doğrulayıcı" | Adım başına doğruLUK üzerine eğitilmiş ödül modeli — STaR'ın zıddı |
| Kısayol gerekçe (Shortcut rationale) | "Doğru cevap, yanlış mantık" | Genelleşmeyen bir kalıp aracılığıyla etikete ulaşan gerekçe; STaR bunları korur |

## İleri Okuma

- [Zelikman ve ark. (2022). STaR: Bootstrapping Reasoning With Reasoning](https://arxiv.org/abs/2203.14465) — orijinal makale.
- [Hosseini ve ark. (2024). V-STaR: Training Verifiers for Self-Taught Reasoners](https://arxiv.org/abs/2402.06457) — çıkarım sırasındaki seçim için DPO doğrulayıcısı ekler.
- [Zelikman ve ark. (2024). Quiet-STaR: Language Models Can Teach Themselves to Think Before Speaking](https://arxiv.org/abs/2403.09629) — her token için iç gerekçeler.
- [Lightman ve ark. (2023). Let's Verify Step by Step](https://arxiv.org/abs/2305.20050) — süreç ödül modelleri, alternatif gradyan sinyali.
- [DeepSeek-R1 makalesi (arXiv:2501.12948)](https://arxiv.org/abs/2501.12948) — doğrulanabilir görevlerde RL, sınır eğitimine ölçeklendirilmiş STaR.
