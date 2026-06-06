# Zihin Kuramı ve Ortaya Çıkan Koordinasyon

> Li ve diğerleri (arXiv:2310.10701), işbirlikçi bir metin oyununda LLM ajanlarının **ortaya çıkan yüksek-dereceli Zihin Kuramını (ToM, Theory of Mind)** sergilediğini — bir ajanın bir diğerinin bir üçüncü ajanın inançları hakkındaki inançları hakkında muhakeme yürüttüğünü — ama bağlam yönetimi ve halüsinasyon nedeniyle uzun-ufuklu planlamada başarısız olduğunu gösterdi. Riedl (arXiv:2510.05174) bir popülasyon boyunca daha yüksek-dereceli sinerjiyi ölçtü ve **yalnızca** ToM-istemi koşulunun kimlik-bağlantılı farklılaşma ve hedef-yönlü tamamlayıcılık ürettiğini buldu; düşük-kapasiteli LLM'ler yalnızca sahte ortaya çıkış gösterir. Yani koordinasyon ortaya çıkışı istem-koşullu ve modele bağımlıdır, bedava değildir. Bu ders minimal bir ToM-farkında ajan uygular, bir işbirlikçi görevi ToM istemiyle ve onsuz çalıştırır ve Riedl 2025 protokolüne karşı koordinasyon farkını ölçer.

**Tip:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Önkoşullar:** Faz 16 · 07 (Zihin Toplumu ve Tartışma), Faz 16 · 17 (Üretken Ajanlar)
**Süre:** ~75 dakika

## Problem

Çok-ajanlı koordinasyon çoğu zaman sihirli görünür: ajanlar iş bölümü yapar, birbirlerini öngörür, fazlalıktan kaçınır. Genellikle bu "ortaya çıkış", istem mühendisliğinin bir yan ürünüdür — birileri ajanlara "koordine olun" demiştir. İstemi kaldırın, koordinasyonu kaldırın.

Riedl'in 2025 bulgusu daha katıdır: kontrollü koşullar altında koordinasyon yalnızca ajanlar **diğer ajanların zihinleri** (ToM) hakkında muhakeme etmeye yönlendirildiğinde ortaya çıkar. ToM istemi olmadan, güçlü modeller bile istatistiksel kontrolleri atlatmayan koordinasyon örüntüleri gösterir. Bu üretim için önemlidir: takımlar, istem-bağımlı ve kırılgan olan "çok-ajanlı koordinasyon" özelliklerini gönderir.

Bu ders ToM'yi belirli bir yetenek (inançlar hakkındaki inançlar hakkında muhakeme) olarak ele alır, minimal bir ToM-farkında ajan inşa eder ve gerçek koordinasyonun neye benzediğini istem süslemesinin neye benzediğini ölçer.

## Kavram

### ToM'nin anlamı

Gelişim psikolojisi: 3 yaşındaki bir çocuk, herkesin iç dünyasının kendisininkiyle aynı olduğunu düşünür. 5 yaşındaki, diğerlerinin farklı inançları olduğunu anlar. 7 yaşındaki, inançlar hakkındaki inançlar hakkında muhakeme yürütür ("o, benim topun bardak altında olduğunu düşündüğümü düşünüyor"). Bunlar sıfırıncı, birinci ve ikinci-derece ToM'dir.

LLM ajanları için ToM dereceleri şunlara eşlenir:

- **Sıfırıncı-derece:** diğerlerinin modeli yok. Ajan yalnızca kendi gözlemlerine göre hareket eder.
- **Birinci-derece:** ajanın her diğer ajanın inançları için bir modeli var. "Alice X'e inanıyor."
- **İkinci-derece:** ajan özyineli inançları modelliyor. "Alice, Bob'un X'e inandığına inanıyor."

Li ve diğerleri 2023, işbirlikçi oyunlarda LLM ajanlarında birinci ve ikinci-derece ToM'nin ortaya çıktığını, ama uzun ufuk ve güvenilmez iletişimle bozulduğunu buldu.

### Sally-Anne testi, kısaca

1985 tarihli yanlış-inanç testi: Sally bir bilyeyi A sepetine koyar, ayrılır. Anne onu B sepetine taşır. Sally döndüğünde nereye bakacak? Birinci-derece ToM'si olan bir çocuk A sepeti der (Sally'nin inancı gerçeklikten farklı). Olmayan B sepeti der.

GPT-4 dönemi LLM'leri Sally-Anne tarzı testleri açıkça sorulduğunda geçer. Anlatı uzun olduğunda, sahne birkaç kez değiştiğinde veya soru dolaylı sorulduğunda başarısız olur. Bu, üretim LLM'lerinde ToM'nin pratik 2026 durumudur.

### Riedl'in koordinasyon ölçümü

Riedl (arXiv:2510.05174) popülasyon-ölçekli bir test kurdu: N ajan, işbirlikçi bir hedef, değişken istem koşulları. Şunları ölçün:

1. **Kimlik-bağlantılı farklılaşma.** Ajanlar zamanla kararlı rol ayrımları geliştiriyor mu?
2. **Hedef-yönlü tamamlayıcılık.** Ajanların eylemleri birbirini tamamlıyor mu (farklı alt görevler) yoksa çoğalıyor mu?
3. **Yüksek-dereceli sinerji.** Grubun herhangi bir alt kümenin başaramayacağını başarıp başaramadığının istatistiksel ölçüsü.

Sonuç: yalnızca ToM istemi koşulunda üç metrik de temel çizginin üzerinde sinyal üretir. ToM istemi olmadan, orta-kapasiteli modeller için metrikler şansa yakın salınır. Büyük modeller açık ToM istemi olmadan bir miktar koordinasyon gösterir, ama etki açık istemle olandan daha küçüktür.

### Koordinasyon illüzyonu

İstatistiksel kontroller olmadan, demoların "emergent koordinasyon"u sıklıkla şunları yansıtır:

- Koordinasyonu içine pişirmiş istem mühendisliği ("birlikte çalışın" diyen sistem istemleri).
- Gözlemci yanlılığı (beklediğimiz örüntüleri görürüz).
- Başarılı koşumların sonradan seçimi (post-hoc selection).

Ölçülebilir sinyal olmadan "emergent koordinasyon" pazarlayan üretim sistemleri pazarlama olarak ele alınmalıdır. İddia etmeden önce ölçün.

### Minimal bir ToM-farkında ajan

Yapı:

```
ajan durumu:
  kendi_inançları:    {ajanın inandığı olgular}
  diğer_modeller:    {diğer_ajan_kimliği -> {ajanın ona atfettiği inançlar}}
  son_N_eylemler:    [diğerlerinin eylemlerinin geçmişi]

gözlem güncelleme:
  - kendi_inançları doğrudan gözlemden güncellenir
  - diğer_modeller[ajan_kimliği] onun eylemi + önceki inançlardan güncellenir

eylem seçimi:
  - aday eylemleri say
  - her biri için, modellenen inançları altında her diğer ajanın ne yapacağını öngör
  - bu öngörüler altında ortak sonucu en üst düzeye çıkaran eylemi seç
```

#### Açıklama
`diğer_modeller` özniteliği ToM durumudur. Birinci-derece ToM yalnızca bir düzey tutar. İkinci-derece `diğer_modeller[i][diğer_modellerin_j]` ekler — benim ajan i'nin ajan j hakkındaki inançlarına dair düşündüğü.

### Neden uzun-ufuk (long-horizon) zorar

Li ve diğerleri belgeler: bağlam sınırları, ajanların hangi inancın kime ait olduğunu unutmasına neden olur. Halüsinasyon, diğer-ajan modellerine yanlış inançlar ekler. İkisi de "onun X'i düşündüğünü sandım" hataları üretir ve zamanla birikir.

Makalede ve 2024-2026 takip çalışmalarında belgelenen hafifletmeler:

- **İstemde açık ToM durumu.** Yapılandırılmış biçim: `{ajan_kimliği: inanç_listesi}`. Geri çağırmayı kimlik-inanç bağını korumaya zorlar.
- **Daha kısa muhakeme zincirleri.** Tur başına daha az ToM güncellemesi, biriken halüsinasyonu azaltır.
- **Dış ToM deposu.** Modeli LLM bağlamının dışında tutun; tur başına yalnızca ilgili kısımları enjekte edin.

### ToM'nin üretimde başarısız olduğu yerler

- **Düşmanca ayarlar.** İyi ToM'si olan ajanlar manipüle edilmesi daha kolaydır (sizin onun sizi nasıl modellediğini modelledikten sonra sömürebilirsiniz).
- **Heterojen takımlar.** Modeller farklı olduğunda, bir muhatap için işe yarayan ToM modeli genelleşmez.
- **Temel-gerçeğe bağımlı görevler.** ToM inançlar hakkındadır; doğruluk olgulara bağlıysa, ToM dikkat dağıtıcı olabilir.

### Gerçekten ölçebileceğiniz koordinasyon

Bir takımın koordinasyonunun istem-süslenmiş yerine gerçek olduğuna dair üç pratik sinyal:

1. **Zaman içinde tamamlayıcılık.** Çok-turlu bir görevde, ajanların eylemleri ayrık alt görevleri kapsıyor mu?
2. **Öngörü.** Ajan A'nın tur T+1'deki eylemi, B'nin tur T+2'deki eylemi hakkındaki doğru çıkan bir öngörüye bağlı mı?
3. **Düzeltme.** A, tur T'de B'nin inancını yanlış okuduğunda, tur T+2'ye kadar düzeltiyor mu?

Bunlar, kaydedilmiş bir multi-agent sistemde ölçülebilirdir. "Koordinasyon" anlatısının maddi versiyonudurlar.

## İnşa Et

`code/main.py` şunları uygular:

- `ToMAgent` — kendi inançlarını ve ajan başına inanç modellerini izler.
- İşbirlikçi bir görev: üç ajan üç kutudan üç jetonu toplamalı; her kutu bir jeton tutabilir. Ajanlar iletişim kuramaz; niyeti birbirlerinin eylemlerinden çıkarır.
- İki konfigürasyon: `zeroth_order` (ToM yok) ve `first_order` (tek-düzeyli inanç modeliyle ToM).
- 200 rastgeleleştirilmiş deneme üzerinden ölçüm: tamamlanma oranı, çoğaltma oranı (aynı kutuya hedeflenen iki ajan), ortalama tamamlanma turu.

Çalıştır:

```
python3 code/main.py
```

#### Açıklama
Beklenen çıktı: sıfırıncı-derece ajanlar ~%35 oranında efor çoğaltır ve denemelerin ~%60'ını 10 turda tamamlar. Birinci-derece ToM ajanları ~%5 çoğaltır ve ~%95 tamamlar. Fark, ölçülebilir koordinasyon etkisidir.

## Kullan

`outputs/skill-tom-auditor.md`, bir multi-agent sisteminin "emergent koordinasyon" iddiasını denetleyen bir beceridir. İstem süslemesi, kontrole karşı istatistiksel anlamlılık ve ölçülen tamamlayıcılık kontrollerini yapar.

## Yayınla

Koordinasyon iddiaları kontrol listesi:

- **Kontrol koşulu.** Sisteminizin koordinasyon istemi olmayan bir sürümü. İkisini de ölçün.
- **İstatistiksel test.** Sistem ve kontrol arasındaki fark, metriğinizde `p < 0.05`'te anlamlı mı?
- **Tamamlayıcılık ölçüsü.** Yalnızca nihai başarı değil, zaman içinde eylem ayrıklığı.
- **Başarısızlık-durumu günlüğü.** Ajanlar koordine olamadığında, ToM durumu nasıl görünür?
- **Model-kapasitesi açıklaması.** Etki daha küçük modellerde kayboluyorsa, söyleyin.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Birinci-derece ToM'nin çoğaltma oranını ~7x azalttığını doğrulayın. 5 ajana ve 5 kutuya ölçeklediğinizde fark sürüyor mu?
2. İkinci-derece ToM uygulayın (ajan A, B'nin C hakkında ne düşündüğünü modelliyor). Birinci-dereceden iyileşiyor mu? Hangi görevlerde?
3. ToM durumuna bir **halüsinasyon** enjekte edin: tur başına rastgele bir inancı çevirin. Bu, birinci-derece performansını ne kadar bozar?
4. Li ve diğerleri (arXiv:2310.10701) okuyun. "Uzun-ufuk bozulması" bulgusunu yeniden üretin: turlar 10'dan 30'a büyüdükçe, birinci-derece ToM performansınız nasıl değişir?
5. Riedl 2025'i (arXiv:2510.05174) okuyun. Simülasyon günlükleriniz üzerinde yüksek-dereceli sinerji istatistiğini uygulayın. ToM istemi koşulu olmadan etki mevcut mu?

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|------|----------------|------------------------|
| Zihin Kuramı | "Diğerlerinin zihinlerini anlama" | Başka bir ajanın inançlarını modelleme kapasitesi. Dereceye göre derecelendirilir (0, 1, 2+). |
| Sally-Anne testi | "Yanlış-inanç testi" | 1985 gelişim psikolojisi; LLM'ler açık versiyonları geçer, karmaşık olanları başarısız olur. |
| Birinci-derece ToM | "A, X'e inanıyor" | Olgular hakkında bir diğerinin inançlarını modelleme. |
| İkinci-derece ToM | "A, B'nin X'e inandığına inanıyor" | Bir düzey daha derin özyineli modelleme. |
| Kimlik-bağlantılı farklılaşma | "Zamanla kararlı roller" | Riedl'in metriği: rastgele değil, roller kalıcıdır. |
| Hedef-yönlü tamamlayıcılık | "Ayrık eylemler" | Ajanlar aynı alt görev yerine farklı alt görevleri hedefler. |
| Yüksek-dereceli sinerji | "Grup herhangi bir alt kümeyi aşar" | Riedl'in gerçek koordinasyon için istatistiksel ölçüsü. |
| Koordinasyon illüzyonu | "Koordine görünüyor" | Ölçülebilir sinyal olmadan istem-süslenmiş koordinasyon görünümü. |

## İleri Okuma

- [Li et al. — Theory of Mind for Multi-Agent Collaboration via Large Language Models](https://arxiv.org/abs/2310.10701) — işbirlikçi oyunlarda emergent ToM; uzun-ufuk başarısızlık kipleri
- [Riedl — Emergent Coordination in Multi-Agent Language Models](https://arxiv.org/abs/2510.05174) — popülasyon-ölçekli ölçüm; ToM istemi yük taşıyan koşuldur
- [Premack & Woodruff — Does the chimpanzee have a theory of mind?](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-chimpanzee-have-a-theory-of-mind/1E96B02CD9850E69AF20F81FA7EB3595) — 1978 ToM kavramının kökeni
- [Baron-Cohen, Leslie, Frith — Does the autistic child have a theory of mind?](https://www.cambridge.org/core/journals/behavioral-and-brain-sciences/article/does-the-autistic-child-have-a-theory-of-mind/) — Sally-Anne makalesi (1985)
