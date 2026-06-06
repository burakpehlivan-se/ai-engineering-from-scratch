---
name: skill-cot-patterns
description: Görev karmaşıklığına, doğruluk gereksinimlerine ve maliyet kısıtlamalarına göre doğru akıl yürütme tekniğini seçme karar çerçevesi
version: 1.0.0
phase: 11
lesson: 02
tags: [chain-of-thought, few-shot, self-consistency, tree-of-thought, react, reasoning, prompting]
---

# Akıl Yürütme Tekniği Seçim Kılavuzu

Bir LLM'nin bir problem üzerinde akıl yürütmesi gerektiğinde, prompt'u yazmadan önce tekniği seçin. Teknik, akıl yürütme mimarisini belirler. Prompt onu doldurur.

## Hızlı Karar Ağacı

1. Görev basit bir olgusal arama mı yoksa tek adımlı sınıflandırma mı?
   - Evet: **zero-shot** kullanın. CoT, doğruluk kazanımı olmadan maliyet ekler.
   - Hayır: devam edin.

2. Görev çok adımlı akıl yürütme (matematik, mantık, planlama) gerektiriyor mu?
   - Evet: **Zincir-düşünce (Chain-of-Thought)** kullanın. Adım 3'e devam edin.
   - Hayır: format önemliyse **few-shot**, önemli değilse zero-shot kullanın.

3. Tek bir akıl yürütme hatası kabul edilebilir mi?
   - Evet: **few-shot CoT** kullanın (tek örnek, sıcaklık 0.0).
   - Hayır: **ö z-tutarlılık (self-consistency)** kullanın (N=5, sıcaklık 0.7). Adım 4'e devam edin.

4. Problem, birçok olası yola sahip bir arama/planlama problemi mi?
   - Evet: **Düşünce Ağacı (Tree-of-Thought)** kullanın.
   - Hayır: öz-tutarlılık yeterlidir.

5. Görev dış bilgi veya hesaplama gerektiriyor mu?
   - Evet: **ReAct** kullanın (akıl yürütme + araç çağrıları).
   - Hayır: saf akıl yürütme teknikleri yeterlidir.

## Teknik Matrisi

| Teknik | Doğruluk Artışı | Maliyet Çarpanı | Gecikme | En İyi Olduğu Yer |
|-----------|--------------|-----------------|---------|----------|
| Zero-shot | Temel | 1x | ~1s | Basit görevler, olgusal S/C |
| Few-shot | +%5-15 | 1.2x | ~1s | Format eşleştirme, sınıflandırma |
| Zero-shot CoT | +%10-20 | 1.3x | ~1.5s | Hızlı akıl yürütme artışı |
| Few-shot CoT | +%15-25 | 1.5x | ~2s | Matematik, mantık, çok adımlı |
| Öz-Tutarlılık (N=5) | CoT üzerine +%2-5 | 5x | ~5s | Yüksek riskli akıl yürütme |
| Öz-Tutarlılık (N=10) | N=5 üzerine +%1-2 | 10x | ~10s | Yalnızca kritik kararlar |
| Düşünce Ağacı | Göreve bağlı | 10-40x | ~30s+ | Arama, planlama, bulmacalar |
| ReAct | Göreve bağlı | 3-10x | ~5-15s | Bilgi temelli görevler |
| Prompt Zincirleme | Tek üzerine +%5-10 | 2-5x | ~5-10s | Karmaşık çok parçalı görevler |

## Modele Özgü Kılavuz

### GPT-4o / GPT-4.1
- Güçlü temel akıl yürütme. Zero-shot CoT genellikle yeterlidir.
- 3 örnekli few-shot CoT, GSM8K'da %95'e ulaşır.
- Öz-tutarlılık marjinal kazanımlar sağlar (%95'ten %97'ye) -- yalnızca kritik görevler için buna değer.
- Cevap çıkarma için yapılandırılmış çıktıları yerel olarak destekler.

### Claude 3.5 Sonnet / Claude 3.7 Sonnet
- Yapılandırılmış prompt formatlarını (XML etiketleri) takip etmede mükemmel.
- XML sınırlayıcılı örneklerle few-shot CoT en iyi çalışır.
- Genişletilmiş düşünme (Extended thinking) (Claude 3.7) yerel CoT'dir -- bunun için prompt'a gerek yoktur.
- Öz-tutarlılık etkilidir çünkü Claude'un akıl yürütmesi sıcaklık 0.7'de iyi değişir.

