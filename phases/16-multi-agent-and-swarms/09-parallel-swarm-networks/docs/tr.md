# Paralel / Swarm / Ağ Mimarileri

> Supervisor ile karşıtlık: merkezi karar verici yok. Agent'lar paylaşılan bir olay veri yolunu (event bus) okur, işi eşzamansız olarak alır, sonuçları geri yazar. LangGraph, merkezsiz, dinamik ortamlar için "Swarm Architecture"yı açıkça destekler. Matrix (arXiv:2511.21686), orkestratör darboğazını ortadan kaldırmak için hem kontrol hem veri akışını dağıtılmış kuyruklardan geçen serileştirilmiş mesajlar olarak temsil eder. Ödünleşim açıktır: ölçeklenebilirlik için determinizm ve izlenebilirlik. Swarm, birçok bağımsız alt problemi olan görevlere uyar; tek bir tutarlı plana ihtiyaç duyan görevlere uymaz.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib, `threading`, `queue`)
**Ön Koşullar:** Faz 16 · 05 (Supervisor Kalıbı), Faz 16 · 04 (İlkel Model)
**Süre:** ~75 dakika

## Problem

Supervisor birkaç işçiye ölçeklenir. Ya yüzlerce? Supervisor'ın kendisi darboğaz haline gelir: kimin ne yapacağına dair her karar bir agent'tan geçer. Tek bir yavaş plan adımı tüm sistemi durdurur.

Swarm mimarileri tasarımı tersine çevirir. Merkezi bir planlayıcı işi dağıtmak yerine, işçiler işi paylaşılan bir kuyruktan alır. "Koordinasyon" olay veri yolu semantiğine gömülüdür. Orkestratör yok; sistem kuyruk ölçeklenene kadar ölçeklenir.

## Kavram

### Şekil

```
 ┌──── paylaşılan kuyruk ────┐
 │ │
 ┌────────┼────────┐ ◄──────┬───┘
 ▼ ▼ ▼ │
 İşçi İşçi İşçi İşçi
 A B C D
 │ │ │ │
 └────────┴────────┴─────────┘
 │
 ▼
 sonuç havuzu
```

Orkestratör yok. Her işçi tekrar eder: bir görev çek, işle, sonucu yaz (ve isteğe bağlı olarak takip görevlerini kuyruğa ekle).

### Swarm ne zaman uyar

- **Birçok bağımsız görev.** Kazıma (scraping), dönüştürme, sınıflandırma. Görevler birbirine bağlı değil.
- **Değişken süreli iş.** Bazı görevler 100ms, bazıları 10s sürüyorsa, swarm yükü otomatik olarak dengeler — hızlı işçiler sonraki işleri çeker. Bir supervisor süreyi önceden tahmin etmek zorundadır.
- **Determinizm üzerinden verim.** Toplam tamamlanma süresi önemsenir, sıkı sıralama değil.

### Swarm ne zaman başarısız olur

- **Sıralı iş akışları.** Adım 3, Adım 2'nin çıktısına ihtiyaç duyuyorsa, swarm Adım 3'ün Adım 2 bitmeden ateşlenmesi riskini taşır.
- **Küresel planlı görevler.** Karmaşık araştırma soruları bir planlayıcıdan faydalanır. Bir araştırmacı swarm'ı bağımsız gerçekler üretir, tutarlı bir rapor değil.
- **Hata ayıklama.** Merkezi bir günlük ve eşzamansız iş olmadan, bir hatayı yeniden üretmek pahalıdır.

### Matrix (arXiv:2511.21686)

Matrix, swarm'ı doğal sonucuna taşıyan 2025 makalesidir: hem kontrol akışı hem veri akışı, dağıtılmış kuyruklardaki serileştirilmiş mesajlardır. Merkezi koordinatör yok. Hata toleransı, mesaj dayanıklılığından gelir. Ölçeklenebilirlik, sistemin değil mesaj komisyoncusunun (broker) sorunudur.

Katkı: multi-agent koordinasyonunun "bu agent hangi mesaj konusuna abone?" olduğu, "supervisor hangi agent'ı bir sonraki olarak seçiyor?" olmadığı bir programlama modeli. Bu, sistemi bir pub/sub olay ağı gibi gösterir.

### LangGraph'ın Swarm Mimarisi

LangGraph 2025 belgeleri, "Swarm Architecture"yı multi-agent kalıplarından biri olarak açıkça tanımlar: agent'lar düğümlerdir, ancak kenarlar döngülerle yönlendirilmiş bir graf oluşturur ve herhangi bir düğüm havuzdan etkinleştirilebilir. Bir işçi, supervisor atamasıyla değil, koşulla havuzdan iş çeker.

### Başarısızlık modu: açlık ve sıcak noktalaşma

Tüm işçiler en hızlı mevcut görevi çekerse, uzun süren görevler tek başlarına kalmayana kadar asla alınmaz. Klasik kuyruk açlığı.

Hafifletmeler:
- Açık yaşlandırma (aging) ile öncelik kuyrukları (bekleme süresiyle önceliği artırın).
- İşçi uzmanlaşması: bazı işçiler yalnızca "uzun" görevleri alır.
- Geri basınç (back-pressure): kuyruğa giren hızlı görev sayısını sınırlayın.

### İçerik tabanlı yönlendirme bağlantısı

Swarm, içerik tabanlı yönlendirmeyle (Ders 22) doğal olarak eşleşir. Genel bir kuyruk yerine, mesaj türü başına bir kuyruğunuz olsun. Uzmanlaşmış işçiler yalnızca kendi türlerine abone olsun. Bu, binlerce agent'a ölçeklenen mesaj veri yolu mimarilerinin temelidir.

