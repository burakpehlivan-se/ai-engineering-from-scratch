# Değişiklik Kaydı

Müfrezeattaki yenilikler. En yenisi en üstte.

Biçim, [Bir Değişiklik Kaydı Tut](https://keepachangelog.com/)'u gevşek olarak takip eder. Her kayıt, fazı, dersi ve neyin değiştiğini belirtir, böylece öğrenciler doğrudan farka atlayabilir.

## [Yayınlanmamış]

### Eklenenler
- `scripts/scaffold-lesson.sh` — `phases/NN-faz/NN-ders/` dizinini tam klasör yapısıyla ve `LESSON_TEMPLATE.md`'den önceden doldurulmuş bir `docs/en.md` iskeletiyle oluşturan iskelet oluşturucu.
- `.github/PULL_REQUEST_TEMPLATE.md` — katkıda bulunan kontrol listesi (kod çalışıyor, kod yorumu yok, sıfırdan oluşturulmuş, ders başına atomik commit, markdown bağlantılı ROADMAP satırı).
- `.github/ISSUE_TEMPLATE/bug_report.md` ve `new_lesson_proposal.md` — hata raporları ve ders önerileri için yapılandırılmış giriş.
- Bu `CHANGELOG.md`.

## 2026-04 — Faz 4: Bilgisayarlı Görüntü tamamlandı

### Eklenenler
- Faz 4'ün tüm 22 dersi, görüntü temellerinden çok modlu görünüme (VLM'ler, 3D, video, öz-denetimli) kadar.
- `ROADMAP.md`'deki Faz 4 satırları, derse bağlantılar olarak markdown olarak bağlandı, böylece web sitesi bunları gösteriyor.

### Düzeltilen
- Faz 4'te 15+ derste hassasiyet geçişi:
  - `phase-4/02`: şekli hesaplayıcı, havuz, düzleştirme ve doğrusal için RF/adım işleyişini belirtiyor.
  - `phase-4/03`: omurga seçici açıklaması tüm kapsanan aileleri listeliyor; OCR, tıbbi, endüstriyel için kafa rehberliği eklendi.
  - `phase-4/04`: sınıflandırma teşhisleri başarısızlık moduna göre niceliksel eşikler kullanıyor; tanımlanmamış metrikler için `n/a` bildiriliyor; 3'ten az sınıf için koruma eklendi.
  - `phase-4/06`: algılama metrik okuyucusu `AP@0.5` kullanıyor (`mAP@0.5` değil); sınıflar arası duyarlılık isteğe bağlı bildiriliyor; çapa tasarımcısı adım kısaltmasını ve seviye başına tek çapa yolunu açıklıyor.
  - `phase-4/10`: örnekleyici seçici `unet_forward_ms`'i girdi olarak bildiriyor; ControlNet koruması 0. kurala terfi etti.
  - `phase-4/14`: ViT denetleyicisi red kuralıyla uyumlu — port denemeleri denetlenir, onaylanmaz.
  - `phase-4/24`: açık sözlük yığını seçicisinde açık kural önceliği ve lisans filtre anlamları var; kavram tasarımcısı 5. adım/80. kural çakışmasını çözüyor.
  - `phase-4/25`: VLM dokümanları `_merge`, yer tutucu uyumsuzluğunda açıklayıcı `ValueError` veriyor; CMER dahili olarak normalleştiriyor.
  - `phase-4/27`: `synthetic_frames`, GT kutularını kare yükseklik/genişliğine kırpıyor.
  - `phase-4/28`: `rope_3d`, boyut bölmesini doğruluyor; DiT blok örneğinden kullanılmayan `F` içe aktarması kaldırıldı.

## 2026-Q1 ve öncesi

### Eklenenler
- Faz 0 (Kurulum ve Araçlar): tüm 12 ders.
- Faz 1 (Matematik Temelleri): tüm 22 ders.
- Faz 2 (ML Temelleri): tüm 18 ders.
- Faz 3 (Derin Öğrenme Çekirdeği): algılayıcı, geri yayılım, optimize edicilere kadar temel dersler.
- Yerleşik Claude Code becerileri: `find-your-level` (yerleştirme sınavı) ve `check-understanding` (faz başına sınav).
- `aiengineeringfromscratch.com` web sitesi: katalog, ders sayfaları, yol haritası, 277 terimlik sözlük.
- Tüm 20 faz için ilk iskelet oluşturma (`phases/00-*`'den `phases/19-*`'e).
- `LESSON_TEMPLATE.md`, `CONTRIBUTING.md`, `ROADMAP.md`, `README.md`.

[Yayınlanmamış]: https://github.com/rohitg00/ai-engineering-from-scratch/compare/HEAD...HEAD
