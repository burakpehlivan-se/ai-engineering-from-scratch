# Capstone 16 — GitHub Sorunundan PR'ına Otonom Ajan

> AWS Remote SWE Agents, Cursor Background Agents, OpenAI Codex cloud ve Google Jules hepsi aynı 2026 ürün şeklini yayınlıyor: bir sorunu etiketleyin, bir PR alın. Bir ajanı bir bulut korumalı alanında çalıştırın, testlerin geçtiğini doğrulayın ve gerekçeyle incelemeye hazır bir PR gönderin. Zor kısımlar, reponun derleme ortamını otomatik olarak yeniden üretmek, kimlik bilgisi sızıntısını önlemek, repo başına bütçeler uygulamak ve ajanın force-push yapamamasını sağlamaktır. Bu capstone self-hosted versiyonu inşa eder ve onu hosted alternatiflerine karşı maliyet ve geçme oranında kıyaslar.

**Type:** Capstone
**Languages:** Python (agent), TypeScript (GitHub App), YAML (Actions)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools), Phase 14 (agents), Phase 15 (autonomous), Phase 17 (infrastructure)
**Phases exercised:** P11 · P13 · P14 · P15 · P17
**Time:** 30 saat

## Problem

Asenkron bulut kodlama ajanı, etkileşimli kodlama ajanlarından (capstone 01) ayrı bir ürün kategorisidir. UX bir GitHub etiketidir. `@agent fix this` ile bir sorunu etiketlersiniz, bir bulut korumalı alanında bir işçi döner, repoyu klonlar, testleri çalıştırır, dosyaları düzenler, doğrular ve ajanın gerekçesi gövdede olan incelemeye hazır bir PR açar. Etkileşimli döngü yok, terminal yok. AWS Remote SWE Agents, Cursor Background Agents, OpenAI Codex cloud, Google Jules ve Factory Droids hepsi bunda birleşir.

Mühendislik zorlukları somuttur: ortam yeniden üretimi (ajan önbelleklenmiş bir dev imajı olmadan repoyu sıfırdan derlemeli), tüylü testler (yeniden çalıştırılmalı veya yalıtılmalı), kimlik bilgisi kapsamı (dar ince-ayarlı izinlere sahip bir GitHub App), repo başına bütçe uygulaması ve force-push yok politikası. Capstone, hosted alternatiflerine karşı geçme oranını, maliyeti ve güvenliği ölçer.

## Concept

Tetik bir GitHub webhook'ıdır (sorun etiketi veya PR yorumu). Bir dağıtıcı işi ECS Fargate veya Lambda'ya sıralar. İşçi, repoyu genel bir Dockerfile ile (dil, çatı) çıkarılmış bir Daytona veya E2B korumalı alanına çeker. Ajan, Claude Opus 4.7 veya GPT-5.4-Codex'a karşı mini-swe-agent veya SWE-agent v2 döngüsü çalıştırır. Yineleme yapar: kodu oku, düzeltme öner, yama uygula, testleri çalıştır.

Doğrulama geçit adımıdır. Tam CI, PR açılmadan önce korumalı alanda geçmelidir. Kapsam deltası hesaplanır; eşiğin ötesinde negatifse, PR açılır ama `needs-review` etiketlenir. Ajan, gerekçeyi PR açıklaması olarak ve incelemeci'nin takipleri için ping atabileceği bir `@agent` iş parçacığı olarak gönderir.

Güvenlik iki farklı GitHub yüzeyi üzerinden kapsamlanır: App, `workflows: read` ve dar repo içerikleri/PR kapsamlarına sahip kısa-ömürlü bir kurulum belirteci sağlar; dal koruması (app izinleri değil) "main'e doğrudan yazma yok" ve "force-push yok" uygular — app asla bypass listesine eklenmez. `.github/workflows` altında yol-kapsamlı salt-okunur erişim gerçek bir GitHub App temeli değil, bu yüzden dosya düzenlemelerinde ajanın izin-listesi bunu işçide uygulamalıdır. Repo başına günlük bütçe tavanları dağıtıcıda uygulanır (ör. repo başına gün başına en fazla 5 PR, PR başına $20).

## Architecture

```
GitHub issue labeled `@agent fix` or PR comment
 |
 v
 GitHub App webhook -> AWS Lambda dispatcher
 |
 v
 ECS Fargate task (or GitHub Actions self-hosted runner)
 - pull repo
 - infer Dockerfile (language, package manager)
 - Daytona / E2B sandbox with target runtime
 - clone -> git worktree -> agent branch
 |
 v
 mini-swe-agent / SWE-agent v2 loop
 Claude Opus 4.7 or GPT-5.4-Codex
 tools: ripgrep, tree-sitter, read/edit, run_tests, git
 |
 v
 verify CI passes in-sandbox + coverage delta check
 |
 v (verified)
 git push + open PR via GitHub App
 PR body = rationale + diff summary + trace URL
 label: needs-review
 |
 v
 operator reviews; can @-mention agent for follow-ups
```

