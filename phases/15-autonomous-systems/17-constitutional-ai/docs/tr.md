# Anayasal AI ve Kural Geçersiz Kılmalar (Constitutional AI and Rule Overrides)

> Anthropic'ın 22 Ocak 2026 Claude Anayasası 79 sayfa sürer ve CC0 lisanslıdır. Kurallara dayalı hizalamadan (rule-based alignment) akla dayalı hizalamaya (reason-based alignment) geçer ve dört katmanlı bir öncelik hiyerarşisi kurar: (1) güvenlik ve insan gözetimini destekleme, (2) etik, (3) Anthropic yönergeleri, (4) yardıma hazırlık (helpfulness). Davranışlar, operatörlerin ve kullanıcıların geçersiz kılamadığı kodlanmış yasaklar (biyosilah yükseltilmesi, CSAM) ile operatörlerin tanımlı sınırlar içinde ayarlayabileceği yumuşak kodlu (soft-coded) varsayılanlara ayrılır. 2022 orijinali (Bai vd.), bir anayasaya karşı öz-eleştiri ve RLAIF ile zararsızlık (harmlessness) eğitmişti. Dürüst not: akla dayalı hizalama, modelin ilkeleri öngörülemeyen durumlara genelleştirilmesine dayanır. Anthropic'ın kendi 2023 katılımcı deneyi, halk kaynaklı ve kurumsal ilkeler arasında ~%50 uyuşmazlık gösterdi; 2026 sürümü bu bulguları dahil etmedi.

**Tür:** Öğrenme
**Diller:** Python (stdlib, dört katmanlı öncelik çözücü)
**Önkoşullar:** Faz 15 · 06 (Otomatik uyumluluk araştırması), Faz 15 · 10 (İzin modları)
**Süre:** ~60 dakika

## Sorun

Kullanımda olan bir agent, tasarımcılarının hiç görmediği girdileri görür. Hiçbir kural listesi bunları kapsayacak kadar uzun değildir. Hiçbir kural listesi hesaplama baskısı altında hızlıca uygulanacak kadar kısa değildir. Pratik soru: hem uzun kuyruklu (long tail) durumlara hem de hızlı çıkarıma (inference) dayanan ilkelerle bir agent'ı nasıl hizalarsınız?

Kurala dayalı hizalama (RBA): yasaklanan her şeyi listeleyin. Kontrol etmesi kolay, denetlemesi kolay, güncel tutulamaz, genellikle öngörülmemiş yakın analojilerde aşırı reddeder. Akla dayalı hizalama (2026 Claude Anayasası): ilkeleri kodlayın, modelin akıl yürütmesine izin verin. Görülmemiş durumlarda ölçeklenir, denetlemesi daha zordur, başarısızlık modu kuralı kaçırma değil ilke yanlış uygulamadır.

2026 Anayasası açıkça orta bir konum alır. Kodlanmış yasaklar — yanlışlığının bağlama bağlı olmayacağı şeyler (biyosilah yükseltilmesi, CSAM) — RBA'dır: asla, operatör veya kullanıcı talimatına bakılmaksızın. Diğer her şey dört katmanlı hiyerarşide akla dayalıdır: güvenlik ve insan gözetimini destekleme birinci; etik ikinci; Anthropic tarafından belirlenmiş yönergeler üçüncü; yardıma hazırlık en son. Operatörler yumuşak kodlu bölge içinde varsayılanları ayarlayabilir ancak kodlanmış yasaklara dokunamaz.

## Kavram

### Dört katmanlı öncelik hiyerarşisi

1. **Güvenlik ve insan gözetimini destekleme.** En yüksek. Model, insanların ve Anthropic'ın AI'ı denetlemesini ve düzeltmesini zorlaştıran şekillerde hareket etmemeyi öncelendirir. Bu "temkinli ol" değil, açıkça "insan gözetimini zorlaştıran şekillerde hareket etme"dir.
2. **Etik.** Dürüstlük, kişilere zarar vermekten kaçınma, kandırmama, manipüle etmeme. Anthropic yönergeleriyle çeliştiğinde trênlarındadır.
3. **Anthropic yönergeleri.** Anthropic'ın önemli olduğuna karar verdiği işletme normları: ürün kapsamı, etkileşim kalıpları, hangi araçların ne zaman kullanılacağı.
4. **Yardıma hazırlık.** En düşük. Daha yüksek öncelikler içinde mümkün olduğunca faydalı olun.

