# Neden Transformer'lar — RNN'lerin Sorunları

> RNN'ler token'ları tek tek işler. Transformer'lar tüm token'ları aynı anda işler. Bu tek mimari karar, 2017'den bu yana derin öğrenme eğrilerinin tamamını değiştirdi.

**Tür:** Öğren
**Diller:** Python
**Önkoşullar:** Faz 3 (Derin Öğrenme Çekirdeği), Faz 5 · 09 (Diziden Diziye), Faz 5 · 10 (Dikkat Mekanizması)
**Süre:** ~45 dakika

## Sorun

2017'den önce, gezegende her bir durum-tespitli (state-of-the-art) dizi modeli — dil, çeviri, konuşma — yinelemeli bir sinir ağıydı (recurrent neural network). LSTM ve GRU'lar ImageNet eşdeğeri çeviri benchmark'larını yarım on yılda kazandı. Başka araçları yoktu.

Üç ölümcül zayıflıkları vardı. Ardışık hesaplama, zaman ekseni boyunca paralelleştiremediğiniz anlamına gelir: token `t+1`, token `t`'den gizli duruma (hidden state) ihtiyaç duyar. 1.024 tokenlık bir dizi, döngü başına 1.000.000 kayan noktalı işlem yapabilen bir GPU'da 1.024 ardışık adım demekti. Eğitim duvar saati, paralellik için tasarlanmış donanımda dizi uzunluğuyla doğrusal olarak ölçekleniyordu.

Kaybolan gradyanlar (vanishing gradients), 50 token gerideki bilginin zaten 50 doğrusal olmayan dönüşümden geçirilerek sıkıştırıldığı anlamına geliyordu. Kapılı yinelemeli üniteler (LSTM, GRU) baskıyı yumuşattı ama hiçbir zaman ortadan kaldırmadı. Uzun menzilli bağımlılıklar — "Geçen yaz Kyoto'ya giden bir uçakta okuduğum kitap şuydu..." — rutin olarak başarısız oluyordu.

Sabit genişlikteki gizli durumlar, kodlayıcının (encoder) tüm kaynak dizisini bir vektöre sıkıştırıp çözücüyü (decoder) bir şey görmeden önce squeezediği anlamına geliyordu. Kaynak 5 token veya 500 token olsun fark etmez; darboğaz aynı şekildedir.

2017 makalesi "Attention Is All You Need" radikal bir şey önerdi: yinelemeyi tamamen bırakın. Her konumun diğer her konuma paralel olarak dikkat etmesine izin verin. 1.024 ardışık çarpım yerine tek büyük bir matris çarpımıyla eğitin.

Sonuç 2026'ya kadar her modelli_domine ediyor. Dil (GPT-5, Claude 4, Llama 4), bilgisayar görü (ViT, DINOv2, SAM 3), ses (Whisper), biyoloji (AlphaFold 3), robotik (RT-2). Aynı blok, farklı girdiler.

## Kavram

![RNN ardışık hesaplama vs Transformer paralel dikkat](../assets/rnn-vs-transformer.svg)

**Yineleme darboğaz olarak.** Bir RNN `h_t = f(h_{t-1}, x_t)` hesaplar. Her adım bir öncekine bağlıdır. `h_4`'ü hesaplamadan `h_5`'i hesaplayamazsınız. 10.000'den fazla paralel çekirdeğe sahip modern GPU'larda, bu durum uzun bir dizide silikonun %99'unu boşa harcar.

**Dikkat olarak yayınım (broadcast).** Self-attention (öz-dikkat), her `(i, j)` çifti için aynı anda `output_i = sum_j(a_ij * v_j)` hesaplar. Tüm N×N dikkat matrisi tek bir toplu matris çarpımıyla (batched matmul) doldurulur. Hiçbir adım diğerine bağlı değildir. GPU'lar bunu sever.

**Hızlanma sabit bir değer değildir.** Bu, `O(N)` ardışık derinlik ile `O(1)` ardışık derinlik arasındaki farktır. Pratikte, transformer'lar N=512'de eşdeğer donanımda epoch başına 5-10× daha hızlı eğitilir ve fark, `O(N²)` dikkat bellek duvarına (Flash Attention'ın sonra düzelttiği — Ders 12'ye bakın) ulaşana kadar dizi uzunluğuyla birlikte büyür.

