# AI-Engineering-Ceviri — Çeviri Projesi Talimat Dosyası

> **Kaynak:** `rohitg00/ai-engineering-from-scratch`
> **Hedef:** 20 faz, 473 ders → Türkçeye sistematik çeviri
> **Durum:** Aktif

---

## 1. Proje Bağlamı

Bu proje, GitHub'daki `rohitg00/ai-engineering-from-scratch` deposunu Türkçeye çevirmek için tasarlanmıştır. Depo, yapay zekâyı sıfırdan öğreten kapsamlı bir müfredattır (20 faz, 473 ders).

**Hedef Kitle:** Lise düzeyinin üstünde, teknik konulara ilgi duyan Türkçe konuşan öğreniciler.

**Dil Seviyesi:**
- Aşırı teknik jargon kullanılmaz
- Gerekirse terimler parantez içinde açıklanır
- Önceki derslerde açıklanan terimler, mevcut derste tekrar açıklanmaz; sadece atıfta bulunulur
- Ancak terimin detaylarına giriliyorsa, detaylandırılabilir (dersler arası süreklilik sağlanır)

**Temel İlkeler:**
- Orijinal İngilizce dosyalar asla değiştirilmez
- Çeviriler `tr.md` olarak ayrı dosyalarda saklanır
- Kod blokları İngilizce kalır, her birinin altına Türkçe açıklama eklenir
- Markdown yapısı (başlıklar, tablolar, listeler) eksiksiz korunur

---

## 2. Depo Yapısı ve Kurulum

### Dizin Yapısı

```
AI-Engineering-Ceviri/
├── AGENTS.MD                          ← Bu dosya
├── glossary/
│   └── terms.md                       ← Terimler sözlüğü
├── phases/
│   ├── 00-faz/
│   │   ├── 00-ders/
│   │   │   ├── docs/
│   │   │   │   ├── en.md              ← Orijinal (dokunulmaz)
│   │   │   │   └── tr.md              ← Çeviri hedefi
│   │   │   ├── code/                  ← Dokunulmaz
│   │   │   └── outputs/               ← Çıktı dosyaları (.md)
│   │   └── ...
│   └── ...
├── README_TR.md
├── CONTRIBUTING_TR.md
├── ROADMAP_TR.md
└── ...
```

### Kurulum Adımları

1. Kaynak repoyu clone et:
   ```bash
   git clone --depth 50 https://github.com/rohitg00/ai-engineering-from-scratch source
   ```
2. Çeviri dosyalarını aynı dizin yapısının içine `tr.md` olarak kaydet
3. Orijinal dosyalara asla dokunma

---

## 3. Agent Tanımları

### Agent 1: `translation-orchestrator`
**Rol:** Tüm çeviri sürecini yönetir.

**Sorumluluklar:**
- Faz sırasını kontrol eder (Faz 0 → Faz 1 → ... → Faz 19)
- Translator agent'lara görev dağıtır
- Fazlar arası kalite kapısını yönetir
- İlerleme raporu tutar
- Checkpoint dosyalarını oluşturur

**Kısıtlar:**
- Direkt çeviri yapmaz, sadece orkestra eder
- Faz bitmeden sonraki fase geçmez
- Her faz sonunda `checkpoint.json` oluşturur

---

### Agent 2: `terminology-agent`
**Rol:** Terim tutarlılığını sağlar.

**Sorumluluklar:**
- `glossary/terms.md` dosyasını oluşturur ve günceller
- Yeni terimleri tanımlar (İngilizce karşılık + Türkçe karşılık + açıklama + ilk kullanım yeri)
- Çevrilmiş dosyalarda terim tutarlılığını denetler

**Kısıtlar:**
- Mevcut terimleri değiştirmez, sadece yenilerini ekler
- Her terim için onaylı karşılıklar listesi tutar
- Terim eklerken önceki derslerdeki kullanımları referans alır

---

### Agent 3: `translator-agent`
**Rol:** Tek bir dersi çevirir.

**Sorumluluklar:**
- `docs/en.md` dosyasını okur
- Glossary ve stil rehberine sadık kalarak çevirir
- Kod bloklarını İngilizce bırakır, altına Türkçe açıklama ekler
- Çıktıyı `docs/tr.md` olarak kaydeder

**Kısıtlar:**
- Kod bloklarını, değişken isimlerini, URL'leri değiştirmez
- Markdown yapısını korur
- Aşırı teknikleşmez, lise üstü seviyede tutar
- Önceki derslerde açıklanan terimleri mevcut derste detaylandırabilir

---

### Agent 4: `qa-agent`
**Rol:** Çeviri kalitesini doğrular.

**Sorumluluklar:**
- Terminoloji tutarlılığını kontrol eder
- Markdown biçimlendirmesini doğrular
- Kod bloğu açıklamalarının eksiksizliğini kontrol eder
- Kalite puanı verir (0-100)

