# Rol Uzmanlaşması — Planlayıcı, Eleştirmen, Yürütücü, Doğrulayıcı

> 2026'daki en yaygın multi-agent ayrıştırma: bir agent planlar, biri yürütür, biri eleştirir veya doğrular. MetaGPT (arXiv:2308.00352) bunu SOP'lar (Standart İşletim Prosedürleri) rol promptlarına kodlanmış olarak resmileştirir — Product Manager (Ürün Yöneticisi), Architect (Mimar), Project Manager (Proje Yöneticisi), Engineer (Mühendis), QA Engineer (QA Mühendisi) — `Code = SOP(Team)` formülünü izler. ChatDev (arXiv:2307.07924) tasarımcıyı, programcıyı, incelemeciyi, testçiyi "iletişimsel halüsinasyonsuzlaştırma" (agents açıkça eksik detayları talep eder) ile bir "sohbet zinciri" yoluyla zincirler. Doğrulayıcı yük taşıyıcıdır (load-bearing): Cemri ve diğerleri (MAST, arXiv:2503.13657) her multi-agent başarısızlığının eksik veya kırık doğrulamaya kadar izlenebileceğini gösterir. PwC, CrewAI'de yapılandırılmış doğrulama döngülerinden 7× doğruluk kazancı (%10 → %70) bildirdi.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model), Faz 16 · 05 (Supervisor)
**Süre:** ~60 dakika

## Problem

Genel multi-agent sistemler genel çıktı üretir. Bir grup sohbetteki üç kod yazarı, aynı vasat kodun üç çeşidini yazar. Daha fazla agent, daha fazla tur ekleyebilirsiniz ve yine de kalite eşiğini geçemezsiniz.

Düzeltme daha fazla agent değil — *farklı* agent'lardır. Farklı roller atayın. Eleştirmene planlayıcının sahip olmadığı araçlar verin. Doğrulayıcıya nesnel bir test paketi verin. Artık sistemin, paralel tahmin yerine, temellenmiş düzeltmeyle dahili anlaşmazlığı vardır.

## Kavram

### Dört kanonik rol

**Planlayıcı (Planner).** Hedefi okur, bir adım listesi veya bir spec üretir. Araçlar: bilgi getirme, belgeler. Çıktı: yapılandırılmış plan.

**Yürütücü (Executor).** Bir seferde bir plan adımını okur, yapıtı üretir. Araçlar: asıl iş araçları (kod derleyici, kabuk, API istemcisi). Çıktı: yapıt.

**Eleştirmen (Critic).** Yürütücünün çıktısını planlayıcının amacına karşı okur. Araçlar: yapıta salt okunur erişim, statik analiz. Çıktı: nedenlerle kabul/red.

**Doğrulayıcı (Verifier).** Yapıtı okur ve deterministik bir kontrol çalıştırır. Araçlar: test çalıştırıcı, tip denetleyici, şema doğrulayıcı. Çıktı: kanıtlarla geç/kal.

Eleştirmen öznel, görüş belirten, genellikle LLM tabanlıdır. Doğrulayıcı nesnel, deterministik, genellikle kod tabanlıdır. Aynı rol değildirler.

### MetaGPT'nin SOP kalıbı

MetaGPT (arXiv:2308.00352), yazılım mühendisliği SOP'larını rol promptları olarak kodlar:

- **Product Manager** PRD'yi yazar.
- **Architect** sistem tasarımını üretir.
- **Project Manager** görevleri böler.
- **Engineer** uygular.
- **QA Engineer** testleri çalıştırır.

Her rolün sıkı bir girdi/çıktı şeması vardır. Rol promptu, rolün *ne olduğunu* ve *neyi üretmesi gerektiğini* söyler. `Code = SOP(Team)` formülasyonu — deterministik SOP'ler bir LLM takımını tahmin edilebilir bir pipeline'a dönüştürür.

### ChatDev'nin iletişimsel halüsinasyonsuzlaştırması

