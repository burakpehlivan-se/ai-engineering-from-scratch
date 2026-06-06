---
name: long-context-eval
description: Belirli bir model ve kullanım senaryosu için uzun bağlam değerlendirme bataryası tasarlar.
version: 1.0.0
phase: 5
lesson: 28
tags: [nlp, long-context, evaluation]
---

Bir hedef model, hedef bağlam uzunluğu ve kullanım senaryosu verildiğinde şunu üretirsiniz:

1. Testler. NIAH derinlik × uzunluk ızgarası; RULER çok sekmeli; özel alan görevi.
2. Örnekleme. Her uzunlukta derinlikler 0, 0,25, 0,5, 0,75, 1,0.
3. Metrikler. Erişim geçme oranı; akıl yürütme geçme oranı; ilk tokena kadar geçen süre; sorgu başına maliyet.
4. Kesim. Etkin erişim uzunluğu (%90 geçer) ve etkin akıl yürütme uzunluğu (%70 geçer). İkisini de raporlayın.
5. Regresyon. Sabit test düzeneği, her model yükseltmesinde yeniden çalıştır, deltaları yüzeye çıkar.

Yalnızca model kartındaki bağlam penceresine güvenmeyi reddedin. Çok sekmeli iş yükleri için yalnızca NIAH değerlendirmesini reddedin. Satıcının öz-bildirdiği uzun bağlam puanlarını bağımsız kanıt olarak reddedin.
