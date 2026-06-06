# Model, Sistem ve Veri Kümesi Kartları

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/26-model-system-dataset-cards/docs/en.md)

> Üç belgelendirme formatı AI şeffaflığını yapılandırır. Model Kartları (Mitchell ve ark. 2019) — modeller için beslenme etiketleri: eğitim verisi, niceliksel ayrıştırılmış analizler, etik hususlar, uyarılar; Hugging Face model kartlarının yalnızca %0.3'ü etik hususları belgeler (Oreamuno ve ark. 2023). Veri Kümeleri için Veri Sayfaları (Gebru ve ark. 2018, CACM) — motivasyon, bileşim, toplama süreci, etiketleme, dağıtım, bakım; elektronik-veri-sayfası analoğu. Veri Kartları (Pushkarna ve ark., Google 2022) — modüler katmanlı ayrıntı (teleskopik, periskopik, mikroskopik) çeşitli okuyucular için sınır nesneleri (boundary objects) olarak. 2024-2025 gelişmeleri: LLM'ler yoluyla otomatik üretim (CardGen, Liu ve ark. 2024); model-kartı ayrıntısı HF'de %29'a kadar indirme artışıyla ilişkilidir (Liang ve ark. 2024); doğrulanabilir tasdikler (Laminator, Duddu ve ark. 2024); karbon/su için sürdürülebilirlik raporlama eklemeleri (Jouneaux ve ark. Temmuz 2025); AB/ISO düzenleyici kartları ortaya çıkıyor. Sistem Kartları (Sidhpurwala 2024; Meta sistem-düzeyi şeffaflık; "Blueprints of Trust" arXiv:2509.20394) — güvenlik yetenekleri, prompt-enjeksiyon koruması, veri-sızdırma tespiti, insan değerleriyle hizalama dahil uçtan uca AI sistemi belgelendirmesi.

**Tür:** Uygulama
**Diller:** Python (stdlib, model-kartı + veri-sayfası + sistem-kartı üreticisi)
**Ön Koşullar:** Faz 18 · 18 (güvenlik çerçeveleri), Faz 18 · 24 (düzenleyici)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Orijinal Mitchell ve ark. 2019 model kartını ve Gebru ve ark. 2018 veri sayfasını açıklayın.
- Veri Kartları'nın teleskopik/periskopik/mikroskopik katmanlamasını açıklayın.
- Sistem Kartları'nı ve onların uçtan uca kapsamını açıklayın.
- Üç 2024-2025 gelişmesini belirtin (otomatik üretim, doğrulanabilir tasdikler, sürdürülebilirlik raporlaması).

## Sorun

Düzenleyici çerçeveler (Ders 24) ve laboratuvar güvenlik politikaları (Ders 18) her ikisi de belgelendirme gerektirir. Belgelendirme formatları, modele özgü (model kartları) veri kümesine özgü (veri sayfaları) ve sisteme özgü (sistem kartları) olacak şekilde gelişti. Her biri farklı bir şeffaflık kapsamını ele alır. 2024-2025 otomasyon ve doğrulanabilir-tasdik çalışması, uzun süredir devam eden benimseme problemini ele alır.

## Kavram

### Model Kartları (Mitchell ve ark. 2019)

Bölümler:
- Model ayrıntıları.
- Kullanım amacı.
- Faktörler (değerlendirme için ilgili demografik veya çevresel faktörler).
- Ölçüler.
- Değerlendirme verisi.
- Eğitim verisi.
- Niceliksel analizler (faktörlere göre ayrıştırılmış).
- Etik hususlar.
- Uyarılar ve öneriler.

Benimseme problemi: Oreamuno ve ark. 2023'ün Hugging Face model kartları denetimi, yalnızca %0.3'ünün etik hususları belgelediğini buldu.

### Veri Kümeleri için Veri Sayfaları (Gebru ve ark. 2018)

Elektronik-veri-sayfası analoğu. Bölümler:
- Motivasyon (veri kümesi neden oluşturuldu).
- Bileşim (içinde ne var).
- Toplama süreci (nasıl bir araya getirildi).
- Etiketleme (geçerliyse).
- Kullanımlar (amaçlanan, yasaklanan, riskler).
- Dağıtım.
- Bakım.

CACM 2021'de yayınlandı. Veri sayfası yukarı yönde belgelendirmedir; model kartı, veri sayfasının doğru olmasına bağlıdır.

### Veri Kartları (Pushkarna ve ark., Google 2022)

Modüler katmanlı ayrıntı. Üç yakınlaştırma düzeyi:
- **Teleskopik (Telescopic).** Uzman olmayanlar için üst düzey özet.
- **Periskopik (Periscopic).** ML uygulayıcıları için orta düzey genel bakış.
- **Mikroskopik (Microscopic).** Denetçiler için ayrıntılı öznitelik düzeyinde belgelendirme.

Sınır-nesne çerçevelemesi: farklı okuyucular aynı belgeden farklı bilgiler çıkarır.

### Sistem Kartları

Kapsam: model + güvenlik yığını + dağıtım bağlamı dahil uçtan uca AI sistemi. Bölümler genellikle şunları içerir:
- Güvenlik yetenekleri.
- Prompt-enjeksiyon koruması.
- Veri-sızdırma tespiti.
- Belirtilen insan değerleriyle hizalama.
- Olay müdahalesi.

