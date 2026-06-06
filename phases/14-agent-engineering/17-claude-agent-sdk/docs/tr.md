# Claude Agent SDK: Subagent'lar ve Oturum Deposu

> Claude Agent SDK, Claude Code harness'ının kitaplık formudur. Yerleşik araçlar, bağlam izolasyonu için subagent'lar, kancalar (hooks), W3C trace propagation, oturum deposu uyumluluğu. Claude Managed Agents, uzun süreli asenkron çalışmalar için barındırılan (hosted) alternatiftir.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 10 (Yetenek Kütüphaneleri)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Anthropic Client SDK (ham API) ile Claude Agent SDK (harness şekli) arasındaki farkı açıklayın.
- Subagent'ları — paralelleştirme ve bağlam izolasyonu — ve ne zaman başvurulacağını tanımlayın.
- Python SDK'sının oturum deposu yüzeyini (`append`, `load`, `list_sessions`, `delete`, `list_subkeys`) ve `--session-mirror`'ın rolünü adlandırın.
- Yerleşik araçlar, izole bağlamla subagent oluşturma, yaşam döngüsü kancaları ve oturum deposuyla stdlib bir harness uygulayın.

## Problem

Ham bir LLM API'si size bir gidiş-dönüş verir. Bir production agent araç çalıştırması, MCP sunucuları, yaşam döngüsü kancaları, subagent oluşturma, oturum kalıcılığı, trace propagation gerektirir. Claude Agent SDK bu şekli bir kitaplık olarak sunar — Claude Code'un kullandığı aynı harness, özel agent'lar için açılmış.

## Kavram

### Client SDK vs Agent SDK

- **Client SDK (`anthropic`).** Ham Messages API. Döngüyü, araçları, state'i siz sahiplenirsiniz.
- **Agent SDK (`claude-agent-sdk`).** Yerleşik araç çalıştırması, MCP bağlantıları, kancalar, subagent oluşturma, oturum deposu. Claude Code döngüsü bir kitaplık olarak.

### Yerleşik araçlar

SDK kutudan 10+ araç sunar: dosya okuma/yazma, shell, grep, glob, web getirme ve daha fazlası. Özel araçlar standart tool-schema arayüzüyle kaydedilir.

### Subagent'lar

Anthropic tarafından belgelenen iki amaç:

1. **Paralelleştirme.** Bağımsız çalışmaları eş zamanlı çalıştırın. "Bu 20 modülün her biri için test dosyasını bul" 20 paralel subagent görevidir.
2. **Bağlam izolasyonu.** Subagent'lar kendi bağlam pencerelerini kullanır; yalnızca sonuçlar orkestratöre döner. Orkestratörün bütçesi korunur.

Python SDK son eklemeler: `list_subagents()`, `get_subagents_messages()` — subagent dökümlerini okumak için.

### Oturum deposu

TypeScript ile protokol uyumluluğu:

- `append(session_id, message)` — bir tur ekleyin.
- `load(session_id)` — konuşmayı geri yükleyin.
- `list_sessions()` — numaralandırın.
- `delete(session_id)` — subagent oturumlarına cascade ile.
- `list_subkeys(session_id)` — subagent anahtarlarını listeleyin.

