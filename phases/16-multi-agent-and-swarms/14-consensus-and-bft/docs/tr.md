# Ajanlar (Agent) İçin Konsensüs ve Bizans Hata Toleransı (BFT)

> Klasik dağıtık-sistemler BFT (Byzantine Fault Tolerance) ile stokastik (stochastic) LLM'ler buluşuyor. 2025-2026'da üç araştırma yönü ortaya çıktı: **CP-WBFT** (arXiv:2511.10400) her oyu bir güven sondasıyla (confidence probe) tartar; **DecentLLMs** (arXiv:2507.14928) lidere bağlı kalmadan paralel işçi önerileri ve geometrik medyan birleştirmesiyle çalışır; **WBFT** (arXiv:2505.05103) ağırlıklı oylamayı Hiyerarşik Yapı Kümelemesi (Hierarchical Structure Clustering) ile birleştirip Çekirdek (Core) ve Uç (Edge) düğümleri ayırır. "Can AI Agents Agree?" (arXiv:2603.01213) çalışmasının dürüst deneysel sonucu, skaler (scalar) uzlaşı bile bugün kırılgan: tek bir aldatıcı ajan bir Ajanlar Karışımını (Mixture-of-Agents) ele geçirebilir. BFT gerekli ama yeterli değil. Bu ders minimal bir BFT protokolü kurar, üç ajana özgü saldırı (Bizans yalanı, sycophantic uyum, ilişkili-hata monokültürü) ekler ve her konsensüs varyantının başa çıkma biçimini ölçer.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 07 (Zihin Toplumu ve Tartışma), Faz 16 · 13 (Paylaşımlı Bellek)
**Süre:** ~75 dakika

## Problem

Elinizde her biri bir cevap üreten N LLM ajanı var. Anlaşmazlığa düşüyorlar. Çoğunluk oyu yanlış olanı seçiyor çünkü iki ajan ilişkili (aynı temel model, aynı eğitim verisi, aynı hata kipleri). Üçüncü bir ajan ise yeni bir biçimde hatalı — yani çoğunluk sahte bir çoğunluktur.

Şimdi bir de aldatıcı ajan ekleyin: bilerek yalan söylüyor. Ya da sycophantic (dalkavukluk eden) bir ajan: son konuşan kişiye katılıyor. Klasik BFT'de varsayım, Bizans düğümlerin `f < n/3` oranında olduğu ve keyfi davrandığıdır. 2026 gerçeği ise LLM düğümlerinin dürüst olsalar bile stokastik olduğu, modeller arasında ilişkili olduğu ve birbirlerinin çıktılarından etkilendiğidir. Onları bağımsız Bernoulli oy vericiler olarak ele alamazsınız.

Klasik BFT (PBFT, 1999) yanlış değildir — eksiktir. Keyfi bit çevirmelerini (bit-flipping) ele alır. "Üç dürüst ajan aynı eğitim verisini paylaştığı için aynı halüsinasyonu görüyor" durumunu ele almaz. Bu ders PBFT'nin temelinden yola çıkar ve üç 2025-2026 uyarlaması ekler.

## Kavram

### Klasik BFT'nin sağladıkları

Pratik Bizans Hata Toleransı (Castro & Liskov, OSDI 1999), `f < n/3` Bizans düğümü tolere eder. Protokolün üç aşaması (ön-hazırlık, hazırlık, commit) ve iki temel öğesi (imzalı mesajlar, çoğunluk sertifikaları) vardır. `n >= 3f + 1` dürüst-veya-kötü niyetli düğüm arasında tek bir değer üzerinde uzlaşı sağlar.

Garantiler güçlüdür ancak şunları varsayar:

1. **Bağımsız hatalar.** Bizans düğümler koordinasyon yapmaz.
2. **Dürüst düğümler gerçekten dürüsttür.** Dürüst çıktıların doğruluğu tartışma konusu değildir; protokol yalnızca anlaşmazlığı hizalar.
3. **Sorunun bir temel-doğru cevabı vardır.** Yanlış bir gerçek üzerindeki konsensüs yine konsensüstür.

