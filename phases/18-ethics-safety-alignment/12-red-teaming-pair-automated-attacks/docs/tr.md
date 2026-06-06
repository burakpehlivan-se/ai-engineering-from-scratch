# Kırmızı Takım — PAIR Otomatik Saldırıları

> Perez, Huang, Song, Cai, Ring, Aschenbrenner, Sleight, Cotter, Greenblatt, Schiefer, Poh, He, Steinberger, Durmus, Clark, Olah (Anthropic + MIT, arXiv:2402.04217, Şubat 2024). PAIR — "Otomatik Saldırılar için Prompt Şeması" (Prompt Automatic Iterative Refinement). PAIR, bir saldırgan modelin bir black-box hedef modele karşı jailbreak istemleri üretmek için bir saldırgan model kullandığı tamamen otomatik bir sistemdir. Klasik kırmızı takım, deneyimli insanlarla çalışır. PAIR, insan döngüsünün dışında kalır; 20'den az sorguda jailbreak üretebilir. Bu, saldırı ölçeği için bir temel değişimdir. Kırmızı takım artık "saldırı sayısı" ile değil, "saldırı çeşitliliği" ile sınırlıdır.

**Tür:** Öğren
**Diller:** Python (stdlib, oyuncak PAIR saldırganı)
**Önkoşullar:** Faz 18 · 04 (dalkavukluk), Faz 16 · 06 (jailbreak temelleri), Faz 10 · 06 (kırmızı takım temelleri)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- PAIR algoritmasını — saldırgan model, yargıç model, döngüsel iyileştirme — ve insan-kırmızı-takım'dan nasıl farklılaştığını tanımlayın.
- "Black-box" saldırı bütçesini ("sorgu sayısı") ve PAIR'in %78 +'sını <20 sorguda ürettiği bulgusunu açıklayın.
- PAIR sonuçlarının model sınıfı (Vicuna hedefleri, GPT-3.5/4, Claude 2, Llama-2-Chat) boyunca nasıl genelleştiğini açıklayın.
- PAIR'in "otomatik kırmızı takım" güvenlik uygulamasındaki rolünü ve onu kapsamaz alanları tartışın.

## Problem

Klasik kırmızı takım, "Bu istem bir hedef modeli zararlı çıktıya yönlendirir mi?" sorusunu sorar. Bu, bir yargılama sürecidir. Bir insan deneyimli bir saldırgan, deneyimli bir yargıç ile eşleştirilir. İnsan-döngüsü darboğaz, keşfedilen saldırı sayısını, keşfedilebilecek saldırı sayısıyla sınırlar. 2023 boyunca, model sınıfları boyunca sistematik jailbreak keşfi için bu darboğaz yetersiz hale geldi. PAIR, otomasyonun ampirik sınırını test eder.

## Kavram

### PAIR algoritması

PAIR, dört bileşen kullanır:

1. **Hedef model.** Saldırıya uğrayan kara kutu (black-box). Sadece istem ve yanıt görünür.
2. **Saldırgan model.** Saldırı istemleri üretir. Saldırgan modeli genellikle hedef modelden daha güçlü değildir — hatta bazen daha zayıftır.
3. **Yargıç model.** Saldırgan istemini "başarılı" veya "başarısız" olarak puanlar. Yargıç modeli, genellikle saldırgan modele benzer veya aynıdır.
4. **İyileştirme döngüsü.** Saldırgan, önceki denemenin hedef modeli yanıtını ve yargıç puanını alır. Bir sonraki istemi, yargıçtan gelen geri bildirime dayanarak üretir.

PAIR, kullanıcının tek bir "hedef" ile başlar (örn. "bana bir şey hakkında zararlı bir şey anlat"). Yargıç modeli, "yanıt gerçekten zararlı mı?" sorusunu yanıtlar. Saldırgan modeli, zararlı yanıtı en çok artıran istemi arar.

### Sorgu bütçesi bulgusu