**Kısıtlar:**
- Düzenleme yapmaz, sadece raporlar
- Eşik değeri: 80/100 (altında kalırsa insana yönlendirme)

---

### Agent 5: `doc-translator`
**Rol:** Üst düzey belgeleri çevirir.

**Sorumluluklar:**
- README.md, CONTRIBUTING.md, vb. çevirir
- `_TR.md` uzantılı dosyalar oluşturur
- Tabloları, butonları, görsel referansları korur
- Bağlantıların sadece görünen metnini çevirir, URL'leri değiştirmez

---

### Agent 6: `proofreader-agent`
**Rol:** Çevirilerin kalitesini kontrol eder ve düşük kaliteli metinleri otomatik olarak düzeltir.

**Sorumluluklar:**
- tr.md dosyalarını cümle bazında analiz eder
- Orijinal en.md ile karşılaştırarak anlam kaybını tespit eder
- Anlaşılabilirlik skoru hesaplar (0-100)
- 75 altındaki cümleleri otomatik olarak yeniden yazar
- MD formatında kalite raporu üretir

**Kısıtlar:**
- Kod bloklarına dokunmaz
- Markdown yapısını korur
- Orijinal en.md dosyasına asla dokunmaz
- Sadece tr.md dosyalarını düzenler

**Tetikleme:** Çevirilerden sonra, GitHub'a commit etmeden önce

---

## 4. Çeviri Pipeline'ı

### Akış Diyagramı

```
BAŞLA
  │
  ▼
[1] Glossary Oluştur (terminology-agent)
  │
  ▼
[2] Üst Düzey Belgeleri Çevir (doc-translator)
  │
  ▼
[3] Faz 0'a Başla
  │
  ├──► Ders 00 çevir (translator-agent) ◄──┐
  ├──► Ders 01 çevir (translator-agent)    │ PARALLEL
  ├──► Ders 02 çevir (translator-agent)    │
  └──► Ders N çevir (translator-agent) ◄──┘
  │
  ▼
[4] Faz Kalite Kapısı (qa-agent)
  │
  ├── Puan ≥ 80 → Devam et
  └── Puan < 80 → Düzelt → Tekrar kontrol
  │
  ▼
[5] Checkpoint Oluştur
  │
  ▼
[6] Sonraki Faz (3'e dön)
  │
  ▼
TÜM FAZLAR TAMAM
  │
  ▼
[7] Final Raporu
  │
  ▼
BİTİR
```

### Parallel Çalıştırma Kuralları
- Aynı faz içindeki dersler parallel çevrilebilir
- Fazlar arası bağımlılık sıralı (Faz 0 bitmeden Faz 1 başlamaz)
- Her ders bağımsız bir birimdir
- Önceki dersin çevirisi context olarak verilir (dersler arası süreklilik için)

---

## 5. Çeviri Dil Kuralları

### Dil Seviyesi
- **Hedef:** Lise üstü, üniversite 1-2. sınıf seviyesi
- Aşırı teknik jargon kullanılmaz
- Gerekirse terimler parantez içinde açıklanır

### Dersler Arası Süreklilik Kuralı
- Bir terim önceki bir derste açıklanmışsa, mevcut derste tekrar açıklanmaz, sadece atıfta bulunulabilir
- Ancak terimin detaylarına giriliyorsa, detaylandırılabilir
- Örnek: "Daha önce gördüğümüz gradyan inişi (gradient descent) algoritmasının temelini şimdi derinlemesine inceleyeceğiz."

### Örnek Çeviri Kalıpları

| İngilizce | Türkçe |
|-----------|--------|
| "This is how X works" | "X'in çalışma mantığı şöyledir" |
| "As we saw in Lesson Y" | "Y dersinde gördüğümüz gibi" |
| "In this lesson, we will learn..." | "Bu derste ... öğreneceğiz" |
| "Note that..." | "Unutmayın ki..." |
| "Let's implement..." | "Şimdi ... uygulayalım" |
| "The output will be..." | "Çıktı şöyle olacaktır" |

### Uyulması Gereken Dil ve Biçim Kuralları
- **Yerleşik Teknik Terimler:** `token`, `backpropagation`, `overfitting` gibi terimler aynen kalır; ilk geçtikleri yerde parantez içinde kısa bir açıklama verilir
- **Genel Teknik Terimler:** `vector → vektör`, `gradient → gradyan`, `matrix → matris` gibi yerleşik karşılıklar kullanılır
- **Projeye Özgü Terimler:** `prompt → istem`, `skill → beceri`, `agent → ajan`, `loop → döngü`. Bu karşılıklar tüm çeviride tutarlı olmalıdır
- **Üslup:** Senli benli ya da aşırı resmî değil; eğitici, açıklayıcı ve akıcı bir dil. "yapabilirsiniz", "kullanılır" gibi ifadeler tercih edilir

