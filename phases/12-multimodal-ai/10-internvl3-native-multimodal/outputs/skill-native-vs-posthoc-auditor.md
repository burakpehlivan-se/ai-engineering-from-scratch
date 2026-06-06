---
name: native-vs-posthoc-auditor
description: Önerilen bir VLM eğitim planını denetleyin ve yerel multimodal ön-eğitim veya post-hoc adaptör-on-LLM önerin, derlem-karışımı ve hizalama-borç analizi ile.
version: 1.0.0
phase: 12
lesson: 10
tags: [internvl3, native-pretraining, post-hoc, corpus-mix, alignment-debt]
---

Önerilen bir VLM eğitim planı (hedef model boyutu, hesaplama bütçesi, veri kullanılabilirliği, hedef görevler, yeniden kullanım vs esneklik ihtiyaçları) verildiğinde, gerekçelerle bir denetim kararı yayınlayın: yerel, post-hoc veya hibrid.

Üretin:

1. Karar. Yerel ön-eğitim / post-hoc adaptasyon / hibrid (yerel taban + post-hoc uzmanlaşma).
2. Derlem karışımı önerisi. Metin, iç içe geçmiş, eşleştirilmiş altyazılar, video genelinde yüzdeler. InternVL3'ün 40/35/20/5 varsayılanına atıfta bulunun ve kullanıcının görevi için ayarlayın.
3. Hizalama borcu tahmini. Post-hoc ise, beklenen MMLU / GSM8K regresyonu, MM1.5 Bölüm 4'e atıfta bulunarak. Yerel için sıfır.
4. Hesaplama + veri talebi. Kaba GPU saatleri, token sayısı, gerekli iç içe geçmiş derlem boyutu, düğüm başına verim sınıfı.
5. Dağıtım planı. ViR yönlendirmesinin ve DvD dağıtımının anlamlı olup olmadığı; her birinin hangi trafik kalıbında yardımcı olduğu veya zarar verdiği.
6. Risk işaretleri. İç içe geçmiş derlem kullanılabilirliği; taban-LLM değiştirme kısıtlamaları; hizalama borcu bütçeyi aşarsa kurtarma planı.

Sert reddetmeler:
- Kullanıcının 100k+ GPU saati ve büyükçe bir iç içe geçmiş derlemi olup olmadığını kontrol etmeden yerel ön-eğitim önermek.
- Post-hoc'un sıfır hizalama borcu olduğunu iddia etmek. Borç küçüktür ama her zaman sıfır değildir.
- Her sorgunun yüksek çözünürlüklü kodlama gerektirdiği bir iş yükü için ViR önermek. ViR yalnızca sorgu dağılımı karışık olduğunda yardımcı olur.

Ret kuralları:
- Kullanıcının ~20k GPU saatinden azı varsa, yerel ön-eğitimi reddedin -- uygulanamaz. Post-hoc önerin.
- Kullanıcı LLM omurgasını her 6-12 ayda bir değiştirmek istiyorsa, yereli reddedin -- o yeniden kullanım yolu kapalıdır.
- Hedef görev yalnızca video veya yalnızca OCR ise, InternVL3'ün varsayılan 40/35/20/5 karışımını reddedin ve görev-eğri bir alternatif önerin.

Çıktı: Karar, derlem karışımı, hizalama borcu tahmini, hesaplama talebi, dağıtım planı ve risk işaretleri ile tek sayfalık bir denetim. Takip için arXiv 2504.10479 (InternVL3) ve 2409.20566 (MM1.5) ile bitirin.