ChatDev, kilit bir hamle ekler: bir yürütücü, planda olmayan belirli bir detaya ihtiyaç duyduğunda, devam etmeden önce açıkça tasarımcıya sorar. Bu, klasik LLM başarısızlığı olan detayı inandırıcı bir şekilde uydurmayı engeller.

Uygulama: rol promptu, "size verilmeyen belirli bilgilere ihtiyacınız olduğunda, çıktı üretmeden önce ada göre ilgili role sorun" ifadesini içerir.

### Doğrulayıcı neden en çok önemli

Cemri ve diğerleri (MAST), 1642 multi-agent yürütme başarısızlığını izledi. %21.3'ü doğrulama boşluklarıydı — sistem kimsenin kontrol etmediği bir yanıt gönderdi. Kalan %79'u genellikle "sessizce başarısız olan veya hiç çalıştırılmayan bir kontrol vardı" ifadesine kadar izlenebilir. Doğrulama, yük taşıyıcı roldür.

PwC (CrewAI dağıtımları, 2025), yapılandırılmış bir doğrulama döngüsü eklemenin doğruluğu %10'dan %70'e taşıdığını bildirdi. Bir rolden 7× kazanç.

### Eleştirmen ve doğrulayıcı

- Eleştirmen, kalite için bir yapıtı inceleyen bir LLM'dir. Öznel. İnandırıcı düzyazı tarafından kandırılabilir.
- Doğrulayıcı, yapıt üzerinde çalışan deterministik bir programdır. Nesnel. Kanıtlarla geç/kal verir.

İkisini de kullanın. Eleştirmen, doğrulayıcının ifade edemeyeceği tat sorunlarını yakalar. Doğrulayıcı, yalnızca çalışma zamanında ortaya çıkan ve eleştirmenin göremediği hataları yakalar.

### Anti-kalıp

Sisteminizdeki her rol bir LLM'dir ve her rolün çıktısı "bence iyi görünüyor"dur. Klasik MAST başarısızlık modu. Geçerli/kal kararını kod veren en az bir doğrulayıcı ekleyin.

### Çatı eşlemeleri

- **CrewAI** — `Agent(role, goal, backstory)` ders kitabı uzmanlaşma yüzeyidir.
- **LangGraph** — düğümler özelleşmiş promptlara sahip olabilir; kenarlar pipeline'ı uygular.
- **AutoGen** — bir GroupChat'te tek kelimelik adlarla role özgü ConversableAgent'lar.
- **OpenAI Agents SDK** — role özelleşmiş Agent'lar arasında handoff araçları.

## İnşa Et

`code/main.py` basit bir Python fonksiyonu inşa eden 4-rol bir pipeline uygular:

- **Planlayıcı** bir spec üretir.
- **Yürütücü** bir kod string'i üretir.
- **Eleştirmen** (LLM-simüle) belirgin sorunları işaretler.
- **Doğrulayıcı** üretilen kodu bir sandbox'ta (`exec`) bir test senaryosuna karşı çalıştırır.

Demo iki kez çalışır: yürütücünün doğru kodu ürettiği bir kez (eleştirmen + doğrulayıcı geçer), yürütücünün spec dışı kodu ürettiği bir kez (eleştirmen inandırıcı göründüğü için hatayı kaçırır, doğrulayıcı test başarısız olduğu için yakalar).

Çalıştırın:

```
python3 code/main.py
```

## Kullan

`outputs/skill-role-designer.md` bir görev alır ve rol kadrosunu (3-5 rol), rol başına girdi/çıktı şemasını ve doğrulayıcı kontrolünü üretir. Agent'ları bir çatıya bağlamadan önce bunu kullanın.

## Dağıt

Kontrol listesi:

- **En az bir deterministik doğrulayıcı.** Asla tümü LLM değil.
- **Rol başına açık I/O şeması.** Planlayıcı bir spec döner, düzyazı değil; yürütücü o şemayı okur.
- **İletişimsel halüsinasyonsuzlaştırma.** Yürütücü, bilgi eksik olduğinde planlayıcıya sormalıdır; asla uydurmamalıdır.
- **Eleştirmen/doğrulayıcı sıralaması.** Önce eleştirmen (ucuz, tasarım sorunlarını yakalar), sonra doğrulayıcı (yavaş, hataları yakalar).
- **Döngü bütçesi.** İnsana yükseltmeden önce maksimum 2 eleştirmen-yürütücü revizyon turu.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın ve doğrulayıcının eleştirmenin kaçırdığı hatayı nasıl yakaladığını gözlemleyin. Ek bir doğrulayıcı olarak statik-analiz kontrolü (`return` oluşumlarını sayma) ekleyin. Çalışma zamanı testinin kaçırdığı neyi yakalar?
2. 5. bir rol ekleyin: kullanıcı isteğini planlayıcıya hazır spec'e çeviren "gereksinim analisti". Hangi iletişimsel halüsinasyonsuzlaştırma istekleri ona akmalıdır?
3. MetaGPT Bölüm 3'ü ("Agents") okuyun. MetaGPT'nin 5 rolünün her birinin girdi/çıktı şemasını listeleyin.
4. ChatDev'nin sohbet-zinciri şemasını (arXiv:2307.07924 Şekil 3) okuyun. İletişimsel halüsinasyonsuzlaştırmanın, aksi takdirde sonsuz olacak bir döngüyü nerede kırdığını belirleyin.
5. PwC'nin 7× doğruluk kazancı doğrulama döngülerinden geldi. Doğrulayıcı eklemenin yardımcı olmayacağı üç görev varsayın — doğruluğun deterministik kontrolünün imkansız veya aşırı pahalı olduğu durumlar.

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Role specialization (Rol uzmanlaşması) | "Farklı agent'lar, farklı işler" | Planlayıcı/yürütücü/eleştirmen/doğrulayıcı rolleri için ayarlanmış farklı sistem promptları. |
| SOP pattern (SOP kalıbı) | "Kodlanmış standart işletim prosedürü" | MetaGPT'nin çerçevelemesi: rol başına sıkı I/O şemaları bir takımı pipeline'a dönüştürür. |
| Communicative dehallucination (İletişimsel halüsinasyonsuzlaştırma) | "Uydurmadan önce sor" | ChatDev kalıbı: yürütücü, bir detay eksik olduğunda onu uydurmak yerine planlayıcıya sorar. |
| Critic (Eleştirmen) | "LLM incelemeci" | Öznel, görüş belirten incelemeci. Tat sorunlarını yakalar. İnandırıcı düzyazı tarafından kandırılabilir. |
| Verifier (Doğrulayıcı) | "Deterministik kontrol" | Kod tabanlı geç/kal. Test çalıştırıcı, tip denetleyici, şema doğrulayıcı. Kandırılamaz. |
| Verification gap (Doğrulama boşluğu) | "Kimse kontrol etmedi" | MAST başarısızlıklarının %21.3'ü. Hatayı yakalayacak kontrol olmadan gönderilen yanıt. |
| Revision loop (Revizyon döngüsü) | "Eleştirmen geri gönderir" | Eleştirmen reddi, yürütücüyü geri bildirimle yeniden çalıştırmayı tetikler. Bütçe gerektirir. |
| All-LLM anti-pattern (Tümü-LLM anti-kalıbı) | "Bence iyi görünüyor" | Her rol bir LLM, deterministik kontrol yok. Klasik MAST başarısızlığı. |

## İleri Okuma

- [Hong ve diğerleri — MetaGPT: Meta Programming for Multi-Agent Collaboration](https://arxiv.org/abs/2308.00352) — SOP-as-role-prompt referans makalesi
- [Qian ve diğerleri — Communicative Agents for Software Development (ChatDev)](https://arxiv.org/abs/2307.07924) — sohbet zinciri + iletişimsel halüsinasyonsuzlaştırma
- [Cemri ve diğerleri — Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — MAST taksonomisi; doğrulama boşlukları başarısızlıkların %21.3'üdür
- [CrewAI belgeleri — Agent rolleri](https://docs.crewai.com/en/introduction) — üretim rol spesifikasyon yüzeyi