---

## 6. Kod Bloğu Yönetimi

### Temel Format
```markdown
[İngilizce kod bloğu aynen kalır]

#### Açıklama
[Türkçe açıklama — kodun ne yaptığı, hangi adımı gerçekleştirdiği]
```

### Kod Bloğu Çeviri Kuralları
- Bütün kod blokları (`python`, `bash`, vb.) aynen İngilizce olarak bırakılır
- Her kod bloğunun hemen altına `#### Açıklama` başlığı açılarak Türkçe açıklama eklenir
- Açıklama, kodun ne yaptığını, hangi adımı gerçekleştirdiğini ve varsa önemli noktaları anlatır
- Açıklamalar orijinal İngilizce metinde bulunmayabilir; bu durumda kendi cümlelerinizle eklenir

### Özel Durumlar
- **Uzun kod blokları (>50 satır):** Her 10-15 satırda bir yorum satırı eklenebilir
- **Çıktı blokları:** Aynen kalır, sadece üstündeki açıklama metni çevrilir
- **Hata mesajları:** Çevrilmez, sadece üstüne "Bu hata mesajı ..." şeklinde açıklama eklenir

### Örnek Dönüşüm

**Orijinal (en.md):**
```python
def forward(x):
    return x * 2
```

**Çeviri (tr.md):**
```python
def forward(x):
    return x * 2
```
#### Açıklama
Bu fonksiyon, girdi olarak aldığı `x` değerini 2 ile çarparak ileri besleme işlemini gerçekleştirir.

---

## 7. Hata Yönetimi

### Hata Türleri ve Müdahale

| Hata | Müdahale | Max Retry |
|------|----------|-----------|
| Dosya bulunamadı | Atla, raporla | 0 |
| Bozuk markdown | Düzelt, devam et | 1 |
| Terminoloji tutarsızlığı | terminology-agent'a gönder | 2 |
| Rate limit | Exponential backoff (1s, 2s, 4s) | 3 |
| Translate hatası | Basitleştirilmiş prompt ile tekrar dene | 2 |

### Dead Letter Queue
- 2 retry sonrası başarısız olan dersler → `failed/` dizinine kaydedilir
- İnsana yönlendirme gerektirir

### Checkpoint Mekanizması
- Her faz sonunda `checkpoint.json` oluşturulur
- İçerik:
  ```json
  {
    "phase": 0,
    "completed_lessons": [0, 1, 2, 3],
    "failed_lessons": [],
    "quality_scores": {"avg": 87, "min": 72, "max": 98},
    "timestamp": "2026-05-29T12:00:00Z"
  }
  ```
- Yeniden başlatma durumunda bu dosyadan devam edilir

### Escalation Kuralları
- 2 retry sonrası hala hata alınıyorsa insana bildir
- Rate limit aşıldı ve workaround yoksa dur ve bildir
- Repo private veya erişilemezse dur ve bildir
- Görev kapsamı başlangıçta tanımlananı aşıyorsa onay iste

---

## 8. Çıktı Format Şablonları

### Şablon 1: `glossary/terms.md`

```markdown
# Teknik Terimler Sözlüğü

| İngilizce | Türkçe | Açıklama | İlk Kullanım |
|-----------|--------|----------|--------------|
| token | token | İşlem birimi | Faz 0, Ders 1 |
| backpropagation | geri yayılım | Hata yayılımı algoritması | Faz 2, Ders 3 |
| gradient | gradyan | Türev vektörü | Faz 1, Ders 2 |
| vector | vektör | Yönlü büyüklük | Faz 0, Ders 0 |
```

### Şablon 2: `docs/tr.md`

```markdown
# [Ders Başlığı]

[Çevrilmiş ders içeriği]

```python
[kod bloğu aynen]
```

#### Açıklama
[Kodun Türkçe açıklaması]

---
```

### Şablon 3: `README_TR.md`

```markdown
# [Çevrilmiş Proje Başlığı]

[Çevrilmiş proje tanıtımı]

## İçindekiler

### Faz 0: [Faz Adı]
- Ders 0: [Ders Adı]
- Ders 1: [Ders Adı]
- ...

### Faz 1: [Faz Adı]
- ...
```

### YAML Front Matter Kuralları
- Anahtar isimleri (`name`, `description`) çevrilmez
- Yalnızca değerleri çevrilir
- Örnek:
  ```yaml
  ---
  name: lesson-zero
  description: Yapay zekaya giriş  ← Bu kısım çevrilir
  ---
  ```

### Şablon 4: `quiz.json` Çeviri Formatı

