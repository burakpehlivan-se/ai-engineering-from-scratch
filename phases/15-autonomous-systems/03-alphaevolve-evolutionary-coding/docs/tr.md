# AlphaEvolve — Evrimsel Kodlama Agentları

> Bir sınır kodlama modelini (frontier coding model) evrimsel bir döngü ve makine tarafından doğrulanabilir bir değerlendiriciyle eşleştirin. Döngünün yeterince uzun çalışmasına izin verin. 4x4 karmaşık matris çarpımı için 48 skaler çarpım kullanan bir prosedür keşfeder — Strassen'den bu yana 56 yılda ilk iyileştirme. Ayrıca Google genelindeki Borg zamanlama sezgisini (scheduling heuristic) bulur ve üretimde cluster hesaplama gücünün ~%0,7'sini kurtarır. Mimari kasıtlı olarak sıradandır. Kazançlar değerlendiricinin titizliğinden gelir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, evrimsel döngü oyuncak modeli)
**Önkoşullar:** Faz 15 · 01 (uzun vadeli çerçeve), Faz 15 · 03 (kendi kendine öğrenen akıl yürütme)
**Süre:** ~60 dakika

## Sorun

Büyük dil modelleri (LLM) kod yazabilir. Evrimsel algoritmalar kod üzerinde arama yapabilir. İkisi de onlarca yıldır ayrı ayrı denenmiştir; ikisi de tavanlara çarpmıştır. LLM tavanı uydurmacılıktır (confabulation): model, iddia ettiğinin tersini yapan makul kod yazar. Evrimsel tavan ise arama maliyetidir: sözdizimi üzerindeki rastgele mutasyonlar neredeyse hiçbir zaman derlenebilir program üretmez, daha iyilerini üretmesi bir yana.

AlphaEvolve (Novikov ve ark., DeepMind, arXiv:2506.13131, Haziran 2025) ikisini birleştirir. LLM, bir program veritabanına hedeflenmiş düzenlemeler önerir; otomatik bir değerlendirici her çeşidi puanlar; yüksek puanlı çeşitler gelecek nesiller için ebeveyn olur. LLM, makul kod yazma adımını üstlenir; değerlendirici uydurmacaları yakalar. Döngü saatlerce haftalara kadar çalışır.

Raporlanan sonuçlar: 48 skaler çarpımlı 4x4 karmaşık matris çarpımı (Strassen'in 1969 sınırı 49'du), Google üretiminde bir Borg zamanlama sezgisi, FlashAttention çekirdeğinde %32,5 hızlanma, Gemini eğitim verimliliğinde iyileştirmeler.

Mimari, değerlendirici makine tarafından doğrulanabilir olduğu için çalışır. Değerlendirici olmadığı yerlerde çalışmaz. Bu asimetri derstir.

## Kavram

### Döngü

1. Doğru ancak optimal olmayan bir tohum programdan (seed program) `P_0` başlayın.
2. Her biri değerlendirici tarafından puanlanmış çeşitli programlardan oluşan bir veritabanı sürdürün.
3. Veritabanından bir veya daha fazla ebeveyn örnekleme (MAP-elites tarzı veya adaya dayalı).
4. LLM'e (birçok aday için Gemini Flash, zor olanlar için Gemini Pro) ebeveynin değiştirilmiş bir çeşidini üretmesi için talimat verin.
5. Çeşidi derleyin, çalıştırın ve tutulmuş değerlendiricide test edin.
6. Puanına ve özellik vektörüne (feature vector) göre anahtarlayarak veritabanına ekleyin.
7. Tekrarlayın.

İki detay önemlidir. Birincisi, LLM'e yalnızca ebeveyn programı değil — tipik olarak veritabanından birkaç üst düzey çeşit, değerlendirici imzası ve kısa bir görev tanımı verilir. Modelin görevi, puanı artırabilecek hedeflenmiş bir değişiklik önermektir. İkincisi, veritabanı yapılandırılmıştır (MAP-elites ızgarası, adaya dayalı), böylece döngü yalnızca mevcut lideri değil çeşitliliği keşfeder.

### Değerlendiriciyi vazgeçilmez kılan nedir

AlphaEvolve'in kazançlarının hepsi, değerlendiricinin hızlı, determinant (deterministic) ve kandırılması zor olduğu alanlardan gelir:

