# Oylama, Öz-Tutarlılık ve Tartışma Topolojisi

> En ucuz toplama: N bağımsız ajan örnekleyin, çoğunluk oyu verin. Wang ve diğerleri 2022'deki öz-tutarlılık (self-consistency) bunu tek bir modelden N kez örnekleyerek yaptı. Multi-agent bunu monokültürden kurtulmak için **heterojen** ajanlarla genişletir — farklı modeller, farklı istemler (prompts), farklı sıcaklıklar (temperatures), farklı bağlamlar. Çoğunluk oyununun ötesinde, tartışma topolojisi önemlidir: MultiAgentBench (arXiv:2503.01935, ACL 2025) yıldız (star) / zincir (chain) / ağaç (tree) / grafik (graph) koordinasyonunu değerlendirdi ve **araştırma için grafik en iyi**, ~4 ajan sonrasında bir "koordinasyon vergisi" buldu. AgentVerse (ICLR 2024) iki emergent (ortaya çıkan) örüntüyü belgeler — gönüllü (volunteer) davranışlar ve uyum (conformity) davranışları — ve uyum hem bir özellik (konsensüs bulma) hem de bir risktir (groupthink, Ders 24). Bu ders topoloji uzayını haritalar, her varyantı inşa eder ve koordinasyon vergisini ölçer.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 07 (Zihin Toplumu ve Tartışma), Faz 16 · 14 (Konsensüs ve BFT)
**Süre:** ~75 dakika

## Problem

Tartışma doğruluğu artırabilir (Du ve diğerleri, arXiv:2305.14325). Aynı zamanda azaltabilir. Tartışmanın yardımcı olup olmadığı dört yapısal seçime bağlıdır:

1. Kim kiminle konuşuyor (topoloji).
2. Kaç tur (Du 2023: hem turlar hem ajanlar bağımsız olarak önemlidir).
3. Ajanlar heterojen mi (farklı temel modeller monokültürü kırar).
4. Düşmanca bir ses var mı (steel-manning, yani karşıt görüşü en güçlü haliyle savunma vs. straw-manning, yani karşıt görüşü zayıf haliyle çarpıtma).

Bir göreve "5 ajan çalıştır ve oyla" diye ekleme yapan takımlar çoğu zaman tek bir ajana göre geriler. Başarısızlıklar rastgele değildir. Topolojiyi ve heterojenliği izler. Bu ders topoloji haritasıdır.

## Kavram

### Öz-tutarlılık, tek-model temel çizgisi

Wang ve diğerleri 2022 ("Self-Consistency Improves Chain of Thought Reasoning") aynı modelden sıcaklık > 0'da N kez örnekleyerek ve muhakeme yolu cevaplarına çoğunluk oyu vererek çalıştı. GSM8K üzerindeki sonuç: tek bir açgözlü (greedy) çözümlemeye göre N=40 örneklemle önemli kazanımlar. Öz-tutarlılık, multi-agent oylamasının tek-ajan öncüsüdür.

Sınır: öz-tutarlılık tek bir temel model kullanır. Hatalar yapısal olarak ilişkilidir. Modelin sistematik bir yanlılığı varsa, N örneklem de onu paylaşır.

### Multi-agent oy, heterojen uzantı

N örneklemin yerine N *farklı* ajan koyun. Farklı temel modeller (Claude, GPT, Llama), farklı istemler, farklı araç erişimi. Fayda: ilişkisiz hatalar. Maliyet: farklı ajanlar farklı maliyetlidir; koordinasyonları ek yük getirir.

Heterojen tartışmanın 2026'da kanonik adı **A-HMAD**'dır — Adversarial Heterogeneous Multi-Agent Debate. Evrensel olarak benimsenmemiştir, ancak makaleler "farklı modeller tartışıyor, bu da monokültür çöküşünden kaynaklanan ilişkili hataları azaltıyor" anlamında terimi kullanır.

### Dört topoloji