### Llama 3.1/3.3 70B
- Few-shot CoT'den en çok faydalanır (zero-shot'a kıyasla daha büyük doğruluk farkı).
- Akıl yürütme görevleri için N=5 ile öz-tutarlılık önerilir.
- Ticari modellerden daha fazla açık format talimatına ihtiyaç duyar.
- Yerel çıkarımda ToT pahalıdır -- yalnızca toplu işleme için düşünün.

### Gemini 2.5 Pro
- Kutudan çıktığı haliyle çok adımlı akıl yürütmede güçlü.
- Düşünce modu, prompt mühendisliği olmadan yerleşik CoT sağlar.
- Few-shot örnekleri, doğruluktan çok format tutarlılığına yardımcı olur.
- Büyük bağlam penceresi (1M), örnek-ağırlıklı few-shot'u pratik hale getirir.

## Anti-Kalıplar

**Basit görevler için CoT**: "2+2 nedir? Adım adım düşünelim" demek token israf eder. Model basit aritmetiği akıl yürütme izleri olmadan doğru yapar. CoT, 3+ adım olduğunda yardımcı olur.

**Sıcaklık 0.0'da öz-tutarlılık**: tüm N örnekler özdeş olacaktır. Çeşitli akıl yürütme yolları için sıcaklık > 0 (0.5-0.8 önerilir) kullanmalısınız.

**Her şey için ToT**: ToT, b=dallanma faktörü ve d=derinlik olmak üzere O(b^d) LLM çağrısı gerektirir. b=3, d=3 olan bir ağaç 39'a kadar çağrı gerektirir. Daha ucuz tekniklerin başarısız olduğu problemler için saklayın.

**Kötü örneklerle few-shot**: akıl yürütme hataları içeren örnekler, modele bu hataları yapmayı öğretir. Her örnek doğrulanmalıdır. Bir yanlış örnek, doğruluğu sıfır örnekten daha fazla azaltabilir.

**Tutarlı bir format olmadan cevapları çıkarmak**: öz-tutarlılık, örnekler arasında cevapları karşılaştırmayı gerektirir. Cevap formatı değişirse ("18$", "18 dolar", "on sekiz"), oylama başarısız olur. Her zaman uygulayın: "Cevap [sayı]."

## Maliyet Optimizasyonu

GPT-4o fiyatlandırmasıyla günde 10.000 sorgu işleyen bir üretim sistemi için (girdi 1M için 2.50$, çıktı 1M için 10$):

| Teknik | Sorgu Başına Ortalama Token | Günlük Maliyet | Doğruluk |
|-----------|-----------------|------------|----------|
| Zero-shot | ~200 | ~5$ | %78 |
| Few-shot CoT | ~600 | ~15$ | %95 |
| Öz-Tutarlılık (N=5) | ~3,000 | ~75$ | %97 |
| ToT (b=3, d=2) | ~6,000 | ~150$ | Göreve bağlı |

Çoğu uygulama için maliyet-optimal strateji: few-shot CoT ile başlayın. Öz-tutarlılığı yalnızca güvenin düşük olduğu sorgular için ekleyin (Build It bölümünden eskalasyon kalıbı).

## Prompt Zincirleme ile Entegrasyon

Akıl yürütme teknikleri, prompt zincirleme ile birleşir:

**Zincir Adımı 1** (Çıkar): zero-shot, sıcaklık 0.0
**Zincir Adımı 2** (Akıl yürüt): few-shot CoT, sıcaklık 0.0
**Zincir Adımı 3** (Doğrula): N=3 ile öz-tutarlılık, sıcaklık 0.7

Bu üç adımlı zincir, tek bir CoT çağrısının ~3 katı maliyetle çıkarma hatalarını, akıl yürütme hatalarını yakalar ve doğrulama adımından bir güven puanı sağlar.

## Prompting'in Ötesine Geçme Zamanı

Prompt'ları mühendis etmeye uygulama kodu yazmaktan daha fazla zaman harcıyorsanız, şunları düşünün:

1. **İnce ayar (fine-tuning)**: 500+ etiketli örneğiniz varsa ve görev darsa
2. **DSPy derlemesi**: otomatik prompt optimizasyonu istiyorsanız
3. **Ajan çerçeveleri**: görev çok turlu araç kullanımı gerektiriyorsa (Faz 14)
4. **RAG**: modelin özel/güncel bilgiye erişmesi gerekiyorsa (Dersler 06-07)

Prompt'lama teknikleri temeldir. Herhangi bir modelle, herhangi bir sağlayıcıyla çalışır ve eğitim verisi gerektirmez. Ama sınırları vardır. Bir sonraki seviyeye ne zaman geçeceğinizi bilmek, tekniklerde ustalaşmak kadar önemlidir.
