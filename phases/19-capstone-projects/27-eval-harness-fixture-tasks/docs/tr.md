# Sabit Görevlerle Eval Çerçevesi

> Bir kodlama ajanı, yalnızca onu ölçtüğünüz görevler demeti kadar iyidir. Bu ders, bir sabit görevler (fixture tasks) klasörünü alan, her birini bir aday ajan üzerinden çalıştıran, deterministik bir doğrulayıcı ile geçer ya da kalır olarak puanlayan ve sonuçları pass@1, pass@k, ortalama gecikme ve ortalama maliyet olarak toplayan bir değerlendirme çerçevesi inşa eder. Çerçeve, bir regresyonu bir yeniden yapılandırmadan ayırt etmenizi sağlayan tek doğru kaynaktır.

**Tür:** Uygulama
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 19 · 25 (doğrulama kapıları), Faz 19 · 26 (sandbox çalıştırıcısı), Faz 14 · 30 (eval odaklı ajan geliştirme), Faz 14 · 19 (SWE-bench ve GAIA kıyaslamaları)
**Süre:** ~90 dakika

## Öğrenme Hedefleri

- Bir sabit görevi hedef, kurulum ve doğrulayıcı üçlüsü olarak tanımlamak.
- Görev başına birden çok örnek çalıştırma puanlamak ve pass@1 ile pass@k hesaplamak.
- Gecikmeyi ve maliyeti ortalama ve 95. yüzdelik metriklerine toplamak.
- Deterministik doğrulayıcıları (dosya farkı, çıkış kodu, regex eşleşmesi) yeniden kullanılabilir fonksiyonlara bağlamak.
- Bir regresyon izleme betiğinin alabileceği yapılandırılmış bir JSON raporu yaymak.

## Problem

Eval çerçevesi olmadan inşa edilen ajan kıyaslamalarını üç başarısızlık modu musallat olur.

Birincisi doğrulanmamış geçiştir. Ajan hatayı düzelttiğini söyler, insan farka göz atar, paket yeşil işaretlenir ve üç hafta sonra regresyon testi aynı hatayı yüzeye çıkarır. Ajan aslında hiçbir şeyi düzeltmeden ikna edici biçimde akıl yürütmüştür.

İkincisi saptanamamış regresyondur. İstem şablonundaki bir değişikik ajanı gürültülü görevde %4 daha iyi, sessiz olanda %14 daha kötü yapar. Altın kümesi ve görev başına puan olmadan, regresyon main'e biner ve ancak bir müşteri şikayet ettiğinde yüzeye çıkar.

Üçüncüsü görev başına kaymadır. Eval Pazartesi günü 100 görevle, Cuma günü bunların 95'iyle çalıştırıldı, çünkü birisi beş sabit görevi yeniden adlandırdı. Geçme oranı %5'lik bir iyileşme gibi görünüyor. Değil.

Çerçeve, bu başarısızlıkları gerçeklere dönüştüren programdır. Her sabit görevi, her zaman, tekrarlanabilir bir sırada, doğrulayıcının deterministik bir denetimde true ya da false döndürdüğü bir denetimle çalıştırır.

## Kavram

```mermaid
flowchart LR
  F1[fixtures/task_001/<br/>task.json + expected/] --> Harness
  F2[fixtures/task_002/<br/>...] --> Harness
  Harness[Harness<br/>for each task:<br/>setup / run agent k samples /<br/>verify each sample /<br/>record latency, cost]
  Harness --> Report[EvalReport<br/>pass@1 / pass@k<br/>mean ms / p95 ms<br/>mean cost]
```

#### Açıklama
Bu diyagram değerlendirme çerçevesinin sabit görevlerden rapor üretimine kadar olan akışını gösterir. Her görev için k örnek çalıştırılır, her biri doğrulanır ve sonuçlar toplanır.

Bir `FixtureTask`, küçük bir JSON dosyası artı isteğe bağlı bir `expected/` dizinidir. JSON bir `id`, bir `goal` (ajanı beslenen istem), bir `setup` bloğu (scratch dizinine bırakılacak dosyalar) ve bir `verifier` bloğu bildirir. Doğrulayıcı bloğu, çerçevenin doğrulayıcı kaydındaki bir fonksiyonu adlandırır ve argümanlarını sağlar.

Üç doğrulayıcı biçimi faydalı görevlerin çoğunluğunu kapsar.

Birincisi `file_equals`'dır. Ajan çalıştıktan sonra, adlandırılmış bir dosyayı beklenen içerikle karşılaştırır. "Bu hatayı tam bu şekilde düzelt" görevlerini yakalar.

İkincisi `regex_match`'tir. Adlandırılmış dosyanın içeriği bir regex'e karşı eşleştirilir. "Fonksiyon var olmalı ve X döndürmeli" görevlerini, birçok kabul edilebilir çözüm olduğunda yakalar.

Üçüncüsü `shell_exit_zero`'dur. Çerçeve bir kabuk komutunu çalıştırır (yirmi altıncı dersteki sandbox üzerinden) ve komut sıfırla çıkarsa görevi geçirir. "Testler geçmeli" görevlerini yakalar.