#### Açıklama

Bu mimari bir GitHub etiketinden incelemeye hazır bir PR'a kadar tam veri akışını gösterir. Kullanıcı bir sorunu `@agent fix` ile etiketlediğinde GitHub App webhook'u bir Lambda dağıtıcısını tetikler. Dağıtıcı ECS Fargate görevini başlatır; görev repoyu çeker, Dockerfile'ı çıkarır, Daytona/E2B korumalı alanı kurar ve bir git worktree dalı oluşturur. mini-swe-agent veya SWE-agent v2 döngüsü Claude Opus 4.7 veya GPT-5.4-Codex ile çalışır. Ajan düzeltme uyguladıktan sonra CI'ın korumalı alanda yeşil olduğunu doğrular ve kapsam delta kontrolünü yapar. Doğrulama başarılıysa dal itilir ve GitHub App aracılığıyla bir PR açılır: gövdede gerekçe, diff özeti, iz URL'si ve maliyet bilgisi bulunur. PR `needs-review` etiketlenir. Operatör inceleme yapabilir ve takipler için ajanı @-mention ile etiketleyebilir.

## Stack

- Tetik: İnce-ayarlı belirteçli GitHub App; Lambda veya Fly.io üzerinden webhook alıcısı
- İşçi: ECS Fargate görevi (veya GitHub Actions self-hosted runner)
- Korumalı alan: Görev başına Daytona devcontainer veya E2B korumalı alanı
- Ajan döngüsü: Claude Opus 4.7 / GPT-5.4-Codex üzerinde mini-swe-agent temel çizgisi veya SWE-agent v2
- Geri getirme: tree-sitter repo-map + ripgrep
- Doğrulama: Korumalı alanda tam CI + kapsam delta kapısı
- Gözlemlenebilirlik: PR gövdesinden bağlanan PR başına iz arşivi ile Langfuse
- Bütçe: Repo başına günlük dolar tavanı; repo başına gün başına maksimum PR

## Build It

1. **GitHub App.** İnce-ayarlı kurulum belirteci: sorunlar oku+yaz, pull_requests yaz, içerikler oku+yaz, iş akışları oku. Dal koruması (bunu yapabilen tek yüzey) "main'e doğrudan itme yok" ve "force-push yok" uygular; app bypass listesinde değildir. İşçi, önerilen diff üzerinde bir izin-listesi kontrolü olarak `.github/workflows` altında "yazma yok" uygular çünkü GitHub App izinleri yol-kapsamlı değildir.

2. **Webhook alıcısı.** Lambda fonksiyonu, sorun etiketi / PR yorum webhook'larını kabul eder. `@agent fix this` etiketine göre filtreler. SQS'ye sıralar.

3. **Dağıtıcı.** SQS'den görevleri alır. Repo başına günlük bütçeyi uygular. Repo URL'si, sorun gövdesi ve taze bir Daytona korumalı alanı ile bir ECS Fargate görevi başlatır.

4. **Ortam çıkarımı.** Dili (Python, Node, Go, Rust) ve paket yöneticisini (uv, pnpm, go mod, cargo) tespit edin. Yoksa uçuş sırasında bir Dockerfile oluşturun.

5. **Ajan döngüsü.** Claude Opus 4.7 ile mini-swe-agent veya SWE-agent v2. Tool'lar: ripgrep, tree-sitter repo-map, read_file, edit_file, run_tests, git. Sert sınırlar: $20 maliyet, 30 dakika duvar-saati, 30 ajan dönüşü.

6. **Doğrulama.** Döngü sona erdikten sonra, tam test paketini korumalı alanda çalıştırın. jacoco / coverage.py ile kapsam deltasını hesaplayın. CI kırmızıysa: durdurun, PR açmayın. Kapsam %2'den fazla düşerse: PR'ı `needs-review` etiketiyle açın.

7. **PR gönderme.** Ajan dalını itin. GitHub API ile PR açın: başlık, gerekçe, diff özeti, iz URL'si, maliyet, dönüşler.

8. **Kimlik bilgisi hijyeni.** İşçi, kısa-ömürlü bir GitHub App kurulum belirteciyle çalışır. Günlükler arşivlenmeden önce gizli bilgiler için temizlenir.

9. **Değerlendirme.** Çeşitli zorlukta 30 dahili tohum sorusu. Geçme oranını, PR kalitesini (diff boyutu, stil, kapsam), maliyeti, gecikmeyi ölçün. Aynı sorularda Cursor Background Agents ve AWS Remote SWE Agents ile karşılaştırın.

