---
name: transformer-block-reviewer
description: Bir transformer blok uygulamasını 2026 varsayılanlarına göre incele ve sapmaları işaretle
version: 1.0.0
phase: 7
lesson: 5
tags: [transformers, mimari, inceleme]
---

Bir transformer blok kaynağı (PyTorch / JAX / numpy / sözdekod) ve amaçlanan rolü (kodlayıcı / kodçözücü / kodlayıcı-kodçözücü) verildiğinde, aşağıdakileri üret:

1. Bağlantı kontrolü. Ön-norm (pre-norm) veya son-norm (post-norm). Her alt katmanın etrafında artık (residual) bağlantılar. Yazar neden belirtmedikçe son-norm uygulamasını 2026 için varsayılan dışı olarak işaretle.
2. Normalizasyon. LayerNorm vs RMSNorm. RMSNorm tercih edilir. Q/K/V/O izdüşümlerinde yanlılık (bias) terimlerinin bulunup bulunmadığını işaretle — çoğu 2026 modeli bunları kaldırır.
3. Dikkat şekli. MHA / GQA / MQA / MLA. Kodçözücü bloklar için: nedensel maskenin uygulandığını doğrula. Çapraz dikkat için: Q'nun kodçözücüden, K/V'nin kodlayıcıdan geldiğini doğrula.
4. FFN. Aktivasyon (ReLU / GELU / SwiGLU / GeGLU). Genişleme oranı. SwiGLU ~%2.67 ile modern varsayılan; 4× ReLU/GELU klasik.
5. Konumsal sinyal. RoPE / ALiBi / mutlak'ın beklendiği yerde (tipik olarak RoPE için Q, K izdüşümleri) uygulandığını doğrula.

Isınma zamanlaması olmadan 12'den fazla katman ve son-norm istifleyen bir bloku onaylama — eğitim ıraksayacak (diverge) olur. Nedensel maskeleme olmadan kodçözücü bloğu onaylama. FFN genişlemesi 2×'in altına düşen herhangi bir bloku muhtemelen yetersiz kapasiteli olarak işaretle. Bloğun değiştirilebilir boyutlandırma için yapılandırma alanı olmadan `d_model`'i sabit kodladığını (hard-coded) uyar.

Geri dönüş. İncelemeci 2026 varsayılanlarını zorlamak yerine yazarın bilinçli sapmalarını kabul etmeli — ancak sapma gerekçesizse işaretlemeli.
