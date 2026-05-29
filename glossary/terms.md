# Yapay Zeka Mühendisliği Terimler Sözlüğü

> Bu sözlük, çeviride kullanılacak tüm terimlerin resmi karşılıklarını içerir.
> Her terim için: İngilizce karşılık, Türkçe karşılık, kısa açıklama ve ilk kullanım yeri.

---

## Kullanım Kuralları

1. **Yerleşik Teknik Terimler:** `token`, `backpropagation`, `overfitting` gibi terimler aynen kalır; ilk geçtikleri yerde parantez içinde kısa bir açıklama verilir.
2. **Genel Teknik Terimler:** `vector → vektör`, `gradient → gradyan`, `matrix → matris` gibi yerleşik karşılıklar kullanılır.
3. **Projeye Özgü Terimler:** `prompt → istem`, `skill → beceri`, `agent → ajan`, `loop → döngü`. Bu karşılıklar tüm çeviride tutarlı olmalıdır.
4. **Tutarlılık:** Bir kez belirlenen karşılık tüm çeviride aynı şekilde kullanılmalıdır.

---

## A

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Agent | ajan | Döngü içinde çalışan, araçları kullanabilen LLM tabanlı sistem | Faz 14 |
| Activation Function | aktivasyon fonksiyonu | Katmanlar arasında doğrusal olmayan dönüşüm uygulayan fonksiyon | Faz 3 |
| Adam (Optimizer) | Adam (optimize edici) | Adaptif Moment Tahmini ile ağırlıkları güncelleyen algoritma | Faz 2 |
| AdamW | AdamW | Ağırlık azaltmalı (weight decay) Adam varyantı | Faz 2 |
| Attention | dikkat | Token'ların birbirine ne kadar önem atfettiğini hesaplayan mekanizma | Faz 7 |
| Alignment | hizalama | Yapay zeka davranışının insan niyetiyle eşleşmesi | Faz 18 |
| Autograd | otomatik gradyan | Türevleri otomatik hesaplayan sistem | Faz 2 |
| Autoregressive | otoregresif | Bir token'ı diğerine bağımlı üreten model | Faz 10 |
| Augmentation | veri artırma | Mevcut veriyi değiştirerek çeşitlilik oluşturma | Faz 4 |

---

## B

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Backpropagation | geri yayılım | Ağdan geriye doğru hata türevlerini hesaplama algoritması | Faz 3 |
| Batch Size | toplu iş boyutu | Bir adımda işlenen örnek sayısı | Faz 2 |
| Batch Normalization | toplu iş normalleştirmesi | Toplu iş boyunca değerleri normalleştirme | Faz 3 |

---

## C

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Chain of Thought (CoT) | düşünce zinciri | Modelin adımları göstermesini sağlayan teknik | Faz 10 |
| Chunking | parçacıklandırma | Metni embedding öncesi parçalara bölme | Faz 11 |
| CNN (Convolutional Neural Network) | evrişimsel sinir ağı | Yerel desenleri tespit eden sinir ağı | Faz 4 |
| Contrastive Learning | karşıtlıklı öğrenme | Benzer çiftleri yakınlaştıran, farklıları uzaklaştıran eğitim | Faz 4 |
| Cosine Similarity | kosinüs benzerliği | İki vektör arasındaki açının kosinüsü | Faz 11 |
| Cross-Entropy | çapraz entropi | İki olasılık dağılımı arasındaki farkın ölçümü | Faz 3 |
| CUDA | CUDA | NVIDIA'nın paralel hesaplama platformu | Faz 0 |

---

## D

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Data Augmentation | veri artırma | Eğitim verisini çoğaltarak çeşitlilik artırma | Faz 4 |
| Decoder | çözümleyici | Transformer'da çıktı üreten kısım | Faz 7 |
| Diffusion Model | difüzyon modeli | Gürültüden temizleyerek veri üreten model | Faz 8 |
| DPO (Direct Preference Optimization) | doğrudan tercih optimizasyonu | Ödül modeli olmadan tercih optimizasyonu | Faz 18 |
| Dropout | bırakma | Eğitim sırasında rastgele nöronları devre dışı bırakma | Faz 3 |