Çerçeve her görevi `k` kez çalıştırır. Pass@k `1 - (1 - p)^k`'dır, burada p ampirik geçme oranıdır; çerçeve ayrıca varyansı görebilmeniz için ham sayıları da raporlar. Gecikme, örnek başına duvar saatidir. Maliyet, ajanın kendi bildirdiği şeydir (token sayısı, USD ya da ikisi); çerçeve örnekler üzerinden toplar ve görev başına ve toplu sayıları sunar.

## Mimari

```mermaid
flowchart TD
  Harness[EvalHarness] -->|load| Task[FixtureTask<br/>goal / setup / verifier]
  Harness --> Loop[her görev için:<br/>setup'tan scratch dizini hazırla<br/>range(k) içindeki örnek için:<br/>adayı çalıştır, scratch_dir -> SampleResult<br/>örneği doğrula, task -> bool<br/>görev başına toplamı kaydet]
  Loop --> TaskReport[TaskReport<br/>task_id / k / passes / pass_rate<br/>mean_latency / mean_cost]
  TaskReport -->|aggregate| EvalReport[EvalReport<br/>total tasks / pass@1 / pass@k / p95 latency]
```

#### Açıklama
Bu mimari diyagram, eval çerçevesinin görevleri yükleme, örnek çalıştırma, doğrulama ve rapor toplama adımlarını gösterir.

Aday, çağrılabilir bir şeydir: `Callable[[FixtureTask, str], SampleResult]`. Çerçeve scratch dizinini `tempfile.mkdtemp()` ile oluşturur ve yolunu düz bir string olarak geçirir. Çerçeve adayın nasıl çalıştığıyla ilgilenmez. Aday deterministik bir yama uygulayıcısı (çerçeve öz testleri için kullanışlı), gerçek bir LLM ajanı, bir fuzzer olabilir. Sözleşme SampleResult'tur.

## Ne İnşa Edeceksiniz

`main.py` şunları sunar:

1. `FixtureTask` veri sınıfı (dataclass).
2. `SampleResult` veri sınıfı (dataclass): success_self_reported, latency_ms, cost_units, edits.
3. `TaskReport`, `EvalReport` veri sınıfları (dataclass) `to_dict()` ile.
4. Doğrulayıcı adını fonksiyona eşleyen `VerifierRegistry`. Yerleşik doğrulayıcılar: file_equals, regex_match, shell_exit_zero.
5. `EvalHarness` sınıfı. Bir adaya karşı bir görev dizini çalıştırır. EvalReport döndürür.
6. `tasks/` içinde paketlenmiş beş sabit görev:
   - `fizzbuzz`'ta off-by-one
   - `factorial`'da eksik dönüş
   - hata mesajında yazım hatası
   - boş fonksiyon gövdesi
   - bağlı liste geçişinde off-by-one
7. Çerçevenin 1.0'lık temiz bir pass@1'i göstermek için kullandığı deterministik bir referans aday (`apply_known_fixes`).
8. Demo, EvalReport JSON'unu yazdırır ve sıfır kodla çıkar.

Sabit görevler, `tasks/` içinde JSON dosyaları ve `tasks/<id>/buggy/` ile `tasks/<id>/expected/` içinde eşleştirilmiş kaynak dosyalar olarak paketlenir. Çerçeve, buggy'yi bir scratch dizinine kopyalar, adaya teslim eder ve expected'a karşı doğrular.

## pass@1 Değil Neden pass@k

Gerçek LLM ajanları stokastiktir. 0.6'lık bir pass@1 başarısızlık gibi görünür. 0.95'lik bir pass@5, ajanın çoğu zaman doğru yanıtı aldığını ama ilk örneklerde yanlış seçtiğini söyler. Çözüm, her zaman daha fazla eğitim değil, örnekleme ve sıralamadır. pass@k bunu görünür kılar.

pass@k, pass@1'in yanı sıra raporlanır çünkü pass@k gerçek bir başarısızlığın üstünü örter: model yirmi denemede bir doğru yanıt alıyorsa, işe yarar bir ajanınız yoktur. Çerçeve ikisini de gösterir.

## Bunun Track A'nın Geri Kalanıyla Nasıl Bileştiği

Yirmi beşinci ders kapı zincirini üretti. Yirmi altıncı ders sandbox'ı üretti. Çerçeve, herhangi bir `shell_exit_zero` doğrulayıcısı için sandbox'ı kullanır. Yirmi sekizinci ders, her çerçeve çalıştırmasını bir OTel izine sarar. Yirmi dokuzuncu ders, uçtan uca demoyu paketlenmiş sabit görevlerden birine karşı çalıştırır ve referans aday için pass@1 = 1.0 olduğunu doğrular.

## Çalıştırma

```bash
cd phases/19-capstone-projects/27-eval-harness-fixture-tasks
python3 code/main.py
python3 -m pytest code/tests/ -v
```

#### Açıklama
Bu komutlar sırasıyla demoyu ve test paketini çalıştırır. Demo, pass@1, pass@5, ortalama gecikme ve görev başına döküm dahil EvalReport'u JSON olarak yazdırır. Çıkış kodu sıfırdır. Testler, doğrulayıcı fonksiyonları, pass@k matematiğini, sabit görev yüklemeyi ve paketlenmiş referans adaya karşı çerçeveyi uçtan uca kapsar.
