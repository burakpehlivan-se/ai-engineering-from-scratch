# Hiyerarşik Mimari ve Başarısızlık Modu

> Hiyerarşik, iç içe supervisor'dır. Alt yöneticilerin üzerindeki yönetici agent'ları, işçilerin üzerindeki alt yöneticiler. CrewAI `Process.hierarchical` ders kitabı sürümüdür: bir `manager_llm` görevleri dinamik olarak devreder ve çıktıları doğrular. LangGraph eşdeğeri `create_supervisor(create_supervisor(...))` şeklindedir. Görev gerçek bir org şeması olduğunda doğal kalıptır. Aynı zamanda yönetsel döngüye (managerial looping) çökme olasılığı en yüksek olan kalıptır — yönetici agent'ları işi kötü atar, alt çıktıları yanlış yorumlar veya fikir birliğine varamaz. Sıralı (sequential) çoğu zaman onu yener.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 05 (Supervisor Kalıbı)
**Süre:** ~60 dakika

## Problem

Supervisor kalıbı bir kez oturduğunda, doğal sonraki adım "işçilerin kendileri supervisor olsaydı?"dır. Takımların alt takımları vardır; şirketlerin departmanların departmanları vardır. Hiyerarşik mimariler bunu yansıtır.

Sorun şu: LLM yöneticileri insan yöneticileriyle aynı değildir. İnsan yöneticisinin raporlarının ne bildiğine dair kararlı öncelikleri (priors) vardır. Bir LLM yöneticisi, bağlamında ne varsa ondan her turda organizasyonu yeniden akıl yürütür. O bağlamdaki küçük bir sürüklenme ve tüm ağaç işi yanlış dağıtır.

## Kavram

### Şekil

```
                 Yönetici
                 ┌─────┐
                 └──┬──┘
           ┌────────┴────────┐
           ▼                 ▼
       Alt-Yön. A        Alt-Yön. B
       ┌─────┐           ┌─────┐
       └──┬──┘           └──┬──┘
         ┌┴──┬──┐          ┌┴──┐
         ▼   ▼  ▼          ▼   ▼
       W1  W2  W3         W4  W5
```

Her iç düğüm planlar, devreder ve sentezler. Yalnızca yapraklar iş yapar.

### Nerede parlar

- **Net organizasyon eşlemesi.** Gerçek görev departmanlara ayrılmışsa ("belgeyi hukuk incelesin, finans incelesin, mühendislik incelesin, sonra yönetim için özetlensin"), hiyerarşi açıktır.
- **Yerel özetleme.** Her alt yönetici, üst yönetici onu görmeden önce takımının çıktısını sentezler. Üst yönetici on beş işçi çıktısı değil, üç alt yönetici özeti görür.

### Nerede kırılır

2026 post-mortemlerinin bulmaya devam ettiği üç başarısızlık modu:

1. **Görev atama hatası.** Yönetici hedefi okur, bir ayrıştırma halüsinasyonu yapar ve yanlış alt yöneticiye devreder. Alt yönetici, verilene itaat ederek çalıştığı için, hata yalnızca en üstteki sentezde, bir insanın yakalayabileceği seviyeden bir kademe uzakta ortaya çıkar.
2. **Çıktı yanlış yorumlama.** Alt yönetici, "iddia X doğrulanamadı" döner. Üst yönetici, "iddia X teyit edilmedi" olarak özetler. Anlam her seviyede sürüklenir.
3. **Fikir birliği döngüleri.** İki alt yönetici anlaşamaz; üst yönetici uzlaşmalarını ister; yeniden aşağı devreder; işçiler yeniden çalışır; alt yöneticiler biraz farklı yanıtlar döner; döngü. CrewAI'nin `Process.hierarchical`'i bunu adım limitleriyle korur, ancak limitin kendisi artık bir hiperparametredir.

### Karar veren soru

Sıralı (doğrusal pipeline) veya hiyerarşik: göreviniz gerçekten bağımsız alt takımlara mı sahip, yoksa ağaç gibi görünen tek bir doğrusal akış mı? Eğer ikincisiyse, sıralı kullanın. Eğer birincisiyse, hiyerarşik kullanın ama açık uzlaştırma kuralları bütçeleyin.

### CrewAI'nin uygulaması

`Process.hierarchical`, uzman ekiplerin üzerine bir yönetici LLM bağlar. Yönetici:

- en üst düzey görevi alır,
- alt görevleri ekiplere atar,
- ekip çıktılarını değerlendirir,
- kabul etme, yeniden devretme veya yineleme kararı verir.

Belgelendirme: https://docs.crewai.com/en/introduction ("Hiyerarşik Süreç"ü Temel Kavramlar altında arayın).

### LangGraph'ın uygulaması

LangGraph, iç içe `create_supervisor` çağrıları kullanır. İç supervisor'ın kendi grafı vardır; dış supervisor, iç grafiği opak bir düğüm olarak ele alır. Bu, CrewAI'den hata ayıklama için daha temizdir (her grafiği ayrı ayrı adımlayabilirsiniz), ancak ağacın dinamik yeniden şekillenmesini ifade etmek daha zordur.

Referans: https://reference.langchain.com/python/langgraph-supervisor.

## İnşa Et

`code/main.py` 3 seviyeli bir hiyerarşi çalıştırır:

- üst yönetici: bir görevi "mühendislik" ve "hukuk" dallarına böler,
- mühendislik alt yöneticisi: "ön yüz" ve "arka yüz" işçilerine böler,
- hukuk alt yöneticisi: bir işçi.

Demo, mutlu yolu (herkes anlaşır) **pertürbe edilmiş yola** karşı kontrastlandırır; burada üst yöneticinin ayrıştırması "hukuk"u "finans" olarak yanlış etiketler ve hatanın basamaklanmasını izler — alt yönetici itaatle finans işi yapar, üst sentezleyici finans bulgularını bildirir, orijinal hukuk sorusu yanıtsız kalır.

Çalıştırın:

```
python3 code/main.py
```

Çıktı, "ne istendi" ile "ne teslim edildi"nin net bir yan yana karşılaştırmasıyla her iki yolu da gösterir.

## Kullan

`outputs/skill-hierarchy-fitness.md`, belirli bir görevin hiyerarşik mi, sıralı mı yoksa düz supervisor mı kullanması gerektiğini değerlendirir. Girdiler: görev açıklaması, organizasyon yapısı, uzlaştırma bütçesi. Çıktı: korunması gereken belirli başarısızlık modlarıyla birlikte kalıp önerisi.

## Dağıt

Hiyerarşik dağıtıyorsanız:

- **Ağaç derinliğini 2 ile sınırlayın.** Üç seviye zaten çoğu hatayı gözlemlenebilirlikten gizler.
- **Açık uzlaştırma bütçesi.** Üst yöneticinin taahhüt etmesi gerekmeden önce maksimum tur sayısını ayarlayın. Genellikle 2.
- **Her sentezde kaynak (provenance) takibi.** Her düğümün özeti, onu üreten yaprak çıktılarını alıntılamalıdır.
- **Ayrıştırma sürüklenmesinde alarm.** Yöneticinin adım başına ayrıştırmasını günlüğe kaydedin; kullanıcı sorgusuna karşı diff'leyin. Ayrıştırma artık sorguyu kapsamıyorsa, alarm verin.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın ve mutlu ile pertürbe edilmişi karşılaştırın. Üst çıktı, kullanıcının sorusundan tamamen saptığında kaç yönetici devri gerekir?
2. Üçüncü bir seviye ekleyin (üst → alt → alt-alt → işçi). Pertürbe edilmiş yolun kendini ne sıklıkla düzelttiğini ve derinlik büyüdükçe tamamen ne sıklıkta saptığını ölçün.
3. Her alt yöneticide, orijinal kullanıcı sorusu değiştirilmeden her zaman sorulan bir "kanarya" işçisi uygulayın. Ayrıştırma sürüklenmesini tespit etmek için kanarya yanıtını kullanın. Kanarya, sentezlenen yanıtla anlaşamazsa yönetici nasıl tepki vermelidir?
4. CrewAI'nin `Process.hierarchical` belgelerini okuyun. CrewAI'nin uyguladığı somut bir koruma önlemini (adım sınırı, manager_llm kısıtlaması) tanımlayın ve hangi başarısızlık modunu hedeflediğini açıklayın.
5. İç içe LangGraph supervisor'ları, CrewAI hiyerarşik ile karşılaştırın. Hangisi uzlaştırma döngülerini tespit etmeyi daha ucuz hale getirir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Hierarchical (Hiyerarşik) | "Organizasyon şeması kalıbı" | Supervisor'ların üzerindeki supervisor'lar; yalnızca yapraklar iş yapar. |
| Manager LLM | "Patron" | Bir iç düğümde ayrıştırma, atama ve doğrulama yapan LLM. |
| Decomposition drift (Ayrıştırma sürüklenmesi) | "Patron konuyu kaybetti" | Üst yöneticinin bölünmesi artık orijinal soruyu kapsamıyor. |
| Reconciliation loop (Uzlaştırma döngüsü) | "Sonsuz toplantılar" | Alt yöneticiler anlaşamıyor; üst yeniden devreder; işçiler yeniden çalışır; bütçe tükenene kadar döngü. |
| Depth-2 ceiling (Derinlik-2 tavanı) | "2 seviyeden derine inme" | Ampirik koruma: 3+ seviye gözlemlenebilirliği çöker. |
| Canary question (Kanarya sorusu) | "Her seviyede temel gerçek" | Orijinal sorgu değiştirilmedis sorulan, sürüklenmeyi tespit eden bir işçi. |
| Provenance chain (Kaynak zinciri) | "Kim ne söyledi" | Her sentezden, onu üreten yaprak çıktılarına geri iz. |

## İleri Okuma

- [CrewAI tanıtımı — Process.hierarchical](https://docs.crewai.com/en/introduction) — yönetici LLM ile ders kitabı hiyerarşik
- [LangGraph supervisor referansı](https://reference.langchain.com/python/langgraph-supervisor) — `create_supervisor` ile iç içe supervisor
- [Anthropic mühendislik — Research sistemi](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic'in neden bilinçli olarak hiyerarşik yerine düz supervisor seçtiği
- [Cemri ve diğerleri — Multi-Agent LLM Sistemleri Neden Başarısız Olur?](https://arxiv.org/abs/2503.13657) — MAST taksonomisi; koordinasyon başarısızlıkları bölümü ayrıştırma sürüklenmesini belgeler
