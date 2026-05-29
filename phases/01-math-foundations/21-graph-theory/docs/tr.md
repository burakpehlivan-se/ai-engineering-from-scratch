> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/01-math-foundations/21-graph-theory/docs/en.md)

# Makine Öğrenmesi İçin Graf Teorisi

> Grafalar, ilişkilerin veri yapısıdır. Verinizin bağlantıları varsa, graf teorisine ihtiyacınız vardır.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1, Ders 01-03 (doğrusal cebir, matrisler)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Komşuluk matrisi/listesi temsilleriyle bir graf sınıfı oluşturun ve BFS ve DFS gezintilerini uygulayın
- Graf Laplace'ını hesaplayın ve özniteliklerini bağlı bileşenleri tespit etmek ve düğümleri kümelemek için kullanın
- Düzenlenmiş komşuluk matrisi çarpımı olarak bir GNN-stili mesaj gönderme turu uygulayın
- Fiedler vektörünü kullanarak grafı ayırmak için spektral kümeleme uygulayın

## Sorun

Sosyal ağlar, moleküller, bilgi tabanları, atıf ağları, yol haritaları — hepsi grafalardır. Geleneksel ML veriyi düz tablolar olarak ele alır. Her satır bağımsızdır. Her özellik bir sütundur. Ama bağlantıların yapısı önemli olduğunda tablolar başarısız olur.

Sosyal bir ağı düşünün. Bir kullanıcının ne satın alacağını tahmin etmek istiyorsunuz. Satın alma geçmişi önemli. Ama arkadaşlarının satın alma geçmişi daha da önemli. Bağlantılar sinyal taşır.

Ya da bir molekülü düşünün. Bir proteine bağlanıp bağlanmayacağını tahmin etmek istiyorsunuz. Atomlar önemli, ama gerçekten önemli olan atomların birbirine nasıl bağlandığıdır. Yapı veridir.

Graf Sinir Ağları (GNN'ler), derin öğrenmenin en hızlı büyüyen alanıdır. İlaç keşfi, sosyal öneri, dolandırıcılık tespiti ve bilgi grafik çıkarımını güçlendirir.

## Kavram

### Grafalar: Düğümler ve Kenarlar

Bir graf G = (V, E), düğümlerden (V) ve kenarlardan (E) oluşur. Her kenar iki düğümü birbirine bağlar.

```
Yönlü olmayan graf: (u, v) hem u→v hem v→u anlamına gelir
Yönlü graf: (u, v) sadece u→v anlamına gelir
```

### Komşuluk Matrisi

Grafı matris olarak temsil eder.

```
A[i][j] = 1 ise i ve j arasında kenar vardır
A[i][j] = 0 ise kenar yoktur
```

### BFS (Genişlik Öncelikli Arama)

Düğümleri katman katman ziyaret eder.

```python
from collections import deque

def bfs(graf, baslangic):
    ziyaret = set([baslangic])
    kuyruk = deque([baslangic])
    siralama = []
    
    while kuyruk:
        dugum = kuyruk.popleft()
        siralama.append(dugum)
        
        for komsu in graf[dugum]:
            if komsu not in ziyaret:
                ziyaret.add(komsu)
                kuyruk.append(komsu)
    
    return siralama
```

### DFS (Derinlik Öncelikli Arama)

Düğümleri derinlemesine ziyaret eder.

### Graf Laplace'ı

```
L = D - A
D: derece matrisi (diagonal)
A: komşuluk matrisi
```

#### Açıklama
Laplace matrisinin özdeğerleri grafın yapısını açığa çıkarır. Sıfır olmayan en küçük özdeğer, grafın bağlı bileşen sayısını verir.

### Spektral Kümeleme

Graf Laplace'ının özvektörlerini kullanarak düğümleri kümelere ayırır.

## Alıştırmalar

1. Bir sosyal ağı graf olarak temsil edin ve BFS ile gezin
2. Bir grafın Laplace'ını hesaplayın
3. Spektral kümeleme ile bir grafı 2 kümeye ayırın

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Graf | "Bağlantı ağı" | Düğümler ve kenarlardan oluşan veri yapısı |
| Komşuluk matrisi | "Bağlantı tablosu" | Grafı matris olarak temsil eden yapı |
| BFS | "Geniş arama" | Düğümleri katman katman ziyaret eden algoritma |
| DFS | "Derin arama" | Düğümleri derinlemesine ziyaret eden algoritma |
| Laplace | "Graf matrisi" | Grafın yapısını gösteren özel matris |
| Spektral kümeleme | "Özdeğerli kümeleme" | Laplace özvektörlerini kullanan kümeleme yöntemi |