`--session-mirror` (CLI flag'i), dökümden akarken transkripti bir dış dosyaya yansıtır, hata ayıklama için.

### Kancalar

Kayıt yapabileceğiniz yaşam döngüsü kancaları:

- `PreToolUse`, `PostToolUse` — araç çağrılarını denetleyin veya denetleyin.
- `SessionStart`, `SessionEnd` — kurulum ve temizlik.
- `UserPromptSubmit` — model girdiyi görmeden önce kullanıcı girdisi üzerinde hareket edin.
- `PreCompact` — bağlam sıkıştırmasından önce çalıştırın.
- `Stop` — agent çıkışında temizlik.
- `Notification` — yan kanal uyarıları.

Kancalar, pro-workflow (Faz 14 müfredat referansı) ve benzeri sistemlerin yatay kesen davranışlar eklemesinin yoludur.

### W3C trace context

Çağrııcıda aktif OTel span'ları, W3C trace context header'ları aracılığıyla CLI alt process'ine yayılır. Tüm çoklu-process trace'i arka ucunuzda tek bir trace olarak görünür.

### Claude Managed Agents

Barındırılan alternatif (beta header `managed-agents-2026-04-01`). Uzun süreli asenkron çalışmalar, yerleşik prompt caching, yerleşik sıkıştırma. Kontrolü yönetilen altyapıyla takas edin.

### Bu kalıp nerede yanlış gider

- **Subagent aşırı oluşturma.** 100 küçük görev için 100 subagent oluşturma. Overhead baskın olur. Toplu yapın.
- **Kanca creep.** Her ekip kancalar ekler; başlatma süresi şişer. Kancaları üç aylık olarak inceleyin.
- **Oturum şişmesi.** Oturumlar birikir; boyut büyür. `list_sissions` + son kullanma politikası kullanın.

## İnşa Et

`code/main.py` SDK şeklini stdlib'da uygular:

- `Tool`, `ToolRegistry` — yerleşik `read_file`, `write_file`, `list_dir` ile.
- `Subagent` — özel bağlam, izole çalıştırma, döndürülen sonuçlar.
- `SessionStore` — append, load, list, delete, list_subkeys.
- `Hooks` — `pre_tool_use`, `post_tool_use`, `session_start`, `session_end`.
- Demo: ana agent paralel olarak 3 subagent oluşturur (her biri izole), sonuçları toplar, oturumu kalıcı hale getirir.

Çalıştırın:

```bash
python3 code/main.py
```

Trace subagent bağlam izolasyonunu (orkestratör bağlam boyutu sınırlı kalır), kanca çalıştırmasını ve oturum kalıcılığını gösterir.

## Kullan

- **Claude Agent SDK** Claude Code harness şeklini isteyen Claude-öncelikli ürünler için.
- **Claude Managed Agents** barındırılan uzun süreli asenkron çalışmalar için.
- **OpenAI Agents SDK** (Ders 16) OpenAI-öncelikli karşılıklar için.
- **LangGraph + özel araçlar** graf şeklindeki durum makinesini istiyorsanız.

## Teslim Et

`outputs/skill-claude-agent-scaffold.md` subagent'lar, kancalar, oturum deposu, MCP sunucu eki ve W3C trace propagation ile bir Claude Agent SDK uygulaması iskeletler.

## Alıştırmalar

1. 20 görevi 5'er paralel subagent gruplarına bölen bir subagent oluşturucu ekleyin. Orkestratör bağlam boyutunu görev başına bire göre ölçün.
2. `write_file` çağrılarını (dakikada oturum başına 5) sınırlayan bir `PreToolUse` kancası uygulayın.
3. `list_subkeys`'i bir subagent ağacı oluşturacak şekilde bağlayın. Derin iç içe geçme nasıl görünür?
4. Toy kodu gerçek `claude-agent-sdk` Python paketine taşıyın. Araç kaydında ne değişir?
5. Claude Managed Agents dokümanlarını okuyun. Ne zaman self-hosted'dan yönetilene geçersiniz?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Agent SDK | "Claude Code kitaplık olarak" | Harness şekli: araçlar, MCP, kancalar, subagent'lar, oturum deposu |
| Subagent | "Çocuk agent" | Ayrı bağlam, kendi bütçesi; sonuçlar yukarı kabarcıklanır |
| Session store | "Konuşma DB'si" | Turları subagent cascade ile kalıcı hale getir, yükle, listele, sil |
| Hook | "Yaşam döngüsü geri çağrısı" | Pre/post araç, oturum, prompt gönderme, sıkıştırma, durdurma |
| W3C trace context | "Çapraz-process trace" | Ana span CLI alt process'ine yayılır |
| Managed Agents | "Barındırılan harness" | Anthropic tarafından barındırılan uzun süreli asenkron çalışmalar |
| `--session-mirror` | "Transkript yansıması" | Oturum turlarını akarken dış dosyaya yazar |
| MCP server | "Araç yüzeyi" | Agent'a eklenen harici araç/kaynak kaynağı |

## İleri Okuma

- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview) — Claude Code'un kitaplık formu
- [Anthropic, Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — production kalıpları
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview) — barındırılan alternatif
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — karşılık