```
yıldız (star) zincir (chain) ağaç (tree) grafik (graph)

 ┌─A─┐ A─B─C─D ┌──A──┐ A───B
 │ │ │ │ │ × │
 B C B C D───C
 │ │ / \ / \
 D E D E F G (tam bağlı)
```

#### Açıklama
Yıldız: tek bir merkez (hub), diğerlerinin tümü yalnızca merkezle konuşur. Geri kanalı olmayan supervisor-worker'a (denetmen-işçi) eşdeğerdir. Zincir: doğrusal, her ajan bir öncekinin çıktısını görür. Boru hattı (pipeline) benzeri. Ağaç: hiyerarşik, hiyerarşik ajan sistemleri tarafından kullanılır (Ders 06). Grafik: herhangi bir düğümden herhangi birine. Tam bağlı klik (clique) ve keyfi yönlendirilmiş çevrimsiz grafikleri (DAG) içerir.

### Koordinasyon vergisi (MultiAgentBench)

MultiAgentBench (MARBLE, ACL 2025, arXiv:2503.01935) araştırma, kodlama ve planlama görevlerinden oluşan bir paket üzerinde yıldız, zincir, ağaç ve grafiği kıyasladı. Ölçülen temel sonuçlar:

- **Grafik** topolojisi araştırma görevlerinde kazanır. Bilgi akışı herhangi bir düğümden herhangi birine olur; ajanlar birbirlerini eleştirebilir.
- **Yıldız** hızlı-cevap olgusal görevlerinde kazanır. Merkez süzüp yoğunlaştırır.
- **Zincir** adım-adım boru hatlarında kazanır (aşamalı iyileştirme).
- **Koordinasyon vergisi** grafik topolojisinde ~4 ajan sonrasında ortaya çıkar. Duvar saati ve token maliyeti kaliteden daha hızlı büyür.

4-ajan tavanı temel değil ampiriktir. 2026 LLM bağlam kapasitesini yansıtır: her ajanın bağlamı akran çıktılarıyla dolar ve herkes herkesi görebildiğinde ajan N+1 eklemenin marjinal değeri düşer.

### Çok-Ajanlı Tartışma Stratejileri ("MAD olmalı mıyız?")

arXiv:2311.17371, 2023 tarihli MAD stratejileri taramasıdır. Başkaları tarafından tekrarlanan temel bulgu: öz-tutarlılığa *yapısal olarak benzeyen* MAD varyantları (bağımsız örnekleme + toplama), aynı bütçeyle kullanıldığında çoğu zaman öz-tutarlılığın gerisinde kalır. MAD, ajanlar gerçekten heterojen olduğunda ve tartışmada düşmanca bir yapı olduğunda (bir ajan aleyhte argüman üretir) en çok yardımcı olur.

### AgentVerse ortaya çıkan örüntüler