## Use It

```
# on github.com
 - user labels issue #842 with `@agent fix this`
 - PR #1903 appears 14 minutes later
 - body:
 > Fixed NPE in widget.dedupe() caused by null comparator entry.
 > Added regression test widget_test.go::TestDedupeNullComparator.
 > Coverage delta: +0.12%
 > Turns: 7 Cost: $1.80 Trace: langfuse:...
 > Label: needs-review
```

#### Açıklama

Bu örnek tipik bir sorun-PR dönüşümünü gösterir. Kullanıcı sorun #842'yi `@agent fix this` ile etiketler. 14 dakika sonra PR #1903 belirir. PR gövdesi açıkça neyin düzeltildiğini (null karşılaştırıcı girdisinin neden olduğu NPE), hangi regresyon testinin eklendiğini, kapsam değişimini (+%0.12), dönüş sayısını (7), maliyeti ($1.80) ve Langfuse izine bağlantıyı belirtir. PR `needs-review` etiketlidir; operatör gözden geçirir ve gerekirse ajanı @-mention ile takip soruları için etiketleyebilir.

## Ship It

`outputs/skill-issue-to-pr.md` teslim edilen şeydir. Sınırlı maliyet ve kapsamlı kimlik bilgileriyle etiketli sorunları incelemeye hazır PR'lara dönüştüren bir GitHub App + asenkron bulut işçisi.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | 30 sorunda geçme oranı | Uçtan uca başarı (CI yeşil + kapsam OK) |
| 20 | PR kalitesi | Diff boyutu, kapsam deltası, stil uyumu |
| 20 | Çözülen sorun başına maliyet ve gecikme | PR başına $ ve duvar-saati |
| 20 | Güvenlik | Kapsamlı belirteç, repo başına bütçe, force-push yok, kimlik bilgisi hijyeni |
| 15 | Operatör UX | Gerekçe yorumları, yeniden deneme kolaylığı, @-mention takibi |
| **100** | | |

## Exercises

1. Bir "tüylü testi düzelt" modu ekleyin: `@agent stabilize-flake TestX` etiketi, testi korumalı alanda 50 kez çalıştırır ve onu stabilize eden minimum değişikliği önerir.

2. Üç paylaşılan sorunda Cursor Background Agents'a karşı maliyeti karşılaştırın. Hangi tool'ların nerede kazandığını raporlayın.

3. Bir bütçe panosu inşa edin: repo başına günlük maliyet, kullanıcı başına maliyet. Anomali üzerine uyarı verin.

4. CI çalıştırmadan bir taslak PR açan bir "kuru-çalıştırma" modu inşa edin, böylece incelemeciler planı ucuza inceleyebilir.

5. Bir saklama politikası ekleyin: 7 günden eski birleştirilmemiş PR dalları otomatik olarak silinir.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| GitHub App | "Kapsamlı bot kimliği" | İnce-ayarlı izinler + kısa-ömürlü kurulum belirteci olan uygulama |
| Asenkron bulut ajanı | "Arka plan ajanı" | Bulut korumalı alanında çalışan, terminal olmayan etkileşimsiz işçi |
| Ortam çıkarımı | "Dockerfile sentezi" | Dil + paket yöneticisini tespit edin, yoksa bir Dockerfile oluşturun |
| Doğrulama | "Korumalı alanda CI" | PR açmadan önce tam test paketini işçinin içinde çalıştırmak |
| Kapsam deltası | "Kapsam korunması" | Temelden ajan dalına kadar test kapsamı % değişimi |
| Repo başına bütçe | "Günlük tavan" | Dağıtıcıda uygulanan dolar ve PR sayısı sınırı |
| Gerekçe | "PR gövdesi açıklaması" | Ajanın neyin değiştiğini ve nedenini özetlemesi; PR gövdesinde zorunludur |

## Further Reading

- [AWS Remote SWE Agents](https://github.com/aws-samples/remote-swe-agents) — kanonik asenkron bulut ajanı referansı
- [SWE-agent](https://github.com/SWE-agent/SWE-agent) — CLI referansı
- [Cursor Background Agents](https://docs.cursor.com/background-agent) — ticari alternatif
- [OpenAI Codex (cloud)](https://openai.com/codex) — hosted rakip
- [Google Jules](https://jules.google) — Google'ın hosted versiyonu
- [Factory Droids](https://www.factory.ai) — alternatif ticari referans
- [GitHub App documentation](https://docs.github.com/en/apps) — kapsamlı bot kimliği
- [Daytona cloud sandboxes](https://daytona.io) — referans korumalı alan