## İnşa Et

`code/main.py` paylaşılan bir `queue. Queue`'dan çeken 4 iş parçacıklı bir swarm uygular. Görevlerin değişken süreleri vardır (bazıları hızlı, bazıları yavaş). Demo kontrastları:

- **Sıralı temel:** bir işçi tüm görevleri seri olarak işler.
- **Sabit atama:** her görev önceden belirli bir işçiye atanır (supervisor tarzı).
- **Swarm:** işçiler paylaşılan bir kuyruktan çeker.

Swarm yükü otomatik olarak dengeler; sabit atama, atanmış görev yavaş olduğunda hızlı işçileri boş bırakır.

Çalıştırın:

```
python3 code/main.py
```

Çıktı, işçi başına görev sayımlarını (swarm eşit olmayan ama en uygun şekilde dağıtır) ve duvar saati sürelerini gösterir.

## Kullan

`outputs/skill-swarm-fit.md`, bir görevin swarm mı yoksa supervisor mı kullanması gerektiğini değerlendirir. Girdiler: görev bağımsızlığı, süre varyansı, sıralama gereksinimleri, hata ayıklanabilirlik ihtiyaçları.

## Dağıt

Kontrol listesi:

- **Yaşlandırmalı öncelik kuyruğu.** Uzun-görev açlığını önleyin.
- **İşçi idempotansı (idempotency).** Bir işçi çalışırken çökerse bir görev birden fazla çekilebilir. İşçiler idempotent olmalıdır.
- **Dayanıklı kuyruk.** Üretim için Kafka, Redis Streams veya veritabanı destekli kuyruk kullanın. `queue. Queue` yalnızca bellek içidir.
- **Görev başına gözlemlenebilirlik.** Her görevin bir iz kimliği (trace ID) vardır; her işçi onunla başlangıç/bitiş kaydeder.
- **Geri basınç (back-pressure).** Kuyruk, işçilerin boşaltmasından daha hızlı büyürse, üreticiyi yavaşlatın.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Değişken süreli iş yükünde swarm, sıralıdan ne kadar hızlıdır? Sabit atamadan ne kadar hızlıdır?
2. Bir öncelik kuyruğu varyantı ekleyin (`queue. PriorityQueue` kullanın). Önceliği görevin "önem" alanına göre atayın. Sürekli yük altında düşük öncelikli görevlerin asla aç kalmadığını gözlemleyin.
3. Bir sıcak nokta (hot-spot) dedektörü uygulayın: herhangi bir işçi en yavaş işçiden 3× daha fazla görev işlediğinde günlüğe kaydedin. Bu, görev-süresi dağılımı hakkında ne gösterir?
4. Matrix makalesini (arXiv:2511.21686) özetini ve Bölüm 3'ü okuyun. Matrix'in kabul ettiği somut bir ödünleşimi (ölçeklenebilirlik kazancı) ve verdiği bir şeyi (izlenebilirlik, determinizm) belirleyin.
5. Swarm demoyu `(task_type, payload)` tuple'larından oluşan bir `queue. Queue` kullanacak şekilde dönüştürün, işçiler yalnızca belirli türlere abone olsun. Görevler heterojen olduğunda hangi yönlendirme kuralları anlamlıdır?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Swarm architecture (Swarm mimarisi) | "Merkezsiz agent'lar" | İşçiler paylaşılan kuyruktan çeker; merkezi orkestratör yok. |
| Event bus (Olay veri yolu) | "Agent'lar konulara abone olur" | Görevleri türe veya içeriğe göre işçilere yönlendiren mesaj komisyoncusu. |
| Starvation (Açlık) | "Görev asla çalışmaz" | Düşük öncelikli görev, daha yüksek öncelikli iş sürekli geldiği için asla alınmaz. |
| Hot-spotting (Sıcak noktalaşma) | "Bir işçi boğulur" | Yük dengesizliği, bir işçi çoğu görevi alır. |
| Back-pressure (Geri basınç) | "Üreticiyi yavaşlat" | Kuyruk dolduğunda yukarı yönde durma sinyali veren mekanizma. |
| Idempotent worker (Idempotent işçi) | "Yeniden çalıştırmak güvenli" | Bir görevin iki kez işlenmesi aynı sonucu üretir. İşçiler çökebileceğinden gereklidir. |
| Durable queue (Dayanıklı kuyruk) | "Çökmelerden sağ çıkar" | Disk veya çoğaltılmış depolama ile desteklenen kuyruk; bir işçi çöktüğünde görevler kaybolmaz. |
| Matrix framework (Matrix çatısı) | "Tam mesaj geçişli swarm" | Hem veri hem kontrol akışı, dağıtılmış kuyruklardaki serileştirilmiş mesajlardır. |

## İleri Okuma

- [LangGraph iş akışları ve agent'ları — Swarm Architecture](https://docs.langchain.com/oss/python/langgraph/workflows-agents) — açık swarm desteği
- [Matrix — A Decentralized Framework for Multi-Agent Systems](https://arxiv.org/abs/2511.21686) — tam mesaj geçişli swarm
- [Anthropic mühendislik — Research'de neden swarm değil supervisor](https://www.anthropic.com/engineering/multi-agent-research-system) — belirli bir üretim sisteminin neden swarm yerine bilinçli olarak supervisor seçtiği
- [AutoGen v0.4 actor-model belgeleri](https://microsoft.github.io/autogen/stable/) — olay güdümlü actor yeniden yazımı, v0.2'nin GroupChat'inden daha çok swarm'a yakın
