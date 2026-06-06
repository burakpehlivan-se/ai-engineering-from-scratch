---
name: router-plan
description: Bir LLM model-yönlendirme (model-routing) planı tasarla — kalıbı (ön-yönlendirme, kaskad, topluluk), sinyalleri (görev, uzunluk, gömme, güven) ve çevrimiçi kalite kapılarını seç.
version: 1.0.0
phase: 17
lesson: 16
tags: [routing, cascade, model-cascade, routellm, notdiamond, cost-reduction]
---

İş yükü karışımı (görev sınıflandırma örneklemi), kalite tabanı, gecikme toleransı ve mevcut aylık harcamaya göre bir yönlendirme planı üret.

Üretilecekler:

1. **Kalıp.** Ön-yönlendirme (en hızlı, sınıflandırıcıya bağımlı), kaskad (en iyi kalite tabanı) veya topluluk (yalnızca A/B örneklemi). Kalite toleransı + gecikme bütçesiyle gerekçelendir.
2. **Sinyaller.** Şunlardan seç: görev sınıflandırması, istem uzunluğu, bilinen-zor örneklerle gömme benzerliği, öz-güven. Hangilerinin birleştiğini (genelde 2-3) ve birleşim kuralını belirt.
3. **Ucuz/ileri çifti.** Belirli modelleri adlandır. Örnek: Claude Haiku 3.5 + GPT-5. Maliyet eğrisi + yetenek ile gerekçelendir.
4. **Beklenen tasarruf.** Önerilen bölünmede harmanlanmış maliyeti hesapla; mevcut duruma karşı beklenen aylık $'ı belirt.
5. **Çevrimiçi kalite kapıları.** Canlı trafiği değerlendiren hakemi belirle: rota başına örneklenen %5, ileri seviye bir hakemle değerlendirilir; Δ kalite > %2 ise uyar. Yükseltme oranını izle; bir ayda 10 puan artarsa uyar.
6. **Yayılım.** Gölge (yönlendir ama yoksay; çevrimdışı karşılaştır), kullanıcı-kohortuna göre %10 kanarya, kapıyı geçince genişlet.

**Hard rejects (zorunlu redler):**
- Çevrimiçi kalite kapıları olmadan yönlendirme. Reddet — sapma 1 numaralı başarısızlıktır.
- Sinyal olarak yalnızca görev sınıflandırması kullanmak. Reddet — görevler içindeki zorluk derecesini kaçırır.
- İleri-seviye uygun görevleri (kod, matematik, çok adımlı) kaskad geri dönüşü olmadan ucuza yönlendirmek. Reddet — kalite tabanı delinecektir.

**Reddetme kuralları:**
- Kalite toleransı "sıfır regresyon" olarak belirtilmişse, ön-yönlendirmeyi reddet ve yüksek yükseltme oranıyla kaskad öner.
- Ucuz model Anthropic/OpenAI/ileri-seviye dışındaysa ve bilinen reddetme kalıpları varsa (ör. sansürsüz modeller ve agent araç-kullanımı), çifti reddet — araç çağrılarını sessizce bozar.
- Yönlendirme ucuz için farklı bir sağlayıcıya yapılıyorsa (sağlayıcılar-arası kaskad), API'leri birleştirmek için AI ağ geçidi katmanını (Phase 17 · 19) zorunlu kıl.

**Çıktı:** Kalıp, sinyaller, model çifti, beklenen tasarruf, çevrimiçi kapılar ve yayılım planını adlandıran tek sayfalık bir plan. Tek bir metrikle bitir: kayan 7 günlük yükseltme oranı (escalation-rate); değişim > 10 yüzde puanı ise sapma tetikleyicisi.