**Transformer'ların maliyeti.** Dikkat belleği `O(N²)` ile ölçeklenir. 2K bağlam için sorun yok. 128K bağlam için, kaydırma pencereleri (sliding windows), RoPE dışa aktarımı, Flash Attention döşemesi veya lineer dikkat (linear attention) varyantlarına ihtiyacınız var. Yineleme hem zamanda hem de bellekte `O(N)` idi; transformer'lar zamanı bellekle değiştirir ve sonra paralelleşme yoluyla zamanı geri kazanır.

**İndüktif önyargı (inductive bias) kayması.** RNN'ler yerelliği ve yakınlığı varsayar. Transformer'lar hiçbir şeyi varsaymaz — her çift dikkat için bir adaydır. Bu yüzden transformer'ların iyi eğitilmesi için daha fazla veriye ihtiyacı vardır, ama bir kez veriyle ölçeklenirler. Chinchilla (2022) bunu resmileştirdi: yeterli token varsa, transformer her zaman eşit parametre sayısına sahip bir RNN'i yener.

## İnşa Et

Burada sinir ağı yok — temel darboğazı sayısal olarak simüle ediyoruz, böylece farkı dizüstü bilgisayarınızda hissedebilirsiniz.

### Adım 1: ardışık derinliği ölç

`code/main.py`'e bakın. İki işlev oluşturuyoruz. Bir tanesi bir diziyi toplama zinciri olarak kodluyor (ardışık, bir RNN gibi). Diğeri paralel azaltma olarak kodluyor (yayınım, dikkat gibi). Aynı matematik, farklı bağımlılık grafiği.

```python
def rnn_style(xs):
    h = 0.0
    for x in xs:
        h = 0.9 * h + x   # paralelleştirilemez: h önceki h'ye bağlı
    return h

def attention_style(xs):
    return sum(xs) / len(xs)  # her x bağımsızdır
```

#### Açıklama
Bu kod iki farklı hesaplama yöntemi arasındaki temel farkı gösterir: RNN tarzı ardışık hesaplama (her adım bir öncekine bağımlı) ve dikkat tarzı paralel hesaplama (tüm girdiler bağımsızdır).

100.000 elemana kadar dizelerde her ikisini de zamanlıyoruz. RNN versiyonu O(N)'dir ve tek bir CPU hattıdır. Saf Python'da bile, dikkat tarzı azaltma 1.000 ve üzeri uzunlukta onu yener çünkü Python'un `sum()` işlevi C'de uygulanmıştır ve her adımda yorumlayıcı (interpreter) yükü olmadan yineler.

### Adım 2: teorik işlemleri say

Her iki algoritma da N toplama yapar. Fark *bağımlılık derinliğidir*: bir sonraki başlamadan önce kaç işlemin ardışık olarak gerçekleşmesi gerekir. RNN derinliği = N. Dikkat derinliği, ağaç azaltması ile log(N) veya paralel tarama ile 1. Derinlik, işlem sayısını değil, GPU zamanını belirler.

### Adım 3: uzun dizelerde ampirik ölçekleme

O(N) farkını görünür kılan bir zamanlama tablosu yazdırıyoruz. 2026 Mac dizüstü bilgisayarında, 1.000'den az elemanlı dizeler ölçülemeyecek kadar hızlıdır. 100.000 elemanlı dizeler temiz bir doğrusal tarama gösterir. Bunu 12 katmanlı LSTM eşdeğeriyle 16.384 tokenlık bir transformer'a ölçeklendirdiğinizde, neden eğitim duvar saati 2016'da bir engel olduğunu görürsünüz.

## Kullan

2026'da hala bir RNN'i ne zaman seçmelisiniz:

