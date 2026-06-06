# AI Scientist v2 — Atölye Düzeyinde Otonom Araştırma

> Sakana'nın AI Scientist v2'si (Yamada ve ark., arXiv:2504.08066) tüm araştırma döngüsünü çalıştırır: hipotez, kod, deneyler, grafikler, yazım, gönderim. Oluşturulan bir makalenin ICLR 2025 atölyesinde (workshop) hakem đánhışından (peer review) geçiren ilk sistemdir. Bağımsız değerlendirme (Beel ve ark.), deneylerin %42'sinin kodlama hatalarından başarısız olduğunu ve literatür taramasının sıkça yerleşik kavramları yeni olarak sınıflandırdığını buldu. Sakana'nın kendi dokümanları, kod tabanının LLM tarafından yazılan kodu çalıştırdığını uyarır ve Docker izolasyonu önerir. Bu görüntünün her iki tarafı da önemlidir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, araştırma döngüsü durum makinesi oyuncak modeli)
**Önkoşullar:** Faz 15 · 03 (AlphaEvolve), Faz 15 · 04 (DGM)
**Süre:** ~60 dakika

## Sorun

Araştırma açık uçlu bir görevdir. AlphaEvolve'in algoritmik araması veya DGM'nin benchmark-sınırıilmiş öz-değişikliğinin aksine, bir araştırma sonucunun makine tarafından doğrulanabilir bir doğruluk kriteri yoktur. Bir makale hakemler tarafından değil, birim testler tarafından değerlendirilir. Bu, döngüyü kapatmayı zorlaştırır — ve kapatılırsa daha değerli hale getirir, çünkü birikimli (compounding) ilerleme araştırma alanındadır.

AI Scientist v1 (Sakana, 2024), insan tarafından yazılmış şablonlardan başlayarak döngüyü kapattı. LLM, sabit bir iskelet içinde deneyleri doldurdu. AI Scientist v2 (Yamada ve ark., 2025), bir görme-dil modeli (vision-language model) eleştiri döngüsüyle ajan ağacı aramasını (agentic tree search) kullanarak şablon gerekliliğini kaldırır. Sistem fikirler üretir, deneyleri uygular, grafikler oluşturur, bir makale yazar ve hakem geri bildirimleriyle yineler.

Hakem đánhışı sonucu: bir v2 tarafından oluşturulan makale ICLR 2025 atölyesinde kabul edildi (açıklamayla). Bağımsız değerlendirme sonucu: sistem güvenilirlikten çok uzaktır. İkisi de doğrudur.

## Kavram

### Mimari

1. **Fikir üretimi.** LLM, bir konu ve önceki literatüre koşullu araştırma fikirleri önerir. v1 şablonlar kullandı; v2 hipotezler üzerinde bir ajan araması kullanır.
2. **Yenilik kontrolü.** Bir literatür getirme (retrieval) adımı, fikrin daha önce yayımlanıp yayımlanmadığını kontrol eder. Beel ve ark.'ın değerlendirmesinin yanlış etiketleme bulduğu adım budur — yerleşik yöntemler sıkça yeni olarak sınıflandırılır.
3. **Deney planı.** Agent bir deney protokolü taslağı çıkarır ve kod yazar.
4. **Çalıştırma.** Kod bir sandbox'ta çalışır. Başarısızlıklar bir yeniden deneme döngüsüne geri beslenir. Beel ve ark.'ın ölçümlerinde deneylerin %42'si bu aşamada kodlama hatalarından başarısız olmuştur.
5. **Grafik üretimi.** Bir görme-dil modeli, oluşturulan grafikleri okur ve netlik için yeniden yazar. Bu, v2'nin teknik eklemesiydi.
6. **Yazım.** LLM bir makale taslağı çıkarır, dahili bir hakemle yineler.
7. **İsteğe bağlı: gönderim.** Makale bir mecraya gönderilir.

### Atölye kabul sonucunun anlamı

Bir v2 tarafından oluşturulan makale ICLR 2025 atölyesinde hakem đánhışından geçti. Yazarlar, makalenin kökenini program komitesine açıkladı. Kabul bir veri noktasıdır; sistemin "araştırma yaptığını" iddia etme lisansı değildir.

