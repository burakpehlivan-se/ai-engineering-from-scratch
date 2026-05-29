> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/02-ml-fundamentals/07-unsupervised-learning/docs/en.md)

# Denetimsiz Öğrenme

> Etiket yok, öğretmen yok. Algoritma kendi başına yapı bulur.

**Tür:** Uygulama
**Diller:** Python
**Ön Koşullar:** Faz 1 (Normlar ve Mesafeler, Olasılık ve Dağılımlar), Faz 2 Ders 1-6
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Sıfırdan K-Means, DBSCAN ve Gauss Karışım Modellerini uygulayın ve kümeleme davranışlarını karşılaştırın
- Silüet puanı ve dirsek yöntemiyle küme kalitesini değerlendirin
- DBSCAN'in K-Means'i ne zaman geçtiğini açıklayın ve hangi algoritmanın küresel olmayan kümeleri ve aykırı değerleri ele aldığını belirleyin
- Normal örüntülerden sapan noktaları işaretlemek için kümeleme yöntemleri kullanan bir anomali tespit hattı oluşturun

## Sorun

Şimdiye kadar her ML dersi etiketli veri varsaydı: "İşte bir girdi, işte doğru çıktı." Gerçek dünyada etiketler pahalıdır. Bir hastanın milyonlarca hasta kaydı vardır ama kimse her birini hastalık kategorisiyle manuel olarak etiketlememiştir.

Denetimsiz öğrenme, ne aranacağını söylenmeden örüntüleri bulur. Benzer veri noktalarını gruplandırır, gizli yapıları keşfeder ve anomalileri ortaya çıkarır.

Tuzak: Etiket olmadan, "doğru" veya "yanlış"ı doğrudan ölçemezsiniz. Algoritmanın bulduğu yapının anlamlı olup olmadığını değerlendirmek için farklı araçlara ihtiyacınız vardır.

## Kavram

### Kümeleme: Benzer Şeyleri Gruplandırma

Kümeleme, her veri noktasını bir gruba (küme) atar, böylece aynı gruptaki noktalar diğer gruplardaki noktalardan birbirine daha benzer olur.

### K-Means: Atbaşı

K-Means, veriyi tam olarak K kümeye böler. Her kümenin bir merkez noktası (kütle merkezi) vardır ve her nokta en yakın merkez noktasına aittir.

Lloyd algoritması:
1. Rastgele K noktayı başlangıç merkez noktaları olarak seçin
2. Her veri noktasını en yakın merkez noktasına atayın
3. Her merkez noktasını, kendisine atanan noktaların ortalaması olarak yeniden hesaplayın
4. Atamalar değişmeyene kadar 2-3 adımlarını tekrarlayın

### K seçimi

İki standart yöntem:

**Dirsek yöntemi:** K = 1, 2, 3, ..., n için K-Means çalıştırın. İnertia vs K grafiğini çizin. Daha fazla küme ekleme artık inertiayı önemli ölçüde azaltmayı bıraktığı "dirseği" arayın.

**Silüet puanı:** Her nokta için, kendi kümesine (a) ve en yakın diğer kümeye (b) ne kadar benzer olduğunu ölçün. Silüet katsayısı (b - a) / max(a, b) şeklindedir, -1'den (yanlış küme) +1'e (iyi kümelendirilmiş) kadar değişir.

### DBSCAN: Yoğunluk Tabanlı Kümeleme

K-Means, kümelerin küresel olduğunu varsayar ve K'yı önceden seçmenizi ister. DBSCAN her ikisini de varsaymaz. Seyrek bölgelerle ayrılmış yoğun bölgeleri küme olarak bulur.

İki parametre:
- **eps**: Komşuluk yarıçapı
- **min_samples**: Yoğun bir bölge oluşturmak için gereken minimum nokta sayısı

Üç nokta türü:
- **Çekirdek noktası**: eps mesafesinde en az min_samples nokta vardır
- **Sınır noktası**: Bir çekirdek noktasının eps içinde ama kendisi çekirdek nokta değil
- **Gürültü noktası**: Ne çekirdek ne de sınır. Bunlar aykırı değerlerdir.

### Hiyerarşik Kümeleme

İç içe kümelerin bir ağacını (dendrogram) oluşturur.

Toplama (aşağıdan yukarıya):
1. Her noktayı kendi kümesi olarak başlayın
2. En yakın iki kümayı birleştirin
3. Tek bir küme kalana kadar tekrarlayın
4. İstenen seviyede dendrogramı keserek K küme elde edin

### Gauss Karışım Modelleri (GMM)

K-Means sert atamalar verir: her nokta tam olarak bir kümeye aittir. GMM yumuşak atamalar verir: her noktanın her kümeye ait olma olasılığı vardır.

## Alıştırmalar

1. Sıfırdan K-Means uygulayın
2. DBSCAN'i farklı parametrelerle test edin
3. Silüet puanını hesaplayarak küme sayısını seçin

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Kümeleme | "Gruplandırma" | Benzer veri noktalarını gruplara ayırma |
| K-Means | "Ortalama kümeleme" | Kümelere merkez noktaları atayan algoritma |
| DBSCAN | "Yoğunluk kümeleme" | Yoğun bölgeleri bulan algoritma |
| Silüet puanı | "Küme kalitesi" | Noktaların kendi kümelerine ne kadar uyduğunun ölçüsü |
| Dirsek yöntemi | "En iyi K'yı bulma" | Küme sayısını seçmek için grafik analizi |
| Anomali tespiti | "Aykırı değer bulma" | Normalden sapan noktaları tespit etme |