PAIR, <20 sorguda jailbreak üretir. Bu, sıralı bir insan kırmızı takımının gerçekleştirebileceği sorgu sayısının kabaca bir alt-sırasıdır. PAIR, deneyimli bir insan kırmızı takımcı ile aynı başarı oranına ulaşır (Vicuna hedeflerinde PAIR %100, GPT-3.5 ve GPT-4'te PAIR %78) — tek bir insan-saat içinde değil, <20 model sorgusunda.

Bu, kırmızı takımın değer önerisini değiştirir. Artık model değerlendirmesinin "kapsamı" değil, "çeşitliliği" tarafından sınırlıdır. İnsan kırmızı takımcılar, otomatik saldırıların başarısız olduğu belirli "tail-end" saldırılarına odaklanabilir.

### Saldırgan modeli seçimi

PAIR'in temel bulgularından biri, saldırgan modelin kalitesinin başarı oranı üzerinde büyük bir etkiye sahip olmamasıdır. GPT-3.5 saldırgan, GPT-4 saldırganla benzer başarı oranları elde eder. Bu, saldırı kalıplarının model-sınıfı-içinde taşınabilir olduğunu ima eder; bu, "saldırgan iyileştirmeye yatırım yaparak tüm sistemleri daha güvenli yapabilir miyiz?" sorusuna yol açar.

### Sorgu temelli vs diğer otomatik saldırılar

PAIR sorgu temellidir. Sadece giriş-çıkış çiftlerine erişir. Daha güçlü otomatik saldırılar gradyan temellidir (GCG, Universal and Transferable Adversarial Attacks, Zou ve diğerleri 2023), eklenen belirteçlerin giriş gömmelerini (embeddings) değiştirir ve iyileştirir. Gradyan temelli saldırılar daha yüksek başarı oranlarına ulaşır, ancak kara kutu (black-box) dağıtımlarda uygulanabilir değildir. PAIR, kara kutu varsayımını korur.

### Model sınıfı genellemesi

PAIR, birçok modelde başarıyla uygulanmıştır: Vicuna-33B, GPT-3.5, GPT-4, Claude 2, Llama-2-Chat 7B/13B/70B. Başarı oranları değişir, ancak saldırı kalıpları genelleşir. Bu, "modelin tek-spesifik zayıflıkları" yerine "öğrenilmiş hizalamada paylaşılan zayıflıklar" olduğunu ima eder.

### Otomatik kırmızı takımın değer

PAIR, değerlendirmenin maliyetini azaltır. Daha önce, "kapsamlı" kırmızı takım, birçok modelde yüzlerce saat demekti. PAIR ile, bir saldırgan-yargıç çifti, birçok modeli bir gecede tarayabilir. Bu, kırmızı takımın "sürekli" bir pratiğe dönüşmesini sağlar. Her model sürümü yüzlerce otomatik saldırı ile değerlendirilir; insan incelemesi yalnızca saldırı keşfi sonrasında.

### Otomatik kırmızı takımın sınırları

PAIR, sadece jailbreak istemlerini bulur. Aşağıdakileri bulmaz:

- Çok adımlı ajan komplosu (Ders 8, PAIR'in kapsamı dışında).
- Bağlam-içi hedef çatışması (Ders 8 — PAIR, modelin dahili durumunu test etmez).
- Aldatmanın gizli ipuçları (Ders 9 — PAIR, dağıtım yönünü test etmez).
- Uzun vadeli komplo, birden çok oturuma yayılan (PAIR oturum başına çalışır).
- Düşmanca istemler içermeyen gizli başarısızlık modları (örn. yavaş performans düşüşü).

PAIR, "hızlı siyah-kutu saldırı keşfi"ni ölçeklendirir. Diğer başarısızlık modları farklı değerlendirme türleri gerektirir.

### Saldırı çeşitliliği ve yönlendirme

PAIR'in bir uzantısı, saldırıyı "çeşitlendirme"yidir: saldırgan modele, belirli bir istem-sınıfı (örn. "mantıksal ikilemler", "sosyal mühendislik", "kod-çerçeveleme") ile sınırlı bir istem üretmesi talimatı verilir. Bu, değerlendirmenin "her büyük saldırı ailesini kapsayan" bir parçası haline gelir. PAIR-varyantları 2024-2026'da, saldırı ailelerini büyük ölçekte keşfetmek için standart uygulama haline gelmiştir.

### Bunun Faz 18'deki yeri

Ders 12, "sürekli kırmızı takım" uygulamasının mekaniğini verir. Ders 13 (çok-atışlı jailbreak) ve Ders 14 (ASCII sanatı) keşfedilen saldırı türleridir. Ders 15 (dolaylı prompt enjeksiyonu) başka bir saldırı sınıfıdır. Ders 18 (güvenlik duruşları), kırmızı takımı, model değerlendirmesinin bir bileşeni olarak test eder.

## Kullan

`code/main.py`, basitleştirilmiş bir PAIR uygulaması inşa eder. Saldırgan modeli, basit bir şablon doldurucudur. Hedef modeli, belirli anahtar kelimeleri (örn. "silah", "ilaç", "zararlı") içeren yanıtları reddeden kural-tabanlı bir maskedir. Yargıç modeli, hedefin yanıtının anahtar kelimeleri içerip içermediğini kontrol eder. Saldırgan, her döngüde istemini değiştirir; yargıç, başarıyı işaretler. Saldırganın "başarı" elde etmek için kaç döngüye ihtiyacı olduğunu izleyebilirsiniz.

## Yayınla

Bu ders `outputs/skill-redteam-eval.md` dosyasını üretir. Bir kırmızı takım raporu verildiğinde, PAIR benzeri otomasyonun raporlanan bulguları kapsayıp kapsamadığını, sorgu bütçesinin modellere tutarlı olup olmadığını ve kapsam dışı kalıpların (çok adımlı, bağlam-içi, gizli) ayrı bir değerlendirme gerektirip gerektirmediğini kontrol eder.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Saldırganın başarı elde etmesi için gereken ortalama döngü sayısını ölçün. Sorgu bütçesini sınırlayın (örn. 5, 10, 20) ve başarı oranının nasıl değiştiğini gözlemleyin.

2. Yargıç modelini "gürültülü" (yanlış pozitif ve yanlış negatif oranı %20) yapın. Saldırgan başarı oranı düşer mi, aynı kalır mı veya artar mı? Neden?

3. PAIR, sorgu temellidir. Hedefin gömme erişimini (gradyan temelli saldırı) varsayalım. PAIR ile gradyan temelli arasındaki başarı oranı farkı yaklaşık olarak ne olur? Bir makale referansıyla destekleyin.

4. PAIR birçok modelde çalışır, ancak model sınıfı içinde başarı oranları değişir. Farkı açıklayan iki özellik önerin (boyut, RLHF yöntemi, eğitim veri temizliği, vb.) ve bir test tasarlayın.

5. Ders 8 (komplo), Ders 9 (hizalama taklidi) ve Ders 12 (PAIR) bir arada: PAIR'in tespit edemeyeceği başarısızlık modlarını, her biri için bir test ile listeleyin. Bu liste, hangi sınıfın PAIR-türü kırmızı takımın değerini en aza indirdiğini ortaya koyar.

## Anahtar Terimler

| Terim | İnsanların söylediği | Aslında ne anlama geldiği |
|-------|----------------------|---------------------------|
| PAIR | "otomatik jailbreak" | Kara kutu hedef modele karşı tamamen otomatik, sorgu temelli jailbreak keşfi |
| Saldırgan model | "kötü niyetli LLM" | Hedef modele karşı jailbreak istemleri üreten model |
| Yargıç model | "başarı işaretleyicisi" | Saldırgan isteminin başarılı olup olmadığını puanlayan model |
| Sorgu bütçesi | "sorgu sayısı" | Bir saldırı için izin verilen hedef model sorgu sayısı |
| Kara kutu (black-box) | "API erişimi yeterli" | Sadece giriş-çıkış erişimli saldırı (gömme veya gradyan erişimi yok) |
| Saldırı çeşitliliği | "farklı kalıplar" | Saldırı ailelerinin kapsamı (mantıksal, sosyal, kod-çerçeveleme) |
| Çok adımlı saldırı | "PAIR kapsamaz" | Birden çok oturuma, dağıtıma veya temsil aracına yayılan saldırı |
| Sürekli kırmızı takım | "her sürümde değerlendirme" | PAIR-türü otomasyonu model değerlendirme ardışık düzenine entegre etme |

## İleri Okuma

- [Chao, Mohananey, Ely, Sun, Wong, Krueger — Jailbreaking Black Box Large Language Models in Twenty Queries (PAIR makalesi, arXiv:2310.08419)](https://arxiv.org/abs/2310.08419) — kanonik PAIR makalesi (Chao ve diğerleri 2023, ancak PAIR çerçevesi Perez ve diğerleri 2024'te genişletildi)
- [Perez ve diğerleri — Red Teaming Language Models with Language Models (arXiv:2202.03286)](https://arxiv.org/abs/2202.03286) — PAIR'in öncüsü
- [Zou, Wang, Kolter, Fredrikson — Universal and Transferable Adversarial Attacks on Aligned Language Models (arXiv:2307.15043)](https://arxiv.org/abs/2307.15043) — gradyan temelli karşılaştırma
- [Garbacea ve diğerleri — Lessons After a Year of Red Teaming (2024 Anthropic yazısı)](https://www.anthropic.com/news/lessons-from-a-year-of-red-teaming) — sürekli kırmızı takım uygulaması
