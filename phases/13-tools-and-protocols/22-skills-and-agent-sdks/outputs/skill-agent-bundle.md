---
name: agent-bundle
description: Bir workflow için Claude Code, Cursor, Codex ve uyumlu agent'lar arasında yüklenebilir, taşınabilir bir SKILL.md + AGENTS.md + MCP-server blueprint üret.
version: 1.0.0
phase: 13
lesson: 21
tags: [skills, agents-md, apps-sdk, cross-agent, portability]
---

Bir workflow açıklaması verildiğinde, bir agent bundle üret.

Şunları üret:

1. SKILL.md. `name` ve `description` içeren YAML frontmatter, numaralı adımlar içeren markdown gövdesi. Gövde uzunsa progressive-disclosure subresource referansları ekle.
2. AGENTS.md girdisi. Skill'in bağımlı olduğu konvansiyonları (linter komutları, test komutları) yansıtarak repo'nun AGENTS.md'sine eklenecek birkaç satır.
3. MCP server blueprint. Skill'in MCP üzerinden çağırdığı tool'lar; isim, açıklama (Use-when deseni) ve input schema.
4. Cross-agent çevirileri. Bu SKILL.md'nin Cursor rules'a, Codex `.codex.md`'ye, Windsurf rules'a nasıl eşlendiğine dair SkillKit tarzı notlar.
5. Yükleme yolu. Agent'ların bu bundle'ı nerede keşfedeceği: `~/.anthropic/skills/`, `./skills/`, `~/.claude/skills/`.

Sert reject sebepleri:
- `name`'i `kebab-case` olmayan herhangi bir SKILL.md. Discovery'yi bozar.
- Frontmatter'da `description` içermeyen herhangi bir SKILL.md. Agent runtime'ları onu atlar.
- MCP tool'ları Faz 13 · 05 kurallarına göre adlandırılmamış herhangi bir bundle.

Refusal kuralları:
- Workflow tek seferlik bir prompt ise, bir skill üretmeyi reddet; inline prompt-engineering öner.
- Workflow OAuth gerektiriyorsa (örn. Slack post), MCP server'ın ilk çalıştırma elicitation'ının bunu halletmesi gerektiğini işaretle.
- Hedef agent'lar SKILL.md'yi desteklemiyorsa (bazı IDE'ler), SkillKit veya benzeri ile çeviri öner.

Çıktı: üç dosyanın taslakları, cross-agent çeviri notları ve yükleme yolu içeren tek sayfalık bir bundle. Bundle'ı ilk önce hangi agent'ta test etmen gerektiğine dair tek bir öneriyle bitir.
