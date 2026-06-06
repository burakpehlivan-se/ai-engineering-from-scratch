---
name: document-ai-stack-picker
description: Alan, ölçek ve düzenleyici ihtiyaçlara göre bir doküman-AI projesi için OCR işlem hattı, OCR'sız uzman ve VLM-yerel arasında seçim yapın.
version: 1.0.0
phase: 12
lesson: 22
tags: [document-ai, ocr, donut, nougat, paligemma, vlm-native]
---

Bir doküman-AI projesi (alan: faturalar / bilimsel makaleler / formlar / karışık; ölçek: günde sayfa sayısı; kalite çubuğu; düzenleyici ihtiyaçlar) verildiğinde, bir yığın seçin ve referans bir yapılandırma üretin.

Üretin:

1. Yığın seçimi. Dönem 1 (OCR işlem hattı + LayoutLMv3), Dönem 2 (Donut / Nougat OCR'sız), Dönem 3 (VLM-yerel) veya hibrid.
2. Sayfa başına maliyet tahmini. Seçilen yığında token sayısı ve gecikme.
3. Doğruluk beklentisi. DocVQA + ChartQA + alana özgü kıyaslamalar.
4. El yazısı stratejisi. Maliyete duyarsız için VLM-yerel; ölçek için özelleşmiş TrOCR + yönlendirme.
5. Matematik / LaTeX çıktısı. Bilimsel makaleler için Nougat; diğerleri için VLM.
6. Düzenleyici geri dönüş. Çapraz-kontrol denetim günlüğü ile hibrid.

Sert reddetmeler:
- Sayfa başına >1M / gün için maliyet analizi olmadan VLM-yerel önermek. Sayfa başına 2576px'te token maliyeti önemlidir.
- Denetim yolları olmadan düzenlenmiş iş akışları için tek-model çözümleri önermek.
- Nougat'ın taranmış faturaları işlediğini iddia etmek. İşlemez -- bilimsel makale uzmanıdır.

Ret kuralları:
- Ölçek >10M sayfa/gün ise, Dönem 3'ü reddedin ve örnekleme doğrulayıcısı olarak Dönem 3 ile Dönem 1'i önerin.
- Alan el yazısı-ağırlıklı ise, OCR işlem hattını reddedin ve VLM-yerel + el yazısı uzmanı (TrOCR) önerin.
- Denklemler için LaTeX sadakati gerekliyse, döngüde Nougat'ı zorunlu kılın.

Çıktı: Yığın, maliyet, doğruluk, el yazısı, matematik, düzenleyici ile tek sayfalık bir plan. arXiv 2308.13418 (Nougat), 2204.08387 (LayoutLMv3), 2111.15664 (Donut) ile bitirin.
