# Moderasyon Sistemleri — OpenAI, Perspective, Llama Guard

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/29-moderation-systems-openai-perspective-llamaguard/docs/en.md)

> Üretim moderasyon sistemleri, Dersler 12-16'da tanımlanan güvenlik politikalarını operasyonel hale getirir. OpenAI Moderation API: `omni-moderation-latest` (2024) GPT-4o üzerine inşa edilmiş, metin + görüntüleri tek çağrıda sınıflandırır; çok dilli test setinde önceki sürümden %42 daha iyi; yanıt şeması 13 kategori booleanı döner — taciz, taciz/tehdit, nefret, nefret/tehdit, yasadışı, yasadışı/şiddet, öz-zarar, öz-zarar/niyet, öz-zarar/talimatlar, cinsel, cinsel/reşit, şiddet, şiddet/grafik; çoğu geliştirici için ücretsiz. Katmanlı örüntüler: Giriş moderasyonu (üretim-öncesi), Çıkış moderasyonu (üretim-sonrası), Özel moderasyon (alan kuralları). Eşzamanlı paralel çağrılar gecikmeyi gizler; bayrak üzerine yer tutucu yanıtlar. Llama Guard 3/4 (Ders 16): 14 MLCommons tehlikesi, Kod Yorumlayıcı Kötüye Kullanımı, 8 dil (v3), çoklu-görüntü (v4). Perspective API (Google Jigsaw): LLM-as-moderator dalgasından önce gelen toksisite puanlaması; birincil olarak şiddetli-toksisite/hakaret/küfür değişkenleriyle tek-boyutlu toksisite; içerik-moderasyon araştırması için temel. Kullanımdan kaldırmalar: Azure Content Moderator Şubat 2024'te kullanımdan kaldırıldı, Şubat 2027'de emekli, Azure AI Content Safety ile değiştirildi.

**Tür:** Uygulama
**Diller:** Python (stdlib, üç-katmanlı moderasyon koşum takımı)
**Ön Koşullar:** Faz 18 · 16 (Llama Guard / Garak / PyRIT)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- OpenAI Moderation API'nin kategori taksonomisini ve Llama Guard 3'ün MLCommons kümesinden nasıl farklılaştığını açıklayın.
- Üç moderasyon-katmanı örüntüsünü (giriş, çıktı, özel) açıklayın ve her birinin bir başarısızlık modunu adlandırın.
- Perspective API'nin LLM-öncesi dönem temeli olarak konumunu ve araştırmada neden kullanılmaya devam ettiğini açıklayın.
- Azure kullanımdan kaldırma zaman çizelgesini belirtin.

## Sorun

Dersler 12-16 saldırıları ve savunma araçlarını açıklar. Ders 29, savunmaları kullanıcıların ürünle etkileşim kurduğu yüzeyde operasyonel hale getiren dağıtılmış moderasyon sistemlerini kapsar. Üç-katmanlı örüntü 2026 varsayılan yapılandırmasıdır.

## Kavram

### OpenAI Moderation API

`omni-moderation-latest` (2024). GPT-4o üzerine inşa edilmiş. Metin + görüntüleri tek çağrıda sınıflandırır. Çoğu geliştirici için ücretsiz.

Kategoriler (yanıt şemasında 13 boolean):
- taciz, taciz/tehdit
- nefret, nefret/tehdit
- öz-zarar, öz-zarar/niyet, öz-zarar/talimatlar
- cinsel, cinsel/reşit
- şiddet, şiddet/grafik
- yasadışı, yasadışı/şiddet

Çoklu-modal destek, `cinsel/reşit` dışında `şiddet`, `öz-zarar` ve `cinsel` için geçerlidir; geri kalanı yalnızca metin.

`code/main.py`'deki kod koşum takımı için, `/tehdit`, `/niyet`, `/talimatlar` ve `/grafik` alt-kategorilerini pedagogik sadelik için üst-düzey ebeveynlerine daraltırız. Üretim kodu tam 13-kategori şemasını kullanmalıdır.

Önceki-nesil moderasyon uç noktasına göre çok dilli test setinde %42 daha iyi. Kategori başına skorlar; uygulamalar eşikleri ayarlar.

### Llama Guard 3/4

Ders 16'da kapsanmıştır. 14 MLCommons tehlike kategorisi (OpenAI'nin 13 yanıt-şeması booleanından farklı düzenlenmiş). 8 dil destekler (v3). Llama Guard 4 (Nisan 2025) doğal olarak çok modludur, 12B.

OpenAI ve Llama Guard taksonomileri örtüşür ama ayrılır. OpenAI'nin "yasadışı" geniş bir kategorisi vardır; Llama Guard'ın "şiddet suçları" ve "şiddet içermeyen suçlar"ı ayrıdır. Dağıtımlar politika-taksonomi uyumlarına göre seçer.

### Perspective API (Google Jigsaw)

LLM-as-moderator dalgasından önce gelen toksisite puanlama sistemi (2020 öncesi). Kategoriler: TOXICITY, SEVERE_TOXICITY, INSULT, PROFANITY, THREAT, IDENTITY_ATTACK. Tek-boyutlu birincil skor (TOXICITY) alt-boyut değişkenleriyle.

API kararlı, belgelenmiş ve yıllarca kalibrasyon verisi olduğu için yaygın olarak içerik-moderasyon araştırma temeli olarak kullanılır. Modern LLM-bitşık kullanım durumları için, Llama Guard veya OpenAI Moderation genellikle daha iyi bir uyumdur.

### Üç-katmanlı örüntü