| Durum | Seç |
|-----------|------|
| Aktarım çıkarımı (streaming inference), tek token, sabit bellek | RNN veya durum-uzay modeli (Mamba, RWKV) |
| Çok uzun dizeler (>1M token) - dikkat belleği patlar | Lineer dikkat, Mamba 2, Hyena |
| Matmul hızlandırıcısı olmayan kenar cihaz | Derinlik-ayrımcı RNN hala FLOP/watt'ta kazanır |
| Diğer her şey (eğitim, toplu çıkarım, 128K'ya kadar bağlam | Transformer |

Mamba gibi durum-uzay modelleri (SSM'ler) aslında her iki dünyanın en iyisini veren yapılandırılmış parametrelendirmeyle RNN'lerdir: `O(N)` tarama belleği, seçici tarama yoluyla paralel eğitim. Transformer kalitesinin %90'ını daha iyi uzun-bağlam ölçeklemesiyle geri kazanırlar. 2026'da çoğu sınır laboratuvarı hibrit SSM+transformer modelleri eğitir (ör. Jamba, Samba) — yineleme ölmedi, bir bileşen.

## Teslim Et

`outputs/skill-architecture-picker.md`'ye bakın. Bu beceri, uzunluk, verim ve eğitim bütçesi kısıtlamaları verildiğinde yeni bir dizi sorunu için bir mimari seçer. 1B token'ın üzerindeki eğitim çalıştırmaları için her zaman bir taviz belirtmeden saf bir RNN önermeyi reddetmelidir.

## Alıştırmalar

1. **Kolay.** `code/main.py`'den `rnn_style`'ı alın ve skaler gizli durumu 64 uzunluğunda bir gizli durum vektörüyle değiştirin. Tekrar ölçün. Seri yük, gizli durum boyutuyla birlikte ne kadar büyür?
2. **Orta.** Saf Python'da paralel ön-toplama (Hillis-Steele taraması) uygulayın. 1024 uzunluğunda seri taramayla aynı sayısal çıktıyı ürettiğini doğrulayın. Derinliği sayın.
3. **Zor.** Dikkat tarzı azaltmayı GPU üzerinde PyTorch'a taşıyın. Dizi uzunluğunu 64'ten 65.536'ya tararken her ikisini de zamanlayın. Eğri şeklini çizin ve açıklayın.

## Anahtar Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|-----------------|-----------------------|
| Yineleme (Recurrence) | "RNN'ler ardışıktır" | Adım `t`, adım `t-1`'e bağlı olan hesaplama, zaman ekseni boyunca seri yürütmeyi zorunlu kılar. |
| Seri derinlik (Serial depth) | "Grafinin ne kadar derin olduğu" | En uzun bağımlı işlem zinciri; sonsuz donanımda bile duvar saatini sınırlar. |
| Dikkat (Attention) | "Token'ların birbirine bakmasını sağla" | `sum_j a_ij v_j` ağırlıklı toplamı, burada `a_ij` i ve j konumları arasındaki benzerlik puanından gelir. |
| Bağlam penceresi (Context window) | "Modelin ne kadar gördüğü" | Bir dikkat katmanının girdi olarak alabileceği konum sayısı; karekoster bellek maliyeti burada ölçeklenir. |
| İndüktif önyargı (Inductive bias) | "Mimaride pişirilmiş varsayımlar" | Verinin nasıl göründüğüne dair öncül; CNN'ler öteleme değişimliliğini (translation invariance), RNN'ler yakınlığı varsayar. |
| Durum-uzay modeli (State-space model) | "Algebresi olan bir RNN" | Yapılandırılmış durum-uzay matrisleri aracılığıyla paralel eğitim için parametrelendirilmiş yineleme. |
| Karekoster darboğaz (Quadratic bottleneck) | "Neden bağlam bu kadar pahalı" | Dikkat belleği = dizi uzunluğunda `O(N²)`; Flash Attention sabitleri gizler, ölçeklemeyi değil. |

## İleri Okuma

- [Vaswani ve diğerleri (2017). Attention Is All You Need](https://arxiv.org/abs/1706.03762) — ana akım NLP'de yinelemeyi öldüren makale.
- [Bahdanau, Cho, Bengio (2014). Neural MT by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — dikkatin doğduğu, bir RNN'e eklenen makale.
- [Hochreiter, Schmidhuber (1997). Long Short-Term Memory](https://www.bioinf.jku.at/publications/older/2604.pdf) — orijinal LSTM makalesi, kayıt olarak.
- [Gu, Dao (2023). Mamba: Linear-Time Sequence Modeling with Selective State Spaces](https://arxiv.org/abs/2312.00752) — transformer'lara modern yinelemeli yanıt.
