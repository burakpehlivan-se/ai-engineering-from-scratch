# Yetenekler ve Ajan SDKs  Antropik Yetenekler, AGENTS.md, OpenAI Apps SDK

> MCP, "ne tür araçlar var" diyor. "Beceriler, "bir görevi nasıl yapacağımı" söylüyor. 2026'da her iki katman da var. Anthropic'in Agent Skills (açık standart, Aralık 2025) gelişmiş açıklama ile SKILL.md olarak gemiye gönderilir. OpenAI'nin Apps SDK'si MCP + widget metadataları. AGENTS.md (şimdi 60,000+ repo) proje düzeyinde ajan bağlamı olarak repo kökeninde yer alır. Bu ders her birinin kapsamını belirler ve ajanlar arasında seyahat eden minimal bir SKILL.md + AGENTS.md paketi oluşturur.

**Type:** Learn
**Languages:** Python (stdlib, SKILL.md parser and loader)
**Prerequisites:** Phase 13 · 07 (MCP server)
**Time:** ~45 minutes

## Öğrenme Hedefleri

- Üç katman ayırt edin: AGENTS.md (proje bağlamı), SKILL.md (yeniden kullanılabilir bilgi) ve MCP (üçereler).
- YAML ön yazısı ve ilerleyen açıklama ile bir SKILL.md yazın.
- Bilgiler dosya sistemini bir ajan çalıştırma süresine yükle.
- Bir MCP sunucusu ve bir AGENTS.md ile bir beceri oluşturun böylece bir paket Claude Code, Cursor ve Codex'ta çalışır.

## Sorun

Bir mühendis bir açıklama not yazma iş akışını çok adımlı bir istekle destekliyor: "En son birleşmiş PR'leri okuyun. Bölgeye göre gruplayın. Her birini özetleyin. Takımın tarzına göre bir değişim logunu yazın. Slack taslakına gönderin. "

Şimdi Claude Code, Cursor ve Codex CLI'den bu iş akışını kullanmak istiyorlar.`.codex.md`Mühendis iş akışını üç kez kopyalayıp üç kopyası korur.

AGENTS.md ve SKILL.md birlikte bunu düzeltecek:

- **AGENTS.md**Bu programın başlamasından sonra, her uyumlu ajan, bu yazıyı okuyor. "Bu proje nasıl çalışır?
- **SKILL.md**YAML ön maddesini (ad, açıklama) + işaretleme bedenini + seçmeli kaynakları.
- **MCP**(Fase 13 · 06-14) becerinin kullanması gereken araçları ele alıyor.

Üç kat, bir taşınabilir eser.

## Anlaşım

### AGENTS.md (agents.md)

2025'in sonlarında başlatıldı, Nisan 2026'a kadar 60.000+ repo tarafından kabul edildi.

```markdown
# Project: my-service

## Conventions
- TypeScript with strict mode.
- Use Pydantic for models on the Python side.
- Tests run with `pnpm test`.

## Build and run
- `pnpm dev` for local dev server.
- `pnpm build` for production bundle.
```

Bu yazıyı, 2026 yılında tüm kodlama ajanları destekleyecek.

### SKILL.md biçimi

Anthropic'in Ajan becerileri (Açık bir standart olarak Aralık 2025'te yayınlandı):

