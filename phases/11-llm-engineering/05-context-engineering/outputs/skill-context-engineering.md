---
name: skill-context-engineering
description: Görev türüne, pencere boyutuna ve gecikme bütçesine göre bağlam derleme pipeline'ları tasarlama karar çerçevesi
version: 1.0.0
phase: 11
lesson: 05
tags: [context-engineering, context-window, rag, memory, tool-selection, lost-in-the-middle]
---

# Bağlam Mühendisliği

Bir LLM uygulaması oluştururken, bağlam derleme pipeline'ını tasarlamak için bu çerçeveyi uygulayın.

## Temel ilkeler

1. **Bağlam kıttır.** 128K pencere büyük gelir, ancak hızla dolar. Her bileşeni açıkça bütçeleyin.
2. **Dikkat düzensizdir.** Modeller başa ve sona daha fazla dikkat eder. Kritik bilgiyi oraya koyun. Orta, ölü bölgedir.
3. **Dinamik, statikten iyidir.** Farklı sorgular farklı bağlamlar gerektirir. Başlangıçta bir kez değil, sorgu başına derleyin.
4. **Az, çoktan iyidir.** Küratörlüğü yapılmış 10K bağlam, dökülmüş 100K bağlamdan daha iyi performans gösterir. Sinyal-gürültü oranı toplam bilgiden daha önemlidir.
5. **Her şeyi ölçün.** Ölçmediğiniz şeyi optimize edemezsiniz. Her istekte bileşen başına token sayısını sayın.

## Bağlam bütçesi kılavuzları

| Bileşen | Tipik Aralık | Öncelik | Sıkıştırma Stratejisi |
|-----------|-------------|----------|---------------------|
| Sistem promptu | 200-1.000 token | Sabit, yüksek | Sıkı yazın, tekrarı kaldırın |
| Araç tanımları | 500-3.000 token | Dinamik, orta | Sorgu niyetine göre budayın |
| Getirilen bağlam | 1.000-5.000 token | Dinamik, yüksek | Yeniden sıralama + eşik + tekilleştir |
| Konuşma geçmişi | 500-5.000 token | Dinamik, orta | Eski turları özetleyin |
| Few-shot örnekleri | 500-2.000 token | Dinamik, yüksek | Görev benzerliğine göre seçin |
| Kullanıcı sorgusu | 50-500 token | Sabit, en yüksek | Yok |
| Üretim rezervi | 2.000-8.000 token | Sabit | Beklenen çıktı uzunluğuna göre ayarlayın |

## Her bellek türü ne zaman kullanılır

**Kısa vadeli (konuşma geçmişi):** Mevcut oturum. Özetleme ile yönetilir. 5-10 değişimden eski turları sıkıştırın. Son 3-4 turu kelimesi kelimesine tutun.

**Uzun vadeli (gerçekler veritabanı):** Oturumlar arasında kalıcı olan tercihler ve proje gerçekleri. Oturum başlangıcında getirin. Örnekler: "kullanıcı Python'u tercih ediyor", "proje PostgreSQL kullanıyor", "ekip trunk-based development izliyor". CLAUDE.md, bir veritabanı veya yapılandırılmış bir bellek sisteminde depolayın.

**Epizodik (geçmiş etkileşimler):** Mevcut görevle ilgili belirli geçmiş konuşmalar. Embedding olarak depolayın, benzerliğe göre getirin. "Geçen hafta benzer bir auth sorununda hata ayıkladık" epizodik bellektir.

## Araç seçim stratejisi

Her istekte tüm araçları dahil etmeyin. Bu, token israf eder ve modeli karıştırır.

1. Sorgu niyetini sınıflandırın (kod, e-posta, takvim, araştırma, veri)
2. Niyetleri araç kategorilerine eşleyin
3. Yalnızca eşleşen araçları dahil edin
4. Niyet belirsizse, en iyi 2 kategoriden araçları dahil edin
5. Her zaman bir "genel" araç (web araması gibi) yedek olarak dahil edin

Beklenen tasarruf: net niyete sahip sorgularda araç tanımı tokenlerinin %60-80'i.

## Getirme en iyi uygulamaları

- **Getirmeden sonra yeniden sıralayın.** Vektör benzerliği kaba bir filtredir. Bir yeniden sıralayıcı (cross-encoder veya LLM tabanlı) hassasiyeti önemli ölçüde artırır.
- **Bir ilgililik eşiği belirleyin.** 0.3 kosinüs benzerliğinin altındaki parçaları dahil etmeyin. Gürültü eklerler.
- **Tekilleştirin.** İki parça %80+ içerik paylaşıyorsa, yalnızca daha yüksek puanlı olanı tutun.
- **Ortada-kayıp sıralamasını uygulayın.** En ilgili parçaları önce ve sona yerleştirin.
- **Toplam getirme tokenlerini sınırlayın.** 15 orta parça yerine 3-5 yüksek oranda ilgili parça.

## Geçmiş yönetimi

- Son 3-4 turu kelimesi kelimesine tutun (modelin son bağlama ihtiyacı var)
- Daha eski turları bir özete dönüştürün ("X'i tartıştık, Y'ye karar verdik ve Z'de takılıp kaldık")
- Bilgi eklemeyen sistem tarafından üretilen turları bırakın (kullanıcıya dönük içeriği olmayan araç çağrıları)
- Geçmiş mevcut bütçenin %30'unu aştığında sıkıştırmayı tetikleyin

## Kırmızı bayraklar

- Sistem promptu 2.000 tokeni aşıyor: muhtemelen dinamik olması gereken bilgiler içeriyor
- Her istekte tüm araçlar dahil: niyete dayalı seçim uygulayın
- Getirmede ilgililik filtrelemesi yok: pencereye gürültü döküyorsunuz
- Geçmiş sınırsız büyüyor: özetleme uygulanmamış
- Üretim rezervi yok: model yanıtlarını kesiyor
- Aynı bilgi 3 yerde (sistem promptu, getirilen belge, geçmiş): tekilleştirin
- Bağlam kullanımı %60'ın üzerinde: modelin "düşünmesi" için çok az yer bırakıyorsunuz
