# Katkıda Bulunma

Dersler, çeviriler, düzeltmeler, çıktılar — hepsi kabul edilir. Her pull request'te
tek bir katkı olması incelemeyi hızlı tutar ve katkıcı sayılarıyla atıfların
doğru çalışmasını sağlar.

## Önemli: README ve ROADMAP siteyi besler

`site/build.js`, `README.md`, `ROADMAP.md` ve `glossary/terms.md` dosyalarını
işleyerek `site/data.js` üretir. Bu dosyalara dokunan herhangi bir pull request'te
iki kalıbın bozulmaması gerekir:

- Faz başlıkları ya `### Faz N: Ad \`X ders\`` biçiminde ya da
  `<details><summary><b>Faz N — Ad</b> ... <code>X ders</code> ... <em>Açıklama</em></summary></details>` biçiminde olmalıdır.
- Ders tabloları `| # | Ders | Tür | Dil |` sütun yapısında olmalıdır
  (capstone tabloları için `| # | Proje | Birleştirir | Dil |`). `Dil` sütunu
  düz metin (`Python, TypeScript`) ya da eski emoji bayraklarını
  (`🐍 🟦 🦀 🟣 ⚛️`) kabul eder; her ikisi de işleyici için eşdeğerdir.
- ROADMAP durum glifleri (`✅`, `🚧`, `⬚`) faz başlıklarında ve ders
  satırlarında kullanılır. Bunları metinle değiştirmeyin — işleyici tam olarak bu
  karakterleri arar.

Bu dosyaları düzenledikten sonra `node site/build.js` komutunu çalıştırın;
`git diff site/data.js` yalnızca zaman damgası değişikliği göstermelidir — bu,
düzenlemenizin yapısal olarak güvenli olduğu anlamına gelir.

## Katkı Türleri

### 1. Yeni Bir Ders Eklemek

Her ders `phases/XX-faz-adi/NN-ders-adi/` altında şu yapıyla bulunur:

```
NN-ders-adi/
├── code/           En az bir çalıştırılabilir uygulama
├── notebook/       Deney için Jupyter notebook (isteğe bağlı)
├── docs/
│   └── en.md       Ders dokümantasyonu (zorunlu)
└── outputs/        Bu dersin ürettiği prompt, skill veya agent (varsa)
```

**Ders doküman formatı** (`en.md`):

```markdown
# Lesson Title

> One-line motto — the core idea in one sentence.

## The Problem

Why does this matter? What can't you do without this?

## The Concept

Explain with diagrams, visuals, and intuition. Code comes later.

## Build It

Step-by-step implementation from scratch.

## Use It

Now use a real framework or library to do the same thing.

## Ship It

The prompt, skill, agent, or tool this lesson produces.

## Exercises

1. Exercise one
2. Exercise two
3. Challenge exercise
```

### 2. Çeviri Eklemek

Herhangi bir dersin `docs/` klasöründe yeni bir dosya oluşturun:

```
docs/
├── en.md    (İngilizce — her zaman zorunlu)
├── zh.md    (Çince)
├── ja.md    (Japonca)
├── es.md    (İspanyolca)
├── hi.md    (Hintçe)
├── tr.md    (Türkçe)
└── ...
```

İngilizce sürümle aynı yapıyı koruyun. İçeriği çevirin, kodu değil.

### 3. Çıktı Eklemek

Bir ders yeniden kullanılabilir bir prompt, skill, agent veya MCP sunucusu üretiyorsa:

1. Dersin `outputs/` klasöründe oluşturun
2. Üst seviye `outputs/` dizinine bir referans ekleyin

**Prompt formatı:**

```markdown
---
name: prompt-name
description: What this prompt does
phase: 14
lesson: 01
---

[System prompt or template here]
```

**Skill formatı:**

```markdown
---
name: skill-name
description: What this skill teaches
version: 1.0.0
phase: 14
lesson: 01
tags: [agents, loops]
---

[Skill content here]
```

### 4. Hata Düzeltmek veya Mevcut Dersleri İyileştirmek

- Çalışmayan kodu düzeltin
- Açıklamaları iyileştirin
- Daha iyi diyagramlar ekleyin
- Güncelliğini yitirmiş bilgileri güncelleyin

### 5. Alıştırma veya Proje Eklemek

Daha fazla alıştırma ve proje her zaman kabul edilir, özellikle birden fazla fazı birleştirenler.

## Kurallar

- **Kod çalışmalı.** Her kod dosyası, listelenen bağımlılıklarla hatasız çalışmalıdır.
- **Kodda yorum olmaz.** Kod kendi kendini açıklamalıdır. Açıklama için dokümantasyonu kullanın.
- **İş için en uygun dil.** TypeScript veya Rust'ın daha iyi seçim olduğu yerde Python'ı zorlamayın.
- **Önce sıfırdan inşa edin.** Framework sürümünü göstermeden önce kavramı her zaman temel prensiplerden uygulayın.
- **Pratik kalın.** Teori pratiğe hizmet eder, tersi değil.
- **Yapay zeka çöpü olmasın.** İnsan gibi yazın. Doğrudan olun. Dolguyu kesin.

## Pull Request Süreci

1. Repo'yu fork'layın
2. Bir feature branch oluşturun (`git checkout -b add-lesson-phase3-gradient-descent`)
3. Değişikliklerinizi yapın
4. Tüm kodun çalıştığından emin olun
5. Açık bir açıklamayla pull request gönderin

## Davranış Kuralları

Bkz. [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Nazik olun, yardımsever olun, yapıcı olun.

## Stil

- Doğrudan ifade. Dolguyu kesin. Pazarlama metni değil, kılavuzun tonunu yakalayın.
- Başlıklarda dekoratif emoji kullanmayın. Dil sütunundaki emoji bayrakları tek
  istisnadır ve yalnızca işleyici onları eşlediği için kullanılır.
- Kod, derste listelenen bağımlılıklarla olduğu gibi çalışır.
- Önce sıfırdan inşa edin, framework ikinci sırada.

