# Başarısızlık Kipleri — MAST, Groupthink, Monokültür, Kademeli Hatalar

> 2026 için referans taksonomi **MAST**'tır (Cemri ve diğerleri, NeurIPS 2025, arXiv:2503.13657), 7 son teknoloji açık kaynak MAS'ta 1642 yürütme izinden türetilmiş ve **%41-86,7 başarısızlık oranı** göstermektedir. Üç kök kategori: **Spesifikasyon Problemleri** (%41,77) — rol belirsizliği, belirsiz görev tanımları; **Koordinasyon Başarısızlıkları** (%36,94) — iletişim kopmaları, durum uyumsuzluğu; **Doğrulama Boşlukları** (%21,30) — eksik doğrulama, bulunmayan kalite kontrolleri. **Groupthink** ailesi (arXiv:2508.05687) şunları ekler: monokültür çöküşü (aynı temel model → ilişkili hatalar), uyum yanlılığı (ajanlar birbirlerinin hatalarını güçlendirir), yetersiz zihin kuramı, karışık-motiv dinamikleri, kademeli güvenilirlik başarısızlıkları. Kademeli örnek: bir ödeme başarısızlığının sipariş yeniden denemelerini tetiklediği, envanter yeniden denemelerini tetiklediği ve envanter hizmetini bunaltan (saniyeler içinde 10x yük — devre kesicilere ihtiyaç var) yeniden deneme fırtınaları. Bellek zehirlenmesi: bir ajanın halüsinasyonu paylaşılan belleğe girer, aşağı akış ajanları onu olgu olarak ele alır; doğruluk kademeli olarak bozulur ve kök neden teşhisi acı verir. **STRATUS** (NeurIPS 2025) uzmanlaşmış tespit/teşhis/doğrulama ajanları aracılığıyla 1,5x hafifletme-başarı iyileşmesi bildirir. Bu ders, başarısızlık kiplerini birinci-sınıf mühendislik hedefleri olarak ele alır.

**Tip:** Öğren
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 13 (Paylaşımlı Bellek), Faz 16 · 14 (Konsensüs ve BFT), Faz 16 · 15 (Oylama ve Tartışma Topolojisi)
**Süre:** ~75 dakika

## Problem

Multi-agent sistemleri gerçek görevlerde zamanın %41-86,7'sinde başarısız olur (Cemri ve diğerleri 2025 bunu 7 açık kaynak MAS'ta ölçtü). Bu, "daha fazla ajan ekle" ile hata ayıklanabilir değildir. Başarısızlıkların yapısal nedenleri vardır. MAST taksonomi size kategorileri verir. Bu ders her kategoriyi somut bir tespit, teşhis ve hafifletme kalıbına eşler, böylece sayılar keyfi görünmeyi bırakır.

2026 üretim pratiği, başarısızlık kiplerini tasarım girdileri olarak ele almaktır. Mimariniz, her MAST kategorisini gösterebilene ve konuşlandırdığınız hafifletmeyi adlandırabilene kadar "yeterince iyi" değildir.

## Kavram

### MAST kategorileri

