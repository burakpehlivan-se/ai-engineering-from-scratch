---
name: training-budget-estimator
description: Hesaplama bütçesi ve dağıtım kısıtlamaları verildiğinde yeni bir transformer eğitim çalışması için (N, D, saat, GPU sayısı) tahmin et
version: 1.0.0
phase: 7
lesson: 13
tags: [ölçekleme-yasaları, eğitim, chinchilla]
---

Bir eğitim amacı (hedef kayıp / hedef MMLU / hedef alt görev metriği), hesaplama bütçesi (dolar veya FLOP), çıkarım hacmi (ayda token) ve kısıtlamalar (hedef cihaz, bellek, gecikme) verildiğinde, aşağıdakileri üret:

1. Hesaplama rejimi. Chinchilla-optimal, aşırı-eğitilmiş (çıkarım-optimize), yetersiz-eğitilmiş (prototip). Çıkarım hacmine bağlı tek cümlelik gerekçe.
2. N ve D. Somut değerler. `D/N` oranını yazdır. Aşırı-eğitilmiş ise, Chinchilla-optimal'a göre kayıp cezasını belirt.
3. Eğitim duvar saati. Varsayılan eğitim verimi (yoğun için MFU ≈ %40, MoE için ~%30) verildiğinde saat × GPU sayısı. Hassasiyeti (bf16 / fp8) ve optimizer'ı (AdamW / Muon) bütçele.
4. Veri kaynakları. Adlandırılmış külliyatlar veya sentetik bütçe. Gerekli `D` mevcut yüksek kaliteli tokenleri aşıyorsa işaretle.
5. Risk notu. Belirli bir başarısızlık modu: veri kontaminasyonu, ölçekte optimizer kararsızlığı, bağlam-uzunluğu tokenizer uyumsuzluğu, değerlendirme paketi doygunluğu.

Yüksek çıkarım hacmi sunacaksa Chinchilla-optimal altında yoğun model >8B eğitme — çıkarım maliyeti birikiyor. Ayrılmış değerlendirme paketi tanımlanmadan hedef kayıp belirleme. Mimari aramaya bütçenin >%1'ini harcayan herhangi bir planı işaretle — getirilerin küçük olduğu biliniyor. Tam bütçeyi taahhüt etmeden önce varsayımları doğrulamak için ölçekte bütçenin %1'i oranında bir çalıştırma gerektir.
