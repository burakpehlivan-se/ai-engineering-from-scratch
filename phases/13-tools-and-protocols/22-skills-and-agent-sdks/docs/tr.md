# Yetenekler ve Ajan SDK'ları — Anthropic Yetenekleri, AGENTS.md, OpenAI Apps SDK

> MCP "hangi araçlar var" der. Yetenekler "bir görev nasıl yapılır" der. 2026 yığını her ikisini de katmanlar. Anthropic'in Agent Skills'i (açık standart, Aralık 2025) kademeli ifşa ile SKILL.md olarak yayınlanır. OpenAI'ın Apps SDK'sı MCP artı widget meta verisidir. AGENTS.md (şimdi 60.000+ depoda) proje düzeyinde ajan bağlamı olarak depo kökünde oturur. Bu ders her birinin neyi kapsadığını isimlendirir ve ajanlar arasında dolaşan minimal bir SKILL.md + AGENTS.md paketi oluşturur.

**Tür:** Öğren
**Diller:** Python (stdlib, SKILL.md ayrıştırıcısı ve yükleyicisi)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu)
**Süre:** ~45 dakika

## Öğrenme Hedefleri

- Üç katmanı ayırt et: AGENTS.md (proje bağlamı), SKILL.md (yeniden kullanılabilir bilgi), MCP (araçlar).
- Kademeli ifşayla YAML ön yüzü (frontmatter) içeren bir SKILL.md yaz.
- Yetenekleri dosya sistemi tarzında bir ajan çalışma zamanına yükle.
- Bir yeteneği bir MCP sunucusu ve bir AGENTS.md ile birleştir, böylece tek paket Claude Code, Cursor ve Codex'te çalışsın.

## Sorun

Bir mühendis, bir sürüm notları yazma iş akışını çok adımlı bir prompt'a dönüştürür: "En son birleştirilmiş PR'ları oku. Alana göre grupla. Her birini özetle. Takımın tarzını takip ederek bir changelog girişi yaz. Slack taslağına gönder." Bunu ekip için bir Notion belgesine koyarlar.

Şimdi bu iş akışını Claude Code, Cursor ve Codex CLI'dan kullanmak istiyorlar. Her ajan talimatları yüklemenin farklı bir yoluna sahip: Claude Code slash-komutları, Cursor kuralları, Codex `.codex.md`. Mühendis iş akışını üç kez kopyalar ve üç kopyayı sürdürür.

AGENTS.md ve SKILL.md birlikte bunu düzeltir:

- **AGENTS.md** depo kökünde oturur. Uyumlu her ajan oturum başlangıcında okur. "Bu proje nasıl çalışıyor? Kurallar neler? Hangi komutlar testleri çalıştırır?"
- **SKILL.md** taşınabilir bir pakettir: YAML ön yüzü (ad, açıklama) + markdown gövdesi + isteğe bağlı kaynaklar. Yetenekleri destekleyen ajanlar bunları talep üzerine adla yükler.
- **MCP** (Faz 13 · 06-14), yeteneğin çağırmak istediği araçları ele alır.

Üç katman, tek taşınabilir sanat eseri.

## Kavram

### AGENTS.md (agents.md)

2025 sonunda yayınlandı, Nisan 2026'ya kadar 60.000+ depo tarafından benimsendi. Depo kökünde tek dosya. Biçim:

```markdown
# Proje: my-service

## Kurallar
- TypeScript ile strict mod.
- Python tarafında modeller için Pydantic kullanın.
- Testler `pnpm test` ile çalıştırılır.

## Oluştur ve çalıştır
- Yerel geliştirme sunucusu için `pnpm dev`.
- Üretim paketi için `pnpm build`.
```

Ajanlar bunu oturum başlangıcında okur ve o proje için davranışlarını ayarlar. 2026'daki her kodlama ajanı AGENTS.md'yi destekler: Claude Code, Cursor, Codex, Copilot Workspace, opencode, Windsurf, Zed.

### SKILL.md biçimi