LLM ajanları bu üçünü de ihlal eder. Aynı temel modeli çalıştıran iki ajan hataları paylaşır. "Dürüst" bir LLM yine de halüsinasyon yapar. Ve belirsiz sorularda "gerçek", ajanların karar verdiği şeydir — dış bir oracle yoktur.

### Üç LLM'ye özgü saldırı

**Bizans yalanı.** Bir ajan bilerek yanlış cevap çıktılar. Klasik BFT, `f < n/3` ise bunu ele alır.

**Sycophantic uygunluk (conformity).** Bir ajan oy vermeden önce diğerlerinin cevaplarını okur ve son konuşan kişiyle aynı hizaya gelir. Kötü niyetli değildir, ama en yüksek sesle konuşanla ilişkilendirilir. Klasik BFT bunu engellemez çünkü ajan her imza kontrolünü geçer.

**İlişkili-hata monokültürü (monoculture).** Üç ajan aynı temel modeli paylaşır. Aynı yanlış cevabı halüsinasyon olarak üretirler. Çoğunluk yanlıştır. Klasik BFT yardımcı olmaz çünkü üçü de "dürüstçe" aynı fikirde.

### 2025-2026 yanıtları

**CP-WBFT** (arXiv:2511.10400) — Güven-Sondalı Ağırlıklı BFT. Her oy veren cevabına bir güven sondası (öz-bildirilen olasılık veya ayrı bir kalibrasyon modelinin tahmini) ekler. Oy ağırlıkları güvene göre ölçeklenir. Tam grafiklerde BFT gelişiminde +%85,71 raporlanmıştır. Şunun için hafifletme: sycophantic uygunluk (uyum sağlayan ajanlar gönüllü pozisyonlarında düşük güvene sahip olma eğilimindedir).

**DecentLLMs** (arXiv:2507.14928) — Lidersiz. İşçi ajanlar paralel olarak öneri sunar, değerlendirici ajanlar önerileri puanlar, son cevap puanlanmış konumların geometrik medyanıdır (geometric median). `f < n/2` olduğunda gürbüzdür (robust). Şunun için hafifletme: Bizans yalanı ve ilişkili hatalar (geometrik medyan aykırı değerlere karşı gürbüzdür ve model yanlılı ortalaması yerine yoğun kümeye doğru çeker).

**WBFT** (arXiv:2505.05103) — Hiyerarşik Yapı Kümelemesi ile Ağırlıklı BFT. Oy ağırlıkları yanıt kalitesi ve geçmişten öğrenilen güven puanıyla atanır. Ajanlar Çekirdek (Core) ve Uç (Edge) olarak kümelenir; Çekirdek ajanlar önce konsensüse ulaşmalı, Uç ajanlar izler. Şunun için hafifletme: ölçeklenebilirlik (Çekirdek konsensüsü küçük ve hızlıdır) ve kısmen monokültür (Çekirdek çeşitlilik için seçilebilir).

### Deneysel: "Can AI Agents Agree?" (arXiv:2603.01213)

Makale, birden fazla ön-sınır model üzerinde skaler uzlaşıyı (LLM ajanlarının tek bir sayısal değer üzerinde anlaşması) ölçer. Bulgu rahatsız edicidir:

- Hiçbir düşman olmadan bile, LLM ajanları birçok kıyaslama (benchmark) üzerinde skaler sorularda %30'un üzerinde oranlarda anlaşmazlığa düşer.
- Aldatıcı bir kişilik benimseyen tek bir ajan, Ajanlar Karışımı (Mixture-of-Agents) konsensüsünü dürüst temel seviyeden 40+ yüzde puanı saptırabilir.
- Anlaşmazlık oranları model çeşitliliğiyle ilişkilidir — heterojen topluluklar homojen olanlardan daha fazla anlaşmaz (iyi: ilişkisiz hatalar) ama aynı zamanda daha yavaş sapar (kötü: daha uzun uzlaşı süresi).

Çıkarım: BFT size çıktıları hizalama mekanizması sağlar, ancak hizalanmış çıktının doğru olup olmadığını söylemez. Doğrulama (Faz 16 · 08 rol uzmanlaşması), çeşitlilik (Faz 16 · 15 tartışma varyantları) ve değerlendirici ajanlarla (Faz 16 · 24 kıyaslamalar) birleştirin.