1. **Giriş moderasyonu.** Üretimden önce kullanıcının promptunu sınıflandırın. Bayraklanırsa reddedin. Gecikme: bir sınıflandırıcı çağrısı.
2. **Çıkış moderasyonu.** Teslimdan önce modelin çıktısını sınıflandırın. Bayraklanırsa bir reddetmeyle değiştirin. Gecikme: üretimden sonra bir sınıflandırıcı çağrısı.
3. **Özel moderasyon.** Alana özgü kurallar (regex, izin-listeleri, iş politikası). Giriş veya çıkışta çalışır.

Üç katman tasarım gereği sıralıdır: giriş moderasyonu üretimden önce tamamlanmalıdır, çıkış moderasyonu üretimden sonra çalışır. Paralellik bir katman içinde geçerlidir — aynı metin üzerinde birden çok sınıflandırıcıyı (örn. OpenAI Moderation + Llama Guard + Perspective) eşzamanlı çalıştırmak, sınıflandırıcı başına gecikmeyi gizler. İsteğe bağlı bir optimizasyon olarak, giriş moderasyonu tamamlanırken bir yer tutucu yanıt ("bir dakika, kontrol ediliyor...") gösterilebilir ve token-1 akışı ertelenir. Bayrak davranışı yapılandırılabilir: reddet, temizle, insan incelemesine ilet.

### Başarısızlık modları

- **Yalnız giriş.** Çıktı halüsinasyonlarını yakalamaz (Ders 12-14 kodlama saldırıları giriş sınıflandırıcılarını atlatır).
- **Yalnız çıktı.** Herhangi bir girdinin modele ulaşmasına izin verir; maliyeti artırır; iç akıl yürütmeyi saldırgana gösterir.
- **Yalnız özel.** Kategoriler arasında sağlam değildir; regex'ler kırılgandır.

Katmanlı varsayılandır. Kemer ve askı.

### Azure kullanımdan kaldırma

Azure Content Moderator: Şubat 2024'te kullanımdan kaldırıldı, Şubat 2027'de emekli. Azure OpenAI ile entegre LLM-tabanlı Azure AI Content Safety ile değiştirildi. Geçiş, Azure dağıtımları için 2024-2027 saha-düzeyi bir projedir.

### Bu, Faz 18'de nereye oturuyor

Ders 16, moderasyon araçlarını kırmızı-ekip bağlamında kapsar. Ders 29, dağıtılmış moderasyonu kapsar. Ders 30, mevcut çift-kullanımlı yetenek kanıtıyla kapanır.

## Uygulama

`code/main.py` üç-katmanlı bir moderasyon koşum takımı inşa eder: giriş moderatörü (anahtar sözcük + kategori skoru), çıkış moderatörü (çıktı üzerinde aynı sınıflandırıcı), özel moderatör (alan kuralları). Girdileri çalıştırabilir ve hangi katmanın ne yakaladığını gözlemleyebilirsiniz.

## Ship It

Bu ders `outputs/skill-moderation-stack.md` üretir. Bir dağıtım verildiğinde, bir moderasyon yığını yapılandırması önerir: girişte hangi sınıflandırıcı, çıkışta hangi sınıflandırıcı, hangi özel kurallar ve uç durumlar için hangi yargıç.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Zararsız, sınırda ve zararlı bir girdiyi üç katman boyunca çalıştırın. Her biri için hangi katmanın tetiklendiğini raporlayın.

2. Koşum takımını belirli bir kategoride Perspective-API-tarzı toksisite puanlamasıyla genişletin. Eşik davranışını kategori skoruyla karşılaştırın.

3. OpenAI Moderation API belgelerini ve Llama Guard 3 kategori listesini okuyun. Her OpenAI kategorisini en yakın Llama Guard kategorilerine eşleyin. Temiz bir şekilde eşlenmeyen üç kategori tanımlayın.

4. Bir kod-asistanı dağıtımı (örn. GitHub Copilot) için bir moderasyon yığını tasarlayın. En çok ve en az ilgili kategorileri tanımlayın ve özel kurallar önerin.

5. Azure Content Moderator Şubat 2027'de emekli. Azure AI Content Safety'ye bir geçiş planlayın. Geçişin en yüksek riskli unsurunu tanımlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| OpenAI Moderation | "omni-moderation-latest" | GPT-4o-tabanlı 13-kategorili (metin) sınıflandırıcı, kısmi çoklu-modal destek |
| Perspective API | "Google Jigsaw toksisite" | LLM-öncesi dönem toksisite puanlama temeli |
| Llama Guard | "MLCommons 14-kategori" | Meta'nın tehlike sınıflandırıcısı (v3: 8B metin, 8 dil; v4: 12B çok modlu) |
| Giriş moderasyonu | "üretim-öncesi filtre" | Model çağrısından önce kullanıcı promptu üzerinde sınıflandırıcı |
| Çıkış moderasyonu | "üretim-sonrası filtre" | Teslimdan önce model çıktısı üzerinde sınıflandırıcı |
| Özel moderasyon | "alan kuralları" | Dağıtıma özgü kurallar (regex, izin-listesi, politika) |
| Katmanlı moderasyon | "üç katmanın tümü" | Standart üretim dağıtımı örüntüsü |

## İleri Okuma

- [OpenAI Moderation API belgeleri](https://platform.openai.com/docs/api-reference/moderations) — omni-moderation uç noktası
- [Meta PurpleLlama + Llama Guard](https://github.com/meta-llama/PurpleLlama) — Llama Guard deposu
- [Google Jigsaw Perspective API](https://perspectiveapi.com/) — toksisite puanlaması
- [Azure AI Content Safety](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/) — Azure değiştirme