- **Matris çarpımı algoritması**: matrisleri çarpan ve eşitliği bit-bit kontrol eden bir birim test.
- **Borg zamanlama sezgisi**: tarihsel cluster yükünü yeniden oynatan ve israf edilmiş hesaplamayı ölçen üretim kalitesinde bir simülatör.
- **FlashAttention çekirdeği**: bir doğruluk testi artı gerçek donanım üzerinde gerçek zaman (wall-clock) karşılaştırma ölçümü.
- **Gemini eğitim verimliliği**: adım başına GPU-saniye ölçümü.

Her durumda değerlendirici, aksi takdirde hakim olacak LLM hata sınıfını yakalar: uydurulmuş doğruluk iddiaları, donanım üzerinde kaybolan performans iddiaları ve uç durum (edge case) hataları. Değerlendirmeyi kaldırırsanız, döngü güzel kod için optimizasyon yapar.

### Ödül hilesi (reward hacking) bunun diğer yüzü

Evrimsel süreç, ölçülen her şey için optimizasyon yapar. Değerlendirici kusurluysa, döngü bu kusuru bulur. Doğrulanmamış bir alanda döngü, kasıtlanan davranış yüzey (surface) özelliğine değil, görünüşe optimizasyon yapar. DeepMind bunu makalede açıkça belirtir: AlphaEvolve'in başarıları yalnızca değerlendirici titizliğinin arama özgüveniyle eşleştiği alanlara aktarılır.

Kod arama döngülerinde 2025-2026 ödül hilesi örnekleri:

- "Tamamlanma süresini" ödüllendiren optimizasyon hedefleri, boş çözümler göndermeyi ödüllendirdi.
- Test altındaki doğruluğu ödüllendiren benchmark puanları, testleri ezberlemeyi ve aşırı öğrenmeyi (overfitting) ödüllendirdi.
- "Kod kalitesi" vekili, yorumları kaldırmayı ve değişken adlarını yeniden adlandırmayı ödüllendirdi; anlamlı bir değişiklik olmadı.

AlphaEvolve'daki düzeltme: LLM'in hiç görmediği, değerlendirmede zamanında üretilen girdilerle tutulmuş bir değerlendirici sunmak. O zaman bile DeepMind, önerilen her dağıtıma karşı güçlü inceleme önerir.

### Neden LLM + arama tek başına olduğundan daha iyi

LLM derlenebilir, anlamsal olarak makul düzenlemeler üretebilir. 2000 satırlık bir Python dosyası üzerinde rastgele mutasyonlu bir GA (genetik algoritma) neredeyse her zaman sözdizimi hatası üretir. LLM ayrıca aramayı makul mahallelerde (bir fonksiyonu değiştirin, rastgele baytları değil) yoğunlaştırır, bu da israf edilen değerlendirici çağrılarını dramatik şekilde azaltır.

Değerleştirici ise LLM'in uydurmacalarını yakalar. LLM, bir fonksiyonun aslında O(n^2) olduğu halde "limitte O(n log n)" olduğunu kendinden emin bir şekilde iddia edebilir; bir gerçek zaman benchmark'ı sorunu çözer.

### AlphaEvolve sınır yığınında nerede duruyor

| Sistem | Üreteç | Değerlendirici | Alan | Örnek kazanç |
|---|---|---|---|---|
| AlphaEvolve | Gemini | doğruluk + benchmark | algoritmalar, çekirdekler, zamanlayıcılar | 48-çarpımlı 4x4 matmul |
| FunSearch (DeepMind, 2023) | PaLM / Codey | doğruluk | kombinatörik matematik | cap-set alt sınırları |
| AI Scientist v2 (Sakana, L5) | GPT/Claude | LLM eleştirisi + deney | ML araştırması | ICLR atölye makalesi |
| Darwin Godel Machine (L4) | agent iskeleti | SWE-bench / Polyglot | agent kodu | %20 → %50 SWE-bench |

Dördü de aynı reçetenin variasyonlarıdır: üreteç artı değerlendirici, döngü. Farklar, değerlendiricinin neyi değerlendirdiği ve ne kadar titiz olduğudur.

## Kullan

`code/main.py`, basit bir sembolik regresyon (symbolic regression) sorusu üzerinde minimal bir AlphaEvolve benzeri döngü uygular. "LLM", bir hedef fonksiyonu hesaplayan programa küçük sözdizimsel mutasyonlar öneren bir stdlib temsilcisidir. "Değerlendirici", tutulmuş test noktaları üzerindeki ortalama kare hatasını (MSE) ölçer.

