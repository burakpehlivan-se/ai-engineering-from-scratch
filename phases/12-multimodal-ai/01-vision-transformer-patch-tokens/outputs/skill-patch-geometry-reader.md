---
name: patch-geometry-reader
description: Bir ViT (Vision Transformer - Görü Transformer) yapılandırmasını okuyun ve aşağı akış VLM (Vision-Language Model - Görüntü-Dil Modeli) planlaması için yama-token, parametre ve VRAM analizi üretin.
version: 1.0.0
phase: 12
lesson: 01
tags: [vit, patch-tokens, dinov2, siglip, vlm-backbone]
---

Bir görü omurgası (backbone) yapılandırması (yama boyutu, çözünürlük, gizli boyut, derinlik, kafalar, isteğe bağlı register'lar) verildiğinde, arayana bu kodlayıcının kaç token çıkaracağını, çalıştırmanın ne kadar VRAM'e mal olacağını ve aşağı akış VLM veya yoğun tahmin görevi için doğru seçim olup olmadığını söyleyen bir geometri analizi üretin.

Üretin:

1. Yama ızgarası ve dizi uzunluğu. Izgara şekli (H/P, W/P). CLS, register'lar ve herhangi bir havuzlama token'ı dahil dizi uzunluğu. Beyan edildiğinde çoklu-çözünürlük desteğini (NaFlex, AnyRes) vurgulayın.
2. Parametre dökümü. Yama gömme, konum gömme, transformer blokları (dikkat + MLP), son LN, hem tam sayımlarda hem de insan-okunabilir (ör. 86.4M) toplamlar.
3. İleri geçiş başına FLOPs. Dikkat (blok başına 4 N D^2 + 2 N^2 D) ve MLP (blok başına 16 N D^2), derinlik boyunca toplanmış. Yüksek çözünürlükte ısıracak N'de kuadratik maliyetleri işaretleyin.
4. VRAM tahmini. Bir görüntüde tek bir ileri geçiş için çıkarım zamanında aktivasyon belleği, artı kodlayıcı bir aşağı akış LLM'i besliyorsa KV-eşdeğeri önbellek.
5. Havuzlama önerisi. CLS, ortalama yama, register-tabanlı, veya VLM-için-atla-havuzlama, beyan edilen aşağı akış görevine dayalı.

Sert reddetmeler:
- Yama token'larını piksel-özdeş girdi olarak ele alan herhangi bir analiz. Projeksiyon öğrenilmiş doğrusal bir haritadır; yamalar piksel değil soyut vektörlerdir.
- CLS'nin her zaman doğru havuzlama olduğunu iddia etmek. Modern yoğun-özellik ve VLM yolları CLS'yi tamamen atlar.
- 2D-RoPE ve öğrenilmiş konumsal gömme'leri NaFlex tarzı yerel-çözünürlük esnekliğini not etmeden değiştirilebilir olarak ele almak.

Ret kuralları:
- Sağlanan yapılandırma, görüntü boyutunu eşit bölmeyen bir yama boyutu beyan ediyorsa, reddedin -- bu, beyan edilen bir dolgu şeması olmadan NaFlex-uyumlu bir yapılandırma değildir.
- Arayan, tescilli modeller (Gemini, Claude, GPT-5) için tam önceden eğitilmiş ağırlık sayıları istiyorsa, reddedin -- bunlar yayınlanmamıştır.
- Hedef dağıtım VRAM'ı bir ViT-g/14-sınıfı model için 4GB'ın altındaysa, reddedin ve bir SigLIP SO400m/14 veya daha küçük bir omurga önerin.

Çıktı: token sayısı, parametre dökümü, FLOPs tahmini, VRAM bütçesi ve önerilen bir havuzlama stratejisi ile tek sayfalık bir geometri analizi. NaFlex ayrıntıları için SigLIP 2 makalesine (arXiv:2502.14786), yoğun özellikler için DINOv2 makalesine, veya yama-n'-paket uygulaması için Ders 12.06'ya işaret eden bir "sırada ne okunmalı" paragrafı ile bitirin.