```markdown
---
name: release-notes-writer
description: Write a changelog entry for the latest merged PRs following this project's style.
---

# Release notes writer

When invoked, run these steps:

1. List PRs merged since the last tag. Use `gh pr list --base main --state merged`.
2. Group by label: feature, fix, chore, docs.
3. For each PR in each group, write one line: `- <title> (#<num>)`.
4. Draft the release notes and stage them in CHANGELOG.md.

If the user says "ship", run `git tag vX.Y.Z` and `gh release create`.

## Notes

- Never include commits without a PR.
- Skip "chore" entries from the public changelog.
```

Ön madde, beceri kimliğini açıklar.

### Gelişmiş açıklama

Yetenekler, ajanın sadece gerektiğinde alacağı alt kaynaklara atıfta bulunabilir.

```
skills/
  release-notes-writer/
    SKILL.md
    style-guide.md
    template.md
    scripts/
      generate.sh
```

SKILL.md, "stil kuralları için stil-guide.md'yi görün". diyor. Ajan stil-guide.md'i yalnızca yetenek aktif olarak çalıştırıldığında çekir. Bu, modelin ihtiyaç duymayabileceği ayrıntılarla isteklenmeyi önler.

### Dosya sistemi keşfi

Ajan çalıştırma zamanları SKILL.md dosyaları için bilinen dizinleri tarar:

- `~/.anthropic/skills/*/SKILL.md`
- Proje`./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

Güçlendirme klasör adı ve ön madde ile yapılır `name`Claude Code, Anthropic Claude Agent SDK ve SkillKit (çapış ajan) hepsi bu örneği izler.

### Antropik Claude Ajan SDK

`@anthropic-ai/claude-agent-sdk`(TypeScript) ve `claude-agent-sdk`(Python) seans başlamasındaki becerileri yükle, onları çalıştırma süresi içinde çağırabilir "ajanlar" olarak ortaya çıkar.

### OpenAI Apps SDK

Ekim 2025'te başlatıldı; doğrudan MCP'de inşa edildi. OpenAI'nin önceki Bağlantıları ve Özel GPT Eylemlerini tek bir geliştiriciler yüzeyi altında birleştirir.

- Bir MCP sunucusu (üçergeleri, kaynakları, istekleri).
- Ayrıca ChatGPT'nin kullanıcı aracına ait meta veriler.
- Ayrıca seçeneği olan MCP Uygulamaları `ui://`Etkin yüzeyler için kaynak.

Aynı protokol, daha zengin bir UX.

### SkillKit üzerinden ajanlar arası taşınabilirlik

SkillKit gibi araçlar ve benzer ajan çaplı dağıtım katmanları tek bir SKILL.md'i 32+ AI ajanının her birinin (Claude Code, Cursor, Codex, Gemini CLI, OpenCode, vb.) ana formatına çevirir.

### Üç katlı yığın

| Layer | File | Loaded when | Purpose |
|-------|------|-------------|---------|
| AGENTS.md | repo root | session start | project-level conventions |
| SKILL.md | skills directory | skill invoked | reusable workflow |
| MCP server | external process | tools needed | callable actions |

Üçü de oluşturulur: ajan seansın başlaması sırasında AGENTS.md okuyor, kullanıcı bir beceri çağrıştırıyor, beceri talimatları MCP araç çağrılarını içerir, ajan bir MCP istemcisi üzerinden gönderir.

```figure
t3-skill-layers
```

## Kullan

`code/main.py`STDlib SKILL.md analiz ve yükleme cihazı kullanıyor.`./skills/`YAML ön maddesini ve işaretleme bedenini analiz eder ve yetenek isimleriyle belirlenen bir dikte oluşturur.`release-notes-writer`Adıyla.

Neye bakılır:

- YAML ön maddesini minimal bir stdlib analizörü ile analiz ediliyor (hayır)`pyyaml`bağımlılık).
- Bilgi vücudu sözde saklanır. Ajan çağrısı üzerine sistem uyarısına hazırlanır.
- Bir  `read_subresource`İsteğe bağlı olarak referans dosyaları çeken bir işlev.

## Gönder

Bu ders bize çok yararlı .`outputs/skill-agent-bundle.md`. İş akışı verildiğinde, beceriler, ortaklıklara taşınabilir olan SKILL.md + AGENTS.md + MCP-server-blueprint paketini oluşturur.

## Egzersizler

1. Çık .`code/main.py`İkinci bir beceri ekle .`skills/`ve yükleme cihazının onu aldığını onayla.

2. Bu kurs repo için bir AGENTS.md yaz. Test komutları, stil konvensiyonları ve 13. aşama zihinsel modeli dahil edin.

3. Ekibinizin iç belgeleriyle çok adımlı bir iş akışını SKILL.md'e aktarın.

4. Bu, çevirme yüzeyinin SkillKit otomatikleri.

5. Antropic Agent Skills blog yazısını okuyun. Claude Agent SDK'de bu dersin yükleme cihazının kapsamadığı bir özelliği belirleyin.

## Anahtar Terimler

| Term | What people say | What it actually means |
|------|----------------|------------------------|
| SKILL.md | "The skill file" | YAML frontmatter plus markdown body, loaded by agent runtime |
| AGENTS.md | "Repo-root agent context" | Project-level conventions file read on session start |
| Progressive disclosure | "Lazy-load sub-resources" | Skill body references files pulled only when needed |
| Frontmatter | "YAML block at top" | Metadata (name, description) in `---` delimiters |
| Claude Agent SDK | "Anthropic's skill runtime" | `@anthropic-ai/claude-agent-sdk`, loads skills and routes |
| OpenAI Apps SDK | "MCP + widget meta" | OpenAI's dev surface built on MCP plus ChatGPT UI hooks |
| Skill discovery | "Filesystem scan" | Walk known dirs for SKILL.md, key by name |
| Cross-agent portability | "One skill many agents" | Translate one SKILL.md to 32+ agents via SkillKit-style tools |
| Agent Skill | "Portable know-how" | Reusable task template outside MCP's tool concept |
| Apps SDK | "MCP plus ChatGPT UI" | Connectors and Custom GPTs unified on MCP |

## Daha Fazla Okumak

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) Aralık 2025'te başlatılmak
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) SKILL.md biçimi referansı
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) ChatGPT için MCP tabanlı geliştiriciler platformu
- [agents.md](https://agents.md/) AGENTS.md biçimi ve kabul listesi
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) Resmi beceri örnekleri