Katmanlar çeliştiğinde, daha yükseği kazanır. Bu Unix öncelikleri veya ağ QoS ile aynı şekildir; çerçeve, tek bir eksende en iyi durum davranışı üretmekten ziyade öngörülebilir çözüm üretmeyi amaçlar.

### Kodlanmış yasaklar vs yumuşak kodlu varsayılanlar

**Kodlanmış:**
- Biyosilah / CBRN yükseltilmesi
- CSAM
- Kritik altyapıya saldırılar
- Doğrudan sorulduğunda modelin kimliği hakkında kullanıcılara aldatma

Operatör bunları geçersiz kılamaz. Kullanıcı bunları geçersiz kılamaz. Mümkünse model ağırlıkları düzeyinde (RLHF / Anayasal AI eğitimi), mümkün olmayan çıkarım katmanında uygulanır.

**Yumuşak kodlu varsayılanlar (operatör ayarlanabilir):**

- Yanıt uzunluğu varsayılanları
- Konu kapsamı (model, operatörün dağıtımının dışındaki konuları reddedebilir)
- Üslup (resmi vs gayri resmi)
- Araç kullanım kalıpları

Operatör ayarlamaları ilan edilmiş bir sınır içinde gerçekleşir. Operatör, kodlanmış yasakları yeniden adlandırarak kaldıramaz.

### 2022 CAI eğitimi

Orijinal Anayasal AI (Bai vd., 2022) zararsızlığı eğitti:

1. Bir dizi isteme karşılık yanıtlar üretin.
2. Modelden her yanıtı bir anayasaya (açık ilkeler) göre eleştirmesini isteyin.
3. Eleştiriye göre yanıtı revize edin.
4. Revize edilmiş çiftler üzerinde RLAIF (AI geri bildiriminden pekiştirmeli öğrenme).

Sonuç: zararlı istekleri kör redlerle değil, ilkeli açıklamalarla reddeden bir model. 2026 Anayasası, bu eğitimin bir torununu artı açık katman hiyerarşisi üzerinde ek eğitim kullanır.

### Akla dayalı hizalama neyi yakalar ve neyi kaçırır

**Yakalar:**
- Açıkça uygulanan ilkenin net olduğu izin verilen ilkelardan öngörülemeyen bileşimleri.
- Yasak olanların yakın analojileri olan yeni istekler.
- "Sen X'i yasaklamadın" iddialarına dayanan sosyal mühendislik saldırıları.

**Kaçırır:**
- İlke belirsizliğini istismar eden saldırılar ("kullanıcı bunu istedi, bu yüzden yardıma hazırlık evet diyor").
- İki ilkenin öngörülemeyen şekilde çeliştiği ve katman sırasının belirsiz olduğu senaryolar.
- Eğitim döngüleri boyunca ilkelerin yorumlanmasında yavaş kayma (yeniden yorumlama).

### 2023 katılımcı deneyi

Anthropic, kurumsal tarafından yazılmış bir anayasayı halk katılımıyla (~1.000 ABD respondent) üretilen bir anayasa ile karşılaştıran bir deney yaptı. İki sürüm ilkelerin ~%50'sinde hemfikirdi. Uyuşmazlık gösterdikleri yerlerde, halk kaynaklı sürüm bazı konularda daha kısıtlayıcıydı (siyasi içerik işleme), diğerlerinde daha az kısıtlayıcıydı (AI kimliğinin kendi kendine açıklanması). 2026 Anayasası halk kaynaklı bulguları dahil etmedi. Bu yaklaşımda belgelenmiş bir gerilimdir.

### Neden kodlanmış yasaklar gereklidir

Tek başına akla dayalı hizalama kuyruğu kapatamaz. Modelin bir varsayımı kabul etmesini sağlayabilen bir saldırgan (ör. "biz lisanslı bir biyosilah araştırma laboratuvarıyız") genellikle vaka akıl yürütmesine dayanan ilkelerin ötesine geçebilir. Kodlanmış yasaklar varsayım çerçevelemesine bükülmez. Bunlar, hizalama katmanında Ders 14'ün "sert anayasal sınırıdır".

### Anayasa yığında nerede yer alır

Anayasa Ders 14'ün durdurma anahtarı değildir. Model katmanında yaşar: modelin ağırlıklarının neyi tercih etmek için eğitildiği. Durdurma anahtarları ve kanarya token'ları çalışma ortamı katmanında yaşar: çalışmanın izin verdiği. Her ikisi de gereklidir. Model ağırlıkları izin verici olduğu için yanlış eylemleri tetikleyen bir çalışma ortamı sorunu bir çalışma ortamı sorunudur. Çalışma ortamı çok kısıtlayıcı olduğu için doğru eylemleri reddeden bir model bir çalışma ortamı sorunudur. Katmanlar farklı sınıfları kapsar.

