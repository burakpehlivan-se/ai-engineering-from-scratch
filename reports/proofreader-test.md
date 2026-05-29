# proofreader-agent Test Raporu

**Tarih:** 2026-05-29
**Kapsam:** Faz 03 - 02-multi-layer-networks
**Hassasiyet:** 75/100

---

## Genel Durum

| Metrik | Değer |
|--------|-------|
| Toplam cümle | 45 |
| Anlaşılır (>75) | 38 (%84) |
| Anlaşılması zor (<75) | 7 (%16) |
| Ortalama skor | 82/100 |

---

## Dosya Detayları

### 02-multi-layer-networks/docs/tr.md

**Skor:** 82/100 ✅

**Düzeltmeler:**

1. **Satır 5:**
   - **Eski:** "Tek bir nöron bir çizgi çizer. Onları istiflerseniz, her şeyi çizebilirsiniz."
   - **Yeni:** "Tek bir nöron yalnızca düz bir çizgi çizebilir. Ama onları üst üste istiflerseniz, her türlü eğriyi çizebilirsiniz."
   - **Neden:** "çizer" ifadesi belirsiz, "çizebilir" daha net

2. **Satır 21:**
   - **Eski:** "Tek bir nöron bir çizgi çizerici. Hepsi bu kadar."
   - **Yeni:** "Tek bir nöron, verinizden yalnızca düz bir çizgi çizebilir. Hepsi bu kadar."
   - **Neden:** "çizerici" Türkçe değil, "çizebilir" daha doğal

3. **Satır 37:**
   - **Eski:** "Her nöron bir önceki katmanın tüm çıktılarını alır, ağırlıklar ve bir bias uygular, sonra sonucu bir aktivasyon fonksiyonundan geçirir."
   - **Yeni:** "Her nöron, bir önceki katmanın tüm çıktılarını alır, ağırlıklar ve bir bias ile çarpıp toplar, ardından sonucu bir aktivasyon fonksiyonundan geçirir."
   - **Neden:** "uygular" belirsiz, "çarpıp toplar" daha teknik olarak doğru

---

## Terminoloji Kontrolü

| Terim | Durum | Not |
|-------|-------|-----|
| nöron | ✅ Tutarlı | 12 kez kullanıldı |
| bias | ✅ Tutarlı | İngilizce olarak bırakıldı |
| ağırlık | ✅ Tutarlı | 8 kez kullanıldı |
| aktivasyon | ✅ Tutarlı | 6 kez kullanıldı |
| sigmoid | ✅ Tutarlı | İngilizce olarak bırakıldı |
| gradyan | ✅ Tutarlı | 4 kez kullanıldı |

---

## Anlaşılabilirlik Analizi

### Olumlu Yönler
- Cümleler kısa ve net
- Teknik terimler doğru kullanılmış
- Kod blokları açıklayıcı
- Adımlar sıralı ve mantıklı

### İyileştirme Alanları
- Bazı cümlelerde "çizer" yerine "çizebilir" daha doğal olurdu
- "çizerici" ifadesi Türkçe değil, "çizebilir" olmalı
- Bazı uzun cümleler bölünebilir

---

## Öneriler

1. **"çizer" → "çizebilir"**: Tüm dosyada tutarlı kullanım
2. **"çizerici" → "çizebilir"**: Türkçe olmayan ifade düzeltilmeli
3. **Uzun cümleler**: 30+ kelimelik cümleler bölünebilir

---

## Proje Geneli (Test)

| Metrik | Değer |
|--------|-------|
| Toplam tr.md | 90 |
| Tam çeviri | 30 |
| Şablon | 60 |
| Tahmini ortalama skor | 78/100 |

---

**Not:** Bu bir test raporudur. Gerçek proofreader-agent, tüm dosyaları otomatik olarak analiz edip düzeltecektir.
