---
name: terminal-coding-agent
description: Sınırlı maliyet, sandbox'lanmış araçlar ve tam 2026 hook yüzeyi ile SWE-bench Pro'ya karşı terminal-yerel bir kodlama ajanı inşa et ve değerlendir
version: 1.0.0
phase: 19
lesson: 01
tags: [capstone, coding-agent, claude-code, swe-bench, mcp, hooks, sandbox]
---

Bir hedef depo ve doğal dil görevi verildiğinde, planlama yapan, bir sandbox'ta yürüten ve bir pull request açan bir iskelet (harness) inşa et. 30-görevlik bir SWE-bench Pro alt kümesinde, görev başına 5 dolar bütçenin altında kalırken mini-swe-agent temel çizgisiyle eşleş veya geç.

İnşa planı:

1. Bir plan bölmesi, araç-çağrı akışı ve canlı token/dolar bütçesi olan bir Bun + Ink TUI iskeleti kur.
2. Model Context Protocol StreamableHTTP üzerinden altı araç tanımla (read_file, edit_file, ripgrep, tree_sitter_symbols, run_shell, git). Her çağrı en fazla 4k token döner.
3. Her araç çağrısını, yeni bir `git worktree add` dalında bir E2B veya Daytona sandbox'ında çalıştır. Ana dosya sistemine asla dokunma.
4. Tüm sekiz 2026 hook olayını bağla: SessionStart, SessionEnd, PreToolUse, PostToolUse, UserPromptSubmit, Notification, Stop, PreCompact. En az dört kullanıcı-yazarlı hook teslim et (yıkıcı-komut koruyucusu, token muhasebesi, OTel span yayıcısı, iz demeti yazıcısı).
5. Üç bütçeyi zorla: 50 tur, 200k token, 5 dolar. 150k'da PreCompact tetiklenir ve eski turları özetler.
6. GenAI semantik kural veya teamüllerine (semantic conventions) sahip OpenTelemetry span'lerini kendi barındırılan bir Langfuse'a yay.
7. Başarıda, dalı push et ve gövdesinde plan ve iz demeti bulunan bir PR aç.
8. mini-swe-agent'a karşı 30-issue'lu bir SWE-bench Pro Python alt kümesinde değerlendir ve görev başına pass@1, tur, token ve dolar kaydet.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | Aynı 30-görev alt kümesinde mini-swe-agent temel çizgisiyle eşleşmiş |
| 20 | Mimari netliği | Plan/eylem/gözlem ayrımı, hook yüzeyi, araç şeması okunabilirliği |
| 20 | Güvenlik | Sandbox kaçışı kırmızı takım + yıkıcı-komut koruyucu denetimi |
| 20 | Gözlemlenebilirlik | Araç çağrılarının %100'ü span'lenmiş, tur başına token muhasebesi |
| 15 | Geliştirici deneyimi | Soğuk başlatma 2 saniyenin altında, çökme kurtarma, Ctrl-C iptal semantiği |

Kesin redler:

- Sandbox içinde yerine ana dosya sisteminde git'e giden iskelet.
- Worktree dışına yazabilen veya açık bir izin listesi hook'u olmadan harici URL'lere curl atabilen herhangi bir ajan.
- Aynı 30 issue üzerinde eşleşmiş temel çizgi çalıştırması olmadan raporlanan değerlendirme sayıları.
- Yeniden denemeler arasında `git reset --hard`'a bağlı olan "geçme oranı" iddiaları; SWE-bench Pro pass@1'dir.

Ret kuralları:

- Herhangi bir yapılandırma altında doğrudan main'e push etmeyi reddet. Yalnızca PR dalları.
- Yıkıcı-komut koruyucusunu devre dışı bırakmayı reddet. Rubriğin sert gereksinimidir.
- Bütçe tavanı olmadan çalıştırmayı reddet. Açık-uçlu çalıştırmalar değerlendirme karşılaştırmasını kirletir.

Çıktı: İskeleti, eşleşmiş mini-swe-agent temel çizgi çalıştırmasıyla sabit 30-görevlik bir SWE-bench Pro değerlendirme iskeleti, en az 5 tam çalıştırma için bir OpenTelemetry iz arşivi ve iskeletin temel çizginin çözdüğü görevleri ve tersini adlandıran bir yazı içeren bir depo. Gözlemlediğiniz en büyük üç başarısızlık kipini ve her birini düzelten hook değişikliğini belirten bir bölümle bitir.
