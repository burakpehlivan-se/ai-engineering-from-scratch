# Milyon Token Bağlamında Uzun Video Anlama

> 24 FPS'de 1 saatlik 4K video, yamalandı ve gömüldüğünde yaklaşık 60 milyon token üretir. 2 saatlik bir podcast bölümünün transkripti 30.000 token'dır. Tam bir Blu-ray film, agresif havuzlama ile bile sıkıştırılsa yüz binlerce token'dır. Google'ın Gemini 1.5'i (Mart 2024) 10 milyon token bağlamıyla bu çağı açtı ve saatlik videolar üzerinde güvenilir iğne-içinde-haystack (needle-in-a-haystack) hatırlaması yaptı. LWM (Liu ve ark., Şubat 2024) ring attention'ın ölçekleme yolunu gösterdi. LongVILA ve Video-XL alımı daha da ölçeklendirdi. VideoAgent ham bağlam yerine ajanlı (agentic) erişimi tercih etti. Her yaklaşım, hesaplama, hatırlama ve mühendislik karmaşıklığı üzerinde farklı bir tavizdir. Bu dersleri yan yana okur.

**Tür:** İnşa Et
**Diller:** Python (stdlib, iğne-içinde-haystack simülatörü + ajanlı-erişim yönlendiricisi)
**Ön koşullar:** Faz 12 · 17 (video zamansal token'ları)
**Süre:** ~180 dakika

## Öğrenme Hedefleri

- Değişken FPS ve havuzlamayla uzun biçimli video için toplam görsel-token sayılarını hesaplayın.
- Üç ölçekleme yolunu açıklayın: ham bağlam (Gemini 1.5), ring attention (LWM), token sıkıştırma (LongVILA / Video-XL).
- Ham bağlam video VLM'lerini ajanlı-erişim video VLM'leriyle (VideoAgent) doğruluk ve gecikme açısından karşılaştırın.
- 30 dakikalık bir video için iğne-içinde-haystack testi tasarlayın ve belirli bir dakikada hatırlamayı ölçün.

## Problem

Qwen2.5-VL boyutunda, 384 yerel çözünürlükte tek bir kare yaklaşık 729 token'dır. 3x3 havuzlamayla kare başına 81 token. 1 FPS'de 30 dakikalık klip = 1800 kare = 145.800 token. 2025 açık VLM'leri için mümkündür, sıkışık. 2 FPS'de 291.600 token — sadece en büyük bağlamlar sığar.

1 FPS'de 2 saatlik film 583k token'dır. 2026'daki çoğu açık modelin ötesinde; Gemini 2.5 Pro veya daha agresif havuzlama gerektirir.

Üç ölçekleme yolu ortaya çıktı.

## Kavram

### Yol 1: Ham bağlam (Gemini 1.5, Claude Opus)

Donanımı soruna fırlatın. Bağlamı milyonlarca token'a ölçekleyin, her şeyi tek bir ileri geçişte işleyin.

Gemini 1.5 Pro 1M token ile başladı; Gemini 1.5 Ultra 10M'ye; Gemini 2.5 Pro 2026'da saatlik videoları güvenilir bir şekilde işler. Makale (arXiv:2403.05530) ~9.5M token'a kadar %99.7 iğne-içinde-haystack hatırlaması belgelemiştir.

Mühendislik: bellek hiyerarşisi (yerel + küresel +seyrek) artı MoE expert yönlendirmesiyle uzun bağlam verimliliği için özel bir attention uygulaması. Tam olarak yayınlanmamış. Açık kaynak değil.

### Yol 2: Ring attention (LWM, LongVILA)

Ring attention, uzun dizileri "halka" (ring) içindeki cihazlara dağıtır; her cihaz bir parçayı tutar. Tüm dizi üzerinde attention, her cihazın parçasını halka deseninde bir sonraki göndermesi, kısmi attention hesaplaması ve toplamasıyla gerçekleşir.

LWM (Liu ve ark., 2024) bu şekilde 1M token bağlam modeli eğitti. Eğitim hesaplaması bağlamla orantılı olarak değil, karesel olarak ölçeklenir — attention'daki karesel vuruş, halkanın cihazları arasında amorti edilir.

LongVILA (arXiv:2408.10188) paterni VLM'lere uyarladı. Kare başına 196 token ile 1400 karelik videolar = 268k bağlam, 8 yollu paralellikle ring attention ile eğitildi.

### Yol 3: Token sıkıştırma (Video-XL, LongVA)

Ham bağlamdan daha ucuz: LLM diziyi görmeden önce agresif olarak sıkıştırın.

Video-XL (arXiv:2409.14485) görsel özet token'ı kullanır: N kareden oluşan her klip, N üzerinden dikkat eden tek bir "özet" token üretir. Çıkarımda LLM klip başına bir özet token'ı görür, bağlamı dramatik olarak küçültür.

LongVA, "uzun bağlam aktarma" tekniğiyle LLM bağlamını 200k'den 2M'ye genişletir. Uzun bağlam metni üzerinde eğitir, ortak temsil aracılığıyla uzun bağlam videosuna aktarır.

Token sıkıştırma, belirli zaman damgalarında hatırlamayı ölçeklenebilirlikle değiştirir. Model genel olarak ne olduğunu bilir ancak bazen kesin kareleri kaçırır.

### Yol 4: Ajanlı erişim (VideoAgent)

Tam videoyu LLM'e beslemeyin. Bunun yerine videoyu bir veritabanı olarak düşünün ve bir LLM ile sorgulayın.

VideoAgent (arXiv:2403.10517):

1. LLM soruyu okur.
2. LLM bir erişim aracından ilgili klipler ister ("bana kedi olan segmentleri göster").
3. Araç eşleşen klip zaman damgalarını döndürür.
4. LLM bu klipleri bir VLM aracılığıyla okur.
5. LLM cevabı birleştirir veya takip sorguları yapar.

Bu, uzun videoya uygulanan LLM-olarak-ajan paternidir. Daha ucuz çıkarım (sadece ilgili klipler kodlanır), daha zor mühendislik (erişim kalitesi darboğaz haline gelir).

### İğne-içinde-haystack benchmark'ları

Standart uzun bağlam testi: videonun rastgele bir noktasına benzersiz bir görsel veya metinsel işaret (marker) yerleştirin, ardından onu hatırlamayı gerektiren bir sorgu sorun.

Metrik: Video uzunluğu ve işaret konumu boyunca Recall@k.

Gemini 2.5 Pro, 90 dakikaya kadar videolarda >99% hatırlama puanı alır. Açık 72B modelleri (Qwen2.5-VL-72B, InternVL3-78B) 30 dakikada ~%85-90 alır ve 60'ın ötesinde bozulur.

VideoAgent, araç iyi ise 2+ saatte ham bağlam modellerini eşleyebilir veya yenebilir çünkü erişim iğneyi bulur.

### Hangi yolu seçmek için

Sınır doğruluğunda 15 dakikalık klip için: açık 72B + doğal bağlam genellikle işe yarar. Qwen2.5-VL-72B'yi seçin.

30 dakika ila 1 saatlik içerik için: açık kaynak için LongVILA veya Video-XL; kapalı kaynak için Gemini 2.5 Pro. Kalite barı önemlidir — sınır kalitesi kapalı kaynaklara gider.

2+ saatlik içerik için: VideoAgent veya benzer erişim paternleri. Alternatif olarak, daha küçük parçalara özetleyin ve hiyerarşik özetler besleyin.

### 2026 üretim paterni

Pratikte, üretim uzun video boru hatları (pipeline) hibritdir:

1. Tüm video üzerinde dinamik-FPS örnekleme + agresif havuzlama çalıştırın (100k token küresel temsil elde edin).
2. Küresel özet için 72B VLM'e besleyin.
3. Kullanıcı ayrıntılı sorular sorarsa, özet indeksini kullanarak ajanlı erişim çalıştırın.

Bu, küresel anlama için ham bağlamı ve yerel ayrıntı için erişimi birleştirir.

## Kullan

`code/main.py`:

- 1 dakika ila 3 saat arası videolar için değişken FPS + havuzlamayla token bütçelerini hesaplar.
- Bir iğne-içinde-haystack çalışmasını simüle eder: rastgele bir zaman damgasına bir işaret enjekte eder, bir soru sorar, hatırlamayı puanlar.
- Belirli klipleri aşağı akım VLM'e beslemek için ajanlı-erişim yönlendiricisi simülatörü içerir.

Bütçe tablosunu çalıştırın ve ölçek farkını hissedin.

## Teslim Et

Bu ders `outputs/skill-long-video-strategy-planner.md` dosyasını üretir. Bir video süresi ve sorgu karmaşıklığı verildiğinde ham bağlam, sıkıştırma ve ajanlı erişim arasında seçim yapar ve gecikme + kalite beklentilerini hesaplar.

## Alıştırmalar

1. 1 FPS'de 45 dakikalık ders, kare başına 81 token. Toplam token? Hangi modellerin bağlamına sığar?

2. Bir iğne-içinde-haystack testi tasarlayın: işareti hangi dakikaya enjekte edersiniz ve kesin sorgu formatı nedir?

3. Ham bağlam Qwen2.5-VL-72B (80k bağlam) ile VideoAgent'ı (Claude 3.5 + erişim) 1 saatlik videoda karşılaştırın. Hangisi hatırlamada kazanır? Hangisi gecikmede kazanır?

4. Ring attention'ın bellek maliyeti dizi uzunluğuyla ve cihaz sayısıyla orantılı olarak ölçeklenir. Nedenini açıklayın ve halka-döngü (ring-rotation) aşamasını düşürürseniz ne olduğunu açıklayın.

5. Gemini 1.5 Bölüm 5'i iğne-içinde-haystack üzerine okuyun. Makale 1M ile 10M token sınırında hatırlama hakkında ne buldu?

## Anahtar Terimler

| Terim | Ne deniyor | Aslında ne anlama geliyor |
|-------|-----------|--------------------------|
| Ham bağlam | "Sadece daha fazla token" | LLM bağlamını milyonlarca token'a ölçekle; her şeyi tek geçişte işle |
| Ring attention | "LWM tarzı paralellik" | Her cihazın bir parçayı tuttuğu ve döndüğü dağıtılmış attention paterni |
| Token sıkıştırma | "Özet token'ları" | Öğrenilmiş bir sıkıştırıcı aracılığıyla klip başına token sayısını LLM'den önce azaltma |
| İğne-içinde-haystack | "NIH testi" | Rastgele bir noktaya benzersiz bir işaret yerleştir, test zamanında modelden hatırlamasını iste |
| Ajanlı erişim | "LLM olarak sorgu planlayıcı" | LLM ilgili klipler için bir erişim aracından ister, bunları bir VLM aracılığıyla okur, cevabı birleştirir |
| VideoAgent | "Video için erişim paterni" | Kanonik ajanlı-erişim tasarımı: soru → araç → klip → cevap |

## Daha Fazla Kaynak

- [Gemini Takımı — Gemini 1.5 (arXiv:2403.05530)](https://arxiv.org/abs/2403.05530)
- [Liu ve ark. — LWM / RingAttention (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Xue ve ark. — LongVILA (arXiv:2408.10188)](https://arxiv.org/abs/2408.10188)
- [Shu ve ark. — Video-XL (arXiv:2409.14485)](https://arxiv.org/abs/2409.14485)
- [Wang ve ark. — VideoAgent (arXiv:2403.10517)](https://arxiv.org/abs/2403.10517)
