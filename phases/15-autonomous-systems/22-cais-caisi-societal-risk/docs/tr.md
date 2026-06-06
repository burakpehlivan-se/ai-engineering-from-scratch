# CAIS, CAISI ve Toplumsal Ölçek Risk

> Yapay Zeka Güvenliği Merkezi (CAIS, San Francisco, Hendrycks ve Zhang tarafından 2022'de kuruldu), dört risk çerçevesini — kötüye kullanım (malicious use), AI yarışları (AI races), örgütsel riskler (organizational risks), başıboş AI'lar (rogue AIs) — ve 2023 Mayıs'ında yüzlerce profesyonel ve şirket lideri tarafından imzalanan tüy riski (extinction risk) beyanını yayınlar. CAIS'in 2026 çıktıları: sınırlı-model değerlendirmesi için AI Dashboard, Uzaktan İş İndeksi (Remote Labor Index, Scale AI ile birlikte), Süperzeka Strateji Belgesi, AI Frontiers bülteni. Farklı bir varlık: NIST Yapay Zeka Standartları ve Yenilik Merkezi (CAISI) — ABD hükümeti odaklı gönüllü anlaşmalar ve siber, biyo ve kimyasal silah risklerine odaklanan sınıflanmamış yetenek değerlendirmeleri. CAIS, dört üst düzey riskten biri olarak örgütsel riski işaretler: güvenlik kültürü, titiz denetimler, çok katmanlı savunmalar ve bilgi güvenliği temeldir ancak hızla dağıtım hızına karşı takas edilir. California SB-53, imzalanırsa, ABD'deki ilk eyalet düzeyinde felaket riski düzenlemesi olur.

**Tür:** Öğrenme
**Diller:** Python (stdlib, dört risk envanteri ve azaltma eşleştirici)
**Önkoşullar:** Faz 15 · 19 (RSP), Faz 15 · 20 (PF + FSF)
**Süre:** ~45 dakika

## Sorun

Dersler 19 ve 20, laboratuvar içi ölçekleme politikalarını ele aldı. Ders 21 bağımsız yetenek değerlendirmesini ele aldı. Bu ders üçüncü perspektifi ele alır: felaket AI riski için kamu tartışmasını ve düzenleyici temeli şekillendiren sivil toplum ve hükümet kuruluşları.

İki farklı varlık önemlidir. CAIS, AI riskini düşünmek için çerçeveler yayınlayan ve kamu beyanlarını koordine eden kar amacı gütmeyen bir araştırma kuruluşudur. CAISI, NIST içindeki bir ABD hükümeti merkezidir; laboratuvarlarla gönüllü anlaşmalar yürütür ve siber, biyo ve kimyasal silah risklerine odaklanan sınıflanmamış yetenek değerlendirmeleri yapar. İsimler benzer; görevler örtüşmez. Bir uygulayıcı her ikisini de bilmelidir.

Pratik içerik: CAIS'in dört risk çerçevesi, literatürdeki en geniş şekilde atıfta bulunulan toplumsal ölçek risk taksonomisidir. Güvenlik kültürü ve örgütsel risk bu dörtten biridir ve bu, bir uygulayıcının kontrolü altında olanıdır. SB-53 (California), imzalanırsa ABD'deki ilk eyalet düzeyinde felaket riski düzenlemesi olur; yasa tasarısının çerçevelemesi önemlidir çünkü eyalet düzeyindeki düzenleme, ABD teknoloji politikasında tarihsel olarak federal eyleme yol açmıştır.

## Kavram

### CAIS — Yapay Zeka Güvenliği Merkezi

- Kuruluş: 2022'de San Francisco'da Dan Hendrycks ve iş arkadaşları tarafından (Zhang ismi mevcut kurucu ortak değil, erken bir işbirlikçiyi ifade eder; mevcut liderlik için CAIS web sitesine bakın).
- Durum: 501(c)(3) kar amacı gütmeyen kuruluş.
- Dikkat çekici 2023 çıktısı: tüy riski beyanı, yüzlerce araştırmacı ve CEO tarafından ortak imzaladı. Belirtildi: "AI'dan kaynaklanan tüy riskinin azaltılması, pandemiler ve nükleer savaş gibi toplumsal ölçekli diğer risklerle birlikte küresel bir öncelik olmalıdır."
- 2026 çıktıları: sınırlı-model değerlendirmesi için AI Dashboard, Uzaktan İş İndeksi (Scale AI ile ortak), Süperzeka Strateji Belgesi, AI Frontiers bülteni.

### Dört risk çerçevesi

CAIS'in çerçevesi felaket AI riskini dört üst düzey kategoride gruplandırır:

1. **Kötüye kullanım:** kötü niyetli bir aktörün AI'yı zarar vermek için kullanması (biyosilah sentezi, dezenformasyon, siber saldırılar).
2. **AI yarışları:** laboratuvarlar, şirketler veya uluslar arasındaki rekabet baskısının dağıtımın güvenli olduğu noktanın ötesine itmesi.
3. **Örgütsel riskler:** iç laboratuvar dinamikleri (güvenlik kültürü hataları, yetersiz denetim, yetersiz kaynaklı güvenlik) kötü bir dağıtım üretir.
4. **Başıboş AI'lar:** yeterince yetenekli bir AI'nın insan refahıyla çelişen hedefleri takip etmesi.

Bu tek takesonomi değildir; en çok atıfta bulunulanıdır. Kategoriler birbirini dışlamaz — hız için denetimi takas eden bir kuruluşun ürettiği başıboş AI dördü de birdir.

### Örgütsel risk nerede yaşar

Dört kategoriden örgütsel risk, uygulayıcılar için en eyleme geçirilebilir olanıdır. Bir laboratuvarın güvenlik kültürü, denetim titizliği, savunma katmanlama ve bilgi güvenliği, modellerinin Ders 10–18'deki kontrollerin gerçekten yerinde olduğu şekilde mi, yoksa kimsenin doğrulamadığı kontrol listesi öğeleri olarak mı çıktığına karar verir.

Somut örgütsel risk kaldıraçları:

- **Güvenlik kültürü:** ekip üyeleri, kariyer maliyeti olmadan bir endişeyi yükseltme (escalate) hissediyor mu? CAIS anketleri, bunun diğer kaldıraçlar için güçlü bir öngörü olduğunu bulur.
- **Titiz denetimler:** dış ve iç. Sadece iç denetimler iyimser raporlar üretir.
- **Çok katmanlı savunmalar:** hiçbir tek katman yeterli değildir (Faz 15'in tekrar eden teması).
- **Bilgi güvenliği:** model ağırlıklarının sızması, verilerin sızması, izleyici atlama tekniklerinin sızması. Ders 19'daki RAND SL-4 belirli bir standarttır.

### CAISI — Yapay Zeka Standartları ve Yenilik Merkezi

- NIST içinde çalışır.
- Sınır laboratuvarlarıyla gönüllü anlaşmalar yürütür.
- Siber, biyo ve kimyasal silah risklerine odaklanan sınıflanmamış yetenek değerlendirmeleri yayınlar.
- CAIS'ten farklıdır; kısaltmalar çakışır; hangisini okuduğunuzu onaylamak için URL'ye (nist.gov) bakın.

CAISI'nin rolü, METR'nin özel laboratuvar temaslarının (Ders 21) kamu, hükümet odaklı karşılığıdır. CAISI raporları sınıflanmamıştır; METR raporları genellikle NDA ile kısıtlıdır. Her ikisini de okuyan bir uygulayıcı daha eksiksiz bir resim elde eder.

### California SB-53

California Senatosu yasa tasarısı (2025–2026 oturumu), sınır modellerinden kaynaklanan felaket riskini ele alır. Taslak olarak temel hükümler:

- Devlet düzeyinde yükümlülükleri tetikleyen belirli yetenek eşikleri.
- AI laboratuvarı çalışanları için muhbir (whistleblower) korumaları.
- Felaketli hatalar için olay bildirme gereksinimleri.

İzlenenrsa, ABD'deki ilk eyalet düzeyinde felaket riski düzenlemesi olur. İzleme durumundan bağımsız olarak, yasa tasarısının çerçevelemesi diğer eyalet meclislerinin soruna nasıl yaklaştığını şekillendirir. California'daki uygulayıcılar yasa tasarısının durumunu takip etmelidir; diğer yerlerdeki uygulayıcılar, ABD eyalet düzeyinde düzenlemenin nasıl olacağını anlamak için okumalıdır.

### Toplumsal ölçek risk tek katmanlı bir sorun değildir

Faz 15'in tekrar eden teması — derinlemesine savunma — toplumsal katmanda da geçerlidir. Hiçbir tek kuruluş, düzenleme veya çerçeve felaket riskini kapatmaz. Ekosistem ancak şunlar çalıştığında işlev görür:

- Laboratuvarlar ölçekleme politikaları yayınlar (Ders 19, 20).
- Bağımsız değerlendiriciler ölçümler üretir (Ders 21).
- Sivil toplum izler ve kamuoyuyla paylaşır (CAIS).
- Hükümet gönüllü programlar ve temel düzenleme yürütür (CAISI, SB-53).
- Uygulayıcılar çok katmanlı kontroller inşa eder (Ders 10–18).

Bu, fase son sentezdir: önceki her ders, bir yığındaki bir katmandır ve eksikliğin tamamlılığı, herhangi bir tek katmanın gücünden daha önemlidir.

## Kullan

`code/main.py`, küçük bir risk envanter aracı uygular. Önerilen bir dağıtım verildiğinde, dağıtımı dört risk kategorisine göre etiketler ve bir azaltma kontrol listesi döndürür. Çerçeve için bir okuma yardımcısıdır, insan judgmentunun yerine geçmez.

## Üret

`outputs/skill-societal-risk-review.md`, bir dağıtımı toplumsal ölçek risk duruşu için inceler: hangi dört kategoriyi dokunduğunu, hangi azaltmaların yerinde olduğunu ve örgütsel risk maruziyetinin ne olduğunu.

## Alıştırmalar

1. `code/main.py` çalıştırın. Farklı ölçekte üç sentetik dağıtım besleyin. Dört risk etiketinin beklentilerinizle eşleştiğini doğrulayın; aracın dưới veya über etiketlediği bir durumu belirleyin.

2. CAIS dört risk makalesini tam olarak okuyun. Bir risk kategorisi seçin ve o kategorideki 2026 gelişmesinin en önemli olduğunu düşündüğünüz hakkında iki paragraf yazın.

3. California SB-53'ün güncel bir taslağını okuyun. Felaket riski duruşunu güçlendirdiğine inandığınız bir hüküm ve zayıflattığına inandığınız bir hüküm belirleyin. Her ikisini de gerekçelendirin.

4. Bildiğiniz bir üretim AI dağıtımını seçin (sizinkini veya yayınlanmış birini). Örgütsel risk kaldıraçlarına göre puanlayın: güvenlik kültürü, denetim titizliği, çok katmanlı savunmalar, bilgi güvenliği. En zayıf olan hangisidir? Eş düzeye getirmenin maliyeti ne olur?

5. Ek bir yıl yetenek ve ek bir yıl dağıtım deneyimini yansıtan 2028 versiyonu bir dört risk çerçevesi çizin. Ne ekler, ne çıkarır veya yeniden gruplandırırsınız?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| CAIS | "Yapay Zeka Güvenliği Merkezi" | Kar amacı gütmeyen kuruluş; dört risk çerçevesi; 2023 tüy riski beyanı |
| CAISI | "ABD hükümeti AI güvenliği" | NIST Merkezi; gönüllü anlaşmalar; sınıflanmamış değerlendirmeler |
| Four-risk framework (Dört risk çerçevesi) | "CAIS'in taksonomisi" | Kötüye kullanım, AI yarışları, örgütsel riskler, başıboş AI'lar |
| Malicious use (Kötüye kullanım) | "Kötü aktör AI'yı kullanır" | Biyosilah, dezenformasyon, siber saldırılar |
| AI races (AI yarışları) | "Rekabet baskısı" | Laboratuvarlar/şirketler/uluslar dağıtımı güvenlik ötesine iter |
| Organizational risk (Örgütsel risk) | "Laboratuvar içi hata" | Güvenlik kültürü, denetim, savunmalar, bilgi güvenliği |
| Rogue AI (Başıboş AI) | "Uyumsuz agent" | İnsan refahıyla çelişen hedefleri takip eden yetenekli AI |
| California SB-53 | "Eyalet düzeyinde düzenleme" | 2025–2026 yasa tasarısı; imzalanırsa ABD'deki ilk eyalet felaket riski düzenlemesi |

## İleri Okuma

- [Yapay Zeka Güvenliği Merkezi](https://safe.ai/) — dört risk çerçevesinin kurumsal evi.
- [CAIS — Felakete Yol Açabilecek AI Riskleri](https://safe.ai/ai-risk) — dört risk makalesi.
- [CAIS — Mayıs 2023 tüy riski beyanı](https://safe.ai/statement-on-ai-risk) — kısa ortak beyan.
- [NIST CAISI](https://www.nist.gov/caisi) — hükümet odaklı AI standartları ve yenilik merkezi.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — laboratuvar düzeyindeki taahhütleri toplumsal ölçekli çerçevelemeye bağlar.
