# Capstone 01 — Terminal-Native (Terminal-uyumlu) Coding Agent (Kodlama Ajanı)

> 2026 itibarıyla kodlama ajanlarının şekli yerleşti: bir TUI (terminal kullanıcı arayüzü) çatısı (harness), durum bilgisi olan bir plan, korumalı (sandboxed) bir tool yüzeyi, planla-eyle-gözle-toparla döngüsü. Claude Code, Cursor 3 ve OpenCode 50 adım öteden bakıldığında hep aynı görünüyor. Bu capstone sizden uçtan uca bir tane inşa etmenizi istiyor — CLI girdi, pull request çıktı — ve onu mini-swe-agent ile Live-SWE-agent üzerinde SWE-bench Pro'da kıyaslamanızı. Zor kısmın model çağrısı değil, tool döngüsü, korumalı alan (sandbox) ve 50 dönüşlük bir çalıştırmadaki maliyet tavanı olduğunu öğreneceksiniz.

**Type:** Capstone
**Languages:** TypeScript / Bun (harness), Python (eval betikleri)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and protocols), Phase 14 (agents), Phase 15 (autonomous systems), Phase 17 (infrastructure)
**Phases exercised:** P0 · P5 · P7 · P10 · P11 · P13 · P14 · P15 · P17 · P18
**Time:** 35 saat

## Problem

Kodlama ajanları 2026'da baskın yapay zekâ uygulama kategorisi oldu. Claude Code (Anthropic), Cursor 3 (Composer 2 ve Agent Tabs ile — Cursor), Amp (Sourcegraph), OpenCode (112k yıldız), Factory Droids ve Google Jules hep aynı mimarinin varyasyonlarını yayınlıyor: bir terminal çatısı, izinli bir tool yüzeyi, bir korumalı alan ve bir frontier (en ileri) model etrafında kurulmuş planla-eyle-gözle-toparla döngüsü. Sınır dar — Live-SWE-agent Opus 4.5 ile SWE-bench Verified'da %79,2'ye ulaştı — ama mühendislik zanaatı geniş. Çoğu hata modu model hatası değil. Bunlar tool döngüsü kararsızlığı, bağlam zehirlenmesi, kontrolden çıkan token maliyeti ve yıkıcı dosya sistemi işlemleri.

Bu ajanları dışarıdan tartışamazsınız. Bir tane inşa etmeli, ripgrep 8 MB eşleşme döndürdüğünde 47. dönüşte döngünün çöktüğünü izlemeli ve kırpma katmanını yeniden inşa etmelisiniz. Bu capstone'ın amacı bu.

## Concept

Çatının dört yüzeyi var. **Plan**, modelin her dönüşte yeniden yazdığı TodoWrite tarzı bir durum nesnesi tutar. **Act**, tool çağrılarını yürütür (oku, düzenle, çalıştır, ara, git). **Observe**, stdout / stderr / çıkış kodlarını yakalar, kırpar ve özeti geri besler. **Recover**, bağlam penceresini patlatmadan veya sonsuza dek döngüye girmeden tool hatalarını ele alır. 2026 şekli bir şey daha ekliyor: **hooks** (kancalar). `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `Notification`, `Stop` ve `PreCompact` — operatörün politika, telemetri ve koruma duvarları enjekte ettiği yapılandırılabilir genişletme noktaları.

Korumalı alan E2B veya Daytona. Her görev, okunabilir-yazılır bağlanmış bir git worktree (çalışma ağacı) ile taze bir devcontainer'da çalışır. Çatı ana bilgisayar dosya sistemine asla dokunmaz. Çalışma ağacı başarı veya başarısızlıkta yıkılır. Maliyet kontrolü üç katmanda uygulanır: dönüş başına token tavanı, oturum başına dolar bütçesi ve sert bir dönüş sınırı (tipik olarak 50). Gözlemlenebilirlik katmanı, self-hosted Langfuse'a gönderilen GenAI semantik kurallarına sahip OpenTelemetry span'leridir.

## Architecture

```
 user CLI -> harness (Bun + Ink TUI)
 |
 v
 plan / act / observe loop <---> Claude Sonnet 4.7 / GPT-5.4-Codex / Gemini 3 Pro
 | (OpenRouter üzerinden, model-donanımı-agnostik)
 v
 tool dispatcher (MCP StreamableHTTP client)
 |
 +------------+------------+----------+
 v v v v
 read/edit ripgrep tree-sitter git/run
 | | | |
 +------------+------------+----------+
 |
 v
 E2B / Daytona sandbox (worktree yalıtılmış)
 |
 v
 hooks: Pre/Post, Session, Prompt, Compact
 |
 v
 OpenTelemetry -> Langfuse (spans, tokens, $)
 |
 v
 PR via GitHub app
