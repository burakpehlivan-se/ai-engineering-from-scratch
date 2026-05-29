# Çürütülen Yapay Zeka Efsaneleri

Yapay zeka, makine öğrenmesi ve derin öğrenme hakkındaki yaygın yanlış anlaşılmazlar. Her biri gerçek durumla açıklanıyor.

---

## "Yapay zeka dili anlıyor"

**Gerçek:** Büyük dil modelleri (LLM), eğitim verisindeki istatistiksel desenlere dayanarak bir sonraki token'ı tahmin eder. Anlayış, inanç veya dünya modeli yoktur (kanıtlayabildiğimiz kadarıyla). Milyarlarca örnekte desen eşleştirmede çok iyidir. Çıktı, anlaşıyormuş gibi görünür çünkü desenler çoğu durumu kapsayacak kadar zengindir.

**Neden önemli:** LLM'i bir akıl yürütme motoru olarak treatederseniz, yanlış şeyleri güvenle söylediğinde şaşırırsınız. Bir desen eşleştirici olarak treatederseniz, etrafında daha iyi sistemler tasarlayabilirsiniz.

---

## "Daha fazla parametre = daha akıllı model"

**Gerçek:** Kaliteli verilerle iyi tekniklerle eğitilmiş 7B parametreli bir model, çöp verilerle eğitilmiş 70B modeli geçebilir. Chinchilla, çoğu modelin aşırı parametreli ve yetersiz eğitimli olduğunu gösterdi. Eğitim verisinin kalitesi ve miktarı, model boyutu kadar önemlidir. Phi-2 (2.7B), birçok benchmark'ta kendisinden 10 kat büyük modelleri yendi.

**Neden önemli:** Varsayılan olarak en büyük modeli seçmeyin. Model boyutunu görevinize ve bütçenize göre eşleştirin.

---

## "Sinir ağları kara kutulardır"

**Gerçek:** Sinir ağlarının ne öğrendiğini anlamak için araçlarımız var. Dikkat görselleştirmesi, modelin hangi token'lara odaklandığını gösterir. Sondaj sınıflandırıcıları, gizli temsillerde hangi bilginin saklandığını ortaya çıkarır. Mekanistik yorumlanabilirlik, gerçek devreleri buluyor (indüksiyon başları, özellik tespit edicileri). Tam bir şeffaflık değil, ama bir kara kutu da değil.

**Neden önemli:** Sinir ağlarını hata ayıklayabilirsiniz. Gradyan analizi, aktivasyon görselleştirmesi ve dikkat haritaları bu kursta ele alınan gerçek araçlardır.

---

## "Yapay zeka programcıların yerini alacak"

**Gerçek:** Yapay zekâ programlamayı değiştirdi, yerini almadı. Yapay zeka şablon kodu yazar. İnsanlar sistemleri tasarlar, mimari kararlar alır, doğruluğu inceler ve yapay zekânın yanlış yaptığı durumları ele alır. Rol "her satırı yazmaktan" "inceleme, yönlendirme ve mimari oluşturmaya" dönüştü. En iyi mühendisler yapay zekayı bir araç olarak kullanır, ondan korkmaz.

**Neden önemli:** Siz yapay zeka mühendisliği öğreniyorsunuz, bu da programlama + yapay zeka demektir. Her iki beceri birlikte, tek başına herhangi birinden daha değerlidir.

---

## "Yapay zeka yapmak için matematikte doktora gerekir"

**Gerçek:** Lise matematiğine artı bu kursun 1. fazındaki belirli konulara ihtiyacınız var. Doğrusal cebir, calculas, olasılık ve optimizasyona ihtiyacınız var. İspatlara ihtiyacınız yok. İşlemlerin ne yaptığına ve neden önemli olduğuna dair sezgiye ihtiyacınız var. Matrisleri çarpabiliyor ve türev alabiliyorsanız, sinir ağları oluşturabilirsiniz.

**Neden önemli:** 1. faz, tam olarak ihtiyacınız olan matematiği vermek için var, fazlası değil.

---

## "GPT, Genel Amaçlı Teknoloji demektir"

**Gerçek:** GPT, Üreteç Önceden Eğitilmiş Transformer demektir. Üreteç = metin üretir. Önceden eğitilmiş = uyarlanmadan önce büyük bir corpus üzerinde bir kez eğitilmiştir. Transformer, 2017 "Attention Is All You Need" makalesindeki mimaridir.

---

## "Sıcaklık yapay zekayı daha yaratıcı yapar"

**Gerçek:** Sıcaklık, logit'leri softmax öncesi ölçeklendirir. Daha yüksek sıcaklık = daha düz olasılık dağıtımı = daha rastgele token seçimi. Daha düşük sıcaklık = daha keskin dağılım = daha belirleyici. Bu yaratıcılık değil, rastgeleliktir. Yüksek sıcaklıklı model daha zor düşünmez, sadece daha düşük olasılıklı token'ları değerlendirir.