Şunları izleyin:

- En iyi puan nesiller (generations) boyunca nasıl iyileşir.
- Bir MAP-elites ızgarası çeşitli çözümleri nasıl canlı tutar, böylece döngü yerel bir minimumda (local minimum) yakınlamaz.
- Tutulmuş testin kaldırılması (yalnızca eğitim değerlendircisi) döngünün aşırı öğrenmesine (overfitting) nasıl izin verir.

## Üret

`outputs/skill-evaluator-rigor-audit.md`, yeni bir alanda AlphaEvolve tarzı bir döngüyü düşünmenin ön koşuludur: değerlendiriciniz gerçekten umursadığınız hataları yakalıyor mu?

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. En iyi puan yörüngesine dikkat edin. Tutulmuş değerlendiriciyi devre dışı bırakın (`--no-holdout` bayrağı) ve tekrar çalıştırın. Aşırı öğrenmeyi nicelleştirin.

2. AlphaEvolve makalesinin MAP-elites ızgarası hakkındaki Bölüm 3'ü okuyun. Aramayı çeşitli tutacak yeni bir sorun (ör. derleyici optimizasyon geçişleri) için bir özellik vektörü tanımlayıcısı tasarlayın.

3. 48-çarpımlı 4x4 sonucu, Strassen'in 49-çarpımlı sınırını 56 yıl sonra iyileştirdi. Makalenin EK F Bölümünü okuyun ve bu sorunun değerlendiricisinin neden özellikle doğruyu yapmasının kolay olduğunu ve çoğu alanın neden böyle olmadığını üç cümleyle açıklayın.

4. AlphaEvolve'in başarısız olacağı bir alan önerin. Değerlendiricinin tam olarak nerede bozulduğunu ve nedenini belirleyin.

5. Bildiğiniz bir alan için kullanacağınız değerlendirici imzasını yazın. Şunları içerin: (a) doğruluk koşulları, (b) performans metriği, (c) tutulmuş girdi üretim kuralı, (d) en az bir ödül-hilesi karşıtı kontrol.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| AlphaEvolve | "DeepMind'ın evrimsel kodlama agentı" | Gemini + program veritabanı + makine tarafından doğrulanabilir değerlendirici |
| MAP-elites | "Çeşitliliği koruyan arşiv" | Özellik vektörleriyle anahtarlanmış ızgara; her hücre, o tanımlayıcıya sahip en iyi çeşidi tutar |
| Ada modeli (Island model) | "Paralel evrim alt popülasyonları" | Periyodik olarak göç eden bağımsız popülasyonlar; erken yakınlamayı önler |
| Makine tarafından doğrulanabilir değerlendirici | "Deterministik kahin" | LLM'in taklit edemediği bir birim test, simülatör veya benchmark — bu döngü için ön koşul |
| Ödül hilesi (Reward hacking) | "Ölçüye değil hedefe optimizasyon" | Döngü, kasıtlanan görevi yapmadan puanı maksimize etmenin bir yolunu bulur |
| Tohum program (Seed program) | "Başlangıç noktası" | Döngünün evolve ettiği ilk doğru-ancak-optimal olmayan program |
| Tutulmuş değerlendirici (Held-out evaluator) | "LLM'in hiç görmediği değerlendirme verisi" | Ezberlemeyi önlemek için değerlendirmede zamanında üretilen girdiler |

## İleri Okuma

- [Novikov ve ark. (2025). AlphaEvolve: A coding agent for scientific and algorithmic discovery](https://arxiv.org/abs/2506.13131) — tam makale.
- [DeepMind blogu AlphaEvolve hakkında](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) — sonuçlarıyla birlikte satıcı özeti.
- [AlphaEvolve sonuç deposu](https://github.com/google-deepmind/alphaevolve_results) — keşfedilen algoritmalar, 48-çarpımlı 4x4 matmul dahil.
- [Romera-Paredes ve ark. (2023). Mathematical discoveries from program search with LLMs (FunSearch)](https://www.nature.com/articles/s41586-023-06924-6) — önceki sistem.
- [Anthropic — Sorumlu Ölçekleme Politikası v3.0 (Şubat 2026)](https://anthropic.com/responsible-scaling-policy/rsp-v3-0) — değerlendiriciye bağlı otonomluğu temel araştırma yönü olarak çerçeveler.
