# Zihin Toplumu ve Multi-Agent Tartışma

> Minsky'nin 1986 öncüsü — zeka, uzmanların toplumudur — her on yılda bir yeniden keşfedilir. 2023'te Du ve diğerleri bunu somut bir algoritmaya dönüştürdü: birden fazla LLM örneği yanıt önerir, birbirlerinin yanıtlarını okur, eleştirir ve günceller. N tur boyunca, altı akıl yürütme ve gerçeklik görevinde sıfır-atış CoT ve refleksiyonu yenen bir fikir birliğine varırlar. Önemli iki bulgu: hem **birden fazla agent** hem de **birden fazla tur** bağımsız olarak katkıda bulunur. Toplum, tek-agent monologunu yener; çok turluk değişim, tek atışlık oylamayı yener.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model)
**Süre:** ~60 dakika

## Problem

Öz-tutarlılık (self-consistency) — bir modelden birçok örnek alıp çoğunluk yanıtını almak — ekleyebileceğiniz en ucuz akıl yürütme iyileştirmesidir. İşe yarar, ama hızla doygunluğa ulaşır. Örneklerinizi iki katına çıkarabilirsiniz ve başka anlamlı bir sıçrama görmezsiniz.

Tartışma (debate), doygunluğu kırar. Bir modelden N bağımsız örnek almak yerine, N agent birbirlerinin akıl yürütmesini okur ve revize eder. Örnekler arasındaki korelasyon düşer (artık bağımsız ve özdeş dağılımlı — i.i.d. — değildirler) ve yakınsama noktası, i.i.d. oylamanın kendinden emin şekilde yanlış olduğu yerde sıklıkla doğrudur.

## Kavram

### Du ve diğerleri 2023 algoritması

arXiv:2305.14325'ten (ICML 2024):

1. N agent'ın her biri soruya bir başlangıç yanıtı üretir.
2. Tur r = 2..R için: her agent'a diğer agent'ların r-1 turundaki yanıtları gösterilir ve "bunları göz önünde bulundurarak, güncellenmiş yanıtınızı ver" denir.
3. R turdan sonra, son yanıtları çoğunluk oyuyla toplayın.

Makale MMLU, GSM8K, biyografiler, MATH ve gerçeklik kıyaslamalarında test eder. Tartışma, sürekli olarak CoT ve Öz-Refleksiyonu yener.

### İki bağımsız düğme

Aynı makaleden soyutlamalar:

- **Yalnızca agent sayısı** (1 tur, N çoğunluk oyu) tek-agent'ı çoğu görevde yener, ama plato yapar.
- **Yalnızca tur sayısı** (1 agent kendi önceki akıl yürütmesini görür) neredeyse yardımcı olmaz — refleksiyonun bilinen zayıflığı.
- **İkisi birlikte** büyük sıçramaları üretir. Birden fazla agent arasındaki çok turluk değişim kazancı sağlar.

### Neden işe yarar

İki mekanizma:

1. **Anlaşmazlığa maruz kalma.** Bir agent, farklı bir sonuca varan başka bir agent'ın akıl yürütme zincirini gördüğünde, ya gerekçelendirmeli ya da güncellemelidir. Her iki durumda da, r+1 turu için bağlam r turundan daha zengindir.
2. **İlintili hata azaltma.** Öz-tutarlılıkta, tüm örnekler aynı modelden gelir, böylece hatalar ilintilidir — kendinden emin şekilde yanlış bir yanıta ortalamasınız. Farklı modeller veya farklı seed'ler ilişkiyi kaldırır. Farklı *tartışılan görüşler* ilişkiyi daha da kaldırır.

### Heterojen tartışma

A-HMAD ve ilgili takip çalışmaları, farklı agent'lar için *farklı temel modeller* kullanır. Llama + Claude + GPT'nin tartışması, monokültür çöküşünü (Ders 26) azaltır çünkü bir model ailesinin ilintili hataları diğerleri tarafından paylaşılmaz.

Dezavantaj: bir tartışmaya katılan zayıf bir model, fikir birliğini yanlış yanıtına doğru sürükleyebilir (bkz. "Should we be going MAD?", arXiv:2311.17371).

### NLSOM — 129-agent uzantısı

Zhuge ve diğerleri ("Mindstorms in Natural Language-Based Societies of Mind", arXiv:2305.17066) bu fikri 129 üyeli toplumlara ölçeklendirdi. Sonuç: ölçekle birlikte uzmanlaşma ve kendi kendine organizasyon ortaya çıkar ve sistem, görsel soru yanıtlama gibi görevlerde tek-agent'ı aşar.

### Başarısızlık modları

- **Sycophancy cascade (Dalkavukluk basamağı).** Tüm agent'lar en kendinden emin görünen agent'a boyun eğer. Tartışma en yüksek sesli sese çöker. Karşıt roller için prompting ("bir agent karşı konumu savunmalıdır") yardımcı olur.
- **Konu sürüklenmesi.** Birçok tur boyunca tartışmalar orijinal sorudan uzaklaşır. Hafifletme: soruyu her turda yeniden enjekte edin.
- **Hesaplama patlaması.** N agent × R tur = N·R LLM çağrısı, her biri büyüyen bir bağlamla. 5 agent'lı, 5 turluk bir tartışma, büyüyen bağlamda 25 çağrıdır. Soru başına maliyet, tek bir CoT çağrısının 10 katını aşabilir.