---

## E

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Eigenvalue | özdeğer | Matrisin vektörleri ne kadar ölçeklediğini gösteren değer | Faz 1 |
| Embedding | embedding | Sayısal temsile dönüştürme (kelime → vektör) | Faz 11 |
| Encoder | kodlayıcı | Transformer'da girdiyi anlayan kısım | Faz 7 |
| Epoch | epok | Eğitim verisinin tamamının bir kez geçilmesi | Faz 2 |

---

## F

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Feature | özellik | Verinin ölçülebilir özelliği | Faz 2 |
| Few-Shot | few-shot | Prompt'a birkaç örnek ekleme tekniği | Faz 10 |
| Fine-tuning | ince ayar | Önceden eğitilmiş modeli üzerinde ince eğitim | Faz 10 |
| Function Calling | fonksiyon çağırma | LLM'lerin harici fonksiyonları çağırma mekanizması | Faz 13 |

---

## G

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| GAN (Generative Adversarial Network) | üreteç-ayırıcı ağ | İki ağın birlikte eğitildiği generatif model | Faz 8 |
| Gradient | gradyan | Türev vektörü (en dik eğim yönü) | Faz 1 |
| Gradient Descent | gradyan inişi | Kaybı azaltmak için ağırlıkları güncelleme algoritması | Faz 2 |
| GPT | GPT | Generative Pre-trained Transformer mimarisi | Faz 10 |
| Guardrails | koruma setleri | LLM etrafındaki güvenlik katmanları | Faz 18 |

---

## H

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Hallucination | halüsünasyon | Modelin gerçek olmayan içerik üretmesi | Faz 18 |
| Hyperparameter | hiperparametre | Eğitimden önce belirlenen ayarlar | Faz 2 |

---

## I

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Inductive Bias | endüktif önyargı | Model mimarisine yerleşik varsayımlar | Faz 3 |
| Inference | çıkarım | Eğitilmiş modelle tahmin yapma | Faz 10 |

---

## J

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| JAX | JAX | NumPy uyumlu, otomatik türev ekleyen kütüphane | Faz 2 |

---

## K

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| KV Cache | KV önbellek | Otoregresif üretimde anahtar-değer matrislerini önbelleğe alma | Faz 10 |

---

## L

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Latent Space | gizli uzay | Öğrenilmiş sıkıştırılmış temsil uzayı | Faz 8 |
| Learning Rate | öğrenme hızı | Adım boyutunu belirleyen skaler değer | Faz 2 |
| LLM (Large Language Model) | büyük dil modeli | Milyarlarca parametre ile eğitilmiş dil modeli | Faz 10 |
| LoRA | LoRA | Düşük rank adaptasyonu ile verimli ince ayar | Faz 10 |
| Loss Function | kayıp fonksiyonu | Tahmin ile gerçek arasındaki farkı ölçen fonksiyon | Faz 2 |

---

## M

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| MCP (Model Context Protocol) | model bağlam protokolü | AI uygulamalarını harici araçlara bağlayan açık protokol | Faz 13 |
| Mixed Precision | karma hassasiyet | Hız için float16, hassasiyet için float32 kullanma | Faz 10 |
| MoE (Mixture of Experts) | uzman karışımı | Yalnızca uzman alt ağların çalıştığı model mimarisi | Faz 10 |

---

## N

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| NaN (Not a Number) | NaN (Sayı Değil) | Tanımsız sonuçları gösteren kayan nokta değeri | Faz 2 |
| Normalization | normalleştirme | Değerleri standart aralığa ayarlama | Faz 3 |

---

## O

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Optimizer | optimize edici | Gradyanları kullanarak ağırlıkları güncelleyen algoritma | Faz 2 |
| Overfitting | aşırı uyum | Modelin eğitim verisine ezberlemesi | Faz 2 |

---

