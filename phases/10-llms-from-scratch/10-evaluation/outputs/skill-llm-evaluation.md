---
name: skill-llm-evaluation
description: Görev türüne, bütçeye ve gereksinimlere göre doğru LLM değerlendirme stratejisini seçme karar çerçevesi
version: 1.0.0
phase: 10
lesson: 10
tags: [evaluation, evals, benchmarks, llm-as-judge, elo, metrics]
---

# LLM Değerlendirme Stratejisi

Bir LLM sistemini değerlendirirken, doğru yaklaşımı seçmek için bu karar çerçevesini uygulayın.

## Her Değerlendirme Türü Ne Zaman Kullanılır

**Kıyaslamalar (Benchmarks) (MMLU, HumanEval, SWE-bench):** İlk model seçimini yapıyorsunuz. 10 aday modeli 3'e daraltmanız gerekiyor. Kıyaslamalar, sıfır maliyetle kabaca bir sıralama verir. Kıyaslamaları son değerlendirmeniz olarak kullanmayın.

**Özel değerlendirmeler:** Üretim için inşa ediyorsunuz. Belirli başarısızlık modlarına sahip belirli bir göreviniz var. Özel değerlendirmeler, gerçek dünya performansını tahmin eden tek değerlendirmedir. Prototip için minimum 50 test durumu, üretim için 200+.

**LLM-as-judge (LLM'i hakem olarak kullanma):** Göreviniz açık uçlu (özetleme, yazma, konuşma). Tam eşleşme ve token örtüşme metrikleri çok katı. LLM-as-judge, yargı başına ~$0.01 maliyetle insanlarla ~%80 oranında hemfikir. Belirsiz bir prompt değil, her zaman bir puanlama cetveli kullanın.

**İnsan değerlendirmeleri:** Riskler yüksek ve otomatik metrikler hemfikir değil. İnsan değerlendirmesi kesin referanstır, ancak yargı başına $0.10-$2.00 maliyetle gelir. Belirsiz durumlar ve otomatik metriklerin periyodik kalibrasyonu için saklayın.

**İkili karşılaştırmalardan ELO:** Aynı görevde birden fazla modeli karşılaştırıyorsunuz. İkili karşılaştırma, mutlak puanlamadan daha güvenilirdir çünkü insanlar (ve LLM hakemler) göreceli yargılarda daha iyidir.

## Puanlama Fonksiyonu Seçimi

- **Tam eşleşme**: sınıflandırma, varlık çıkarma, bilinen yanıtlı yapılandırılmış çıktılar
- **Token F1**: kısmi puanın önemli olduğu çıkarma görevleri
- **ROUGE-L**: özetleme, çeviri
- **BLEU**: makine çevirisi
- **LLM-as-judge**: açık uçlu üretim, konuşma kalitesi, yardımseverlik
- **Yürütmeye dayalı**: kod üretimi (kodu çalıştırın, testlerin geçip geçmediğini kontrol edin)
- **Şema uyumu**: yapılandırılmış çıktılar (JSON şemayla eşleşiyor mu?)

## Değerlendirme Tasarımındaki Kırmızı Bayraklar

- Değerlendirme seti 50 durumdan küçük: sonuçlar istatistiksel olarak anlamsız
- Uç durum yok: mutlu yol performansını ölçüyorsunuz, bu her zaman gerçek dünyadan yüksektir
- Tek metrik: farklı metrikler farklı hikayeler anlatır, en az iki kullanın
- Sürümleme yok: sürümlenmiş değerlendirme setleri olmadan iyileştirmeyi izleyemezsiniz
- Değerlendirme seti kontaminasyonu: ince ayar verisine veya few-shot (az-örnekli) promptlara değerlendirme örneklerini asla dahil etmeyin
- Yalnızca bir modeli test etme: karşılaştırma için bir temel (basit bir sezgisel olsa bile) gerekir

## Değerlendirme Pipeline'ı Kontrol Listesi

1. Görevi kesin olarak tanımlayın ("soru cevaplama" değil, "destek biletlerini 5 kategoriye sınıflandırma")
2. Mutlu yol, uç durumlar ve bilinen regresyonlar boyunca test durumları oluşturun
3. Görev türüne uygun 2-3 puanlama fonksiyonu seçin
4. Üretim gereksinimlerine göre geçer/kalır eşiklerini belirleyin
5. Yürütmeyi otomatikleştirin: tek bir komut tüm paketi çalıştırır
6. Her şeyi sürümleyin: test durumları, puanlama fonksiyonları, prompt'lar, model sürümleri
7. Her değişiklikte çalıştırın: prompt güncellemeleri, model değişiklikleri, kod dağıtımları
8. Eğilimleri izleyin: tek bir puan gürültüdür, bir eğri sinyaldir
9. Üç ayda bir insan yargısına karşı kalibre edin
10. Üretim başarısızlığı keşfedildiğinde regresyon durumları ekleyin
