---
name: radix-scheduler-advisor
description: Önek-ağırlıklı ve RadixAttention'ın önbellek yeniden kullanımını isteyen iş yükleri için SGLang benimsenmesi ve istem-sıralama disiplini konusunda tavsiye ver.
version: 1.0.0
phase: 17
lesson: 06
tags: [sglang, radixattention, prefix-caching, scheduler, prompt-ordering]
---

Bir iş yükü tanımı (istem-şablonu şekli, erişim kalıbı, konuşma uzunluğu, eşzamanlı kiracı sayısı, donanım) verildiğinde bir SGLang / RadixAttention benimseme tavsiyesi üret.

Üretilecekler:

1. **İş yükü parmak izi.** Önek-ağırlıklı (tekrarlanan ön sözle RAG, tekrarlanan araç şemalarıyla agent'lar, tekrarlanan bağlamla ses) veya önek-hafif (benzersiz tek-seferlik istemler) olarak sınıflandır. Paylaşılan önek uzunluğunu ve tekrarlama oranını adlandır.
2. **İstem-sıralama denetimi.** Mevcut istem şablonunu yukarıdan aşağıya yürü. Değişmez bölüme serpiştirilmiş herhangi bir dinamik içeriği işaretle. Kanonik sırayı öner: sistem → araçlar/şemalar → erişim bağlamı → konuşma geçmişi → kullanıcı girdisi.
3. **Beklenen isabet oranı.** İş yükü parmak izinden, ulaşılabilir önbellek isabet oranını tahmin et. Genel sohbet %10-30. Tutarlı şablonla RAG %60-85. Sabit ön sözle ses/görüntü %80-95.
4. **SGLang vs vLLM kararı.** Beklenen isabet oranı > %40 ise ve iş yükü tek-seferlik değilse, SGLang öner. < %30 ise, `--enable-prefix-caching` ile vLLM daha basittir. %30-40 ise, bir örneklem üzerinde ikisini de çalıştır ve seç.
5. **Yayılım planı.** SGLang üzerinde mevcut istem şablonuyla 48-saatlik gölge kıyaslama. İsabet oranını kaydet. İstem-sıralama sorunlarını düzelt. Yeniden kıyaslama. İsabet oranı hedefi aşarsa yayınla.

**Hard rejects (zorunlu redler):**
- Trafikte gerçek önek paylaşımını ölçmeden SGLang önermek. Reddet.
- İş yükü şekline atıf yapmadan 6.4x sayısını iddia etmek. Sayı iş yüküne özgüdür.
- İstem-sıralama disiplinini yok saymak. Şablon önbellek anahtarıdır; onsuz scheduler yardımcı olamaz.

**Reddetme kuralları:**
- İş yükü tek-seferlikse (tekrarlanan sistem istemi yok), SGLang'ı reddet ve vLLM öner.
- Ekip istem şablonunu kontrol edemiyorsa (üçüncü-taraf tüketici), reddet ve yeniden ziyaret etmeden önce proxy-düzeyi şablon normalleştirmesi öner.
- Çok-kiracılı izolasyon kiracı başına ayrı KV havuzları gerektiriyorsa, SGLang'ın bunu desteklediğini not et, ancak ağaç-dalı çıkarma (tree-branch eviction) daha küçük kiracıları aç bırakabilir; kiracı başına bütçe tahsisi öner.

**Çıktı:** İş yükü parmak izi, istem-sıralama düzeltmeleri, beklenen isabet oranı, motor seçimi ve yayılım planı listeleyen tek sayfalık bir SGLang tavsiyesi. En büyük boşluğa bağlı olarak SGLang makalesine, vLLM prefix-caching belgelerine veya bu dersteki istem-sıralama alıştırmasına yönlendiren bir "sırada ne okunacak" paragrafıyla bitir.
