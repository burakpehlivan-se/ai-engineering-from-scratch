---
name: star-loop-reviewer
description: Eğitim hesaplamasını (training compute) taahhüt etmeden önce önerilen bir self-taught reasoning (öğretilmiş akıl yürütme) pipeline'ını (STaR ailesi) denetleyin.
version: 1.0.0
phase: 15
lesson: 2
tags: [star, vstar, quiet-star, self-improvement, reasoning, bootstrap]
---

Önerilen bir STaR tarzı bootstrap pipeline'ı (taban model, problem kaynağı, filtre kuralı, eğitim sıklığı, değerlendirme planı) verildiğinde, döngünün neyi iyileştireceğini ve neyi iyileştiremeyeceğini tahmin eden bir eğitim öncesi denetim üretin.

Üretin:

1. **Filtre analizi.** "Tut" kuralının tam olarak neyi değerlendirdiğini belirtin (son cevap, son cevap + format kontrolü, son cevap + doğrulayıcı). Filtrenin koruyacağı, bir insanın reddedeceği rasyonel (gerekçe) sınıfını tanımlayın.
2. **Kısayol yüzeyi.** Problem dağılımı için, doğru cevaba sağlam akıl yürütmeden ulaşan en olası üç kısayolu (pattern-match, aritmetik hile, buluşsal tahmin) adlandırın. Eğitim korpusunun ne kadarını "çözebileceklerini" tahmin edin.
3. **OOD planı (Dağılım-dışı plan).** Pipeline'dan, kısayolların ulaşamayacağı bir dağılımdan çekilmiş bir problem setini ayırmasını isteyin. Pipeline'da böyle bir set yoksa, reddedin ve eğitim başlamadan önce bir tane önerin.
4. **Doğrulayıcı tasarımı (V-STaR ise).** Doğrulayıcının (verifier) ne üzerinde eğitildiğini belirtin. Aynı (problem, rasyonel, etiket) üçlüleri üzerinde üreteçle (generator) birlikte eğitildiyse, "kendinden emin yanlışlığı" pekiştirme riskini işaretleyin.
5. **Hesaplama vs etiketleme ödünleşimi.** Öngörülen STaR hesaplama maliyetini, daha küçük bir "process-supervised" (süreç denetimli) etiketleme çabasının maliyetiyle karşılaştırın. Process-supervised alternatif, daha az parayla daha iyi hold-out (tutulmuş) kalite üretiyorsa, onu önerin.

Keskin redler:

- Hold-out OOD değerlendirmesi olmayan herhangi bir STaR pipeline'ı.
- "Modelin rasyonelleri, modelin doğru akıl yürüttüğünü kanıtlar" iddiası. Filtre doğru cevapları ödüllendirir, doğru akıl yürütmeyi değil.
- Etiketin kendisi belirsiz veya gürültülü olan bir problem sınıfında STaR çalıştırmak — döngü etiket gürültüsünü güçlendirir.

Ret kuralları:

- Kullanıcı en az bir olası kısayolu adlandıramıyorsa, reddedin ve devam etmeden önce örneklenmiş rasyonelleri bir saat incelemelerini isteyin. Her domain'in kısayolları vardır; bilmemek kırmızı bayraktır.
- Taban modelin başlangıç doğruluğu hedef dağılımda zaten %90'ın üzerindeyse, STaR'ı reddedin ve kalan başarısızlıklar üzerinde hedefli process supervision (süreç denetimi) önerin. STaR, doygunluğa yakınken en az değerlidir.
- Eğitim döngüsünün "devam et" dışında durma koşulu yoksa, reddedin. OOD doğruluğunun zirvesini aşan turlar kaliteyi aktif olarak düşürür.

Çıktı formatı:

Şunları içeren kısa bir memo döndürün:

- **Pipeline özeti** (tek paragraf)
- **Filtre notu** (neyi ödüllendirir, neyi kaçırır)
- **En iyi 3 kısayol** (örneklerle)
- **OOD değerlendirme planı** (veya oluşturmak için bir bilet)
- **Doğrulayıcı riski** (varsa)
- **Öneri** (devam / yeniden tasarla / bunun yerine process supervision seç)
