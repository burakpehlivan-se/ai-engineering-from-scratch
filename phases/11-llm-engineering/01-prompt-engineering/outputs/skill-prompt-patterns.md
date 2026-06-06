---
name: skill-prompt-patterns
description: Görev türüne, güvenilirlik gereksinimlerine ve hedef modele göre doğru prompt kalıbını seçme karar çerçevesi
version: 1.0.0
phase: 11
lesson: 01
tags: [prompt-engineering, patterns, llm, temperature, cross-model, few-shot, chain-of-thought]
---

# Prompt Kalıbı Seçim Kılavuzu

LLM destekli bir özellik oluştururken, prompt'u yazmadan önce prompt kalıbınızı seçin. Kalıp yapıyı belirler. İçerik onu doldurur.

## Kalıp Karar Matrisi

| Görev Türü | Birincil Kalıp | İkincil Kalıp | Sıcaklık | Few-Shot Gerekli mi? |
|-----------|----------------|-------------------|-------------|-----------------|
| Veri çıkarma | Şablon Doldurma | Few-Shot | 0.0 | Evet (2-3 örnek) |
| Sınıflandırma | Few-Shot | Koruma Duvarı (Guardrail) | 0.0 | Evet (3-5 örnek) |
| Özetleme | Kişilik + Şablon | Hedef Kitle Adaptasyonu | 0.3 | Hayır |
| Kod üretimi | Kişilik | Zincir-düşünce (Chain-of-Thought) | 0.0 | İsteğe bağlı |
| Yaratıcı yazı | Kişilik | Eleştiri (Critique) | 0.7-1.0 | Hayır |
| Çok adımlı akıl yürütme | Zincir-düşünce | Ayrıştırma (Decomposition) | 0.3 | İsteğe bağlı |
| Soru cevaplama | Kişilik + Koruma Duvarı | Sınır (Boundary) | 0.3 | Hayır |
| Prompt üretimi | Meta-Prompt | Eleştiri | 0.7 | Evet (1-2 örnek) |
| İçerik moderasyonu | Koruma Duvarı + Sınır | Few-Shot | 0.0 | Evet (5+ örnek) |
| Çeviri/adaptasyon | Hedef Kitle Adaptasyonu | Few-Shot | 0.3 | Evet (2-3 örnek) |

## Her Kalıp Ne Zaman Kullanılır

**Kişilik (Persona) Kalıbı**: temel olarak her prompt için kullanın. Tek soru, rolü ne kadar spesifik yapacağınızdır. Genel görevler için geniş bir rol yeterlidir. Alana özgü görevler için, rol alanı, kıdem düzeyini ve bağlamı adlandırmalıdır.

**Few-Shot Kalıbı**: çıktı formatı içerikten daha önemli olduğunda kullanın. Modelin belirli bir JSON şekli, CSV formatı veya sınıflandırma etiketi üretmesi gerekiyorsa, örnekler talimatlardan daha etkilidir. Kural başparmak: basit formatlar için 2-3 örnek, karmaşık veya belirsiz formatlar için 5+.

**Zincir-düşünce (Chain-of-Thought) Kalıbı**: matematik, mantık, çok adımlı analiz ve modelin "çalışmasını göstermesi" gereken herhangi bir görev için kullanın. Akıl yürütme görevlerinde doğruluğu %10-40 artırır (Wei ve ark., 2022). Basit olgusal aramalar veya çıkarma için KULLANMAYIN — token israf eder.

**Şablon Doldurma (Template Fill) Kalıbı**: her çıktının aynı şekle sahip olması gereken yapılandırılmış çıkarma için kullanın. Sıcaklık=0.0 ve eksik alanlar için açık "N/A" işleme ile en iyi çalışır.

**Eleştiri (Critique) Kalıbı**: kalitenin hızdan daha önemli olduğu durumlarda kullanın. Model üretir, eleştirir ve iyileştirir. Token maliyetini kabaca ikiye katlar, ancak doğruluğu ve tamlığı önemli ölçüde artırır. Yüksek riskli çıktılar (raporlar, öneriler, kamuya dönük içerik) için en iyisidir.

**Koruma Duvarı (Guardrail) Kalıbı**: kullanıcıya dönük her sistem için kullanın. Her zaman şunları dahil edin: kapsam sınırları, kapsam dışı istekler için reddetme davranışı ve açık "bilmiyorum" işleme. Uygulama tarafında girdi doğrulaması ile birleştirin.