Önemli bağlam: atölye makaleleri, ana konferans makalelerinden daha düşük bir barajdır. Hakem değerlendirmesi gürültüldür; belirli bir günde gönderimlerin küçük bir kısmı kabul edilir. Bir başarı, bir kanıt konseptidir (proof of concept), güvenilirlik iddiası değildir. Nature 2026 makalesi uçtan uca döngüyü belgeler ve kendisi insan araştırmacılar tarafından ortak yazılmıştır; "sistemin bir Nature makalesi yazdığı" anlamına gelmez.

### Bağımsız değerlendirme neyi buldu

Beel ve ark. (arXiv:2502.14297) harici bir değerlendirme başlattı. Başlıca bulgular:

- **Deney başarısızlıkları.** Deneylerin %42'si kodlama hatalarından başarısız olmuştur (yanlış import'lar, şekilsel uyumsuzluklar, tanımsız değişkenler). Yeniden deneme döngüsü bazılarını yakaladı, hepsini değil.
- **Yenilik yanlış etiketleme.** Literatür getirme adımı, yerleşik kavramları sıkça yeni olarak işaretledi. Bu, halüsinasyonun (hallucination) araştırma karşılığıdır.
- **Sunum kalitesi boşluğu.** Görme-dil grafik eleştirisi, yayın kalitesinde görseller üretti, temel deney zayıflıklarını maskeliyor.

Son bulgu bu aşama için önemlidir. İkna edici çıkışlar üreten, ancak ikna edici araştırma yapmayan bir sistem, bariz şekilde başarısız olandan daha tehlikeli, daha güvenli değildir. Değerlendirmenin temel iddialara ulaşması, grafikte durmaması gerekir.

### Sandbox kaçışı endişesi

Sakana'nın kendi deposu README'si uyarıyor:

> Bu yazılım, LLM tarafından üretilen kodu çalıştırdığından, güvenliği garanti edemeyiz. Tehlikeli paketler, kontrolsüz web erişimi ve istenmeyen işlemlerin başlatılması riskleri vardır. Kendi sorumluluğunuzda kullanın ve Docker izolasyonunu değerlendirin.

Bu, doğrulanmamış bir alanda otonomluğun operasyonel şeklidir. LLM kod yazar; kod çalışır; kod, sürecin izin verdiği her şeyi yapabilir. Dosya sistemi, ağ ve süreç eylemlerini sert bir şekilde sınırlandıran bir sandbox olmadan, herhangi bir öz-yönlümlü araştırma agentı veri sızdırabilir, hesaplama gücü yakabilir veya kendini yeniden yazabilir.

AlphaEvolve'in sandbox hikayesi daha kolaydır çünkü değerlendiricisi dardır. AI Scientist v2'nin döngüsü açık uçlu kodla açık uçlu hedefler çalıştırır. Bu yüzden daha güçlü izolasyona (minimum Docker; tercihen seccomp / gVisor) ve her gönderimin sistemden ayrılmadan önce elle incelenmesine ihtiyacı vardır.

### v2 sınır yığınında nerede duruyor

| Sistem | Hedef | Çıkış türü | Değerlendirici | Bilinen hata |
|---|---|---|---|---|
| AlphaEvolve | algoritmalar | kod | birim test + benchmark | değerlendirici titizliği ile sınırlı |
| DGM | agent iskeleti | kod | SWE-bench | ödül hilesi |
| AI Scientist v2 | araştırma makaleleri | metin + kod + grafikler | hakem değerlendirmesi (zayıf) | deney başarısızlıkları, yanlış etiketleme, cilanın zayıflığı gizlemesi |

v2'nin üçü arasında en zayıf otomatik değerlendiricisi, en geniş çıkış yüzeyi ve halka açık ürünlere en kısa yolu vardır. Operasyonel kontroller (sandbox, inceleme, açıklama) güvenlik işinin çoğunu yapar.

## Kullan

