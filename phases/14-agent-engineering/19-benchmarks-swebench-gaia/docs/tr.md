# Benchmark'lar: SWE-bench, GAIA, AgentBench

> Üç benchmark 2026'da agent değerlendirmesini çapa alır. SWE-bench kod yamalama testi yapar. GAIA genel amaçlı araç kullanımı testi yapar. AgentBench çoklu ortam akıl yürütmesi testi yapar. Kompozisyonlarını, kontaminasyon hikayelerini ve neyi ölçmediklerini bilin.

**Tür:** Öğren
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 06 (Araç Kullanımı)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- SWE-bench'in test harness'ını (FAIL_TO_PASS) adlandırın ve neden unit test'lerle kapandığını açıklayın.
- Neden SWE-bench Verified'ın (OpenAI, 500 görev) var olduğunu ve neyi kaldırdığını açıklayın.
- GAIA'nın tasarımını tanımlayın: insanlar için basit, AI için zor; üç zorluk seviyesi.
- AgentBench'in sekiz ortamını ve açık kaynak LLM'ler için birincil engelleyicisini adlandırın.
- SWE-bench+ kontaminasyon bulgusunu ve sonuçlarını özetleyin.

## Problem

Liderlik tabloları bir benchmark'ta hangi modelin kazandığını söyler. Şunları söylemez:

- Benchmark'ın kontamine olup olmadığı (çözümler eğitim verisinde, test sızıntısı).
- Benchmark'ın önemli olanı ölçüp ölçmediği (kod vs tarama vs genel amaçlı).
- Değerlendiricinin dayanıklı olup olmadığı (AST eşleme, durum kontrolleri, insan incelemesi).

Bir sayıyı alıntılamadan önce üç çapa benchmark'ı ve hata modlarını bilin.

## Kavram

### SWE-bench (Jimenez ve diğerleri, ICLR 2024 oral)

- 12 popüler Python deposundan 2.294 gerçek GitHub sorunu.
- Agent'a verilen: düzeltme öncesi commit'teki kod tabanı + doğal dil sorun açıklaması.
- Agent'ın ürettiği: bir yama.
- Değerlendirici: yamayı uygula, deponun test paketini çalıştır. Yama FAIL_TO_PASS testlerini (önce başarısız olan, şimdi geçen) çevirmeli ancak PASS_TO_PASS testlerini bozmamalıdır.

SWE-agent (Yang ve diğerleri, 2024) yayınlandığında agent-bilgisayar arayüzlerine (dosya düzenleyici komutları, modelin anladığı arama sözdizimi) vurgu yaparak %12.5'e ulaştı.

### SWE-bench Verified

Openai, Ağustos 2024. İnsan tarafından seçilmiş 500 görevlik alt küme. Belirsiz sorunları, güvenilmez testleri ve düzeltmenin belirsiz olduğu görevleri kaldırır. "Agent'ınız gerçek yamaları mı teslim ediyor?" için birincil benchmark.

### Kontaminasyon

- SWE-bench sorunlarının %94'ü çoğu model kesme tarihinden önce gelir.
- **SWE-bench+** başarılı yamaların %32.67'sinin sorun metninde sızıntı çözümleri buldu (model düzeltmeyi açıklamada gördü) ve %31.08'i zayıf test kapsamı nedeniyle şüpheli bulundu.
- Verified daha temiz ancak kontaminasyonsuz değil.

Pratik sonuç: SWE-bench'te %50 alan bir model SWE-bench+'ta %35 alabilir. SWE-bench performansı iddia ediyorsanız her ikisini de raporlayın.

### GAIA (Mialon ve diğerleri, Kasım 2023)

- 466 soru; 300'u huggingface.co/gaia-benchmark'taki özel liderlik tablosu için korunur.
- Tasarım felsefesi: "insanlar için kavramsal olarak basit (%92) ancak AI için zor (GPT-4 eklentilerle: %15)."
- Akıl yürütme, çoklu-modalite, web, araç kullanımını test eder.
- Üç zorluk seviyesi; Seviye 3 çoklu-modaliteler arası uzun araç zincirleri gerektirir.