```

#### Açıklama

Bu diyagram bir terminal tabanlı kodlama ajanının (coding agent) tam veri akışını gösterir. Kullanıcı CLI üzerinden bir görev verir; çatı (harness) Ink tabanlı TUI ile dönüş-dönüş planla-eyle-gözle-toparla döngüsünü yürütür. Model çağrıları OpenRouter üzerinden farklı frontier modellere yönlendirilebilir. Tool çağrıları MCP'nin StreamableHTTP istemcisi üzerinden yönlendirilir. Tüm tool yürütmeleri ana bilgisayar dosya sisteminden yalıtılmış E2B veya Daytona korumalı alanında, geçici bir git worktree içinde gerçekleşir. Sekiz yaşam döngüsü kancası (hook) politika ve gözlemlenebilirlik enjekte eder. OpenTelemetry span'leri Langfuse'a akar ve sonunda bir GitHub PR'ı açılır.

## Stack

- Çatı çalışma zamanı: Bun 1.2 + Ink 5 (terminal-içi React)
- Model erişimi: Claude Sonnet 4.7, GPT-5.4-Codex, Gemini 3 Pro, Opus 4.5 (en zor görevler için) ile OpenRouter birleşik API'si
- Tool taşıma: Model Context Protocol StreamableHTTP (MCP 2026 revizyonu)
- Korumalı alan: E2B sandboxes (JS SDK) veya Daytona devcontainer'lar
- Kod arama: ripgrep alt süreci, 17 dil için tree-sitter ayrıştırıcıları (önceden derlenmiş)
- Yalıtım: görev başına `git worktree add`, başarı/başarısızlıkta temizlik
- Eval çatısı: SWE-bench Pro (doğrulanmış alt küme) + Terminal-Bench 2.0 + kendi 30-görevlik holdout'ınız
- Gözlemlenebilirlik: `gen_ai.*` semconv ile OpenTelemetry SDK → self-hosted Langfuse
- PR gönderme: ince-ayarlı tokenlı, hedef repo ile sınırlı kapsamlı GitHub App

## Build It

1. **TUI ve komut döngüsü.** Ink ile bir Bun projesi oluşturun. `agent run <repo> "<task>"` kabul edin. Bölünmüş bir görünüm yazdırın: plan bölmesi (üst), tool çağrı akışı (orta), token bütçesi (alt). Çıkıştan önce `SessionEnd` kancasını tetikleyen Ctrl-C iptali ekleyin.

2. **Plan durumu.** Tipli bir TodoWrite şeması tanımlayın (notlarla birlikte pending / in_progress / done öğeleri). Model durumu her dönüşte artımlı olarak değil bir tool çağrısı olarak yeniden yazar. Çökmelerin kurtarabilmesi için planı `.agent/state.json`'a kalıcı kılın.

3. **Tool yüzeyi.** Altı tool tanımlayın: `read_file`, `edit_file` (diff önizlemeli), `ripgrep`, `tree_sitter_symbols`, `run_shell` (zaman aşımı ile), `git` (status / diff / commit / push). Çatının taşıma-agnostik olması için MCP StreamableHTTP üzerinden açığa çıkarın. Her tool kırpılmış çıktı döndürür (çağrı başına 4k token ile sınırlı).

4. **Korumalı alan sarmalama.** Her görev bir E2B korumalı alanı başlatır. `git worktree add -b agent/$TASK_ID` ile taze bir dal oluşturur. Tüm tool çağrıları korumalı alan içinde yürütülür. Ana bilgisayar dosya sistemine ulaşılamaz.

5. **Hook'lar (kancalar).** 2026'nın sekiz hook türünün tümünü uygulayın. En az dört kullanıcı yazımı kancayı bağlayın: (a) `PreToolUse` yıkıcı-komut koruması, worktree dışında `rm -rf` çağrılarını engeller, (b) `PostToolUse` token hesaplaması, (c) `SessionStart` bütçe başlatma, (d) `Stop` son bir iz (trace) demeti yazar.

6. **Eval döngüsü.** SWE-bench Pro Python'unun 30-sorunluk bir alt kümesini klonlayın. Çatınızı her birine karşı çalıştırın. pass@1, görev başına dönüş ve görev başına $-cinsinden mini-swe-agent (minimal temel) ile karşılaştırın. Sonuçları `eval/results.jsonl`'e yazın.

7. **Maliyet kontrolü.** Sert kesim noktaları: 50 dönüş, 200k bağlam, görev başına $5. `PreCompact` kancası, 150k işaretinde eski dönüşleri bir önceki-durum bloğuna özetler ve planı kaybetmeden yeni gözlemler için yer açar.

8. **PR gönderme.** Başarıda son adım `git push` ve plan ile diff özetini gövdeye yazan bir GitHub API çağrısıdır.

## Use It

```
$ agent run ./my-repo "Fix the race condition in worker.rs"
[plan] 1 locate worker.rs and enumerate mutex uses
 2 identify shared state under contention
 3 propose fix, verify tests
