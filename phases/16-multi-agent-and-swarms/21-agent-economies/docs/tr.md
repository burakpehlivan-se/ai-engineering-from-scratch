# Ajan Ekonomileri, Token Teşvikleri, İtibar

> Uzun-ufuklu otonom ajanlar (METR'nin 1-saat-ile-8-saat çalışma eğrisi) ekonomik temsil gerektirir. Ortaya çıkan **5-katmanlı yığın** şudur: **DePIN** (fiziksel hesaplama) → **Kimlik** (W3C DID'leri + itibar sermayesi) → **Biliş** (RAG + MCP) → **Uzlaşma** (hesap soyutlama) → **Yönetişim** (Ajanik DAO'lar). Üretim ajan-teşvik ağları şunları içerir: **Bittensor** (TAO alt-ağları göreve-özgü modelleri ödüllendirir), **Fetch.ai / ASI İttifakı** (ASI-1 Mini LLM + FET token'ı) ve **Gonka** (verimli AI görevlerine hesaplamayı yeniden tahsis eden transformatör-tabanlı PoW). Akademik çalışma: AAMAS 2025'in merkezsiz LaMAS'ı, katkıda bulunan ajanları adil biçimde ödüllendirmek için **Shapley-değeri kredi atfı** kullanır; Google Research "Mechanism design for large language models" monoton toplama altında **ikinci-fiyat ödemeli token açık artırmaları** önerir. Bu ders minimal bir ajan pazarı inşa eder, çok-ajanlı bir boru hattına Shapley-değeri kredi atfı uygular ve oyun-teorisi mekanizmasının somut olarak yerleşmesi için ikinci-fiyat token açık artırması çalıştırır.

**Tip:** Öğren
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 16 (Müzakere ve Pazarlık), Faz 16 · 09 (Paralel Sürü Ağları)
**Süre:** ~75 dakika

## Problem

Multi-agent sistemleri, ajanlar ortak değer ürettiğinde ancak bireysel olarak ödüllendirilmesi gerektiğinde karmaşıklaşır. Klasik mekanizmalar — eşit bölüşüm, son-katkıda-bulunan-alır — adaletsiz veya oynanabilirdir. Shapley değerleri aracılığıyla koalisyon-tabanlı ödüllendirme yapısal olarak adildir ancak hesaplanması pahalıdır. 2025-2026 literatürü yararlı yaklaşımlıklar iter: Shapley örneklemesi, monoton toplama açık artırmaları ve onaylanmış katkılardan biriken zincir-üstü itibar.

Kredi atfının ötesinde, alan gerçek ekonomik ajanlara yöneldi: Bittensor TAO, ince-ayar alt-ağa-özgü modeller için madencilik hesaplamasını ödüllendirir; Fetch.ai/ASI, ASI-1 Mini LLM kullanımını FET token'ları ile ödüllendirir; Gonka, transformatör proof-of-work'unu verimli AI görevlerine yeniden tahsis eder. Otonom olarak işlem yapan ajanlar bugün vardır; sorun teşviklerin nasıl hizalanacağıdır.

Bu ders, ajan ekonomilerini belirli bir problem ailesi — kredi atfı, mekanizma tasarımı ve itibar — olarak ele alır ve fikirlerin yapışması için her birini minimal matematikle inşa eder.

## Kavram

### 5-katmanlı ajan-ekonomisi yığını