### Çekirdek protokol, sadeleştirilmiş

LLM ajanları için minimal bir BFT turu:

```
1. görev gelir; her ajan i cevap a_i üretir
2. her ajan cevabına güven sondası c_i ∈ [0, 1] ekler
3. toplayıcı tüm n ajandan (a_i, c_i) toplar
4. toplayıcı anlamsal kümeye göre gruplar (eşdeğer cevaplar)
5. toplayıcı her küme C için ağırlık hesaplar:
 w(C) = sum_{i in C} c_i
6. kazanan = max ağırlıklı küme, eğer max > eşik * sum(c_i)
 aksi halde: yeniden dene veya yükselt
7. azınlık kümeleri, sonradan denetim için kaynağıyla birlikte kaydedilir
```

#### Açıklama
Anlamsal kümeleme adımı LLM'ye özgü büküm noktasıdır. "Çalışma %4,2 bildiriyor" ve "%4,2 iyileşme" cevapları aynı kümededir. Saf bir dize-eşitlik (string-equality) kontrolü bunu kaçırırdı. Üretimde ucuz bir gömme (embedding) modeli veya açık kanonizasyon kullanın.

### Eşik ayarı

`threshold` parametresi ne zaman kabul edileceğine ve ne zaman yeniden deneneceğine karar verir. Çok düşük: zayıf çoğunlukları kabul edersiniz. Çok yüksek: hiçbir şeyi kabul etmezsiniz. Ampirik aralık: `n=5-7` ajan için 0,5-0,67, daha küçük `n` için daha yüksek. Eşiğin altında, bir insana veya farklı bir ajan topluluğuna yükseltme (escalate) yapın.

### Konsensüsün yardımcı olmadığı yerler

- **Belirsiz sorular.** Sorunun temel bir gerçeği yoksa, konsensüs bir görüştür. Öyle adlandırın.
- **Bileşik sorular.** "Kod yaz ve açıkla" — iki cevap. Her birine bağımsız olarak oy verin.
- **Düşmanca çok turlu.** Ajanlar önceki turları gözlemleyip taklit edebiliyorsa (Du 2023 tartışması), gerçek ne olursa olsun birbirleriyle aynı fikirde olmaya başlarlar. Turları sınırlayın (tipik olarak 2-3).

## İnşa Et

`code/main.py` şunları uygular:

- `AgentVoter` — (cevap, güven) çiftine sahip komut dosyası (scripted) politikası.
- `MajorityVote` — klasik çoğunluk (plurality).
- `CPWBFT` — anlamsal kümelemeyle güven-ağırlıklı oylama.
- `DecentLLMs` — puanlanmış öneriler üzerinde geometrik medyan birleştirmesi.
- `Scenario` — her toplayıcıyı üç saldırı örüntüsü altında çalıştırır.

Uygulanan saldırı örüntüleri:

1. `byzantine`: bir ajan yüksek güvenle yalan söyler.
2. `sycophancy`: bir ajan gördüğü ilk cevabı, eşleşen güvenle kopyalar.
3. `monoculture`: üç ajan orta güvenle aynı yanlış cevabı paylaşır (ilişkili hata).

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: (saldırı, toplayıcı) -> nihai cevap tablosu, doğru cevap vurgulanmış. Çoğunluk (plurality) monokültür durumunda başarısız olur. CPWBFT'nin güven ağırlıklandırması sycophancy'yi hafifletir. DecentLLMs'in geometrik medyanı, monokültür nüfusun yarısından az olduğunda dürüst kümeye doğru çeker.

## Kullan

`outputs/skill-consensus-designer.md` bir multi-agent (çoklu ajan) topluluğu için konsensüs protokolü tasarlar: kümeleme yöntemi, ağırlıklandırma, eşik ve eşik-altı turlar için yükseltme politikası.

## Yayınla

Herhangi bir konsensüs mekanizmasını yayınlamadan önce:

