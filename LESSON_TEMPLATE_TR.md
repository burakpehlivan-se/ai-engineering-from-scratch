# Ders Şablonu

Yeni bir ders oluştururken bu şablonu kullanın. Dizin yapısını kopyalayın ve içeriği doldurun.

## Dizin Yapısı

```
NN-ders-adı/
├── code/
│   ├── main.py            (birincil uygulama)
│   ├── main.ts            (TypeScript sürümü, varsa)
│   ├── main.rs            (Rust sürümü, varsa)
│   └── main.jl            (Julia sürümü, varsa)
├── notebook/
│   └── lesson.ipynb       (deneme için Jupyter defteri)
├── docs/
│   └── en.md              (ders dokümantasyonu)
└── outputs/
    ├── prompt-*.md         (bu dersin ürettiği istemler)
    └── skill-*.md          (bu dersin ürettiği beceriler)
```

## Dokümantasyon Biçimi (docs/en.md)

```markdown
# [Ders Başlığı]

> [Tek satırlık motto — akılda kalıcı temel fikir]

**Tür:** Uygulama | Öğrenme
**Diller:** Python, TypeScript, Rust, Julia (kullanılanları listele)
**Ön Koşullar:** [Gerekli önceki dersler]
**Süre:** ~[tahmini süre] dakika

## Sorun

[2-3 paragraf. Bunu bilmeden ne yapamazsınız? Neden umursamalısınız?
Somut olun — bunu bilmemenin zarar verdiği bir senaryo gösterin.]

## Kavram

[Shemalar ve sezgiyle açıklayın. Henüz kod yok.
ASCII şemaları, tablolar veya web uygulamasındaki görsellere bağlantı kullanın.
Uygulamadan önce zihinsel modeller oluşturun.]

## Uygulama

[Sıfırdan adım adım uygulama.
En basit sürümle başlayın, sonra karmaşıklık ekleyin.
Her kod bloğu kendi başına çalıştırılabilir olmalı.]

### Adım 1: [Ad]

[Açıklama]

    [kod bloğu]

### Adım 2: [Ad]

[Açıklama]

    [kod bloğu]

[...devam edin...]

## Kullanım

[Şimdi çerçeve/kütüphanelerin aynı şeyi nasıl yaptığını gösterin.
Sıfırdan yazdığınız sürümü kütüphane sürümüyle karşılaştırın.
Bu, kavramı kanıtlar ve pratik araçları tanıştırır.]

## Teslimat

[Bu ders hangi yeniden kullanılabilir ürünü üretiyor?
Bir istem, beceri, ajan, MCP sunucusu veya araç olabilir.
Buraya ekleyin ve outputs/ klasörüne kaydedin.]

## Alıştırmalar

1. [Kolay — temel pekiştirme]
2. [Orta — farklı bir soruna uygulama]
3. [Zor — genişletme veya önceki derslerle birleştirme]

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| [terim] | [yaygın yanlış anlama] | [gerçek tanım] |

## İleri Okuma

- [Kaynak 1](url) — [neden okumaya değer]
- [Kaynak 2](url) — [neden okumaya değer]
```

## Kod Dosyası Kuralları

- Kod hatasız çalışmalı
- Yorum olmamalı — kod kendini açıklamalı
- Konu için en uygun dili kullanın
- Bağımlılıklar varsa `requirements.txt` veya eşdeğeri ekleyin
- Basit başlayın, karmaşıklığı artırın
- Her fonksiyon ve sınıfın net bir amacı olmalı

## Çıktı Dosyası Biçimi

### İstemler

```markdown
---
name: istem-adı
description: Bu istemin ne yaptığı
phase: [faz numarası]
lesson: [ders numarası]
---

[İstem içeriği]
```

### Beceriler

```markdown
---
name: beceri-adı
description: Bu becerinin öğrettiği şey
version: 1.0.0
phase: [faz numarası]
lesson: [ders numarası]
tags: [ilgili, etiketler]
---

[Beceri içeriği]
```