Her dersin `quiz.json` dosyası çevrilmelidir. JSON yapısı korunur, yalnızca metin alanları çevrilir.

**Çevrilecek Alanlar:**
- `question`: Soru metni
- `options[]`: Şıkların metinleri
- `explanation`: Açıklama metni

**Dokunulmayan Alanlar:**
- `stage`: Sınıf bilgisi (`pre`, `check`, `post`) aynen kalır
- `correct`: Doğru cevap indeksi aynen kalır (0'dan başlar)

**Örnek Dönüşüm:**
```json
// Orijinal (en.md)
{
  "stage": "pre",
  "question": "Why do AI projects need a separate virtual environment?",
  "options": [
    "Virtual environments make code run faster",
    "They isolate dependencies so different projects don't conflict"
  ],
  "correct": 1,
  "explanation": "Virtual environments isolate package versions per project."
}

// Çeviri (tr.md)
{
  "stage": "pre",
  "question": "Yapay zeka projeleri neden ayrı bir sanal ortama ihtiyaç duyar?",
  "options": [
    "Sanal ortamlar kodun daha hızlı çalışmasını sağlar",
    "Farklı projelerin çakışmaması için bağımlılıkları izole ederler"
  ],
  "correct": 1,
  "explanation": "Sanal ortamlar, her proje için paket sürümlerini izole eder."
}
```

**Çeviri Kuralları:**
- Sorular eğitici ve açıklayıcı olmalı
- Teknik terimler `glossary/terms.md`'deki karşılıklarıyla çevrilmeli
- Şıklar kısa ve net olmalı (maksimum 2 satır)
- Açıklama, neden o cevabın doğru olduğunu kısa bir şekilde anlatmalı
- `quiz.json` dosyası aynı dizine `quiz_tr.json` olarak kaydedilmeli

---

## 9. Kalite Kontrol Sistemi

### Otomatik Kontroller
1. **Terminoloji eşleşme:** `glossary/terms.md`'deki her terim, tr.md dosyalarında aynen kullanılmalı
2. **Markdown doğrulama:** Başlık hiyerarşisi, kod bloğu bütünlüğü, bağlantı geçerliliği
3. **Kod bloğu kontrolü:** Her kod bloğunun altında `#### Açıklama` var mı?

### İnsan Kontrolü
- Her 5 fasın sonunda 1 ders insan tarafından incelenmeli
- Kalite puanı < 80 olan dersler insana yönlendirilmeli

### Fazlar Arası Kalite Kapısı
- Bir sonraki fazа geçiş için önceki fazın ortalama kalite puanı ≥ 80 olmalı
- Puan < 80 ise: düzelt → tekrar kontrol → geç

### Rapor Formatı
```json
{
  "phase": 0,
  "total_lessons": 25,
  "completed": 25,
  "quality_scores": {"avg": 87, "min": 72, "max": 98},
  "issues": [
    "Ders 12: eksik açıklama",
    "Ders 18: terim tutarsızlığı"
  ]
}
```

### Son Özet Rapor
Tüm çeviriler bittiğinde (veya büyük bir bölümü tamamlandığında) şu bilgileri içeren bir rapor oluşturulur:
- Çevrilen faz sayısı
- Oluşturulan tr.md dosya sayısı
- Karşılaşılan özel durumlar veya belirsiz terimler
- Genel başarı durumu

---

## 10. Sınır ve Kısıt Tanımları

### Kesinlikle Dokunulmazlar
- Kod blokları (içerikleri)
- Değişken, fonksiyon, sınıf isimleri
- Komut satırı örnekleri ve dosya yolları
- URL bağlantı adresleri
- YAML front matter anahtarları (yalnızca değerleri çevrilebilir)
- `code/` dizinindeki tüm dosyalar
- `scripts/` dizinindeki Python dosyaları (sadece stdout mesajları çevrilebilir)

### Çeviri Yapılmayacak İçerikler
- Kod yorumları (İngilizce kalacak)
- Hata mesajları
- API endpoint'leri
- Konfigürasyon dosyaları

### Güvenlik Kısıtlamaları
- `.env`, `*.pem`, `*.key` dosyaları okunmaz
- Secret içeren dosyalar commit edilmez
- API key'leri loglanmaz
- Duyarlı bilgi içeren dosyalar paylaşılmaz

### Token Bütçesi Considerations
- Uzun ders dosyaları (>500 satır) chunking ile bölünmeli
- Her chunk bağımsız çevrilebilir, sonra birleştirilir
- Context window dolmaya yaklaşıyorsa mevcut chunk tamamlanıp yeni chunk'a geçilmeli

---

## Güncelleme Geçmişi

| Tarih | Değişiklik |
|-------|-----------|
| 2026-05-29 | İlk sürüm: 10 bölümlük kapsamlı çeviri talimatları |