## P

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Parameter | parametre | Modelde öğrenilebilir değer (ağırlık veya sapma) | Faz 2 |
| Perplexity | perplexity | Ortalama çapraz entropi kaybının üstel değeri | Faz 10 |
| Precision & Recall | kesinlik ve duyarlılık | Sınıflandırma metrikleri | Faz 4 |
| Prompt | istem | Modelle iletişime geçilen girdi metni | Faz 10 |
| Prompt Engineering | istem mühendisliği | İstenen çıktıyı üretmek için girdi tasarım teknikleri | Faz 10 |
| Prompt Injection | istem enjeksiyonu | Kötü niyetli metinle modeli manipüle etme saldırısı | Faz 18 |

---

## Q

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| QLoRA | QLoRA | Nicelleştirilmiş LoRA (4-bit taban model + 16-bit LoRA) | Faz 10 |
| Quantization | nicelleştirme | Ağırlık hassasiyetini düşürerek modeli küçültme | Faz 10 |

---

## R

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| RAG (Retrieval-Augmented Generation) | geri récupération destekli üretim | Belge bulma + LLM ile yanıt üretme | Faz 11 |
| ReLU | ReLU | Doğrusal olmayan aktivasyon fonksiyonu: max(0, x) | Faz 3 |
| RLHF | insan geri bildiriminden pekiştirmeli öğrenme | İnsan tercihleriyle model eğitimi | Faz 18 |
| ROUGE | ROUGE | Özetleme kalitesi ölçüm metriği | Faz 5 |

---

## S

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Semantic Search | anlamsal arama | Anlama göre belge bulma | Faz 11 |
| Self-Attention | öz-dikkat | Token'ların birbirine dikkat etme mekanizması | Faz 7 |
| SFT (Supervised Fine-Tuning) | denetimli ince ayar | talimat-cevap çiftleriyle ince ayar | Faz 18 |
| Softmax | softmax | Sayıları olasılık dağılımına dönüştürme | Faz 3 |
| Streaming | akış | Yanıtların token token gösterilmesi | Faz 10 |
| Swarm | sürü | Birlikte çalışan çoklu ajan sistemi | Faz 16 |
| System Prompt | sistem istemi | Modelin davranışını belirleyen özel mesaj | Faz 10 |

---

## T

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Temperature | sıcaklık | Rastgelelik düzeyini ayarlayan skaler değer | Faz 10 |
| Tensor | tensör | Derin öğrenme çerçevelerinin temel veri yapısı | Faz 1 |
| Token | token | Metnin işlenmesinde kullanılan alt kelime birimi | Faz 10 |
| Tokenizer | tokenize edici | Metni token'lara bölen araç | Faz 10 |
| Transfer Learning | aktarmalı öğrenme | Önceden eğitilmiş modeli farklı görev için kullanma | Faz 10 |
| Transformer | transformer | Öz-dikkat kullanan sinir ağı mimarisi | Faz 7 |

---

## U

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Underfitting | yetersiz uyum | Modelin verideki desenleri yeterince öğrenememesi | Faz 2 |

---

## V

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| VAE (Variational Autoencoder) | değişken oto-kodlayıcı | Düzgün gizli uzay öğrenen oto-kodlayıcı | Faz 8 |
| Vector | vektör | Yönlü büyüklük (sayı dizisi) | Faz 1 |
| Vector Database | vektör veritabanı | Vektörler için optimize edilmiş veritabanı | Faz 11 |

---

## W

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Weight | ağırlık | Modelin parametre matrisindeki tek bir değer | Faz 2 |
| Weight Decay | ağırlık azaltma | Kayba ağırlık büyüklüğü cezası ekleme | Faz 2 |

---

## Z

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| Zero-Shot | zero-shot | Örnek olmadan modeli görevde kullanma | Faz 10 |

---

## Güncelleme Geçmişi

| Tarih | Değişiklik |
|-------|-----------|
| 2026-05-29 | İlk sürüm: 100+ terim için Türkçe karşılıklar |