1. **DePIN (fiziksel hesaplama).** GPU, depolama, bant genişliği kiralayan merkezsiz altyapı. Bittensor alt-ağları, Render Network, Akash. Ajana özgü değildir; ajanlar kullanır.
2. **Kimlik.** W3C Merkezsiz Tanımlayıcıları (DID'ler) her ajana platformdan bağımsız dayanıklı bir kimlik verir. İtibar DID'ye bağlanır. Ağ Protokolü (ANP) keşif katmanı olarak DID kullanır.
3. **Biliş.** Ajanın muhakeme döngüsü: LLM + RAG + MCP. Diğer fazların inşa ettiği budur.
4. **Uzlaşma (Settlement).** Hesap soyutlama (ERC-4337) ajanların ETH tutmadan kendi bakiyelerinden gas ödemesine izin verir. Ajanlar hizmetler, birbirleri veya hesaplama için ödeyebilir.
5. **Yönetişim.** Ajanik DAO'lar: insanların *ve* ajanların protokol değişiklikleri üzerinde oy kullandığı, oy gücü itibara bağlı yönetişim yapıları.

Her üretim sistemi beşini de kullanmaz. Bittensor 1, 2, kısmen 3, kısmen 4 kullanır, 5'i kullanmaz. OpenAI ajanları 3 dışında hiçbirini kullanmaz. Yığın referans haritadır, gereklilik değil.

### Bittensor, Fetch.ai, Gonka — neler çalışır

**Bittensor (TAO).** Alt-ağlar uzmanlaşmış görevlerdir (dil modelleme, görüntü üretimi, tahmin). Madenciler model çıktıları sunar. Doğrulayıcılar onları sıralar; stake-ağırlıklı puanlama TAO ödüllerini dağıtır. Her alt-ağın kendi değerlendirmesi vardır. Ekonomik ders: kullanılan hesaplama için değil, göreve-özgü çıktı kalitesi için öde.

**Fetch.ai / ASI İttifakı.** ASI-1 Mini LLM Fetch.ai ağında çalışır; kullanıcılar çıkarım için FET token'ları öder. Ajanlar-akranlar anlatısı burada daha güçlüdür: Fetch'teki bir ajan, bir görev için diğerini çağırabilir ve FET ile ödeyebilir.

**Gonka.** Transformatör proof-of-work: "iş" bir transformatörün ileri geçişleridir. Madenciler, bilinen doğru çıktıları olan (eğitim verisinden) çıkarım görevlerini çalıştırarak kazanır. Hash-tabanlı PoW yerine kaynak-verimli PoW.

Üçü de Nisan 2026 itibarıyla üretim-düzeyindedir. Kazanç dağılımı farklıdır. Bittensor, alt-ağ doğrulayıcılarına göre kaliteyi ödüllendirir; Fetch, ödeyen kullanıcılar tarafından ölçülen faydayı ödüllendirir; Gonka doğrulanabilir çıkarım işini ödüllendirir.

### Shapley-değeri kredi atfı

Üç ajan bir görevde işbirliği yapar. Çıktı 0,8 puan alır. Kim ne kadar katkıda bulundu?

Shapley değeri: dört aksiyomu (verimlilik, simetri, doğrusallık, boş) karşılayan tekil kredi tahsisi. Ajan `i` için:

```
shapley(i) = (1/N!) * tüm sıralamalar O üzerinden toplam (v(S_i_O ∪ {i}) - v(S_i_O))
```

#### Açıklama
Burada `S_i_O`, sıralama `O`'da `i`'den önce gelen ajanlar kümesidir. Pratikte: tüm permütasyonları say, her permütasyonda her ajanın marjinal katkısını kaydet, ortala.

N=3 ajan için 6 permütasyon vardır. N=10 için 3,6M — yani pratikte permütasyonları saymak yerine örnekleyin.

### Toplama için ikinci-fiyat açık artırması

Google Research ("Mechanism design for large language models") LLM çıktılarını toplamak için ikinci-fiyat token açık artırmaları önerir. Kurulum: N ajan her biri bir tamamlama önerir; her birinin seçilmek için özel bir değeri vardır. Açık artırmacı en yüksek değerli öneriyi seçer ve *en yüksek ikinci* değeri öder. Monoton toplama (değer, kaç teklif verildiğine değil hangi önerinin seçildiğine bağlı) altında bu doğru söylüdür — ajanlar gerçek değerleri üzerinden teklif verir.

Bu neden LLM sistemleri için önemlidir: tamamlama görevlerini farklı fiyatlandırmaya sahip birden fazla ajana dış kaynak olarak verebilirsiniz; açık artırma en iyiyi seçer + adil öder ve ajanların yanlış raporlama teşviki yoktur.

### İtibar sermayesi

DID'ye bağlı bir itibar puanı, onaylanmış katkılardan birikir. Basit bir güncelleme kuralı:

```
itibar(i, t+1) = alfa * itibar(i, t) + (1 - alfa) * katkı_kalitesi(i, t)
```

#### Açıklama
Yakın 1'e eşit bozunma faktörü `alfa` ile. İtibar:
- Yönlendirme kararları için okunması ucuz ("zor görevleri yüksek-itibarlı ajanlara gönder").
- Üretilmesi pahalı (zaman içinde birikir, DID'ye bağlıdır).
- Düşürülebilir: doğrulamayı geçemeyen katkılar çıkarılır.

### AAMAS 2025 merkezsiz LaMAS

LaMAS önerisi (AAMAS 2025) şunları birleştirir: DID kimliği, Shapley-değeri kredi atfı ve basit bir açık artırma mekanizması. Temel iddia: kredi atfı adımını merkezsizleştirmek, sistemi denetlenebilir ve tek-nokta manipülasyonuna bağışık kılar.

### Ekonominin nerede çöktüğü

- **Fiyat oracle manipülasyonu.** Kredi fonksiyonu oynanabiliyorsa, ajanlar onu oynar. Her mekanizmanın düşmanca bir testi gerekir.
- **Sybil saldırıları.** Tek bir operatör kendi katkısını şişirmek için N sahte ajan çalıştırır. DID'ler bunu yavaşlatır ama durdurmaz; üretim maliyeti hafifletmedir.
- **Doğrulama maliyeti.** Kredi atfı yalnızca doğrulayıcı kadar adildir. Doğrulama ucuzsa (küçük LLM) oynanabilir; pahalıysa (insan paneli) sistem ölçeklenmez.
- **Düzenleyici belirsizlik.** Ajan ekonomileri finansal düzenleme ile kesişir. Bittensor, Fetch ve Gonka 2026 itibarıyla bazı yargı bölgelerinde yasal gri alanlarda faaliyet gösterir.

### Ajan ekonomilerinin ne zaman anlamlı olduğu

- **Heterojen operatörlü açık ağlar.** Tek bir takım tüm ajanları kontrol etmez.
- **Doğrulanabilir çıktılar.** Doğrulama olmadan, kredi atfı bir tahmindir.
- **Uzun-ufuklu iş akışları.** Tek seferlik görevler itibar birikiminden yararlanmaz.
- **Tokenleştirilmiş ödemeler yargı bölgenizde yasal olarak uygulanabilir.**

Kapalı kurumsal sistemlerde, ekonomi daha basit tahsise yol açar (yöneticiler iş atar, metrikler dahilidir). Ekonomi literatürü çoğunlukla açık ağlara uygulanır.

## İnşa Et

`code/main.py` şunları uygular:

- `shapley(value_fn, agents)` — küçük N için numaralandırmayla kesin Shapley hesaplaması.
- `second_price_auction(bids)` — doğru-söylü mekanizma; kazanan en yüksek ikinci fiyatı öder.
- `Reputation` — üstel bozunma ve düşürme ile DID'ye bağlı itibar.
- Demo 1: üç ajan işbirliği yapar, kesin Shapley kredi atfını yapar.
- Demo 2: beş ajan bir görev yuvası için teklif verir; ikinci-fiyat açık artırması kazananı + ödemeyi seçer.
- Demo 3: heterojen itibarlı ajanlara 100 tur görev ataması; itibar-ağırlıklı yönlendirme rastgeleyi yener.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: her ajan için Shapley değerleri; doğru-teklif dengesini gösteren açık artırma sonucu; ısınma sonrası kalitede rastgele üzerinden %10-20 kazanç gösteren itibar-ağırlıklı yönlendirme.

## Kullan

`outputs/skill-economy-designer.md` minimal bir ajan ekonomisi tasarlar: kimlik katmanı seçimi, kredi atfı mekanizması, ödeme mekanizması, itibar kuralı.

## Yayınla

2026'da ajan ekonomisi çalıştırmak:

- **Tokenlerle değil, itibarla başlayın.** İtibar tek başına uygulanması ucuz ve değerlidir; tokenler yasal ve ekonomik karmaşıklık ekler.
- **Ödüllendirmeden önce doğrulayın.** Bağımsız bir doğrulama adımı olmadan asla kredi dağıtmayın. Öz-bildirilen kalite sybil oyunlarını biriktirir.
- **Shapley-örnekle, Shapley-kesin değil.** 100-1000 sıralama örnekleyin; kesin numaralandırma ölçeklenmez.
- **Bozunma faktörünü sınırlayın ve itibarı tabanlayın.** Sınırsız bozunma meşru katkıda bulunanları siler; çok yavaş bozunma bayat yüksek-itibarlı ajanları ödüllendirir.
- **Mekanizmaları düşmanca denetleyin.** Ağı açmadan önce kırmızı-takım senaryoları çalıştırın. Her mekanizmanın bir oyun teorisi vardır; delikleri siz bulmak istersiniz, saldırganlar değil.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Shapley değerlerinin toplam değere eşit olduğunu doğrulayın (verimlilik aksiyomu). Değer fonksiyonunu değiştirin; Shapley tahsisleri beklenen yönde değişiyor mu?
2. Shapley *örneklemesi* uygulayın (K sıralama üzerinde Monte Carlo). K, yaklaşık doğruluğu nasıl etkiler? N=4 için kesin ile karşılaştırın.
3. Açık artırmadan önce bir koalisyon-oluşturma adımı uygulayın: ajanlar takımlar halinde birleşebilir ve birim olarak teklif verebilir. Hangi koalisyonlar oluşur? Sonuç, bireysel teklif vermekten Pareto-daha-iyi mi?
4. Google Research mekanizma-tasarımı yazısını okuyun. İhlal edildiğinde doğruluğu bozan bir varsayımı belirleyin. LLM ayarında bu başarısızlık kipi nasıl görünür?
5. AAMAS 2025 merkezsiz LaMAS makalesini okuyun. Sentezik bir görev üzerinde 10 ajan üzerinde Shapley adımlarını uygulayın. Kesin hesaplama ne kadar sürer? 100 çekilişle örnekleme ne kadar yakınlaşır?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| DePIN | "Merkezsiz fiziksel altyapı" | Token-teşvikli hesaplama/depolama/bant genişliği. Bittensor, Akash, Render. |
| DID | "Merkezsiz tanımlayıcı" | W3C spesifikasyonu, taşınabilir kimlikler için. Ajan itibarı platforma değil DID'ye bağlanır. |
| ERC-4337 | "Hesap soyutlama" | Gas sponsor olabilen sözleşme hesapları, ajan ödemelerine izin verir. |
| Shapley değeri | "Adil kredi atfı" | Verimlilik, simetri, doğrusallık, boş aksiyomlarını karşılayan tekil tahsis. |
| İkinci-fiyat açık artırması | "Vickrey açık artırması" | Doğru-söylü mekanizma: kazanan en yüksek ikinci teklifi öder. Monoton toplama uyumlu. |
| İtibar sermayesi | "Birikmiş kalite puanı" | DID'ye bağlı, onaylanmış katkılardan gelen puan; zamanla bozunur. |
| Ajanik DAO | "Ajanlar + insanlar yönetir" | Birinci-sınıf ajan oy verenleri olan DAO; oy gücü itibara bağlı. |
| TAO / FET / GPU kredileri | "Token birimleri" | Bittensor TAO, Fetch.ai FET, çeşitli DePIN token'ları. |

## İleri Okuma

- [The Agent Economy](https://arxiv.org/abs/2602.14219) — 2026 5-katmanlı ajan-ekonomisi yığını taraması
- [Google Research — Mechanism design for large language models](https://research.google/blog/mechanism-design-for-large-language-models/) — monoton toplamalı token açık artırmaları
- [AAMAS 2025 — merkezsiz LaMAS](https://www.ifaamas.org/Proceedings/aamas2025/pdfs/p2896.pdf) — Shapley-değeri kredi atfı
- [Bittensor TAO belgeleri](https://docs.bittensor.com/) — alt-ağ yapısı ve ödül dağılımı
- [Fetch.ai / ASI İttifakı](https://fetch.ai/) — ASI-1 Mini LLM ve FET token'ı
- [W3C Merkezsiz Tanımlayıcılar (DID'ler) spesifikasyonu](https://www.w3.org/TR/did-core/) — kimlik temeli