**Neden önemli:** Çıktınız çok tekrarlayıcıysa sıcaklığı artırın. Çok kaotikse düşürün. Bu bir rastgelelik düğmesi, fazlası değil.

---

## "İnce ayar, modele yeni bilgi öğretir"

**Gerçek:** İnce ayar, mevcut bilgiyi nasıl kullandığını ayarlar, ne bildiğini değil. Bilgi önceden eğitim verisinde yoksa, ince ayar onu güvenilir bir şekilde ekleyemez. İnce ayar, yeni olgular eklemekten ziyade davranışı (stil, biçim, ton, goreve özgü desenler) değiştirmek için daha uygundur. Yeni bilgi için RAG kullanın.

**Neden önemli:** Modelin şirket içi belgelerinizi bilmesini istiyorsanız RAG kullanın. Belirli bir biçimde yanıt vermesini istiyorsanız ince ayar yapın.

---

## "Daha büyük bağlam penceresi = daha iyi"

**Gerçek:** Modeller uzun bağlamlarda düşüş gösterir. "Ortada kaybolma" sorunu, modellerin uzun istemlerin başında ve sonuna daha fazla, ortasına daha az dikkat ettiğini gösterir. 200K bağlam penceresi, modelin tüm 200K token'ı eşit derecede iyi kullandığı anlamına gelmez. Ayrıca daha uzun bağlamlar daha pahalı ve daha yavaştır.

**Neden önemli:** Her şeyi bağlama boşaltmayın. Seçici olun. Hedefli geri alma ile RAG, tüm belgeyi doldurmaktan daha iyidir.

---

## "Yapay zeka ajanları özerktir"

**Gerçek:** Mevcut yapay zeka ajanları bir döngü içinde çalışır: düşün, gözlemle, tekrarla. Çerçevenin tanımladığı kalıbı izlerler. Hedefleri, planları veya öz farkındalıkları yoktur. LLM'leri bir sonraki aracı çağırmasına karar vermek için kullanan tepkisel sistemlerdir. "Özerklik", yapay zekadan değil döngüden gelir.

**Neden önemli:** Ajan oluştururken, döngüyü, araçları ve koruma setlerini oluşturuyorsunuz. LLM, sisteminizin içindeki sadece karar verme bileşenidir.

---

## "Transformerlar konumsal kodlama sayesinde sırayı anlar"

**Gerçek:** Transformerların doğal bir sıralama algısı yoktur. Öz-dikkat girdiyi bir dizi olarak değil, bir küme olarak ele alır. Konumsal kodlama, konuma bağlı vektörleri ekleyerek sıralama bilgisini enjekte etmek için bir geçici çözümdür. Farklı yöntemler (sinüzoidal, öğrenilmiş, RoPE, ALiBi) bunu farklı şekilde ele alır. Hiçbiri, RNN'lerin sahip olduğu şekilde modele gerçek anlamda sıralı anlayış kazandırmaz.

**Neden önemli:** Bu yüzden konumsal kodlama araştırması hala aktiftir. Çoğu kullanım için yeterince çözülmüş bir sorundur, ama temelde bir geçici çözümdür.

---

## "Önceden eğitim sadece internette okumaktır"

**Gerçek:** Önceden eğitim, devasa bir corpus üzerinde bir sonraki token tahminidir. Model, önceden gelenlere dayanarak ne geleceğini tahmin etmeyi öğrenir. Bu basit amaçla dilbilgisi, olgular, akıl yürütme desenleri, kod yapısı ve daha fazlasını öğrenir. Ama aynı zamanda internet saçmalıklarını, önyargıları ve yanlış bilgileri de öğrenir. Veri hazırlama, filtreleme ve duplike kaldırma son derece önemlidir.

**Neden önemli:** Girilen çöptür, çıkan da çöptür. Önceden eğitim verisinin kalitesi, modeller arasındaki en büyük farklılaştırıcılardan biridir.

---

## "RLHF, yapay zekayı insan değerleriyle hizalar"

**Gerçek:** RLHF, yapay zekayı geri bildirim sağlayan belirli insanların tercihleriyle hizalar. Bu insanlar birbirleriyle aynı fikirde değildir, önyargıları vardır ve her durumu kapsayamazlar. RLHF, modeli değerlendiricilerin tanımladığı şekillerde faydalı ve zararsız yapar, bazı evrensel insan değer sistemiyle hizalı yapmaz.

**Neden önemli:** RLHF bir eğitim tekniğidir, hizalama çözümü değil. Daha geniş bir araç kutusundaki bir araçtır.

---

## "Embeddingler anlamı yakalar"

**Gerçek:** Embeddingler istatistiksel eş-zamanlılık desenlerini yakalar. Benzer bağlamlarda geçen kelimeler benzer vektörler alır. Bu, anlamı kullanışlı olacak kadar iyi关联, ama anlamsal anlama değil. "King - Man + Woman = Queen" desen sayesinde çalışır, modelin monarji veya cinsiyeti anlaması nedeniyle değil.