[tool] ripgrep mutex.*lock -t rust (44 matches, truncated)
[tool] read_file src/worker.rs 120..180
[tool] edit_file src/worker.rs (+8 -3)
[tool] run_shell cargo test worker:: (passed)
[plan] 1 done · 2 done · 3 done
[done] PR opened: #482 turns=9 tokens=38k cost=$0.41
```

#### Açıklama

Bu terminal oturumunda ajan bir Rust dosyasındaki yarış durumunu düzeltmek için üç adımlı bir plan çıkarır: önce `mutex.*lock` aramasıyla kilit kullanımlarını bulur, sonra `worker.rs` dosyasının ilgili satırlarını okur, ardından küçük bir düzenleme yapar. `cargo test` geçer ve ajan üç adımı da tamamlanmış olarak işaretleyip bir PR açar. Maliyet raporu dönüş sayısını, harcanan token sayısını ve dolar cinsinden maliyeti gösterir.

## Ship It

Teslim edilen skill (beceri dosyası) `outputs/skill-terminal-coding-agent.md` içinde yaşar. Bir repo yolu ve görev açıklaması verildiğinde, korumalı alanda tam planla-eyle-gözle-toparla döngüsünü çalıştırır ve bir PR URL'si ile iz demeti döndürür. Bu capstone için değerlendirme ölçütü:

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1, temel çizgiye karşı | Çatınız vs mini-swe-agent, 30 eşleşmiş Python görevi |
| 20 | Mimari netliği | Plan/eyle/gözle ayrımı, hook yüzeyi, tool şeması — Live-SWE-agent düzeni ile karşılaştırılarak |
| 20 | Güvenlik | Korumalı alan kaçış testleri, izin istemleri, yıkıcı-komut koruması red-team'i geçer |
| 20 | Gözlemlenebilirlik | İz tamlığı (tool çağrılarının %100'ü span'lendi), dönüş başına token hesabı |
| 15 | Geliştirici deneyimi | Soğuk başlatma < 2s, çökme kurtarma planı sürdürür, Ctrl-C tool ortasında temiz iptal eder |
| **100** | | |

## Exercises

1. Arkadaki modeli Claude Sonnet 4.7'den vLLM üzerinde servis edilen Qwen3-Coder-30B ile değiştirin. pass@1 ve görev başına $-cinsini karşılaştırın. Açık modelin nerede geri kaldığını raporlayın.

2. PR göndermeden önce diff'i okuyan ve revizyon döngüsü isteyebilen bir `reviewer` alt-ajanı ekleyin. Yanlış-pozitif incelemelerin SWE-bench geçme oranını tek-ajan temel çizgisinin altına düşürüp düşürmediğini ölçün (ipucu: genellikle evet).

3. Korumalı alanı zorlayın: harici bir URL'ye `curl` çekmeye çalışan ve worktree dışına yazan birer görev yazın. İkisinin de `PreToolUse` kancası tarafından engellendiğini doğrulayın. Denemeleri günlüğe kaydedin.

4. Daha küçük bir modelle (Haiku 4.5) `PreCompact` özetlemeyi uygulayın. 3x sıkıştırmada ne kadar plan sadakati kaybedildiğini ölçün.

5. MCP StreamableHTTP taşımasını stdio ile değiştirin. Soğuk başlatma ve çağrı başına gecikmeyi kıyaslayın. Sadece yerel kullanım için bir kazanan seçin.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Harness (çatı) | "Ajan döngüsü" | Tool'ları yönlendiren, plan durumunu koruyan ve bütçeleri uygulayan modeli çevreleyen kod |
| Hook (kanca) | "Ajan olay dinleyicisi" | Çatı tarafından sekiz yaşam döngüsü olayından birinde çalıştırılan kullanıcı yazımı betik |
| Worktree | "Git korumalı alanı" | Ayrı bir yolda bağlı bir git checkout; ana klonu (clone) dokunmadan atılabilir |
| TodoWrite | "Plan durumu" | Modelin her dönüşte yeniden yazdığı, tipli bir pending/in-progress/done öğeleri listesi |
| StreamableHTTP | "MCP taşıması" | 2026 MCP revizyonu: çift yönlü akış (streaming) ile uzun-ömürlü HTTP bağlantısı; SSE'nin yerini alır |
| Token ceiling (token tavanı) | "Bağlam bütçesi" | Dönüş veya oturum başına girdi+çıktı token sınırı; sıkıştırmayı veya sonlanmayı tetikler |
| pass@1 | "Tek-deneme geçme oranı" | Yeniden deneme veya test kümesine göz atma olmadan ilk çalıştırmada çözülen SWE-bench görevlerinin oranı |

## Further Reading

- [Claude Code documentation](https://docs.anthropic.com/en/docs/claude-code) — Anthropic'ten referans çatı
- [Cursor 3 changelog](https://cursor.com/changelog) — Agent Tabs ve Composer 2 ürün notları
- [mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent) — SWE-bench çatı karşılaştırması için minimal temel
- [Live-SWE-agent](https://github.com/OpenAutoCoder/live-swe-agent) — Opus 4.5 ile SWE-bench Verified'da %79,2
- [OpenCode](https://opencode.ai) — açık çatı, 112k yıldız
- [SWE-bench Pro leaderboard](https://www.swebench.com) — bu capstone'ın hedeflediği değerlendirme
- [Model Context Protocol 2026 roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) — StreamableHTTP, yetenek meta verileri
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — tool çağrıları ve token kullanımı için span şeması