**Meta-Prompt Kalıbı**: yeni görevler için prompt üretmek amacıyla kullanın. Sıfırdan bir prompt yazmak yerine, görevi tanımlayın ve modelin prompt'u yazmasına izin verin. Sonra test edin ve yineleyin. İlk prompt geliştirmede zaman kazandırır.

**Ayrıştırma (Decomposition) Kalıbı**: böl-ve-yönet'ten fayda gören karmaşık problemler için kullanın. Model problemi parçalara ayırır, her birini çözer ve birleştirir. 3-7 alt problemi olan görevler için en etkilidir.

**Hedef Kitle Adaptasyonu (Audience Adaptation) Kalıbı**: aynı içeriğin farklı hedef kitlelere hizmet etmesi gerektiğinde kullanın. Hedef kitlenizi açıkça belirtin — modelin bağlamdan tahmin etmesine güvenmeyin.

**Sınır (Boundary) Kalıbı**: belirli soru türlerini ASLA cevaplamaması gereken üretim sistemleri için kullanın. Koruma duvarlarından daha güçlüdür, çünkü kesin bir reddetme mesajı ile sert bir kapsam tanımlar. Uyumluluk açısından hassas alanlar için gereklidir.

## Modeller Arası Uyumluluk

GPT-4o, Claude 3.5 Sonnet, Gemini 1.5 Pro ve Llama 3 arasında ne kadar tutarlı çalıştıklarına göre sıralanan kalıplar:

| Kalıp | Modeller Arası Tutarlılık | Notlar |
|---------|------------------------|-------|
| Few-Shot | Çok yüksek | Örnekler tüm modeller arasında iyi aktarılır |
| Şablon Doldurma | Çok yüksek | Açık yapı sapma için az yer bırakır |
| Zincir-düşünce | Yüksek | Tüm büyük modeller "adım adım düşün"ü destekler |
| Kişilik | Yüksek | Her yerde çalışır, ancak farklı modeller farklı rol spesifitesi düzeylerine yanıt verir |
| Koruma Duvarı | Orta | Claude koruma duvarlarını en sıkı takip eder; GPT-4o uzun konuşmalarda bazen sapar |
| Eleştiri | Orta | Öz-eleştirinin kalitesi modele göre önemli ölçüde değişir |
| Meta-Prompt | Orta | GPT-4o ve Claude farklı prompt stilleri üretir |
| Sınır | Düşük-Orta | Reddetme davranışı değişir; model başına test edin |

## Yaygın Hatalar

1. **Her şey için Zincir-düşünce kullanmak**: CoT, token ve gecikme ekler. Yalnızca akıl yürütme adımları gerektiğinde kullanın.
2. **Çok fazla kısıtlama**: 5-7'den fazla kısıtlama ile model bazılarını düşürmeye başlar. En önemli 3 tanesini önceliklendirin.
3. **Çelişkili kişilik + kısıtlamalar**: "Yaratıcı bir yazarsınız" + "Asla mecaz kullanmayın" modeli karıştırır.
4. **Sıcaklık belirtmemek**: deterministik çıktıya ihtiyacınız olduğunda sıcaklığı varsayılanda (genellikle 1.0) bırakmak.
5. **Modeller arasında prompt'ları kopyalayıp yapıştırmak**: her zaman test edin. GPT-4o için ayarlanmış bir prompt, Claude'da düşük performans gösterebilir ve bunun tersi de geçerlidir.
6. **Sistem mesajını göz ardı etmek**: kalıcı kurallar için sistem mesajını kullanmak yerine her şeyi kullanıcı mesajına koymak.
7. **Olumsuz kısıtlamalara aşırı güvenmek**: "X, Y, Z, A, B, C YAPMAYIN" "YALNIZCA W yap" ifadesinden daha az etkilidir. Olumlu çerçeveleme modele net bir hedef verir.

## Güvenilirlik Hedefleri

| Kullanım Senaryosu | Kalıp Kombinasyonu | Beklenen Doğruluk | Token Maliyeti |
|----------|-------------------|-------------------|------------|
| Üretim çıkarma | Şablon + Few-Shot | %95+ | Düşük (500-1K) |
| Kullanıcıya dönük S/C | Kişilik + Koruma Duvarı + Sınır | %90+ | Orta (1-2K) |
| Kod üretimi | Kişilik + Zincir-düşünce | %85+ | Orta (1-3K) |
| İçerik üretimi | Kişilik + Eleştiri | %90+ kalite | Yüksek (2-4K, çift geçiş) |
| Sınıflandırma | Few-Shot + Koruma Duvarı | %95+ | Düşük (300-800) |
| Karmaşık analiz | Ayrıştırma + Zincir-düşünce | %85+ | Yüksek (3-5K) |