`code/main.py`, v2 döngüsünü bir durum makinesi (state machine) olarak simüle eder: fikir → yenilik kontrolü → deney → grafik → yazım → inceleme → kabul-et-veya-yinele. Her durum, Beel ve ark. bulgularından çekilebilir bir başarısızlık olasılığına sahiptir. Simülatörü N döngü çalıştırın ve şunları sayın:

- Kaç fikir gönderime ulaşır.
- Kaç gönderim, cilalanmış makalenin gizlediği kritik bir deney kusuru içerir.
- Yeniden deneme bütçeleri kalite ile verim (yield) arasında nasıl takas yapar.

## Üret

`outputs/skill-ai-scientist-sandbox-review.md`, araştırma döngüsü agentı tarafından üretilen her şey için sandbox'tan ayrılmadan önce uygulanacak iki kapılı (two-gate) inceleme kontrol listesidir.

## Alıştırmalar

1. `code/main.py` dosyasını varsayılan parametrelerle çalıştırın. Döngü çalışmalarının kaçta kaçı "temiz" bir makale üretir? Kaçta kaçı, grafik eleştirisi tarafından cilalanmış bir deney başarısızlığı kusuru içerir?

2. Varsayılanlar zaten Beel ve ark.'ın %42 / %25 değerlerini kullanıyor. `--experiment-failure 0,20 --novelty-mislabel 0,10` ile ve ardından `--experiment-failure 0,60 --novelty-mislabel 0,40` ile tekrar çalıştırın. Cilalanmış-ancak-kusurlu oran iki çalışma arasında nasıl değişir?

3. Sakana'nın AI Scientist v2 deposu README'sinde sandbox gereksinimlerini okuyun. Çok günlük bir otonom çalışma için uygulayacağınız Docker dışında iki ek kısıtlamaya ad verin.

4. Beel ve ark.'ın sunum kalitesi boşluğu hakkındaki Bölüm 4'ü okuyun. Cilalanmış görünümlü ancak deneysel olarak kusurlu makaleleri yakalayacak ek bir değerlendirici tasarlayın.

5. "Bir doktora her makaleyi okusun" modelinden daha iyi ölçeklenen, araştırma agentı çıktıları için bir insan inceleme protokolü önerin. Darboğazı (bottleneck) belirleyin ve onu tasarlayın.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| AI Scientist v1 | "Sakana'nın şablonlu araştırma agentı" | Sabit bir iskelete deneyleri doldurdu |
| AI Scientist v2 | "Şablonsuz araştırma agentı" | VLM grafik eleştirisiyle ajan ağacı araması |
| Ajan ağacı araması (Agentic tree search) | "Dallanan araştırma agentı" | Birden fazla deney planını paralel olarak genişletir; dahili eleştirmenle budar |
| Görme-dil eleştirisi (Vision-language critique) | "VLM ile grafik cilası" | Çok modelli (multimodal) model grafikleri okur ve netlik için yeniden yazar |
| Literatür getirme (Literature retrieval) | "Yenilik kontrolü" | Fikrin yeniliğini onaylamak için önceki çalışmaları araştırır — yanlış etiketlendiği belgelenmiştir |
| Cilalama maskelenmesi (Polish masking) | "Güzel makale, bozuk araştırma" | Sunum kalitesi deney kalitesini aşar; zayıflıkları gizler |
| Sandbox kaçışı (Sandbox escape) | "LLM kodu dışarı çıkar" | Agent tarafından çalıştırılan kod, döngü tasarımcısının kasıtlanmadığı şeyleri yapar |

## İleri Okuma

- [Yamada ve ark. (2025). The AI Scientist-v2](https://arxiv.org/abs/2504.08066) — makale.
- [Sakana blogu Nature 2026 yayını hakkında](https://sakana.ai/ai-scientist-nature/) — hakem değerlendirmesi bağlamıyla satıcı özeti.
- [Beel ve ark. (2025). Independent evaluation of The AI Scientist](https://arxiv.org/abs/2502.14297) — harici değerlendirme sayıları.
- [Sakana AI Scientist v1 makalesi](https://arxiv.org/abs/2408.06292) — şablonlu önceki.
- [Anthropic — AI Agent Otonomunu Ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — açık uçlu araştırma agentları için daha geniş çerçeve.