- **Yukarıdaki üç örüntüyle saldırı testi yapın.** Protokolünüz sessizce değil, öngörülebilir biçimde başarısız olmalı.
- **Her azınlık kümesini kaynağıyla birlikte kaydedin.** Azınlık kümeleri, ilişkili hatalar için erken uyarı sisteminizdir.
- **Sınırlı turlar uygulayın.** "Anlaşmaya varana kadar tartışmaya devam et" yok — bu sycophancy'yi ödüllendirir.
- **Anlaşmayı doğruluktan ayırın.** Konsensüs çıktısı bir doğrulayıcıya (verifier) gider; doğrulayıcı topluluktan bağımsızdır.
- **Anlaşma oranını izleyin.** Keskin bir yükseliş uyum yanlılığı (conformity bias) anlamına gelir; keskin bir düşüş model kayması (model drift) anlamına gelir.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Çoğunluğun monokültür saldırısında başarısız olduğunu, ancak monokültür güveni 0,7'nin altında olduğunda CPWBFT'nin bunu kısmen hafiflettiğini doğrulayın.
2. Dördüncü bir saldırı örüntüsü ekleyin: **sessiz çekimserlik (silent abstention)** — bir ajan cevap vermeyi reddeder ("Bilmiyorum"). Her toplayıcı çekimserlikleri nasıl ele almalıdır? Seçiminizi uygulayın.
3. Anlamsal kümelemeyi dize kanonizasyonundan gömme benzerliğine (embedding similarity) değiştirin (herhangi bir açık kaynak gömme modeli kullanın). Sycophancy saldırısına ne olur?
4. CP-WBFT'yi (arXiv:2511.10400) okuyun. Güven-sondası kalibrasyon adımını uygulayın (ayrı bir kalibrasyon modeli her ajanın öz-bildirilen güvenini kontrol eder). Monokültür senaryosundaki doğruluk kazanımını ölçün.
5. "Can AI Agents Agree?" (arXiv:2603.01213) çalışmasını okuyun. Basitleştirilmiş bir skaler-uzlaşı deneyini yeniden üretin: üç ajan, bir skaler soru, aldatıcı-kişilik (deceptive persona) istemi. CPWBFT veya DecentLLMs bunu yakalıyor mu?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| BFT | "Bizans hata toleransı" | Castro-Liskov 1999 protokolü, `f < n/3` keyfi hata ile konsensüs. |
| Bizans | "Herhangi bir kötü davranış" | Yalan söyleyebilen, mesaj düşürebilen, sessizce başarısız olabilen bir düğüm — güvenli çökmeyi (crash) saymazsak her şeyi yapabilir. |
| Güven sondası | "Ne kadar eminsin?" | Öz-bildirilen veya kalibratör-tahminli, oya eklenen olasılık. |
| Anlamsal kümeleme | "Aynı cevap, farklı kelimeler" | Oyları saymadan önce eşdeğer cevapları gruplama. |
| Geometrik medyan | "Gürbüz merkez" | Örnek noktalarına uzaklıkların toplamını en aza indiren nokta. Ortalama (mean) gibi aykırı değerlere duyarlı değildir. |
| Monokültür | "Aynı model, aynı hatalar" | Ajanlar eğitim verisini veya temel modeli paylaştığında oluşan ilişkili hatalar. |
| Sycophantic uygunluk | "En yüksek sesle aynı fikirde olmak" | Ajanın oyu ilk/ en yüksek sesle konuşana doğru kayar. |
| Core/Edge | "Hiyerarşik BFT" | WBFT ayrımı: önce küçük Çekirdek (Core) konsensüsü, Uç (Edge) düğümleri izler. Gecikmeyi sınırlar. |

## İleri Okuma

- [Castro & Liskov — Practical Byzantine Fault Tolerance (OSDI 1999)](https://pmg.csail.mit.edu/papers/osdi99.pdf) — temel
- [CP-WBFT — Confidence-Probed Weighted BFT](https://arxiv.org/abs/2511.10400) — güvene göre oy ağırlıklandırma
- [DecentLLMs — leaderless multi-agent consensus](https://arxiv.org/abs/2507.14928) — geometrik medyan birleştirmesi
- [WBFT — Weighted BFT with Hierarchical Structure Clustering](https://arxiv.org/abs/2505.05103) — sınırlı gecikme için Core/Edge ayrımı
- [Can AI Agents Agree?](https://arxiv.org/abs/2603.01213) — skaler-uzlaşı kırılganlığı ve aldatıcı-kişilik saldırısı
