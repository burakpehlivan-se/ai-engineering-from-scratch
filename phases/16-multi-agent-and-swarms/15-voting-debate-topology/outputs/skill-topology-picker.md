---
name: topology-picker
description: Belirli bir görev için çok-agent'lı bir tartışma topolojisi (yıldız / zincir / ağaç / grafik), bir agent sayısı, bir heterojenlik profili ve bir tur sınırı seçin.
version: 1.0.0
phase: 16
lesson: 15
tags: [multi-agent, debate, topology, voting, self-consistency]
---

Bir görev tanımı verildiğinde, bir çok-agent'lı topoloji ve boyutlandırma önerin.

Üretin:

1. **Görev parmak izi.** Araştırma (uzun-horizon, açık-uçlu), hızlı-gerçek (kapalı-form yanıt), aşamalı-iyileştirme (aşamalı pipeline) veya görüş (ground truth yok). Birini seçin; ikisini kapsıyorsa, baskın şekli seçin.
2. **Topoloji.** Yıldız, zincir, ağaç veya grafik. Parmak izinden gerekçelendirin:
 - araştırma → grafik (herhangi birinden-herhangi birine eleştiri)
 - hızlı-gerçek → yıldız (hub toplar)
 - aşamalı-iyileştirme → zincir (veya böl-ve-yönet ise ağaç)
 - görüş → yukarıdakilerin hiçbiri; tek agent + insan kararı önerin
3. **Agent sayısı.** 3 en ucuz yararlı topluluk; 5 yaygın tatlı nokta; 7+ uzmanlık. Grafik topolojisinde 5'in üzerinde, koordinasyon vergisi konusunda uyarın.
4. **Heterojenlik profili.** Tek-tür önemliyse (araştırma, akıl-yürütme) en az bir agent farklı bir temel model ailesinden gelmelidir. N=5'te 3 farklı temel modeli tercih edin.
5. **Tur sınırı.** 1 tur = oy. 2 tur = bir iyileştirme. 3 tur = uyum baskın olmadan önce maksimum. Asla sınırsız.
6. **Birleştirme.** Çoğunluk (ucuz), güven-ağırlıklı (Ders 14'ten CP-WBFT), geometrik medyan (DecentLLMs) veya hakem-puanlı. Maliyet kısıtları çoğunluğu zorunlu kılmadıkça, varsayılan olarak güven-ağırlıklı.
7. **Çıkış.** Eşik-altı fikir birliği → nereye çıkarsınız? İnsan, farklı temel modellerle başka bir topluluk veya çekimserlik?

Keskin redler:

- Grafik topolojisinde 10+ agent önerisi. Koordinasyon vergisi baskındır; önce ölçün.
- Açık araştırma soruları için yıldız topolojisi. Yıldız, herhangi-birinden-herhangi-birine eleştiri avantajını kaybeder.
- Aynı temel modeli N kez çalıştırıp buna çok-agent'lı diyen herhangi bir öneri. Bu gizlenmiş öz-tutarlılıktır; doğru etiketleyin.
- Sınırsız turlar. Uyumu ödüllendirir; tartışma ne kadar uzun sürerse, agent'lar mantık yerine baskıyla o kadar çok anlaşır.

Ret kuralları:

- Görevin ground truth'u yoksa (görüş, sentez, yaratıcı), oylamanın danışman olduğunu belirtin. Tek agent + insan kararı önerin.
- Kullanıcının birden fazla temel modele erişimi yoksa, tek-tür tavanını işaretleyin ve sıcaklık varyasyonuyla öz-tutarlılığı geri-dönüş olarak önerin.
- Görev basitse (tek gerçek arama, 100 token'ın altında akıl-yürütme), N=5 öz-tutarlılığıyla tek agent önerin.

Çıktı: Tek sayfalık özet. Tek cümlelik bir öneriyle başlayın ("Grafik topolojisi, 3 farklı temel modelden N=5 agent, 2 tur, güven-ağırlıklı birleştirme, eşik-altında insana çıkış."), sonra yukarıdaki yedi bölüm. Bütçe tahminiyle bitirin: sorgu başına beklenen token ve saniye cinsinden beklenen gecikme.