AgentVerse (ICLR 2024, https://proceedings.iclr.cc/paper_files/paper/2024/file/578e65cdee35d00c708d4c64bce32971-Paper-Conference.pdf) açık tasarım olmadan bile çok-ajanlı tartışmadan ortaya çıkan iki davranışı belgeler:

- **Gönüllü (Volunteer).** Bir ajan istemeden yardım önerir ("Sonraki adımı ben alabilirim"). Yararlıdır: işi o alt görev için en yetenekli ajana atar.
- **Uyum (Conformity).** Bir ajan, eleştirmen yanlış olsa bile tavrını eleştirmene uyacak şekilde ayarlar. Bu, tartışmanın sycophancy eşdeğeridir (Ders 14).

Uyum, tartışma-anlaşmaya-kadar yapısının zorbaları ödüllendirmesinin nedenidir. Sınırlı turlar ve ayrı bir yargıç bunu hafifletir.

### Heterojenlik: doğruluğu gerçekten hareket ettiren düğme

2024-2026 pratik literatüründeki bir örüntü: N ajanınızdan birini farklı bir temel modelle değiştirmek, N'i 1 artırmaktan daha büyük bir doğruluk artışı sağlar. Sezgi monokültürdür — her yeni bağımsız-hata kaynağı, ek bir ilişkili örneklemden daha değerlidir.

Sınırda, heterojenlik sayıyı yener. Üç farklı model, çoğu temel gerçeği temiz olan görevde aynı modelin beş kopyasını yener.

### Jüri yöntemleri

Sibyl çerçevesi (Minsky-LLM literatüründe anılır) bir "jüri"yi resmileştirir — her aşamada oylama yaparak cevapları iyileştiren küçük bir uzman ajan kümesi. Düz çoğunluk oyununun aksine, bir jüri rollere sahiptir: bir ajan çapraz-sorgulama yapar, biri bağlam sağlar, biri inandırıcılığı puanlar. Jüri yöntemleri düz oylama (ucuz, monokültüre eğilimli) ve tam MAD (pahalı, uyuma eğilimli) arasında bir orta noktadır.

### Tartışmalı oylamanın üstün geldiği durumlar

- Sorunun temel bir gerçeği var (olgusal, matematik, kod davranışı). Oy yakınsaması anlamlıdır.
- Ajanlar farklı kaynaklara veya araçlara erişebilir (heterojenlik mevcut).
- Turlar sınırlıdır (tipik 2-3) ve ayrı bir yargıç veya doğrulayıcı vardır.
- Bütçe 3-5 ajana izin verir. Grafik topolojisinde 5-7'nin ötesinde koordinasyon vergisi baskın olur.

### Tartışmalı oylamanın zarar verdiği durumlar

- Soru görüş-biçimlidir. Ajanlar en doğru olana değil, en güvenli görünene yakınsar.
- Tüm ajanlar aynı temel modeli paylaşır. Monokültür konsensüsü anlamsız kılar.
- Turlar sınırsızdır. Uyum her seferinde kazanır.
- Görev basittir. N=5 öz-tutarlılığı olan tek bir ajan daha ucuz ve aynı derecede doğrudur.

## İnşa Et

`code/main.py` şunları uygular:

- `run_star(agents, hub, question)` — merkez her işçiyi yoklar, toplar.
- `run_chain(agents, question)` — sıralı iyileştirme.
- `run_tree(root, children, question)` — derinlik-2 toplamalı hiyerarşik.
- `run_graph(agents, question, rounds)` — tümünden tümüne tartışma, sınırlı turlar.
- Komut dosyası (scripted) bir heterojenlik kadranı: her ajanın sistematik yanlışlığını gösteren bir `error_bias` değeri vardır.
- Her topolojiyi N=3, 5, 7'de çalıştıran ve (doğruluk, toplam_token, simüle_edilmiş_duvar_saati) raporlayan bir ölçüm donanımı.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: topoloji × N → (doğruluk, token, gecikme) tablosu. Grafik, araştırma tarzı görevlerde N=3-5'te kazanır; yıldız hızlı-olgusal görevlerde kazanır; grafik N=7'de koordinasyon vergisini gösterir (gecikme doğruluktan daha hızlı şişer).

## Kullan

`outputs/skill-topology-picker.md`, bir görev açıklamasını okuyan ve bir topoloji (yıldız / zincir / ağaç / grafik), bir N (ajan sayısı), bir heterojenlik profili (kullanılacak temel modeller) ve bir tur sınırı öneren bir beceridir (skill).

## Yayınla

Herhangi bir topluluk için:

- **Tek güçlü temel modelle N=5 öz-tutarlılıkla başlayın.** Ucuz temel çizgidir.
- **Doğruluk önemliyse N=3 heterojen oylamaya yükseltin.** Farkı ölçün.
- **Yalnızca görevin yapısı varsa (araştırma, çok adımlı) ve sınırlı turlar uygulanabilirse tartışma topolojisine yükseltin.**
- **Azınlık kümesini her zaman kaydedin.** Bir azınlık ısrarla doğru çıkıyorsa, çeşitlilik sinyali yakalamışsınızdır.
- **Duvar saati ve token'ları doğrulukla birlikte kıyaslayın.** "10x maliyetle daha iyi doğruluk" bir iş kararıdır.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Grafik topolojisi için koordinasyon-vergisi eğrisini çizin: doğruluk vs N, token vs N. Eğri hangi N'de kırılır?
2. A-HMAD uygulayın: bilerek farklı yanlılıklara sahip üç ajan. Ders 14'ten monokültür saldırısı üzerinde tümü-aynı-yanlılık temel çizgisi A-HMAD ile nasıl karşılaştırılır?
3. Grafik topolojisine oy vermeyen, yalnızca nihai konsensüsü puanlayan bir "yargıç" rolü ekleyin. Bu, ortaya çıkan uyum davranışını değiştiriyor mu?
4. AgentVerse makalesini (ICLR 2024) okuyun. Uygulamanızın en güçlü şekilde sergilediği emergent davranışı belirleyin. Bir istem (prompt) değişikliğiyle ters davranışı ortaya çıkarabilir misiniz?
5. MultiAgentBench (arXiv:2503.01935) Bölüm 4'ü (topoloji deneyleri) okuyun. "Grafik-araştırmayı-kazanır" sonucunu kendi donanımınızla makaleden bir görev üzerinde yeniden üretin.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Öz-tutarlılık | "N kez örnekle, oyla" | Wang 2022. Tek model, N sıcaklık>0 örneklem, muhakeme yollarına çoğunluk oyu. |
| Heterojenlik | "Farklı modeller" | Farklı temel modeller veya istem ailelerinden oluşan topluluk. Monokültürü kırar. |
| MAD | "Çok-ajanlı tartışma" | Ajanların turlar boyunca eleştirilerini değiştiği genel terim. Bkz. Du 2023. |
| A-HMAD | "Adversarial Heterojen MAD" | Farklı modelleri ve düşmanca yapıyı vurgulayan MAD varyantı. |
| Topoloji | "Kim kiminle konuşur" | Yıldız, zincir, ağaç, grafik. Bilgi akışını belirler. |
| Koordinasyon vergisi | "Azalan getiri" | Grafik üzerinde ~4 ajanın üzerinde maliyet kaliteden daha hızlı büyür. |
| Gönüllü davranış | "İstemsiz yardım" | AgentVerse emergent örüntüsü: bir ajan bir adım almayı önerir. |
| Uyum davranışı | "Baskı altında anlaşma" | AgentVerse emergent örüntüsü: bir ajan bir eleştirmenle aynı hizaya gelir. |
| Jüri | "Küçük uzman paneli" | Sibyl tarzı rollere sahip topluluk (sorgulayıcı, bağlam, puanlayıcı). |

## İleri Okuma

- [Wang et al. — Self-Consistency Improves Chain of Thought Reasoning](https://arxiv.org/abs/2203.11171) — tek-model temel çizgisi
- [Du et al. — Improving Factuality and Reasoning via Multiagent Debate](https://arxiv.org/abs/2305.14325) — hem ajanlar hem turlar bağımsız olarak önemlidir
- [MultiAgentBench / MARBLE](https://arxiv.org/abs/2503.01935) — topoloji kıyaslaması; araştırma için grafik, boru hatları için zincir
- [Should we be going MAD?](https://arxiv.org/abs/2311.17371) — MAD-stratejisi taraması; MAD'nin eşit bütçede öz-tutarlılığa sıkça kaybettiğini bulur
- [AgentVerse (ICLR 2024)](https://proceedings.iclr.cc/paper_files/paper/2024/file/578e65cdee35d00c708d4c64bce32971-Paper-Conference.pdf) — gönüllü ve uyum emergent örüntüleri
- [MARBLE repo](https://github.com/ulab-uiuc/MARBLE) — referans kıyaslama uygulaması