Anthropic'in Agent Skills'i (Aralık 2025'te açık standart olarak yayınlandı):

```markdown
---
name: release-notes-writer
description: En son birleştirilmiş PR'lar için bu projenin tarzını takip ederek bir changelog girişi yazın.
---

# Sürüm notları yazarı

Çağrıldığında şu adımları çalıştırın:

1. Son etiketten beri birleştirilmiş PR'ları listeleyin. `gh pr list --base main --state merged` kullanın.
2. Etikete göre gruplayın: feature, fix, chore, docs.
3. Her grup içindeki her PR için bir satır yazın: `- <başlık> (#<numara>)`.
4. Sürüm notlarını taslak olarak çıkarın ve CHANGELOG.md'ye yerleştirin.

Kullanıcı "yayınla" derse, `git tag vX. Y. Z` ve `gh release create` çalıştırın.

## Notlar

- PR'siz asla commit dahil etmeyin.
- Herkese açık changelog'dan "chore" girişlerini atlayın.
```

Ön yüz, yeteneğin kimliğini beyan eder. Gövde, yetenek yüklendiğinde modele gösterilen prompt'tur.

### Kademeli ifşa (Progressive disclosure)

Yetenekler, yalnızca gerekli olduğunda çekilen alt kaynaklara atıfta bulunabilir. Örnek:

```
skills/
 release-notes-writer/
 SKILL.md
 style-guide.md
 template.md
 scripts/
 generate.sh
```

SKILL.md "stil kuralları için style-guide.md'ye bakın" der. Ajan, style-guide.md'yi yalnızca yetenek aktif olarak çalışırken çeker. Bu, modelin gerekmeyebilecek detaylarla prompt'un şişmesini önler.

### Dosya sistemi keşfi

Ajan çalışma zamanları, bilinen dizinleri SKILL.md dosyaları için tarar:

- `~/.anthropic/skills/*/SKILL.md`
- Proje `./skills/*/SKILL.md`
- `~/.claude/skills/*/SKILL.md`

Yükleme klasör adı ve ön yüz `name` ile yapılır. Claude Code, Anthropic Claude Agent SDK ve SkillKit (çapraz-ajan) bu paterni takip eder.

### Anthropic Claude Agent SDK

`@anthropic-ai/claude-agent-sdk` (TypeScript) ve `claude-agent-sdk` (Python) yetenekleri oturum başlangıcında yükler, çalışma zamanında çağrılabilir "ajan" olarak sunar. Ajan döngüsü, kullanıcı çağırdığında bir yeteneğe dağıtır.

### OpenAI Apps SDK

Ekim 2025'te yayınlandı; doğrudan MCP üzerine inşa edildi. OpenAI'ın önceki Connectors ve Custom GPT Actions'larını tek bir geliştirici yüzeyi altında birleştirir. Bir Apps SDK uygulaması:

- Bir MCP sunucusu (araçlar, kaynaklar, istemler).
- ChatGPT UI'sı için widget meta verisi.
- İsteğe bağlı bir MCP Apps `ui://` kaynağı etkileşimli yüzeyler için.

Aynı protokol, daha zengin UX.

### SkillKit aracılığıyla çapraz-ajan taşınabilirliği

SkillKit ve benzeri çapraz-ajan dağıtım katmanları gibi araçlar, tek bir SKILL.md'yi 32+ AI ajanının (Claude Code, Cursor, Codex, Gemini CLI, OpenCode vb.) yerel biçimine dönüştürür. Tek gerçek kaynağı; birçok tüketici.

### Üç katmanlı yığın

| Katman | Dosya | Ne zaman yüklenir | Amaç |
|-------|------|-------------|---------|
| AGENTS.md | depo kökü | oturum başlangıcı | proje düzeyinde kurallar |
| SKILL.md | yetenekler dizini | yetenek çağrıldığında | yeniden kullanılabilir iş akışı |
| MCP sunucusu | harici süreç | araçlar gerektiğinde | çağrılabilir eylemler |

Üçü de birleşik: ajan oturum başlangıcında AGENTS.md'yi okur, kullanıcı bir yeteneği çağırır, yeteneğin talimatları MCP araç çağrılarını içerir, ajan bir MCP istemcisi aracılığıyla dağıtır.

## Kullan

`code/main.py`, stdlib bir SKILL.md ayrıştırıcısı ve yükleyicisi sunar. `./skills/` altında yetenekleri keşfeder, YAML ön yüzünü artı markdown gövdesini ayrıştırır ve yetenek adıyla anahtarlanmış bir dict üretir. Ardından `release-notes-writer`'ı adla çağıran bir ajan döngüsünü simüle eder.

Neye bakılmalı:

- YAML ön yüzü minimal stdlib ayrıştırıcısıyla ayrıştırılır (`pyyaml` bağımlılığı yok).
- Yetenek gövdesi birebir saklanır; ajan, çağırmada onu system prompt'unun başına ekler.
- Kademeli ifşa, başvurulan dosyaları talep üzerine çeken `read_subresource` fonksiyonuyla gösterilir.

## Sun

Bu ders `outputs/skill-agent-bundle.md` dosyasını üretir. Bir iş akışı verildiğinde, beceri birleşik SKILL.md + AGENTS.md + MCP-sunucu-planı paketini üretir, ajanlar arasında taşınabilir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın. `skills/` altında ikinci bir yetenek ekleyin ve yükleyicinin bunu aldığını doğrulayın.

2. Bu ders depo için bir AGENTS.md yazın. Test komutları, stil kuralları ve Faz 13 zihinsel modeli dahil edin.

3. Ekibinizin iç belgelerinden çok adımlı bir iş akışını bir SKILL.md'ye taşıyın. Claude Code'da yüklendiğini doğrulayın.

4. Yeteneği elle Cursor'ın ve Codex'in yerel kural biçimlerine çevirin. Biçimler arasındaki farkı sayın — bu, SkillKit'in otomatikleştirdiği çeviri yüzeyidir.

5. Anthropic Agent Skills blog yazısını okuyun. Bu dersin yükleyicisinin kapsmadığı Claude Agent SDK'daki bir özelliği belirleyin. (İpucu: ajan alt-çağrısı.)

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| SKILL.md | "Yetenek dosyası" | YAML ön yüzü artı markdown gövdesi, ajan çalışma zamanı tarafından yüklenir |
| AGENTS.md | "Depo-kökü ajan bağlamı" | Oturum başlangıcında okunan proje düzeyinde kurallar dosyası |
| Progressive disclosure (Kademeli ifşa) | "Alt kaynakları tembel yükle" | Yetenek gövdesi, yalnızca gerekli olduğunda çekilen dosyalara atıfta bulunur |
| Frontmatter | "En üstteki YAML bloğu" | `---` sınırlayıcılarında meta veri (ad, açıklama) |
| Claude Agent SDK | "Anthropic'in yetenek çalışma zamanı" | `@anthropic-ai/claude-agent-sdk`, yetenekleri yükler ve yönlendirir |
| OpenAI Apps SDK | "MCP artı widget meta" | MCP üzerine inşa edilmiş, ChatGPT UI kancaları eklenmiş OpenAI geliştirici yüzeyi |
| Skill discovery (Yetenek keşfi) | "Dosya sistemi taraması" | Bilinen dizinlerde SKILL.md'yi yürü, adla anahtarla |
| Cross-agent portability (Çapraz-ajan taşınabilirliği) | "Bir yetenek birçok ajan" | Tek SKILL.md'yi SkillKit tarzı araçlarla 32+ ajan çevirir |
| Agent Skill (Ajan Yeteneği) | "Taşınabilir bilgi" | MCP'nin araç kavramının dışında yeniden kullanılabilir görev şablonu |
| Apps SDK | "MCP artı ChatGPT UI" | Connectors ve Custom GPT'ler MCP'de birleştirildi |

## İleri Okuma

- [Anthropic — Agent Skills announcement](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — Aralık 2025 lansmanı
- [Anthropic — Agent Skills docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — SKILL.md biçimi referansı
- [OpenAI — Apps SDK](https://developers.openai.com/apps-sdk) — ChatGPT için MCP tabanlı geliştirici platformu
- [agents.md](https://agents.md/) — AGENTS.md biçimi ve benimseme listesi
- [Anthropic — anthropics/skills GitHub](https://github.com/anthropics/skills) — resmiyet yetenek örnekleri