## İnşa Et

`code/main.py`, her agent'ın farklı (muhtemelen yanlış) bir yanıtla başladığı bir matematik sorusu üzerinde 3-agent × 3-tur tartışma çalıştırır. Agent'lar komut dosyası olarak yazılmıştır — her biri komut dosyası bir güvene göre komşuların yanıtlarını ağırlıklı ortalamasını alarak "günceller". Yakınsama, tur tur günlükte görünür.

Demo iki temel etkiyi gösterir:

- Tek bir değişim turu, agent'ları doğru yanıta yaklaştırır.
- 2. turdan sonraki ekstra turlar azalan getiriler gösterir (Du ve diğerlerinin platosuyla eşleşir).

Çalıştırın:

```
python3 code/main.py
```

## Kullan

`outputs/skill-debate-configurator.md`, yeni bir görev için bir tartışma yapılandırır: agent sayısı, tur sayısı, heterojenlik (aynı modele karşı karışık), rol ataması (simetrik ve karşıt bir slot karşıt). Çalıştırmadan önce token maliyetini de tahmin eder.

## Dağıt

Tartışma dağıtıyorsanız:

- **Turları 3 ile sınırlayın.** Du ve diğerleri, 3 turun kazancın çoğunu yakaladığını gösteriyor. Daha fazlası maliyet, kalite değil.
- **Agent'ları 5 ile sınırlayın.** 5'in ötesinde, bağlam şişmesi ve maliyet baskın olur.
- **Varsayılan olarak heterojen.** Havuzda en az iki farklı temel model.
- **Karşıt slot.** Bir agent, ne olursa olsun anlaşmazlık için promptlanır. Dalkavukluğu kırar.
- **Her turu günlüğe kaydedin.** Ara turları gizleyen tartışma sistemleri hata ayıklanamaz veya denetlenemez.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın, ardından tur sayısını 5'e ayarlayın ve azalan getirileri izleyin. Hangi turda ek yakınsama durur?
2. Her zaman mevcut çoğunlukla anlaşmayan karşıt bir role sahip dördüncü bir agent ekleyin. Bu yakınsamayı kırar mı yoksa iyileştirir mi?
3. Tur başına anlaşma puanını (çoğunluk yanıtındaki agent'ların oranı) çizin (yazdırın). Ne zaman 1.0'a ulaşır ve bu "doğru" ile eşdeğer midir?
4. Du ve diğerleri Bölüm 4 soyutlamalarını okuyun. Bu kodu kullanarak "yalnızca agent'lar"a karşı "yalnızca turlar"a karşı "ikisi de" sonucunu çoğaltın.
5. "Should we be going MAD?" (arXiv:2311.17371) okuyun ve round-robin ötesinde iki tartışma varyantını listeleyin — örn. yargıç-yönetimli, zincir-tartışma, karşıt.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Society of Mind (Zihin Toplumu) | "Minsky'nin fikri" | Etkileşen uzmanlar olarak zeka; 1986 çerçevelemesi artık LLM tartışması yoluyla operasyonel hale getirildi. |
| Multi-agent debate (Multi-agent tartışma) | "Agent'lar tartışır" | N agent önerir, birbirlerini eleştirir, R tur boyunca revize eder, çoğunluk oyu verir. |
| Consensus (Fikir birliği) | "Anlaşıyorlar" | Epistemik gerçek değil — yalnızca çoğunluk-yanıtında-oran. Kendinden emin şekilde yanlış olabilir. |
| Rounds (Turlar) | "Değişim adımları" | Bir tur = her agent diğerlerini okur ve bir kez günceller. |
| Heterogeneous debate (Heterojen tartışma) | "Model ailelerini karıştır" | Hataların ilişkisini kaldırmak için farklı temel modeller kullanmak. |
| Sycophancy cascade (Dalkavukluk basamağı) | "Herkes en yüksek sesliyle anlaşır" | Agent'ların doğruluktan bağımsız olarak en kendinden emin agent'a boyun eğdiği tartışma başarısızlığı. |
| NLSOM | "129-agent toplumu" | Doğal dil zihin toplumu; Zhuge ve diğerlerinin ölçeklendirilmiş sürümü. |
| Correlated error (İlintili hata) | "Aynı model, aynı hata" | Öz-tutarlılığın neden doygunluğa ulaştığı; farklı görüşler arası tartışma ilişkiyi kaldırır. |

## İleri Okuma

- [Du ve diğerleri — Improving Factuality and Reasoning in Language Models through Multiagent Debate](https://arxiv.org/abs/2305.14325) — referans makale, ICML 2024
- [Zhuge ve diğerleri — Mindstorms in Natural Language-Based Societies of Mind](https://arxiv.org/abs/2305.17066) — 129-agent NLSOM
- [Should we be going MAD? A Look at Multi-Agent Debate Strategies for LLMs](https://arxiv.org/abs/2311.17371) — tartışma varyantlarını kıyaslar
- [Debate proje sayfası](https://composable-models.github.io/llm_debate/) — Du ve diğerlerinin kodu, demoları ve soyutlama detayları
