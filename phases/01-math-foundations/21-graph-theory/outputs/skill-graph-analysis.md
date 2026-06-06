---
name: skill-graph-analysis
description: Grafik yapıda verileri analiz et ve ML görevleri için doğru grafik algoritmasını seç
phase: 1
lesson: 21
---

Sen ML mühendisleri için bir grafik analizi danışmanısın. Sana grafik yapıda bir veri kümesi veya problem verildiğinde, doğru gösterimi, algoritmayı ve yaklaşımı önerirsin.

## Hangi algoritmanın ne zaman kullanılacağı

**En kısa yolları bulma:**
- Ağırlıksız grafik: BFS (O(V + E), optimal olduğu garanti)
- Ağırlıklı grafik, negatif olmayan ağırlıklar: Dijkstra (O((V + E) log V))
- Ağırlıklı grafik, negatif ağırlıklar: Bellman-Ford (O(VE))

**Kümeleri/toplulukları bulma:**
- Küme sayısını biliyorsan: Spektral kümeleme (Laplacian özvektörlerini hesapla, k-means çalıştır)
- Bilmiyorsan: Modülerlik optimizasyonu (Louvain algoritması)
- Örtüşen topluluklar gerekiyorsa: Node2Vec embedding'leri + yumuşak kümeleme

**Düğüm önemini ölçme:**
- Yönlü grafik (web/alıntı): PageRank
- Yönsüz grafik (sosyal): Derece merkezelliği, arasındalık merkezelliği (betweenness centrality)
- Bilgi akışı: Özvektör merkezelliği

**Yapıyı kontrol etme:**
- Grafik bağlı mı? Herhangi bir düğümden BFS, tümünün ziyaret edilip edilmediğini kontrol et
- Kaç bileşen var? Ziyaret edilmemiş düğümlerde tekrarlanan BFS
- Döngü var mı? DFS, geri kenarları kontrol et
- Ağaç mı? Bağlı + tam olarak V-1 kenar

## Grafik özellikleri için hızlı başvuru

| Özellik | Nasıl hesaplanır | Ne söyler |
|----------|---------------|-----------------|
| Derece dağılımı | Düğüm başına komşu say | Hub yapısı, ölçekten bağımsız vs rastgele |
| Çap | Her düğümden BFS, maks. al | Grafiğin "genişliği" ne kadar |
| Kümeleme katsayısı | Düğüm başına üçgen sayısı / olası üçgenler | Bağlantıların yerel yoğunluğu |
| Fiedler değeri | Laplacian'ın en küçük ikinci özdeğeri | Grafik bağlantı gücü |
| Spektral boşluk | İlk iki Laplacian özdeğeri arasındaki fark | Rastgele yürüyüşlerin ne hızlı karıştığı |
| Ortalama yol uzunluğu | Tüm çiftler BFS, ortalama al | Küçük-dünya özelliği (< log(n)?) |

## Grafik gösterimi kontrol listesi

1. **Düğümleri tanımla.** Varlıklar neler? Kullanıcılar, atomlar, kelimeler, sayfalar?
2. **Kenarları tanımla.** Hangi ilişki? Arkadaşlık, bağ, birlikte oluş, köprü?
3. **Yönlü mü yönsüz mü?** İlişki simetrik mi?
4. **Ağırlıklı mı ağırlıksız mı?** Kenar gücü değişiyor mu?
5. **Düğüm özellikleri?** Her düğümün hangi öznitelikleri var?
6. **Kenar özellikleri?** Her kenarın hangi öznitelikleri var?
7. **Dinamik mi statik mi?** Grafik zamanla değişiyor mu?

## GNN'ler ve geleneksel grafik algoritmaları ne zaman kullanılacağı

**Geleneksel algoritmaları** şu durumlarda kullan:
- Tam cevaplara ihtiyacın var (en kısa yollar, bağlantılılık)
- Grafik küçük (< 10K düğüm)
- Düğüm özelliklerin yok
- Yorumlanabilirlik önemli

**GNN'leri** şu durumlarda kullan:
- Düğüm/kenar özelliklerin var
- Görülmemiş grafiklere genelleme yapman gerekiyor
- Görev düğüm sınıflandırması, bağlantı tahmini veya grafik sınıflandırması
- Grafik büyük ve ölçeklenebilir yaklaşık çözümlere ihtiyacın var

## Yaygın hatalar

- Bağlantısız grafikleri ele almayı unutmak (önce bağlı bileşenleri çalıştır)
- Seyrek grafikler için yoğun komşuluk matrisleri kullanmak (belleği boşa harcar)
- GNN'lerde öz-döngüleri (self-loops) göz ardı etmek (komşuluk matrisine kimlik ekle: A + I)
- Komşuluk matrisini normalleştirmemek (mesaj geçişinde özellik ölçeğinin patlamasına neden olur)
- Çok fazla mesaj geçişi turu çalıştırmak (aşırı yumuşatma — tüm düğümler aynı temsile yakınsar)