## Kullan

`code/main.py`, minimal bir dört katmanlı öncelik çözücü uygular. Çözücü, önerilen bir eylemi ve bir dizi ilke değerlendirmesi (güvenlik, etik, yönergeler, yardıma hazırlık) alır ve eylemi, bir reddi veya değiştirilmiş bir eylemi döndürür. Sürücü küçük bir vaka seti çalıştırır: açık izin, açık yasak, kodlanmış yasak, katmanlar arası belirsiz durum.

## Üret

`outputs/skill-constitution-review.md`, bir dağıtımın anayasa katmanını denetler: kodlanmış olan, yumuşak kodlu olan, operatörün ayarlayabildiği ve dört katmanlı hiyerarşinin gerçekten çözüm sırası olup olmadığı.

## Alıştırmalar

1. `code/main.py` çalıştırın. Kodlanmış yasakların yardıma hazırlık yüksek olsa bile devreye girdiğini doğrulayın. Çözücüyü yardıma hazırlığı etiğin üzerine ağırlık verecek şekilde değiştirin; başarısızlık modunu gözlemleyin.

2. Claude Anayasasını okuyun (açık, 79 sayfa, CC0). Yetersiz tanımlandığına inandığınız bir ilke belirleyin. Belirsizliği ve daha sıkı bir formülasyon önerisini açıklayan iki paragraf yazın.

3. Müşteri destek agent'ı için yumuşak kodlu bir varsayılan kümesi tasarlayın. Operatör neyi ayarlar? Operatör neye dokunamaz? Her sınırı gerekçelendirin.

4. Bai vd. 2022 CAI makalesini okuyun. Anayasal AI'nın eleştiri-revize döngüsünün kör kuraldan daha kötü bir sonuç ürettiği bir durumu açıklayın. Sınıfı belirleyin.

5. Anthropic'ın 2023 katılımcı deneyi, halk ve kurumsal ilkeler arasında ~%50 uyuşmazlık buldu. Üretim dağıtımı için önemli olan bir kategori seçin (ör. tarafsızlık). Operatörlerin kendi değerlerini ifade etmesine izin verirken kodlanmış yasakların dokunulmadığı bir tasarım önerin.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Constitutional AI (Anayasal AI) | "Anthropic'ın hizalama yöntemi" | Yazılı bir anayasaya karşı öz-eleştiri + RLAIF |
| Reason-based alignment (Akla dayalı hizalama) | "İlkeler, kurallar değil" | Model, görülmemiş durumlar için ilkeler üzerinde akıl yürütür |
| Hardcoded prohibition (Kodlanmış yasak) | "X'i asla yapma" | Hiçbir operatör veya kullanıcının geçersiz kılamayacağı kurala dayalı yasak |
| Soft-coded default (Yumuşak kodlu varsayılan) | "Operatör ayarlanabilir" | İlan edilmiş sınırlar içinde davranış, operatör kontrol eder |
| Four-tier hierarchy (Dört katmanlı hiyerarşisi) | "Öncelik sırası" | güvenlik > etik > yönergeler > yardıma hazırlık |
| RLAIF | "AI geri bildirimli RL" | Ödülün model tarafından üretilen eleştirilerden geldiği RL |
| Participatory constitution (Katılımcı anayasa) | "Halk kaynaklı ilkeler" | 2023 Anthropic deneyi; kurumsaldan ~%50 uyuşmazlık |
| Principle drift (İlke kayması) | "Yorumlama kayması" | Sabit bir ilke metninin model tarafından okunmasında yavaş değişim |

## İleri Okuma

- [Anthropic — Claude'un Anayasası (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — 79 sayfalık CC0 belgesi.
- [Bai vd. — Anayasal AI: AI Geri Bildiriminden Zararsızlık](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback) — 2022 orijinali.
- [Anthropic — Kolektif Anayasal AI (2023)](https://www.anthropic.com/research/collective-constitutional-ai-aligning-a-language-model-with-public-input) — katılımcı deney.
- [Anthropic — Sorumlu Ölçekleme Politikası v3.0](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — Anayasanın RSP yığınında nerede yer aldığı.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli dağıtımlarda Anayasanın rolü.