**Neden önemli:** Embeddingler benzerlik arama, kümeleme ve geri alma için güçlüdür. Ama "benzer" ne anlama geldiği konusunda aşırı yorum yapmayın.

---

## "Zero-shot, eğitim yok demektir"

**Gerçek:** Zero-shot, çıkarım sırasında görev için özgün örnekler olmadığı anlamına gelir. Model hala milyarlarca token üzerinde eğitilmiştir. Sadece bu özel görev biçimini görmemiştir. Önceden eğitim desenlerinden genelleme yapar. Few-shot, prompt'a birkaç örnek vermek demektir. Hiçbiri, modelin eğitimsiz öğrenmesi demek değildir.

---

## "Yapay zeka modelleri insanlar gibi öğrenir"

**Gerçek:** İnsanlar az örnekle öğrenir, alanlar arası genelleme yapar ve inançlarını sürekli günceller. Sinir ağları milyonlarca örneğe ihtiyaç duyar, eğitim dağılımı içinde genelleme yapar ve eğitimden sonra sabit ağırlıklara sahip olur. Öğrenme benzetmesi en iyi ihtimalle gevşektir. Geri yayılım, biyolojik nöronların nasıl öğrendiğiyle hiç alakası yoktur.

**Neden önemli:** Modelleri insancıllaştırmayın. Bu, yapabildikleri ve yapamadıkları konusunda yanlış beklentilere yol açar.

---

## "Ölçekleme yasaları, daha büyüğün her zaman daha iyi olduğu anlamına gelir"

**Gerçek:** Ölçekleme yasaları, hesaplama, veri ve model boyutu arasındaki öngörülebilir ilişkileri tanımlar. Azalan getiriler gösterirler: parametreleri iki katına çıkarmak performansı iki katına çıkarmaz. Ayrıca veriyi orantılı olarak ölçeklediğinizi varsayarlar. Birçok pratik iyileştirme, daha iyi mimarilerden, eğitim tekniklerinden ve veri kalitesinden gelir, sadece ölçekten değil.

**Neden önemli:** İyi mühendislikle 7B model sorununuzu çözebilir. Varsayılan olarak 70B'ye uzanmayın.

---

## "Açık kaynak yapay zeka, açık ağırlıklarla aynıdır"

**Gerçek:** Çoğu "açık kaynak" model, açık ağırlıklardır. Model dosyalarını alırsınız ama eğitim verisini, eğitim kodunu veya veri hattını almazsınız. Gerçek açık kaynak (OLMo gibi) her şeyi yayınlar: veri, kod, aralık kontrolleri, değerlendirme. Açık ağırlıklar kullanışlıdır ama açık kaynakla aynı taahhüt değildir.

**Neden önemli:** Ne aldığınızı bilin. Açık ağırlıklar, çalıştırmanızı ve ince ayar yapmanızı sağlar. Gerçek açık kaynak, tekrar üretmenizi ve anlamanızı sağlar.

---

## "İstem mühendisliği gerçek bir mühendislik değil"

**Gerçek:** İstem mühendisliği sistem tasarımıdır. İnsan niyeti ile model davranışı arasındaki arayüzü tasarlıyorsunuz. İyi istem mühendisliği, tokenize etme, desen deseni, bağlam penceresi sınırları ve çıktı ayrıştırma gerektirir. Bu, "yapay zekaya güzel konuşmaktan" ziyade API tasarımına yakındır.

**Neden önemli:** Bu kurs, istem mühendisliğini 11. fazda gerçek bir mühendislik disiplini olarak öğretir.

---

## "CNN'ler modası geçti, artık her şey transformer"

**Gerçek:** Görüntü Transformerları (ViT) birçok benchmark'ta CNN'leri yener, ama CNN'ler hala yaygın olarak kullanılır. Çıkarma için daha hızlıdır, mobil/kenarda iyi çalışır, daha az veriye ihtiyaç duyar ve faydalı endüktif önyargılara sahiptir (öteleme değişmezliği, yerel desenler). Birçok üretim görüntü sistemi hala CNN kullanır. En iyi mimariler genellikle her ikisini birleştirir.

**Neden önemli:** Her ikisini de öğrenin (4. ve 7. fazlar). Kısıtlarınıza uyanı kullanın.

---

## "Yararlı modeller eğitmek için devasa hesaplama gücü gerekir"

**Gerçek:** Temel modelleri önceden eğitmek için devasa hesaplama gücü gerekir. Ama ince ayar, LoRA ve aktarmalı öğrenme, modelleri tek bir GPU'daicl etmenizi sağlar. Birçok yararlı yapay zeka uygulaması hiç eğitim gerektirmez, sadece iyi istem ve RAG gerektirir. "Hesaplama engeli" temel modelleri oluşturma içindir, onları kullanmak için değil.

**Neden önemli:** Dizüstü bilgisayarınızla gerçek yapay zeka uygulamaları oluşturabilirsiniz. Bu kurs bunu kanıtlıyor.
