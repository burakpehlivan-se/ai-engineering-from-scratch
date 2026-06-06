# Kırmızı Ekip (Red-Team) Araçları — Garak, Llama Guard, PyRIT

> **Orijinal İçerik:** [docs/en.md](https://github.com/rohitg00/ai-engineering-from-scratch/blob/main/phases/18-ethics-safety-alignment/16-red-team-tooling-garak-llamaguard-pyrit/docs/en.md)

> Üç üretim aracı 2026'nın kırmızı ekip yığınını çerçeveler. Llama Guard (Meta) — 14 MLCommons tehlike kategorisi üzerinde ince ayar yapılmış bir Llama-3.1-8B sınıflandırıcı; 2025 Llama Guard 4, Llama 4 Scout'tan budanmış (pruned) 12B parametreli doğal olarak çok modlu (multimodal) bir sınıflandırıcı. Garak (NVIDIA) — halüsinasyon, veri sızıntısı, prompt enjeksiyonu, toksisite ve jailbreak'ler için statik, dinamik ve uyarlanabilir problar (probes) sunan açık kaynaklı bir LLM güvenlik açığı tarayıcısı. PyRIT (Microsoft) — derin istismar için Crescendo, TAP ve özel dönüştürücü (converter) zincirleriyle çok turluk kırmızı ekip kampanyaları. Llama Guard 3, Meta'nın "Llama 3 Herd of Models" (arXiv:2407.21783) çalışmasında belgelenmiştir; Llama Guard 3-1B-INT4 arXiv:2411.17713'te; Garak'ın prob mimarisi github.com/NVIDIA/garak adresinde. Bu araçlar, kırmızı ekip araştırması (Dersler 12-15) ile dağıtım (Ders 17+) arasındaki 2026 üretim arayüzüdür.

**Tür:** Uygulama
**Diller:** Python (stdlib, araç mimarisi simülatörü ve Llama Guard tarzı sınıflandırıcı maketi)
**Ön Koşullar:** Faz 18 · 12-15 (jailbreak'ler ve IPI)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Llama Guard 3/4'ün güvenlik yığınındaki konumunu açıklayın: giriş sınıflandırıcısı, çıkış sınıflandırıcısı veya her ikisi.
- 14 MLCommons tehlike kategorisini sayın ve bariz olmayan birini belirtin (Kod Yorumlayıcı Kötüye Kullanımı — Code Interpreter Abuse).
- Garak'ın prob mimarisini açıklayın: problar (probes), detektörler, koşum takımları (harnesses).
- PyRIT'in çok turluk kampanya yapısını ve Garak problarıyla nasıl birleştiğini açıklayın.

## Sorun

Dersler 12-15 saldırı yüzeyini sunar. Üretim dağıtımları tekrarlanabilir, ölçeklenebilir değerlendirmeye ihtiyaç duyar. 2026'da üç araç baskındır: Llama Guard (savunma sınıflandırıcısı), Garak (tarayıcı), PyRIT (kampanya düzenleyicisi). Her biri kırmızı ekip yaşam döngüsünün farklı bir katmanını hedefler.

## Kavram

### Llama Guard (Meta)

Llama Guard 3, MLCommons AILuminate 14 kategorisi üzerinde giriş/çıkış sınıflandırması için ince ayar yapılmış bir Llama-3.1-8B modelidir:
- Şiddet suçları, şiddet içermeyen suçlar, cinsel içerikle ilgili, CSAM, iftira
- Uzmanlaşmış tavsiyeler, gizlilik, fikri mülkiyet, kapsamsız silahlar, nefret
- İntihar/öz-zarar, cinsel içerik, seçimler, kod yorumlayıcı kötüye kullanımı

8 dili destekler. Kullanım: LLM'den önce (giriş moderasyonu), LLM'den sonra (çıkış moderasyonu) veya her ikisinde. İki kullanım farklı eğitim dağılımları üretir — Llama Guard 3, her ikisini de ele alan tek bir model olarak gelir.

Llama Guard 3-1B-INT4 (arXiv:2411.17713, 440MB, mobil CPU'da ~30 token/s) kuantize edilmiş kenar (edge) varyantıdır.

Llama Guard 4 (Nisan 2025) 12B parametreli, doğal olarak çok modludur, Llama 4 Scout'tan budanmıştır. Hem 8B metin hem de 11B görüntü öncüllerini, metin + görüntü alan tek bir sınıflandırıcıyla değiştirir.

### Garak (NVIDIA)

Açık kaynaklı güvenlik açığı tarayıcısı. Mimari:
- **Problar (Probes).** Halüsinasyon, veri sızıntısı, prompt enjeksiyonu, toksisite, jailbreak'ler için saldırı üreteçleri. Statik (sabit promptlar), dinamik (üretilmiş promptlar), uyarlanabilir (hedef çıktısına yanıt verir).
- **Detektörler (Detectors).** Çıktıları beklenen başarısızlık modlarına göre puanlar — toksik, sızmış, jailbreak'lenmiş.
- **Koşum takımları (Harnesses).** Prob-detektör çiftlerini yönetir, kampanyalar çalıştırır, raporlar üretir.

TrustyAI, Garak'ı Llama-Stack kalkanlarıyla (Prompt-Guard-86M giriş sınıflandırıcısı, Llama-Guard-3-8B çıkış sınıflandırıcısı) uçtan uca kalkanlı hedef değerlendirmesi için bütünleştirir. Katman tabanlı puanlama (TBSA — Tier-Based Scoring) ikili geçer/kalır'ı (binary pass/fail) değiştirir — bir model aynı prob üzerinde şiddet katmanı 3'te geçebilir ve katman 5'te kalabilir.

### PyRIT (Microsoft)

Python Risk Identification Toolkit (Python Risk Tanımlama Araç Seti). Çok turluk kırmızı ekip kampanyaları. Etrafında inşa edilmiştir:
- **Dönüştürücüler (Converters).** Bir tohum promptu dönüştürür — yeniden ifade etme (paraphrase), kodlama, çeviri, rol yapma.
- **Orkestratörler (Orchestrators).** Kampanyayı çalıştırır: Crescendo (tırmandırma), TAP (dallanma), RedTeaming (özel döngü).
- **Puanlama (Scoring).** LLM-as-judge (yargıç olarak LLM) veya sınıflandırıcı-as-judge.

PyRIT, Garak'ın daha ağır kuzenidir. Garak binlerce tek turluk prob çalıştırır; PyRIT belirli başarısızlık modlarını kırmak için tasarlanmış derin çok turluk kampanyalar çalıştırır.

### Yığın

Llama Guard'u modelin her iki tarafına da yerleştirin. Regresyon için Garak'ı her gece çalıştırın. Sürüm öncesi kampanyalar için PyRIT çalıştırın. Bu, çoğu üretim dağıtımı için 2026 varsayılan yapılandırmasıdır.

### Değerlendirme tuzakları

- **Yargıç kimliği.** Üç araç da LLM yargıcı kullanabilir; yargıç kalibrasyonu raporlanan ASR'leri yönlendirir (Ders 12). Aracın yanında yargıcı belirtin.
- **Prob eskimesi.** Modeller bunlara karşı yamalıyken Garak probları eskir. Uyarlanabilir problar (PAIR şeklinde) statik problardan daha yavaş eskir.
- **İçerikte Llama Guard FPR.** Llama Guard'ın erken sürümleri siyasi ve LGBTQ+ içeriği aşırı işaretledi; Llama Guard 3/4 kalibrasyonları iyileştirildi ancak dağıtım başına kalibre edilmedi.

### Bu, Faz 18'de nereye oturuyor

Dersler 12-15 saldırı aileleridir. Ders 16 üretim araçlarıdır. Ders 17 (WMDP) çift kullanımlı (dual-use) yetenek değerlendirmesidir. Ders 18, bu araçları bir politika yapısı içinde saran sınır güvenliği çerçeveleridir.

## Uygulama

`code/main.py` bir oyuncak Llama Guard tarzı sınıflandırıcı (14 kategori üzerinde anahtar sözcük + anlamsal öznitelikler), bir oyuncak Garak koşum takımı (prob-detektör döngüsü) ve PyRIT tarzı çok turluk dönüştürücü zinciri inşa eder. Üç aracı bir maket hedefe karşı çalıştırabilir ve farklı kapsama imzalarını gözlemleyebilirsiniz.

## Ship It

Bu ders `outputs/skill-red-team-stack.md` üretir. Bir dağıtım açıklaması verildiğinde, üç araçtan hangilerinin uygun olduğunu, her birinde ne yapılandırılacağını ve hangi regresyon kafesinin (cadence) çalıştırılacağını adlandırır.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Llama-Guard tarzı sınıflandırıcının tek turluk ve çok turluk saldırılardaki tespit oranını karşılaştırın.

2. Yeni bir Garak probunu uygulayın: base64 kodlanmış zararlı bir istek. Llama-Guard tarzı sınıflandırıcı tarafından tespitini ölçün.

3. PyRIT tarzı dönüştürücü zincirini "Fransızcaya çevir, sonra yeniden ifade et" dönüştürücüsüyle genişletin. Saldırı başarısını yeniden ölçün.

4. Llama Guard 3'ün tehlike kategorileri listesini okuyun. Eğitim verilerinin meşru geliştirici içeriğinde gerçekçi olarak yüksek yanlış pozitif oranları üreteceği iki kategori tanımlayın.

5. Garak ve PyRIT'in tasarım ilkelerini karşılaştırın. Her birinin doğru araç olduğu bir dağıtımı savunun.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|---------------------|---------------|
| Llama Guard | "sınıflandırıcı" | 14 tehlike kategorisiyle ince ayar yapılmış Llama-3.1-8B/4-12B güvenlik sınıflandırıcısı |
| Garak | "tarayıcı" | NVIDIA'nın açık kaynaklı güvenlik açığı tarayıcısı; problar, detektörler, koşum takımları |
| PyRIT | "kampanya aracı" | Microsoft'un çok turluk kırmızı ekip düzenleyicisi; dönüştürücüler, orkestratörler, puanlama |
| Prompt-Guard | "küçük sınıflandırıcı" | Llama Guard ile eşleştirilmiş Meta'nın 86M prompt enjeksiyonu sınıflandırıcısı |
| TBSA | "katman tabanlı puanlama" | İkili sonuçların yerini alan Garak'ın katman tabanlı geçer/kalır'ı |
| Dönüştürücü zinciri | "yeniden ifade et + kodla + ..." | Çok adımlı saldırılar kurmak için PyRIT bileşim ilkeli |
| MLCommons tehlike kategorileri | "14 taksonomi" | Llama Guard'ın hedeflediği endüstri standardi taksonomi |

## İleri Okuma

- [Meta — Llama Guard 3 (Llama 3 Herd makalesinde, arXiv:2407.21783)](https://arxiv.org/abs/2407.21783) — 8B sınıflandırıcı
- [Meta — Llama Guard 3-1B-INT4 (arXiv:2411.17713)](https://arxiv.org/abs/2411.17713) — kuantize edilmiş mobil sınıflandırıcı
- [NVIDIA Garak — GitHub](https://github.com/NVIDIA/garak) — tarayıcı deposu ve belgeler
- [Microsoft PyRIT — GitHub](https://github.com/Azure/PyRIT) — kampanya araç seti