Sidhpurwala 2024 ve Meta sistem-düzeyi şeffaflık çalışması. "Blueprints of Trust" (arXiv:2509.20394) Sistem Kartını Model Kartlarının dağıtım-katmanı tamamlayıcısı olarak biçimselleştirir.

### 2024-2025 gelişmeleri

- **CardGen (Liu ve ark. 2024).** LLM'ler yoluyla otomatik model-kartı üretimi; standartlaştırılmış Mitchell 2019 alanlarında birçok insan-yazılı karttan daha yüksek tarafsızlık bildirir.
- **İndirme korelasyonu (Liang ve ark. 2024).** Ayrıntılı model kartları HF'de %29'a kadar daha yüksek indirme oranlarıyla ilişkilidir — benimseme baskısı artık yalnızca uyum-tahrikli değil, pazar-tahrikli.
- **Laminator (Duddu ve ark. 2024).** Donanım TEE / kriptografik imzalar yoluyla doğrulanabilir tasdikler — model kartının yalnızca bir iddia değil, bir kanıt-iddiası taşımasına izin verir.
- **Sürdürülebilirlik (Jouneaux ve ark. Temmuz 2025).** Karbon, su ve hesaplama-enerji ayak izi için eklemeler; ortaya çıkan ISO standartları.
- **Düzenleyici kartlar.** AB AI Yasası (Ders 24) GPAI Uygulama Kuralları Şeffaflık bölümü, uyum yapıtı olarak model kartları gerektirir.

### Bu, Faz 18'de nereye oturuyor

Dersler 24-25 düzenleyici ve CVE katmanlarıdır. Ders 26 belgelendirme katmanıdır. Ders 27, veri sayfasının yukarı yönü olan eğitim-veri yönetişimidir. Ders 28, kartlarda referans verilen değerlendirmeleri üreten araştırma ekosistemidir.

## Uygulama

`code/main.py` oyuncak bir dağıtım için minimal bir model kartı, veri sayfası ve sistem kartı üretir. Her biri kanonik bölüm yapısını takip eder. Formatı inceleyebilir ve üç kapsamı karşılaştırabilirsiniz.

## Ship It

Bu ders `outputs/skill-card-audit.md` üretir. Bir model kartı, veri sayfası veya sistem kartı verildiğinde, bölüm kapsamını, sayısal ayrıştırmayı ve doğrulanabilir tasdiklerin mevcut olup olmadığını denetler.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Üretilen kartları inceleyin. Zayıf olan (yalnızca yer tutucu) bölümleri tanımlayın ve onları güçlendirecek kanıtları belirtin.

2. Model kartını iki demografik grup boyunca niceliksel ayrıştırılmış analizle genişletin (Ders 20).

3. Oreamuno ve ark. 2023'ü %0.3 benimseme oranı üzerine okuyun. Etik-hususlar benimsemesini artıracak model kartı belirtimine yapısal bir değişiklik önerin.

4. Laminator (Duddu ve ark. 2024) doğrulanabilir tasdikler için TEE'leri kullanır. Bir değerlendirme sonucunun kriptografik tasdikini taşıyan bir model-kartı alanı tasarlayın ve doğrulayıcının rolünü açıklayın.

5. Geçmiş projelerinizden biri veya varsayımsal bir dağıtım için bir Sistem Kartı (Model Kartı değil, Sistem Kartı) yazın. Üçüncü taraf denetçiler için en yüksek değer bölümünü tanımlayın.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| Model Kartı | "Mitchell kartı" | Mitchell ve ark. 2019 standart ML modeli belgelendirmesi |
| Veri Sayfası | "Gebru veri sayfası" | Gebru ve ark. 2018 standart veri kümesi belgelendirmesi |
| Veri Kartı | "Pushkarna kartı" | Google 2022 modüler katmanlı veri belgelendirmesi |
| Sistem Kartı | "dağıtım kartı" | Güvenlik yığını dahil uçtan uca AI sistemi belgelendirmesi |
| Sınır nesnesi | "farklı okuyucular, bir belge" | Veri Kartları çerçevelemesi: aynı belge çeşitli kitlelere hizmet eder |
| Doğrulanabilir tasdik | "Laminator tasdiki" | Belgelendirme iddiasına eklenen kriptografik veya TEE kanıtı |
| Sürdürülebilirlik alanı | "karbon / su ayak izi" | Çevresel muhasebe için ortaya çıkan 2025 eki |

## İleri Okuma

- [Mitchell ve ark. — Model Cards for Model Reporting (arXiv:1810.03993, FAT* 2019)](https://arxiv.org/abs/1810.03993) — kanonik model kartı
- [Gebru ve ark. — Datasheets for Datasets (CACM 2021, arXiv:1803.09010)](https://arxiv.org/abs/1803.09010) — veri sayfası makalesi
- [Pushkarna ve ark. — Data Cards (Google 2022)](https://arxiv.org/abs/2204.01075) — katmanlı veri belgelendirmesi
- [Sidhpurwala ve ark. — Blueprints of Trust (arXiv:2509.20394)](https://arxiv.org/abs/2509.20394) — Sistem Kartı biçimselleştirmesi