**Spesifikasyon Problemleri (başarısızlıkların %41,77'si).** Ajanın görevi yeterince sıkı tanımlanmamıştır. Örnekler:

- Rol belirsizliği: iki ajan da kendisinin gözden geçiren olduğunu düşünür.
- Görev yetersiz tanımlanmış: kullanıcı belirli bir açı istediğinde "bunu özetle".
- Başarı kriterleri örtük: ajan başarıp başaramadığını söyleyemez.

Hafifletmeler:
- Açık rol sözleşmeleri yazın. Her ajanın istemi ne yaptığını *ve ne yapmadığını* belirtir.
- Görev başına kabul testleri. Ajan başlamadan önce, "bitti X gibi görünür" tanımlayın.
- Uçuş öncesi spesifikasyon kontrolü: ayrı bir ajan, göndermeden önce görev tanımını gözden geçirir.

**Koordinasyon Başarısızlıkları (%36,94).** İletişim veya durum kopmaları.

Örnekler:
- İki ajan senkronizasyon olmadan paylaşılan durumu günceller.
- Ajanlar arasında mesaj kaybolur (kuyruk başarısızlığı, zaman aşımı).
- Durum kayması: ajan A görevin bittiğini düşünür; ajan B hâlâ yürütüyor.

Hafifletmeler:
- İyimser eşzamanlılıkla sürümlenmiş paylaşılan durum.
- Kritik mesajlar için açık onay (kabul edilene kadar yeniden dene).
- Periyodik durum-senkronizasyonu kontrol noktaları; kaymayı erken tespit edin.

**Doğrulama Boşlukları (%21,30).** Çıktılar üzerinde bağımsız kontrol yok.

Örnekler:
- Bir ajan başarı iddia eder; kimse doğrulamaz.
- Ajanlar zincirinin her biri bir öncekinin çıktısına güvenir.
- Acilen oluşan birleşik davranışta test kapsamı eksik.

Hafifletmeler:
- Bağımsız doğrulayıcı ajan (Ders 13). Salt okunur, bağımsız kaynak erişimi.
- Açık teslim sözleşmesi: "A'nın çıktısı, B başlamadan önce denetçi C'yi geçmelidir."
- Sonradan analiz için sonuç günlüğü.

### Groupthink ailesi (arXiv:2508.05687)

Ajanlar homojenleştiğinde veya birbirini taklit ettiğinde beş ilişkili başarısızlık:

**Monokültür çöküşü.** Aynı temel model veya eğitim verisi → ilişkili hatalar. Üç ajan bir LLM'yi paylaştığında, halüsinasyonlarını paylaşırlar.

**Uyum yanlılığı (conformity bias).** Ajanlar, yanlış olsa bile en yüksek sesli veya en güvenli akrana doğru ayar yapar.

**Yetersiz ToM.** Ajanlar birbirlerinin inançlarını modellemede başarısız olur; koordinasyon bozulur (Ders 18).

**Karışık-motiv dinamikleri.** Kısmen hizalanmış teşviklere sahip ajanlar kimseyi tatmin etmeyen orta-uzlaşmaya kayar.

**Kademeli güvenilirlik başarısızlıkları.** Bir bileşenin hata örüntüsü, bağımlı bileşenlerde hata örüntülerini tetikler.

### Kademeli örnek — yeniden deneme fırtınası

Klasik 2026 olay kalıbı:

```
ödeme hizmeti isteklerin %10'unda başarısız olur
   ↓
sipariş ajanı ödemeyi yeniden dener (üstel geri çekilme ama saf)
   ↓
her yeniden deneme yeni bir sipariş-envanter kontrolüdür
   ↓
envanter hizmeti normal yükün 2 katını görür
   ↓
envanter hizmeti zaman aşımına uğramaya başlar
   ↓
her sipariş envanter kontrolünü yeniden dener
   ↓
envanter hizmeti normal yükün 10 katını görür
   ↓
küme çöker
```

#### Açıklama
Çözüm klasiktir: **devre kesiciler (circuit breakers)**. Aşağı akış hata oranı eşiği aştığında, önbelleğe alınmış veya varsayılan sonuçlarla kısa devre yapın. Artı istek başına sınırlı yeniden deneme bütçesi.

Devre kesiciler, değişiklik olmadan doğrudan dağıtık sistemlerden ödünç aldığınız az sayıdaki multi-agent başarısızlık hafifletmesidir.

### Bellek zehirlenmesi (yeniden ziyaret edildi)

Ders 13'ten: bir ajanın halüsinasyonu paylaşılan-bellek olgusu olur; aşağı akış ajanları zehirli olgudan muhakeme yürütür. MAST terimleriyle, bu paylaşılan-bellek katmanında bir doğrulama boşluğudur.

Kademeli doğruluk bozulması semptomdur. Çökme almazsınız; teşhisi zor olan yavaş bir kayma alırsınız.

Hafifletme: yalnızca-eklemeli günlük, kaynak takibi, yazılamaz doğrulayıcı. Zaten Ders 13'te ele alındı.

### STRATUS — başarısızlık tespiti için uzmanlaşmış ajanlar

STRATUS (NeurIPS 2025) şunları konuşlandırdığınızda 1,5x hafifletme-başarı iyileşmesi bildirir:

- **Tespit ajanı.** Semptom örüntülerini izler (yüksek anlaşmazlık, yeniden deneme sıçramaları, doğruluk kayması).
- **Teşhis ajanı.** Semptomlar verildiğinde, MAST taksonomisinden olası kök nedeni çıkarır.
- **Doğrulama ajanı.** Bir hafifletme uygulandıktan sonra, semptomların temizlendiğini kontrol eder.

Bu, ajan sistemlerine uygulanan SRE-tarzı olay yanıtıdır. Üç rol de uzmanlaşmış istemli LLM ajanları olabilir.

### Başarısızlık-kipleri denetimi

2026 en iyi pratiği yıllık (veya büyük-sürüm başına) bir başarısızlık-kipleri denetimidir:

1. **İz örneği.** ~1000 gerçek yürütme izi toplayın.
2. **Kategorize edin.** Her izin başarısızlıklarını MAST + Groupthink kategorilerine eşleyin.
3. **Kategori başına başarısızlık oranını hesaplayın.** Sisteminizde hangi kategoriler baskın?
4. **Hafifletmeleri sıralayın.** Hangi düzeltme en fazla başarısızlığı ortadan kaldırır?
5. **2-3 hafifletme seçin.** Uygulayın; gelecek çeyrekte yeniden denetleyin.

Disiplin, belirli seçimlerden daha önemlidir. Denetimler olmadan, başarısızlıklar gürültüye karışır ve sistematik olarak ele alınmaz.

### Sistemler sessizce başarısız olduğunda

En tehlikeli başarısızlık kategorisi sessiz doğruluk başarısızlığıdır. Yüksek sesle başarısız olan bir sistem (çökme, istisna, uyarı) izlenebilir. İnandırıcı-ama-yanlış çıktılar üreten bir sistem istisna günlükleriyle tespit edilemez. Bu, doğrulama boşluklarının sayıca yalnızca %21,30 olmasına rağmen başarısızlık başına en pahalı kategori olmasının nedenidir.

Şunlara yatırım yapın:
- Örnekleme-tabanlı insan incelemesi.
- Altın veri kümesi regresyon testleri.
- Önemli çıktılarda ajanlar-arası çapraz-kontrol.

### Başarısızlık vs yavaş başarısızlık

Bazı başarısızlıklar anlıktır; bazıları yavaştır. Anlık başarısızlıklar (zaman aşımı, şema uyumsuzluğu, kimlik doğrulama hatası) tespit edilmesi ucuzdur. Yavaş başarısızlıklar (bellek zehirlenmesi, monokültür kayması, rol belirsizliği) tespit edilmesi ve önlenmesi pahalıdır.

2026 mühendislik hamlesi: yavaş başarısızlık vekillerini, görünür bir hata olmadan önce kaymayı yakalayabilecek şekilde izleyin. Anlaşma oranı, yeniden deneme oranı, çıktı-uzunluk dağılımı ve art arda gelen ajan sürümleri arasındaki düzenleme mesafesi (edit distance) yararlı vekillerdir.

## İnşa Et

`code/main.py` şunları uygular:

- `FailureTaxonomy` — simüle edilmiş olayları MAST + Groupthink kategorilerine ayırır.
- `CircuitBreaker` — klasik kalıp; hata oranı eşiği aştığında açılır.
- `RetryStormSimulator` — kademeli başarısızlığı gösterir; devre kesiciyi açar/kapar.
- `DetectionAgent` — komut-dosyalı STRATUS tarzı semptom eşleştirici.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı:
- devre kesici olmadan yeniden deneme fırtınası: envanter hataları patlar (simüle).
- devre kesici ile: eşikte sınırlanır; bozulmuş-kip yanıtları sunulur.
- tespit ajanı kalıbı işaretler ve MAST kategorisini adlandırır.

## Kullan

`outputs/skill-mast-auditor.md` bir multi-agent sistem üzerinde MAST tarzı başarısızlık-kipleri denetimi çalıştırır. İzler → kategorizasyon → hafifletme sıralaması.

## Yayınla

Üretimde başarısızlık-kipleri disiplini:

- **Çeyrek başına MAST denetimi.** Yıllık değil. Sisteminiz büyüdükçe kategoriler kayar.
- **Her yerde devre kesiciler.** Herhangi bir bağımlı hizmete yapılan her giden çağrı. Varsayılan açık eşik %5-10 hata oranı.
- **Altın veri kümeleri.** Küçük, yüksek kaliteli, elle denetlenmiş. Onlara karşı haftalık regresyon-testi.
- **STRATUS üçlüsü.** Üretimi izleyen tespit + teşhis + doğrulama ajanları. Yalnızca tespit ajanıyla başlayın; semptomlar gürültülü olduğunda teşhis ekleyin.
- **Başarısızlık bütçesi.** Kategoriye göre başarısızlık oranı için açık SLO. Bütçeyi aşmak, göndermeyi-durdurma konuşmasını tetikler.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Devre kesicinin yeniden deneme fırtınasını sınırlandırdığını doğrulayın. Başarısızlık eşiğini değiştirin ve değiş-tokuşu gözlemleyin.
2. Bir **yavaş-başarısızlık vekili** uygulayın: 3 paralel ajan arasında anlaşma oranı. Keskin biçimde düştüğünde, uyarı tetikleyin. Ajan çıktılarını kademeli olarak ilişkilendirerek monokültür kaymasını simüle edin.
3. Cemri ve diğerleri (arXiv:2503.13657) okuyun. 7 MAS sistemlerinden birini seçin ve ilk 3 başarısızlık kategorisini eşleyin. Bunlar MAST'nin öngördükleriyle nasıl karşılaştırılır?
4. Groupthink makalesini (arXiv:2508.05687) okuyun. Beş kalıptan hangisinin üretimde tespit edilmesinin en zor olduğunu belirleyin. Bir vekil metrik önerin.
5. Bildiğiniz belirli bir multi-agent sistemi için STRATUS tarzı bir tespit-teşhis-doğrulama üçlüsü tasarlayın. Tespit hangi semptomları izler? Teşhis hangi hafifletmeleri önerir? Doğrulama çalıştıklarını nasıl doğrular?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| MAST | "2026 taksonomisi" | Cemri 2025; 3 kök kategori + 14 alt-tür başarısızlık. |
| Spesifikasyon Problemi | "Rol belirsizliği" | Görev veya rol yetersiz tanımlanmış; ajanlar ne yapacaklarını bilmiyor. |
| Koordinasyon Başarısızlığı | "Durum kayması" | Ajanlar arası iletişim veya senkronizasyon kopması. |
| Doğrulama Boşluğu | "Kimse kontrol etmedi" | Çıktılar bağımsız doğrulama olmadan kabul edildi. |
| Groupthink ailesi | "Homojenlik başarısızlıkları" | Monokültür, uyum, yetersiz ToM, karışık-motiv, kademeli. |
| Monokültür çöküşü | "Aynı model, aynı halüsinasyonlar" | Paylaşılan temel model veya eğitim verisinden ilişkili hatalar. |
| Yeniden deneme fırtınası | "Kademeli hata büyütmesi" | Bir başarısızlık, aşağı akışta yükü büyüten yeniden denemeleri tetikler. |
| Devre kesici | "Hata oranında hızlı başarısız ol" | Hata oranı eşiği aştığında aç; varsayılanla kısa devre yap. |
| STRATUS | "Olay yanıtı üçlüsü" | Tespit + teşhis + doğrulama ajanları. 1,5x hafifletme başarısı. |
| Bellek zehirlenmesi | "Halüsinasyonlar yayılır" | Paylaşılan-bellek olgusu kirli; aşağı akış ajanları zehirden muhakeme yürütür. |

## İleri Okuma

- [Cemri et al. — Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — MAST taksonomisi, NeurIPS 2025
- [Groupthink failures in multi-agent LLMs](https://arxiv.org/abs/2508.05687) — monokültür, uyum ve beş-aile taksonomisi
- [STRATUS — MAS olay yanıtı için uzmanlaşmış ajanlar](https://neurips.cc/) — NeurIPS 2025 proceedings girdisi (tespit + teşhis + doğrulama)
- [Release It! — stabilite kalıpları (Nygard)](https://pragprog.com/titles/mnee2/release-it-second-edition/) — kanonik devre kesici referansı
- [Anthropic — Çok-ajanlı araştırma sistemi](https://www.anthropic.com/engineering/multi-agent-research-system) — üretim başarısızlık-kipleri notları
