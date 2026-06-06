# Multimodal Ajanlar ve Bilgisayar Kullanımı (Bitirme Projesi)

> 2026 sınır ürünü, ekran görüntülerini (screenshot) okuyan, düğmelere tıklayan, web arayüzlerinde gezinen, formları dolduran ve iş akışlarını uçtan uca tamamlayan bir multimodal ajandır. SeeClick ve CogAgent (2024) GUI temelleme (grounding) ilkesini kanıtladı. Ferret-UI mobil'i ekledi. ChartAgent grafikler için görsel araç kullanımını tanıttı. VisualWebArena ve AgentVista (2026) sınırın peşinden koştuğu benchmark'lardır — ve hatta Gemini 3 Pro ve Claude Opus 4.7 AgentVista'nın zor görevlerinde ~%30 alır. Bu bitirme projesi, Faz 12'nin tüm ipliklerini bir araya getirir: algılama (yüksek çözünürlüklü VLM), çıkarma (araç kullanan LLM), temelleme (koordinat çıktısı), uzun vadeli bellek ve değerlendirme.

**Tür:** Bitirme Projesi
**Diller:** Python (stdlib, eylem şeması + ajan döngüsü iskeleti)
**Ön koşullar:** Faz 12 · 05 (LLaVA), Faz 12 · 09 (Qwen-VL JSON), Faz 14 (Ajan Mühendisliği)
**Süre:** ~240 dakika

## Öğrenme Hedefleri

- Bir multimodal ajan döngüsü tasarlayın: algıla → çıkar → hareket et → gözlemle → tekrarla.
- VLM'in JSON olarak üretebileceği bir GUI temelleme çıktı şeması (tıklama koordinatları, metin yazdırma, kaydırma, sürükleme) inşa edin.
- Sadece ekran görüntüsü kullanan ajanları erişilebilirlik ağacı (accessibility tree) ajanlarıyla ve hibrit ajanları karşılaştırın.
- Küçük bir VisualWebArena diliminde multimodal ajan benchmark değerlendirmesi kurun.

## Problem

Bir rezervasyon sitesi iş akışı: "bana 15 Nisan için Tokyo'ya 800$ altında koridor koltuğu olan bir uçuş bul, rezervasyon yap."

Bir multimodal ajan şunları yapmalıdır:

1. Tarayıcının bir ekran görüntüsünü alır.
2. Ekran görüntüsünü + URL'yi + hedefi bir plana ayrıştırır.
3. Yapılandırılmış bir eylem üretir: tıkla (x,y'de), "Tokyo" yaz (E unsurunda), aşağı kaydır, seç (radyo düğmesi).
4. Eylemi tarayıcıya uygular.
5. Yeni durumu gözlemler (bir sonraki ekran görüntüsü).
6. Görev tamamlanana kadar tekrarlar.

Her adım bir multimodal VLM çağrısıdır. VLM çıktısı ayrıştırılabilir JSON olmalıdır. Hatalar adımlar boyunca birikir, bu yüzden kurtarma önemlidir.

## Kavram

### GUI temelleme — ilke

GUI temelleme: bir ekran görüntüsü ve doğal dil talimatı verildiğinde, tıklanacak (x, y) koordinatını (veya diğer eylemi) çıktı olarak vermek.

SeeClick (arXiv:2401.10935) büyük ölçekte ilk açık sonuçtu: sentetik + gerçek GUI verisiyle bir VLM'i ince ayarlayın, koordinatları düz metin token'ları olarak üretin. Çalışır.

CogAgent (arXiv:2312.08914) yoğun arayüzler için 1120x1120 yüksek çözünürlüklü kodlama ekledi. Puan: web gezintisinde ~%84.

Ferret-UI (arXiv:2404.05719) mobil arayüzlere odaklanır, iOS erişilebilirlik verisiyle bütünleşir.

Çıktı formatı genellikle JSON'dur:

```json
{"action": "click", "x": 384, "y": 220, "element_desc": "Search button"}
```

`element_desc` kurtarmaya yardımcı olur: koordinatlar ekran görüntüleri arasında kayarsa, semantik ipucu sistemin yeniden temellenmesine olanak tanır.

### Eylem şemaları

Tipik bir eylem şeması 6-10 eylem türüne sahiptir:

- `click`: (x, y)
- `type`: (metin, x?, y?)
- `scroll`: (yön, miktar)
- `drag`: (x0, y0, x1, y1)
- `select`: (seçenek_indeksi)
- `hover`: (x, y)
- `navigate`: (url)
- `wait`: (ms)
- `done`: (başarı, açıklama)

Ajan adım başına bir eylem üretir. Tarayıcı sarıcı (wrapper) uygular ve yeni durumu döndürür.

### Sadece ekran görüntüsü vs erişilebilirlik ağacı

İki girdi modu:

- Sadece ekran görüntüsü: tam görüntü, yapısal bilgi yok. En genel; herhangi bir uygulamada çalışır.
- Eryişilebilirlik ağacı: yapılandırılmış DOM / iOS erişilebilirlik bilgisi. Temelleme için çok daha güvenilir; ağacın mevcut olduğu yerde çalışır.
- Hibrit: her ikisi de, atomik eylemler için güvenilir temelleyici olarak ağaç ve semantik bağlam için ekran görüntüsü.

Üretim ajanları mümkün olduğunca hibrit kullanır. Tarayıcı otomasyonu (Selenium + erişilebilirlik) her zaman ağaçtır; masaüstü uygulamaları bazen öyle.

### Uzun vadeli bellek

20 adımlık bir iş akışı 20 ekran görüntüsü üretir. VLM'in bağlamı hızla dolar. Üç sıkıştırma stratejisi:

- Özet zinciri (summary-chain): her 5 adımdan sonra ne olduğunu özetleyin, eski ekran görüntülerini bırakın.
- Atlamalı kare: ilkini, sonuncusunu ve her 3.'yü saklayın.
- Araç-kayıtlı günlük: eylemleri uygulayın, ne yapıldığına dair metin günlük saklayın; eski ekran görüntülerine tekrar bakmayın.

Claude'nin bilgisayar kullanımı API'si günlük paternini kullanır. Daha basit, daha güvenilir.

### Görsel araç kullanımı

ChartAgent (arXiv:2510.04514) grafik anlama için görsel araç kullanımını tanıtır: kırpma, yakınlaştırma, OCR, harici algılayıcı çağırma. Ajan "bölgeyi (100, 200, 300, 400) kırp sonra OCR çağır" şeklinde bir araç çağrısı üretebilir. Araç metni döndürür; VLM çıkarmaya devam eder.

Bu patern genelleşir: set-of-mark prompting, bölge notlandırma ve harici algılayıcı araçların tümü aynı "bir araç çağrısı üret, yapılandırılmış yanıt al" şemasına uyar.

### 2026 benchmark'ları

- ScreenSpot-Pro. ~1k web ekran görüntüsü üzerinde GUI temelleme. Açık SOTA Qwen2.5-VL-72B ~%85. Sınır ~%90.
- VisualWebArena. Uçtan uca web görevleri (alışveriş, forum, ilanlar). Açık SOTA ~%20. Gemini 3 Pro ~%27.
- AgentVista (arXiv:2602.23166). En zor 2026 benchmark'ı. 12 gerçekçi iş akışı. Sınır modelleri %27-40 alır; açık modeller %10-20.
- WebArena / WebShop. Daha eski benchmark'lar; sınır tarafından doyurulmuş.

### Neden hâlâ zor

Ajan performansı darboğazları:

1. İnce ölçekte görsel temelleme. "Küçük X'e tıkla" mobil çözünürlükte sık sık başarısız olur.
2. Uzun vadeli planlama. 10 eylemden sonra ajan hedeften sapar.
3. Hata kurtarma. Bir tıklama başarısız olduğunda (yanlış düğme), algılama + kurtarma nadiren eğitilmiş veridir.
4. Sayfalar arası bağlam. Sekmeler veya uzun formlar arası atlama durumu kaybeder.

Araştırma yönleri: bellek mimarileri, açık yeniden planlama, multimodal doğrulama (eylem başarısı için ekran görüntüsü eşleşmesi).

### Bitirme projesi inşası

Bitirme görevi: bir bilgisayar kullanan ajan inşa edin ki:

1. Bir rezervasyon sitesi sahte sayfasının HTML + ekran görüntüsünü okusun.
2. Çok adımlı bir dizi planlasın: ara → seç → form doldur → gönder.
3. Eylem şemasına uyan JSON eylemleri ürete sabit 10 görev diliminde değerlendirin.

Ders, gerçek bir tarayıcıya kolayca genişletilebilir iskelet kodu sağlar.

## Kullan

`code/main.py` bitirme projesi iskeletidir:

- Eylem şeması JSON tanımı (10 eylem).
- Sözlük olarak sahte tarayıcı durumu.
- Ajan döngüsü iskeleti: durumu al, eylem üret, uygula, döngü.
- Uçtan uca başarı oranını ölçmek için 10 görevlik mini benchmark (sentetik sayfalar).
- Bir eylem başarısız olduğunda hata kurtarma kancası.

## Teslim Et

Bu ders `outputs/skill-multimodal-agent-designer.md` dosyasını üretir. Bir bilgisayar kullanan ürün (alan, eylem kümesi, değerlendirme hedefi) verildiğinde tam ajan döngüsünü, bellek stratejisini, temelleme modunu ve beklenen benchmark puanını tasarlar.

## Alıştırmalar

1. Eylem şemasını `screenshot_region` aracıyla (kırpma + yakınlaştırma) genişletin. Hangi görevler yararlanır?

2. AgentVista'yı okuyun (arXiv:2602.23166). En zor görev kategorisini ve neden sınır modellerinin hâlâ başarısız olduğunu tanımlayın.

3. Uzun vadeli bellek sıkıştırması: canlı tutulan ≤4 ekran görüntüsüyle bir özet zinciri tasarlayın, herhangi bir sayıda günlük saklayın.

4. Bir hata kurtarma kancası inşa edin: eylem başarısız olduğunda (düğme bulunamadı), ajan bir sonraki adımda ne yapar?

5. Sadece ekran görüntüsü kullanan Claude 4.7'yi hibrit ekran görüntüsü + erişilebilirlik ağacı Qwen2.5-VL ile 10 web görevinde karşılaştırın. Hangi görevlerde hangisi kazanır?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| GUI temelleme | "Tıklama koordinatları" | Model ekran görüntüsünde bir talimatın hedefi için (x,y) çıktısı verir |
| Eylem şeması | "Araç tanımları" | Geçerli eylemlerin (tıkla, yaz, kaydır, sürükle) JSON tanımı |
| Erişilebilirlik ağacı | "Yapılandırılmış DOM" | Tarayıcı/iOS API'lerinden makine-okunabilir arayüz hiyerarşisi |
| Hibrit ajan | "Ekran görüntüsü + ağaç" | Hem görüntü hem yapısal bilgi kullanır; her ikisinden daha güvenilir |
| Görsel araç kullanımı | "Yakınlaştır/kırp/algıla" | Ajan plan sırasında harici görme araçlarını (OCR, algılama) çağırır |
| Özet zinciri | "Bellek sıkıştırması" | Periyodik metin özetleri uzun ekran görüntüsü geçmişinin yerini alır |
| VisualWebArena | "Uçtan uca web benchmark'ı" | 2024 uçtan uca web görevleri benchmark'ı |
| AgentVista | "2026 zor benchmark" | 12 gerçekçi iş akışı; hatta Gemini 3 Pro ~%30 alıyor |

## Daha Fazla Kaynak

- [Cheng ve ark. — SeeClick (arXiv:2401.10935)](https://arxiv.org/abs/2401.10935)
- [Hong ve ark. — CogAgent (arXiv:2312.08914)](https://arxiv.org/abs/2312.08914)
- [You ve ark. — Ferret-UI (arXiv:2404.05719)](https://arxiv.org/abs/2404.05719)
- [ChartAgent (arXiv:2510.04514)](https://arxiv.org/abs/2510.04514)
- [Koh ve ark. — VisualWebArena (arXiv:2401.13649)](https://arxiv.org/abs/2401.13649)
- [AgentVista (arXiv:2602.23166)](https://arxiv.org/abs/2602.23166)
