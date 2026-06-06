---
name: ai-scientist
description: Deney ağacı araması çalıştıran, görüntü eleştirisiyle LaTeX makaleleri yazan ve bir sandbox-kaçış kırmızı takımını geçen otonom bir araştırma ajanı inşa et
version: 1.0.0
phase: 19
lesson: 05
tags: [capstone, autonomous-agent, ai-scientist, sakana, langgraph, sandbox, research]
---

Bir tohum fikir, dar bir alan ve 30 dolarlık bir hesaplama bütçesi verildiğinde, bir deney ağacı araması çalıştıran, gözden geçirilebilir bir LaTeX makalesi yazan ve bir yeniden-üretilebilirlik demeti yayan bir ajan inşa et.

İnşa planı:

1. Literatür geçişi: Semantic Scholar Graph API + OpenAlex; özetleri FAISS'te önbelleğe al; 1 sayfalık bir alan özeti üret.
2. Ağaç araması: en iyi-ilk genişletmeyi `expand(node) -> children` (çocuk başına bir yapılandırma düzenlemesi) ve `score(node) = yenilik*0,4 + kalite*0,5 + bütçe*0,1` ile uygula.
3. Düğüm başına sandbox: her deney `docker run --network=none --memory=8g --cpus=2 --pids-limit=256 --read-only` veya E2B eşdeğeri çalıştırır; belirleyici tohumlar; kaynak sınırı zorunlu.
4. Plan-çalıştır-doğrula: doğrulama adımı, kaybın yakınsadığını, temel çizgilerin çalıştığını, ablasyonların iddiayı yalıttığını kontrol eder.
5. Yazar: LaTeX üret, PDF'e derle, düzen ve iddia-kanıt hizalaması için Claude Opus 4.7 görüntü moduna besle, en fazla 3 kez yinele.
6. Hakem topluluğu: beş yargıç (Opus 4.7, GPT-5.4, Gemini 3 Pro, DeepSeek R1, Qwen3-Max) NeurIPS rubriğinde (yenilik, titizlik, netlik, yeniden-üretilebilirlik, etki) puanlar; ortalama < 4,0 yazara geri döner.
7. Kırmızı takım: karşıt görevleri (çatal bombası, dosya sistemi kaçışı, LLM-yazılı ağ çağrısı) entegre et. Tümünün engellendiğini doğrula. `red_team.md` yay.
8. Yeniden-üretilebilirlik demeti: paper.pdf + review.md + ağaç-arama izi JSON + tohumlar + W&B çalıştırma bağlantıları + sandbox yapılandırması + tek satırlık yeniden çalıştırma komutu.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Makale kalitesi | Aynı tohum konusundaki yayınlanmış atölye makalelerine karşı kör rubrik incelemesi |
| 20 | Deneysel titizlik | Temel çizgiler, tohumlar, ablasyonlar; her iddia sonuç tablosundaki bir hücreyle desteklenir |
| 20 | Maliyet ve hesaplama disiplini | Makale başına 30 dolar tavanı zorunlu, Langfuse izli |
| 20 | Güvenlik | Sandbox kırmızı takımı geçer; ağ politikası ve öldürme-anahtarı, kaydedilmiş denemelerle doğrulanır |
| 15 | Yeniden-üretilebilirlik | Tek-komut yeniden çalıştırma, aynı tohumlarla makaleyi yeniden üretir |

Kesin redler:

- Sandbox dışında çalışan deneyler. Capstone'ın tezi, yürütmenin kapsanmasıdır.
- Derlenmiş PDF'i yeniden okumayan yazar adımları (görüntü eleştirisi yük taşımaktadır).
- Temel çizgileri, tohumları veya ablasyon bölümü olmayan makaleler.
- Yalnızca son-ezik uyarıları olarak zorlanan maliyet bütçeleri, sert tavanlar olarak değil.

Ret kuralları:

- 4,0/5 altında ortalama hakem puanı olan bir makaleyi açık bir insan geçersiz kılması olmadan yayınlamayı reddet.
- Sandbox içinden ağ erişimi gerektiren bir tohum fikir üzerinde çalıştırmayı reddet. Bunun yerine ayrı bir salt-okunur veri kümesi hacmi ekle.
- Kırmızı takımı yürütülmemiş ve kaydedilmemiş bir makaleyi yeniden çalıştırmayı reddet.

Çıktı: Ağaç-arama motorunu, sandbox politikasını, yazar/hakem döngüsünü, yeniden-üretilebilirlik demetleriyle üç örnek çalıştırmayı, bir kırmızı takım raporunu, bir maliyet-defteri csv'sini ve Sakana v2 başarısızlık kiplerinden hangisini yeniden ürettiğinizi ve hafifletmenin nasıl çalıştığını adlandıran bir yazıyı içeren bir depo.
