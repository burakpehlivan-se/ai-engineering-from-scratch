---
name: parallel-inference-router
description: Bir akıl yürütme iş yükünü oylama, düşünce ağacı (tree-of-thought), çoklu ajan, Hogwild! ve spekülatif kod çözme stratejileri arasında yönlendirin.
version: 1.0.0
phase: 10
lesson: 22
tags: [parallel-inference, hogwild, speculative-decoding, tree-of-thought, multi-agent, reasoning]
---

Bir akıl yürütme iş yükü profili (görev başına token bütçesi, görev paralellik özellikleri, model ailesi, dağıtım hedefi, gecikme bütçesi) verildiğinde, paralel çıkarım stratejisi veya kombinasyonu önerin.

Şunu üretin:

1. Görev sınıflandırması. Uzun akıl yürütme (5k+ token), orta zincir-düşünce (1k-5k), kısa sohbet (1k'nin altı) veya sınıflandırma. İlk geçiş kararını yönlendirir.
2. Paralellik ekseni. Dizi-içi (spekülatif kod çözme) vs diziler-arası (oylama, Hogwild!, çoklu ajan). Çoğu iş yükü önce dizi-içi ekseninden fayda görür.
3. Strateji önerisi. Şunlar arasından seçin: yalnızca spekülatif kod çözme (100 tokenin üzerindeki herhangi bir iş yükü için güvenli varsayılan), spekülatif + Hogwild! (paralelleştirilebilir yapıya sahip uzun akıl yürütme), düşünce ağacı (açık dal-budak problemleri), çoklu ajan (rol-uzmanlaşması problemleri), oylama topluluğu (yüksek riskli sınıflandırma).
4. Parametre ayarları. Spekülatif kod çözme için: taslak ailesi (EAGLE-3 varsayılan) ve `N` (Faz 10 · 15 becerisi). Hogwild! için: işçi sayısı N (2 ile 4, nadiren daha fazla), koordinasyon prompt şablonu, tek düğüm dağıtım onayı.
5. Birleşik hızlanma tahmini. Spekülatif kod çözmeyi Hogwild! ile birleştiriyorsanız, çarpımsal hızlanmayı raporlayın (tipik aralık: 3x spec * 1.5-2x Hogwild! = 4.5-6x).

Sert redler:
- 2000 tokenin altındaki herhangi bir iş yükü için Hogwild!. Koordinasyon ek yükü baskındır.
- Akıl yürütme yapmayan modellerde Hogwild! (ortaya çıkan koordinasyon yok).
- Doğal bir rol ayrıştırması olmayan problemler için çoklu ajan çerçevesi.
- Açık dal-budak mantığı olmadan düşünce ağacı (aksi takdirde strateji doğrusal CoT'ye indirgenir).
- Hogwild!'ı düğümler arasında çalıştırmak (düğümler arası önbellek senkronizasyonu çok yavaş).

Reddetme kuralları:
- İş yükü deneysel araştırmaysa, Hogwild!'ı bir üretim bahsi yerine deney olarak önerin. Hızlanmalar göreve bağlıdır ve Nisan 2026 itibarıyla gerçek dünya dağıtımı nadirdir.
- Kullanıcı garantili hızlanma isterse, reddedin ve yalnızca spekülatif kod çözmenin güçlü-garanti özelliğine (çıktı dağılımı korunur) sahip olduğunu açıklayın. Hogwild! deneyseldir.
- Kullanıcının sınırlı VRAM'ı varsa, Hogwild! N>2'yi reddedin — her işçi, önbellek paylaşılsa bile kendi aktivasyon belleğine ihtiyaç duyar.

Çıktı: Görev sınıflandırmasını, paralellik eksenini, stratejiyi, parametreleri ve birleşik hızlanma tahminini listeleyen tek sayfalık bir öneri. Hogwild! ilk 100 üretim isteğinde karşılığını vermezse yalnızca spekülatif kod çözmeye geri dönmeyi gerekçelendirecek belirli gecikme veya doğruluk metriğini adlandıran bir "geri dönüş tetikleyicisi" paragrafıyla bitirin.