GAIA, "genel amaçlı yeteneği" ölçmek için çalıştırılır. Kod-özgü benchmark'larla karıştırmayın.

### AgentBench (Liu ve diğerleri, ICLR 2024)

- Kod (Bash, DB, KG), oyunlar (Alfworld, LTP), web (WebShop, Mind2Web) ve açık uçlu üretim olmak üzere 8 ortam.
- Çoklu tur, bölüm başına ~4k-13k tur.
- Ana bulgu: uzun vadeli akıl yürütme, karar alma ve talimat izleme, ticari modelleri yakalamak için OSS LLM'lerin engelleyicileridir.

### Bunların ölçmedikleri

- Gerçek dünya operasyonel maliyeti (token, duvar saati).
- Düşmanca koşullarda güvenlik davranışı.
- Alanınızdaki performans (kendi eval'larınızı kullanın, Ders 30).
- Kuyruk hataları (benchmark'lar ortalaması; production operatörleri en kötü %1 ile ilgilenir).

### Benchmark nerede yanlış gider

- **Tek sayı saplantısı.** SWE-bench %50, P50/P75/P95 maliyet + adım dağılımından daha az söyler.
- **Kontamine iddialar.** Verified veya SWE-bench+'dan bahsetmeden SWE-bench raporlamak yanıltıcıdır.
- **Benchmark-geliştirme hedefi olarak.** Benchmark'a optimizasyon production kullanışlılığından sapar.

## İnşa Et

`code/main.py` bir oyuncak SWE-bench benzeri harness uygular:

- Sentetik hata düzeltme görevleri (3 görev).
- Yamalar öneren betiklenmiş bir "agent".
- FAIL_TO_PASS (hata şimdi düzeldi) ve PASS_TO_PASS (bir şey bozulmadı) kontrol eden bir test çalıştırıcı.
- Soru çözümleme derinliğine dayalı GAIA tarzı zorluk sınıflandırıcısı.

Çalıştırın:

```bash
python3 code/main.py
```

## Kullan

- **SWE-bench Verified** kod agent'ları için. Her zaman Verified puanlarını raporlayın.
- **GAIA** genel amaçlı agent'lar için. Özel liderlik tablosu bölümünü kullanın.
- **AgentBench** çoklu ortam karşılaştırması için.
- **Özel eval'lar** (Ders 30) ürününüzün gerçek şekli için.

## Teslim Et

`outputs/skill-benchharness.md` FAIL_TO_PASS / PASS_TO_PASS kapamasıyla herhangi bir kod tabanı-görev çifti için SWE-bench tarzı bir harness oluşturur.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| SWE-bench | "Kod agent benchmark'ı" | 2.294 GitHub sorunu; yama FAIL_TO_PASS testlerini çevirmeli |
| SWE-bench Verified | "Temiz SWE-bench" | 500 insan tarafından seçilmiş görev, OpenAI |
| FAIL_TO_PASS | "Düzeltme kapısı" | Düzeltme sonrası geçmesi gereken önceki başarısız testler |
| PASS_TO_PASS | "Geri regression kapısı" | Geçen ve hâlâ geçmesi gereken testler |
| GAIA | "Genel amaçlı benchmark" | 466 insan-kolay / AI-zor çoklu-araç sorusu |
| AgentBench | "Çoklu-ortam benchmark'ı" | 8 ortam; uzun vadeli çoklu tur |
| Contamination | "Eğitim seti sızıntısı" | Model eğitiminde bulunan benchmark görevleri |
| SWE-bench+ | "Kontaminasyon denetimi" | Başarılı SWE-bench yamalarında %32.67 çözüm sızıntısı bulundu |

## İleri Okuma

- [Jimenez ve diğerleri, SWE-bench (arXiv:2310.06770)](https://arxiv.org/abs/2310.06770) — orijinal benchmark
- [OpenAI, SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/) — seçilmiş alt küme
- [Mialon ve diğerleri, GAIA (arXiv:2311.12983)](https://arxiv.org/abs/2311.12983) — genel amaçlı benchmark
- [Liu ve diğerleri, AgentBench (arXiv:2308.03688)](https://arxiv.org/abs/2308.03688) — çoklu ortam paketi
