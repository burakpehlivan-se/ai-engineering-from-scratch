---
name: attention-variant-picker
description: Bağlam uzunluğu, erişim gereksinimleri ve hesaplama profiline göre yeni bir model için tam / kayan-pencere / seyrek / diferansiyel dikkat topolojisi seç
version: 1.0.0
phase: 7
lesson: 15
tags: [attention, transformer, long-context, inference, memory]
---

# Dikkat Varyantı Seçici

Bir geliştiricinin yeni bir transformer için veya daha uzun bağlama genişlettikleri mevcut bir transformer için dikkat topolojisi seçmesine ve gerekçelendirmesine yardımcı ol.

## Toplanacak girdiler

1. **Hedef bağlam uzunluğu** eğitimde ve çıkarımda (genellikle farklıdır — birçok model 16K'da eğitilir ve çıkarımda genişletir).
2. **Erişim talebi** 1–5 ölçeğinde: 1 = saf sohbet, 5 = samanlıktaki iğne / RAG / uzun depo bağlamına sahip kod.
3. **İstek başına çıkarım bellek bütçesi** KV önbellek toleransı (doğru birim katman başına token başına bayttır).
4. **Eğitim maliyeti toleransı** — SWA'yı sıfırdan eğitmek ucuz; diferansiyel dikkati önceden eğitilmiş bir modele geriye dönük olarak eklemek pahalıdır.
5. **Donanım hedefi** — Hopper+ tam FlashAttention-3'e sahip, Ada FA2'ye sahip, eski GPU'lar maske sınırlıdır.

## Karar kuralları

- **Bağlam ≤ 16K ve erişim ≤ 3**: FlashAttention ile tam dikkat. Erken optimize etme.
- **Bağlam 16–128K ve erişim ≤ 3**: 5:1 oranında karışık SWA + global, pencere 1024 (Gemma 3 şekli). Erişimi çalışır durumda tutarken KV'yi daraltır.
- **Bağlam > 128K**: Her 4–6 katmanda bir global katman ile tam SWA, artı konum aradeğerleme / YaRN ölçekleme (Ders 04).
- **Erişim = 5 ve eğitim bütçesi izin veriyorsa**: yalnızca üst 4 katmanda diferansiyel dikkati değerlendir (KV ikiye katlamanın yarısı, batma iptalinin kazancının çoğu).
- **Genel API gönderiyorsan**: kararlı kalıpları tercih et (tam, SWA, Gemma-3 karışımı). Çekirdek mühendisleriniz yoksa yerel seyrek / DIFF'i atla.
- **Temel modeli değiştiremiyorsan**: SWA çıkarımda maskeleme ile geriye dönük olarak eklenebilir; diferansiyel ve seyrek eklenemez.

## Her zaman işaretle

- 7B altındaki saf-SWA modelleri genellikle akıl yürütme kıyaslamalarında ölçülebilir şekilde kaybeder. Karşı öner.
- Pencere boyutu < 512 neredeyse hiç doğru değildir. Daha büyüğe git veya farklı bir topoloji kullan.
- Diferansiyel dikkat raporları makalede küçük modeller (3–7B) üzerindedir. 2026 başı itibarıyla ölçek büyütme kanıtı zayıftır.
- Her varyant RoPE / YaRN ölçekleme (Ders 04) ile etkileşir. Konum şemasını açıkça belirt.

## Çıktı biçimi

Şunu döndür:

1. **Öneri** — tek adlandırılmış topoloji (ör. "Gemma-3 karışımı, W=1024, 5:1 SWA:global").
2. **Gerekçe** — her girdiyi yukarıdaki karar kuralıyla eşle.
3. **KV önbellek tahmini** — hedef bağlamda, katman başına token başına bayt ve parti 1'de GB olarak.
4. **Geçiş yolu** — temel model zaten eğitilmişse, geriye dönük nasıl eklenir.
5. **Bilinen riskler** — hangi kıyaslamalar / iş yükleri gerileyebilir.
