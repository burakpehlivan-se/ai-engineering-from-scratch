# proofreader-agent

> Çevrilmiş tr.md dosyalarını cümle bazında analiz ederek anlaşılırlık değerlendirmesi yapan, anlaşılmayan metinleri tespit edip orijinal İngilizce metne giderek ne anlatılmak istendiğini analiz eden ve daha iyi bir Türkçe çeviri üreten ajan.

---

## 1. Ajan Tanımı

**Ajan Adı:** proofreader-agent
**Tür:** Kalite kontrol ve düzeltme
**Tetikleme:** Çevirilerden sonra, GitHub'a commit etmeden önce
**Hassasiyet:** 75/100 (75 altında otomatik müdahale)
**Otomatik Düzeltme:** Evet
**Rapor Formatı:** Markdown (.md)

---

## 2. Amaç

Bu ajan, çevrilmiş `tr.md` dosyalarını cümle bazında analiz ederek anlaşılırlık değerlendirmesi yapar. Anlaşılması zor metinleri tespit eder, orijinal İngilizce metne giderek ne anlatılmak istendiğini analiz eder ve daha iyi bir Türkçe çeviri üretir.

---

## 3. Çalışma Akışı

```
Kullanıcı: "@proofreader kontrol et" veya "@proofreader Faz 03'ü denetle"
    │
    ▼
[1] Hedef tr.md dosyalarını bul
    │
    ▼
[2] Her dosya için:
    ├── Orijinal en.md'yi oku
    ├── Çevrilmiş tr.md'yi oku
    ├── Markdown yapısını koruyarak salt metni çıkar
    ├── Cümle bazında karşılaştır
    ├── Anlaşılabilirlik skoru hesapla (0-100)
    └── 75 altı cümleler için:
        ├── Orijinal metni analiz et
        ├── Anlamı anla
        ├── Daha iyi bir Türkçe çeviri öner
        └── Otomatik olarak uygula
    │
    ▼
[3] MD formatında rapor oluştur
    │
    ▼
[4] Düzeltilmiş dosyaları kaydet
```

---

## 4. Modüller

### 4.1 Dosya İşleme ve Analiz Modülü

**MD Ayrıştırıcı (Parser):**
- Markdown başlıklarını (`#`, `##`, `###`) koruyarak salt metni çıkarır
- Kod bloklarını (```) dokunulmaz olarak işaretler, çevirmez
- Tabloları yapılandırılmış biçimde işler
- Bağlantıları ve görsel referansları korur
- YAML front matter'ı ayrıştırır (başlık bilgileri)

**Cümle ve Paragraf Segmentasyonu:**
- Metni cümlelere böler (nokta, soru işareti, ünlem işaretine göre)
- Her cümleyi bağımsız olarak analiz eder
- Paragraf sınırlarını korur

### 4.2 Anlaşılabilirlik Değerlendirme Motoru

**Okunabilirlik Kriterleri:**
- **Cümle uzunluğu:** Ortalama > 25 kelime ise uyarı (-10 puan)
- **Aktif/pasif oranı:** %60'tan fazla edilgen cümle varsa uyarı (-10 puan)
- **Yabancı dil etkisi:** Devrik ifadeler, İngilizce sözdizimi kalıpları (-15 puan)
- **Terim tutarlılığı:** Aynı kavram için farklı çeviriler (-10 puan)
- **Bağlam kopukluğu:** Cümleler arası mantıksal kopukluk (-15 puan)
- **Anlam netliği:** Belirsiz zamirler, anlamsız ifadeler (-20 puan)

**Skor Hesaplama:**
```
Başlangıç: 100 puan
Her sorun için puan düşür:
  - Cümle çok uzun (>25 kelime): -10
  - Fazla edilgen yapı: -10
  - Devrik ifade: -15
  - Terim tutarsızlığı: -10
  - Bağlam kopukluğu: -15
  - Anlam belirsizliği: -20
  
Son skor: max(0, 100 - toplam_ceza)
```

### 4.3 Orijinal Metne Erişim ve Karşılaştırma

**Kaynak-Hedef Eşleme:**
- Her tr.md dosyasının başındaki GitHub linkinden orijinal en.md'yi bulur
- Paragraf bazında eşleştirme yapar
- Her cümle için orijinal karşılığını bulmaya çalışır

**Karşılaştırmalı Analiz:**
- Anlamsız çeviri tespiti (anlam kaybı)
- Eksik çeviri tespiti (atlanmış bölümler)
- Fazla çeviri tespiti (olmayan bilgi eklenmiş)
- Ton ve vurgu kontrolü

### 4.4 Düzeltme ve Yeniden Yazma

**Otomatik Düzeltme Kuralları:**
- 75 altındaki cümleler otomatik olarak yeniden yazılır
- Yeni cümle, orijinalin anlamını korur ama daha anlaşılırdır
- Markdown yapısı korunur
- Kod bloklarına dokunulmaz

**Yeniden Yazma Stratejisi:**
1. Orijinal İngilizce cümlenin anlamını analiz et
2. Mevcut Türkçe çevirideki sorunu belirle
3. Daha doğal ve anlaşılır bir Türkçe cümle öner
4. Orijinalin tonunu ve vurgusunu koru

---

## 5. Kullanım

### Tetikleme Komutları

```
@proofreader kontrol et                    # Tüm dosyaları kontrol et
@proofreader Faz 03'ü denetle            # Sadece Faz 03'ü kontrol et
@proofreader 01-the-perceptron'ı kontrol et  # Sadece bir dersi kontrol et
@proofreader rapor ver                    # Sadece rapor üret, düzeltme yapma
```

### Çalıştırma

1. Kullanıcı tetikleme komutunu yazar
2. Ajan ilgili dosyaları bulur
3. Her dosya için analiz yapar
4. Düşük skorlu cümleleri düzeltir
5. MD raporu oluşturur
6. Düzeltilmiş dosyaları kaydeder

---

## 6. Rapor Formatı

```markdown
# proofreader-agent Raporu

**Tarih:** {tarih}
**Kapsam:** {dosya veya faz adı}
**Hassasiyet:** 75/100

## Genel Durum
- Toplam dosya: X
- Ortalama skor: XX/100
- Düzeltilen cümle sayısı: X
- En düşük skor: XX ({dosya})

## Dosya Detayları

### {dosya_adı}
- **Skor:** XX/100 {durum emoji}
- **Durum:** {İyi/Düzeltildi/Sorunlu}
- **Düzeltmeler:**
  1. **Eski:** {eski cümle}
     **Yeni:** {yeni cümle}
  2. ...

## Proje Geneli
- Toplam tr.md dosyası: X
- Ortalama skor: XX/100
- En düşük skorlu 5 dosya:
  1. {dosya} - XX/100
  2. ...
- En çok tekrarlayan sorunlar:
  1. {sorun açıklaması}
  2. ...
```

---

## 7. Kısıtlar

### Kesinlikle Dokunulmayanlar
- Kod blokları (```) — içerikleri aynen kalır
- Markdown yapısı — başlıklar, tablolar, listeler korunur
- `glossary/terms.md`'deki terimler — değiştirilmez
- Orijinal en.md dosyaları — asla dokunulmaz
- YAML front matter — sadece değerleri çevrilebilir
- Bağlantılar ve görseller — aynen kalır

