# OpenAI Hazırlık Çerçevesi ve DeepMind Sınır Güvenlik Çerçevesi

> OpenAI Hazırlık Çerçevesi v2 (Nisan 2025), İzlenen Kategorilerden (Tracked Categories) ayrılan Araştırma Kategorileri (Research Categories) tanıtır — Uzun Vadeli Otonomi (Long-range Autonomy), Kuma Oturtma (Sandbagging), Otonom Üreme ve Uyum (Autonomous Replication and Adaptation), Güvenlik Önlemlerini Baltalama (Undermining Safeguards). İzlenen Kategoriler, Güvenlik Danışma Grubu (Safety Advisory Group) tarafından incelenen Yetenek Raporları (Capabilities Reports) artı Güvenlik Önlemleri Raporlarını (Safeguards Reports) tetikler. DeepMind'ın FSF v3'ü (Eylül 2025; İzlenen Yetenek Düzeyleri 17 Nisan 2026'da eklendi), otonomiyi ML R&D ve Siber alanlara dahil eder (ML R&D otonomi düzeyi 1 = AI R&D hattını insan + AI araçlarına karşı rekabetçi maliyetle tamamen otomatikleştirmek). FSF v3, araçsal akıl yürütme (instrumental reasoning) kötüye kullanımı için otomatik izleme yoluyla aldatmacalı uyumluluğu (deceptive alignment) açıkça ele alır. Dürüst not: PF v2'deki Araştırma Kategorileri (Uzun Vadeli Otonomi dahil) otomatik olarak azaltmaları tetiklemez; politika dili "potansiyel"dir. DeepMind'ın kendisi, araçsal akıl yürütme güçlenirse otomatik izlemenin "uzun vadede yeterli kalmayacağını" söyler.

**Tür:** Öğrenme
**Diller:** Python (stdlib, üç çerçeve karar tablosu fark aracı)
**Önkoşullar:** Faz 15 · 19 (Anthropic RSP)
**Süre:** ~45 dakika

## Sorun

Ders 19 Anthropic'ın ölçekleme politikasını dikkatle okudu. Bu ders tabloyu OpenAI ve DeepMind'ınkileri okuyarak tamamlar. Üç belge, aynı soruyu ele alan kardeş eserlerdir — bir sınır laboratuarı ne zaman bir modeli durdurmalı veya kapamalı — ve küçük bir kategori kümesinde birleşir, önemli olan belirli yerlerde ayrışır.

Birleşme: üçü de uzun vadeli otonomiyi izlenmeye değer bir yetenek sınıfı olarak etiketler. Üçü de aldatmacalı davranışı (uyumluluk taklidi (alignment faking), kuma oturtma) belirli bir risk sınıfı olarak kabul eder. Üçünün de iç bir inceleme kurumu vardır. Ayrışma: OpenAI kategorileri "İzlenen" (zorunlu azaltma) ve "Araştırma" (otomatik tetikleme yok) olarak böler. DeepMind otonomiyi ayrı olarak adlandırmak yerine iki alana dahil eder. Laboratuar adları İzlenen vs Araştırma, Kritik vs Orta, veya Düzey-1 vs Düzey-2'dir; bir yeteneğin hangi kutuya yerleştirilmesinin operasyonel sonucu laboratuvarlar arasında farklıdır.

Onları birlikte okumak yararlı egzersizdir. Aynı yetenek, Anthropic'ta "zorunlu azaltma", OpenAI'da "izlenen ama tetiklemeyen" ve DeepMind'da "belirli bir alanda izlenen" olabilir. Politika duruşu önemlidir.

## Kavram

### OpenAI Hazırlık Çerçevesi v2 (Nisan 2025)

Yapı:

- **İzlenen Kategoriler:** Yetenek Raporlarını (modelin ne yapabildiği) ve Güvenlik Önlemleri Raporlarını (hangi azaltmaların yerinde olduğu) tetikler. Dağıtımdan önce Güvenlik Danışma Grubu tarafından incelenir.
- **Araştırma Kategorileri:** laboratuvarın izlediği ancak henüz belirli azaltmalara taahhütte bulunmadığı model yetenekleri. Uzun Vadeli Otonomi, Kuma Oturtma, Otonom Üreme ve Uyum, Güvenlik Önlemlerini Baltalama dahildir.

v2'deki temel çerçeve: Araştırma Kategorileri otomatik olarak azaltmaları tetiklemez. Politika dili "potansiyel" azaltmalardır. Bu, izlenmesi gereken belirli farktır: bir kategorinin İzlenen vs Araştırma'daki konumu "kapalı" ile "gözlenen" arasındakierruptedir.

### DeepMind Sınır Güvenlik Çerçevesi v3 (Eylül 2025; İzlenen Yetenek Düzeyleri 17 Nisan 2026'da eklendi)

Yapı:

- **Kritik Yetenek Düzeyleri (CCLs):** beş alanda yetenek eşikleri: Siber, Biyo, ML R&D, CBRN, Otonomi (ML R&D ve Siber'a dahil edildi).
- **İzlenen Yetenek Düzeyleri:** Nisan 2026'da eklenen ekstra ayrıntı. Somut örnek: ML R&D otonomi düzeyi 1 = AI R&D hattını insan + AI araçlarına karşı rekabetçi maliyetle tamamen otomatikleştirmek.
- **Aldatmacalı uyumluluk izlemesi:** araçsal akıl yürütme kötüye kullanımı için otomatik izleme taahhüdü.

Otonomi çerçevelemesi OpenAI'ınkinden farklıdır. DeepMind "Otonomiyi" üst düzey bir alan olarak tutmaz; otonominin zarar vereceği alanlara (ML R&D ve Siber) dahil edilir. Argüman, alan olmadan otonominin risksiz bir yetenek olduğudur; karşıt argüman, alanlar arası otonominin çerçevenin adlandırması gereken bir meta-risk olduğudur.

### Üçünün birleştiği yerler

- İç Güvenlik Danışma Grubu (Anthropic SAG, OpenAI SAG, DeepMind iç komitesi olarak adlandırılır). Yüksek yetenekli modeller için dağıtımdan önce inceleme.
- Aldatmacalı uyumluluk / uyumluluk taklidinin risk sınıfı olarak açıkça anılması.
- İlan edilmiş bir ritimle sürekli eserler (Anthropic: Sınır Güvenlik Yol Haritası, Risk Raporu; OpenAI: Yetenek ve Güvenlik Önlemleri Raporları; DeepMind: FSF güncelleme döngüsü).
- Sadece izleme savunmalarının bir tavanı olduğunu kabul etme. DeepMind açıktır: "otomatik izleme uzun vadede yeterli kalmayacak."

### Nerede ayrışırlar

- **Anthropic:** v3.0'da durma taahhüdü kaldırıldı; AI R&D-4 eşiği adlandırılmış bir sonraki kapı.
- **OpenAI:** İzlenen vs Araştırma ayrımı; Araştırma Kategorileri (Uzun Vadeli Otonomi dahil) otomatik olarak kapamaz.
- **DeepMind:** otonomi diğer alanlara dahil edildi; İzlenen Yetenek Düzeyleri Nisan 2026'da ayrıntı ekler.

### Kuma Oturtma: üçünü de karmaşıklaştıran belirli bir yetenek

Kuma oturtma (sandbagging) (bir modelin değerlendirmelerde stratejik olarak düşük performans sergilemesi), OpenAI'ın Araştırma Kategorilerindedir. Anthropic RSP v3.0 bunu değerlendirme-bağlam boşluğu (eval-context gap) üzerinden ele alır (Ders 1). DeepMind FSF v3'te aldatmacalı uyumluluk izlemesi yoluyla ele alır.

Bir model değerlendirmelerde kuma oturtursa, her çerçeveninyetenek eşikleri低估lanır. Çerçeve ancak ölçüm çalışıyorsa çalışır. Bu yüzden bağımsız ölçüm (Ders 21, METR) ve düşmanca değerlendirme, laboratuvar öz-değerlendirmesinin yanı sıra gereklidir.

### Politika okuma becerisi

- Konumlandır: ilgilendiğiniz her yetenek politikada bulunabilir olmalıdır. Bulunamıyorsa politika onu kapsamaz.
- Sınıflandır: İzlenen (azaltmayı tetikler) mi yoksa Araştırma (izleniyor ama tetiklemiyor) mu? OpenAI buna isim verir; Anthropic ve DeepMind'ın kendi eşdeğerleri vardır.
- Ritim: politika ilan edilmiş bir programda mı yoksa sadece belirli olaylardan sonra mı güncellenir? İlan edilmiş ritim daha güçlüdür.
- Bağımsızlık: dış inceleme zorunlu mu yoksa opsiyonel mi? Anthropic Apollo ve US AI Safety Institute ile; OpenAI METR ile; DeepMind ağırlıklı olarak iç SAG ile ortaklık yapar.

## Kullan

`code/main.py`, küçük bir karar tablosu fark aracı uygular. Bir yetenek verildiğinde (otonomi, aldatmacalı uyumluluk, R&D otomasyonu, siber yükselme vb.), üç politikanın her birinin yeteneği nasıl sınıflandırdığını ve hangi azaltmaların tetiklendiğini çıktı olarak verir. Okuma yardımıdır, politika aracı değil.

## Üret

`outputs/skill-cross-policy-diff.md`, üç çerçeveyi referans olarak kullanarak belirli bir yetenek için çapraz-politika karşılaştırması üretir.

## Alıştırmalar

1. `code/main.py` çalıştırın. Fark aracının çıktısının, kaynak belgelerle doğrulayabileceğiniz en az iki yetenekle politikalarla eşleştiğini doğrulayın.

2. OpenAI Hazırlık Çerçevesi v2'yi tam olarak okuyun. Her Araştırma Kategorisini belirleyin. Her biri için, neden Araştırma'da İzlenen olmadığını tek bir cümle yazın.

3. DeepMind FSF v3'ü tam olarak okuyun, ayrıca Nisan 2026 İzlenen Yetenek Düzeyleri güncellemesini. ML R&D otonomi düzeyi 1'in belirli değerlendirme kriterlerini belirleyin. Bunu dışarıdan nasıl ölçersiniz?

4. Kuma oturtma OpenAI'ın Araştırma Kategorilerindedir. Kuma oturtan bir modeli asıl yeteneğini göstermeye zorlayacak bir değerlendirme tasarlayın. Ders 1 değerlendirme-bağlam oyunu tartışmasına atıfta bulunun.

5. Üç politikayı belirli bir yetenek üzerinde karşılaştırın (siz seçin). Hangi politikanın sınıflandırmasını daha titiz bulduğunuzu ve hangisini daha az titiz bulduğunuzu adlandırın. Kaynak metinle gerekçelendirin.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Preparedness Framework (Hazırlık Çerçevesi) | "OpenAI'ın ölçekleme politikası" | PF v2 (Nisan 2025); İzlenen vs Araştırma kategorileri |
| Tracked Category (İzlenen Kategori) | "Zorunlu azaltma" | Yetenek + Güvenlik Önlemleri Raporlarını tetikler; SAG incelemesi |
| Research Category (Araştırma Kategorisi) | "Sadece izlenen" | İzleniyor ama otomatik azaltma yok; Uzun Vadeli Otonomi dahil |
| Frontier Safety Framework (Sınır Güvenlik Çerçevesi) | "DeepMind'ın ölçekleme politikası" | FSF v3 (Eylül 2025) + İzlenen Yetenek Düzeyleri (Nisan 2026) |
| CCL | "Kritik Yetenek Düzeyi" | DeepMind alanı başına eşik (Siber, Biyo, ML R&D, CBRN) |
| ML R&D autonomy level 1 | "R&D otomasyonu" | AI R&D hattını rekabetçi maliyetle tamamen otomatikleştirmek |
| Sandbagging (Kuma oturtma) | "Stratejik düşük performans" | Model değerlendirmelerde düşük performans gösterir; OpenAI Araştırma Kategorilerinde |
| Instrumental reasoning (Araçsal akıl yürütme) | "Amaçlar-arası akıl yürütme" | Hedeflere nasıl ulaşılacağına ilişkin akıl yürütme; DeepMind izlemesinin hedefi |

## İleri Okuma

- [OpenAI — Hazırlık Çerçevelerimizi Güncelleme](https://openai.com/index/updating-our-preparedness-framework/) — v2 duyurusu.
- [OpenAI — Hazırlık Çerçevesi v2 PDF](https://cdn.openai.com/pdf/18a02b5d-6b67-4cec-ab64-68cdfbddebcd/preparedness-framework-v2.pdf) — tam belge.
- [DeepMind — Sınır Güvenlik Çerçevelerimizi Güçlendirme](https://deepmind.google/blog/strengthening-our-frontier-safety-framework/) — FSF v3 duyurusu.
- [DeepMind — Sınır Güvenlik Çerçevesini Güncelleme (Nisan 2026)](https://deepmind.google/blog/updating-the-frontier-safety-framework/) — İzlenen Yetenek Düzeyleri eklentisi.
- [Gemini 3 Pro FSF Raporu](https://storage.googleapis.com/deepmind-media/gemini/gemini_3_pro_fsf_report.pdf) — FSF biçiminde bir Risk Raporu örneği.