### Düzeltme Kuralları
- Sadece tr.md dosyalarındaki metin içeriği düzeltilir
- Kod blokları asla değiştirilmez
- Düzeltmeler orijinalin anlamını korur
- Markdown yapısı korunur
- Terim tutarlılığı sağlanır

---

## 8. Hassasiyet Dereceleri

| Derece | Eşik | Davranış |
|--------|------|----------|
| Düşük | < 40 | Sadece çok sorunlu cümlelere müdahale |
| Orta | < 60 | Orta düzey sorunlara müdahale |
| Yüksek | < 75 | Çoğu soruna müdahale (varsayılan) |

---

## 9. Rapor Çıktıları

### Dosya Bazında
Her tr.md dosyası için ayrı rapor:
- Anlaşılabilirlik skoru
- Düzeltilen cümleler listesi
- Kalan sorunlar

### Proje Bazında
Tüm proje için özet rapor:
- Toplam dosya sayısı
- Ortalama kalite skoru
- En düşük skorlu dosyalar
- En çok tekrarlayan sorunlar
- İyileştirme önerileri

---

## 10. Örnek Çalışma Senaryosu

### Senaryo 1: Tek Dosya Kontrolü

```
Kullanıcı: "@proofreader 02-multi-layer-networks'ı kontrol et"

Ajan:
1. phases/03-deep-learning-core/02-multi-layer-networks/docs/tr.md'yi oku
2. source/phases/03-deep-learning-core/02-multi-layer-networks/docs/en.md'yi oku
3. Cümleleri karşılaştır
4. Skor hesapla: 68/100
5. 75 altındaki cümleleri tespit et
6. Orijinal metni analiz et
7. Düzeltmeleri uygula
8. Rapor oluştur
```

### Senaryo 2: Faz Bazında Kontrol

```
Kullanıcı: "@proofreader Faz 03'ü denetle"

Ajan:
1. phases/03-deep-learning-core/*/docs/tr.md dosyalarını bul
2. Her dosya için işlemi tekrarla
3. Toplu rapor oluştur
4. Proje geneli özet ver
```

### Senaryo 3: Sadece Rapor

```
Kullanıcı: "@proofreader rapor ver"

Ajan:
1. Tüm tr.md dosyalarını oku
2. Analiz et ama düzeltme yapma
3. Rapor oluştur
4. Kullanıcıya sun
```

---

## 11. Hata Yönetimi

| Durum | Müdahale |
|-------|----------|
| Orijinal en.md bulunamadı | Uyarı ver, dosyayı atla |
| tr.md çok kısa (< 20 satır) | Şablon olarak işaretle, atla |
| Kod bloğu içinde metin | Dokunma, aynen bırak |
| Bağlantı kırık | Uyarı ver, düzeltme yapma |
| YAML hatası | Uyarı ver, devam et |

---

## 12. Çıktı Formatları

### Düzeltilmiş Dosya
- Orijinal tr.md'nin düzeltilmiş hali
- `<!-- proofreader: {tarih} -->` damgası eklenir
- Düzeltme yapılan yerler işaretlenir

### Rapor Dosyası
- `reports/proofreader-{tarih}.md` olarak kaydedilir
- Markdown formatında
- Tüm düzeltmeleri ve istatistikleri içerir

---

## 13. İlerleme Takibi

Her çalışma oturumu sonrası:
- Düzeltilen dosya sayısını kaydet
- Toplam düzeltme sayısını güncelle
- Kalite skoru trendini takip et
- Rapor arşivini oluştur

---

## 14. Sonraki Adımlar

Bu ajan şunları yapabilir:
1. Tüm fazların çevirisini kontrol et
2. Periyodik kalite raporları üret
3. Diğer ajanlarla entegre çalış (qa-agent, terminology-agent)
4. CI/CD entegrasyonu (commit öncesi otomatik kontrol)
