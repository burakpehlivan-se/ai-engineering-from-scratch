# Capstone 09 — Kod Taşıma Ajanı (Repo-Düzeyinde Dil / Çalışma Zamanı Yükseltme)

> Amazon'un MigrationBench'i (Java 8'den 17'ye) ve Google'ın App Engine Py2'den Py3'e taşıyıcısı 2026 çıtasını belirledi. Moderne'un OpenRewrite'ı ölçekte deterministik AST yeniden yazımları yapar. Grit aynı sorunu kod-mod tarzı bir DSL ile hedefler. Üretim deseni ikisini birleştirir: güvenli yeniden yazımlar için deterministik bir alt-tabaka artı belirsiz vakalar için bir ajan katmanı, dal başına derleme için bir korumalı alan ve PR açılmadan önce yeşile dönen bir test çatısı. Capstone 50 gerçek repoyu taşımak ve başarısızlık taksonomisi ile bir geçme oranı yayınlamaktır.

**Type:** Capstone
**Languages:** Python (agent), Java / Python (hedefler), TypeScript (pano)
**Prerequisites:** Phase 5 (NLP), Phase 7 (transformers), Phase 11 (LLM engineering), Phase 13 (tools), Phase 14 (agents), Phase 15 (autonomous), Phase 17 (infrastructure)
**Phases exercised:** P5 · P7 · P11 · P13 · P14 · P15 · P17
**Time:** 30 saat

## Problem

Büyük ölçekli kod taşıma, 2026 kodlama ajanlarının en temiz üretim uygulamalarından biridir. Temel gerçek açıktır (taşıma sonrası test paketi geçiyor mu?), ödüller gerçektir (Java-8 filosu taşıma işlemi kadro-ölçekli bir projedir) ve kıyaslamalar herkese açıktır (MigrationBench 50-repo alt kümesi). Moderne'un OpenRewrite'ı deterministik tarafı yönetir. Ajan katmanı, OpenRewrite reçetelerinin yapamadığı her şeyi yönetir: belirsiz yeniden yazımlar, derleme-sistemi kayması, uzun-kuyruk sözdizimi, geçişli bağımlılık kırılması.

Bir Java 8 reposunu (veya Python 2 reposunu) alıp yeşil-CI taşınmış bir dal üreten bir ajan inşa edeceksiniz. Geçme oranını, test-kapsamı korunmasını, repo başına maliyeti ölçecek ve bir başarısızlık taksonomisi inşa edeceksiniz. Deterministik-sadece temel çizgisine karşı yan yana karşılaştırma, ajanın değerinin gerçekte nerede yaşadığını söyler.

## Concept

Boru hattının iki katmanı var. **Deterministik alt-tabaka** (Java için OpenRewrite, Python için libcst) mekanik yeniden yazımların büyük kısmını güvenle yürütür: içe aktarmalar, metot imzaları, null-güvenliği düzenlemeleri, try-with-resources, kullanımdan kalkmış API değiştirmeleri. Hızlıdır ve denetlenebilir diff'ler üretir. **Ajan katmanı** (OpenAI Agents SDK veya Claude Opus 4.7 ve GPT-5.4-Codex üzerinde LangGraph) reçetelerin yapamadığı vakaları yönetir: derleme-dosyası yükseltmeleri (Maven/Gradle/pyproject), geçişli bağımlılık çakışmaları, test tüyleri, özel ek açıklamalar.

Her repo, hedef çalışma zamanı önceden yüklenmiş bir Daytona korumalı alanı alır. Ajan yineleme yapar: derleme çalıştır, başarısızlıkları sınıflandır, düzeltme uygula, yeniden çalıştır. Sert sınırlar: repo başına 30 dakika, repo başına $8, 20 ajan dönüşü. Tüm testler geçerse ve kapsam deltası negatif değilse, dal bir PR açar. Değilse, repo kanıtlarla bir başarısızlık sınıfı altında dosyalanır.

Başarısızlık taksonomisi teslim edilen şeydir. 50 repo boyunca, ne kırıldı? Geçişli bağımlılıklar? Özel ek açıklamalar? Derleme aracı sürümü? Taşımayla ilgisiz test tüyleri? Her sınıf bir sayı ve örnek bir diff alır. Gelecekteki reçete yazarları ilk üçü hedefleyebilir.

## Architecture

```
target repo
      |
      v
OpenRewrite / libcst deterministic recipes
   (safe, fast, auditable, ~70-80% of fixes)
      |
      v
Daytona sandbox per branch
      |
      v
agent loop (Claude Opus 4.7 / GPT-5.4-Codex):
   - run build -> capture failures
   - classify failures (build, test, lint)
   - apply fix (patch or retry recipe)
   - rerun
   - budget: 30 min, $8, 20 turns
      |
      v
test + coverage delta gate
      |
      v (passed)
open PR
      |
      v (failed)
file under failure class + attach repro
```

#### Açıklama

Bu mimari bir hedef repodan taşıma PR'ına (veya başarısızlık kaydına) kadar tam veri akışını gösterir. Önce OpenRewrite (Java) veya libcst (Python) deterministik tarifleri çalıştırılır; bunlar vakaların %70-80'ini mekanik olarak çözer. Kalan %20-30 için dal başına bir Daytona korumalı alanı kurulur. Ajan döngüsü derlemeyi çalıştırır, başarısızlıkları sınıflandırır (derleme, test, lint), düzeltme uygular ve yeniden dener. 30 dakika / $8 / 20 dönüş bütçesi aşılırsa döngü durur. Başarı durumunda test + kapsam kapısı geçilir ve PR açılır; aksi takdirde repo uygun başarısızlık sınıfı altında dosyalanır.

## Stack

- Deterministik alt-tabaka: OpenRewrite (Java) veya libcst (Python)
- Ajan: OpenAI Agents SDK veya Claude Opus 4.7 + GPT-5.4-Codex üzerinde LangGraph
- Korumalı alan: Dal başına Daytona devcontainer'lar, önceden yüklenmiş hedef çalışma zamanı (Java 17 / Python 3.12)
- Derleme sistemleri: Maven, Gradle, uv (Python)
- Kıyaslamalar: Amazon MigrationBench 50-repo alt kümesi (Java 8'den 17'ye), Google App Engine Py2'den Py3'e repoları
- Test çatısı: Paralel çalıştırıcı, Jacoco (Java) veya coverage.py (Python) ile kapsam
- Gözlemlenebilirlik: Langfuse + repo başına her diff parçası ile iz demeti
- Pano: Sınıf başına sayılar ve örnek diff'ler ile başarısızlık-taksonomisi panosu

## Build It

1. **Reçete geçişi.** Önce OpenRewrite (Java) veya libcst (Python) tariflerini çalıştırın. Mekanik olan taşımaların %70-80'ini yakalayın. "Reçete" commit'i olarak işleyin.

2. **Derleme denemesi.** Daytona korumalı alanı: hedef çalışma zamanını yükleyin, derlemeyi çalıştırın. Yeşil ise, testlere atlayın. Kırmızı ise, ajana devredin.

3. **Ajan döngüsü.** Tool'ları olan LangGraph: `run_build`, `read_file`, `edit_file`, `run_test`, `git_diff`. Ajan başarısızlığı sınıflandırır (bağımlılık, sözdizimi, test, derleme-aracı) ve hedefli bir düzeltme uygular. Yeniden çalıştırın.

4. **Bütçe sınırları.** Repo başına 30 dakika duvar-saati, $8 maliyet, 20 ajan dönüşü. Herhangi bir ihlal durdurur ve mevcut diff ile "budget_exhausted" altında dosyalar.

5. **Test + kapsam kapısı.** Derleme yeşile döndükten sonra, test paketini çalıştırın. Kapsamı temel repo ile karşılaştırın. Kapsam %2'den fazla düştüyse, "coverage_regression" altında dosyalayın.

6. **PR açma.** Başarıda, dalı itin, hangi tariflerin uygulandığını ve hangi commit'lerin ajan tarafından yazıldığını özetleyen diff ile PR'ı açın.

7. **Başarısızlık taksonomisi.** Başarısız her repo için bir sınıfla etiketleyin: `dep_upgrade_required`, `build_tool_drift`, `custom_annotation`, `test_flake`, `syntax_edge_case`, `budget_exhausted`. Bir pano inşa edin.

8. **50-repo çalıştırması.** MigrationBench alt kümesinde yürütün. Sınıf başına geçme oranını, repo başına maliyeti, kapsam-korunmasını ve deterministik-sadece temel çizgisine karşı bir karşılaştırmayı raporlayın.

## Use It

```
$ migrate legacy-java-service --target java17
[recipe]   27 rewrites applied (JUnit 4->5, HashMap initializer, try-with-resources)
[build]    FAIL: cannot find symbol sun.misc.BASE64Encoder
[agent]    turn 1 classify: removed_jdk_api
[agent]    turn 2 apply: sun.misc.BASE64Encoder -> java.util.Base64
[build]    OK
[tests]    412/412 passing; coverage 84.1% -> 84.3%
[pr]       opened #1841  cost=$3.20  turns=4
```

#### Açıklama

Bu oturum günlüğü tipik bir Java 8'den 17'ye taşıma işlemini gösterir. Reçete aşaması 27 deterministik yeniden yazma uygular (JUnit 4'ten 5'e, HashMap initializer, try-with-resources). Derleme aşaması `sun.misc.BASE64Encoder` simgesinin Java 17'de kaldırıldığını tespit eder. Ajan iki dönüşte sorunu sınıflandırır ve `java.util.Base64`'e geçirir. Test paketi 412/412 geçer, kapsam %84.1'den %84.3'e hafifçe yükselir. Toplam 4 dönüş ve 3.20 dolar maliyetle PR açılır.

## Ship It

`outputs/skill-migration-agent.md` teslim edilen şeydir. Bir repo verildiğinde, deterministik tarifleri yürütür, sonra yeşil taşınmış bir dal üretmek için bir ajan döngüsü veya repoyu bir taksonomi sınıfı altında dosyalar.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | MigrationBench geçme oranı | 50-repo alt kümesi pass@1 |
| 20 | Test-kapsamı korunması | Temele karşı ortalama kapsam deltası |
| 20 | Taşınan repo başına maliyet | Geçen çalıştırmalarda $/repo |
| 20 | Ajan / deterministik araç entegrasyonu | OpenRewrite'ın işlediği vs ajanın yazdığı düzeltmelerin oranı |
| 15 | Başarısızlık analizi yazımı | Örneklerle taksonomi tamlığı |
| **100** | | |

## Exercises

1. Boru hattını yalnızca OpenRewrite ile (ajan olmadan) çalıştırın. Geçme oranını tam boru hattıyla karşılaştırın. Ajanın tek başına fark olduğu vakaları belirleyin.

2. Bir "lint-temiz" kontrolü uygulayın: taşıma sonrasında, bir stil linter'ı (Java için spotless, Python için ruff) çalıştırın. Yeni lint hataları görünürse PR'ı başarısız kılın. Kapsamı-korunmuş-ama-stili-bozulmuş oranını ölçün.

3. Bir "minimum-diff" iyileştiricisi ekleyin: ajanın dalı testleri geçtikten sonra, ikinci bir geçişle gereksiz değişiklikleri budayın. Diff boyutu azalmasını raporlayın.

4. Üçüncü bir taşımaya genişletin: Node 18'den Node 22'ye. Korumalı alan sarmalamasını yeniden kullanın; reçete katmanını özel bir kod moduyla değiştirin.

5. Bir UX metriği olarak ilk-yeşil-derleme-süresini (TTFGB) ölçün. Hedef: p50 10 dakika altında.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Deterministik alt-tabaka | "Reçete motoru" | OpenRewrite / libcst: güvenlik garantileriyle deklaratif AST yeniden yazımları |
| Codemod | "Kodu değiştiren program" | Kaynak kodu mekanik olarak değiştiren bir yeniden yazma kuralı |
| Derleme kayması | "Araç sürümü eğriliği" | Büyük sürümler arasında Maven / Gradle / uv davranış değişikliklerinin ince farkları |
| Başarısızlık sınıfı | "Taksonomi kovası" | Bir reponun taşınmama nedeninin etiketli açıklaması: bağımlılık, sözdizimi, test, derleme-aracı, bütçe |
| Kapsam deltası | "Kapsam korunması" | Temelden taşınmış dala kadar test kapsamı % değişimi |
| Ajan dönüşü | "Tool çağrı turu" | Ajan döngüsünde bir plan -> eyle -> gözle döngüsü |
| Bütçe tükenmesi | "Tavana ulaşıldı" | Reponun 30 dakikalık / $8 / 20 dönüşlük sınırını geçmeden geçememesi |

## Further Reading

- [Amazon MigrationBench](https://aws.amazon.com/blogs/devops/amazon-introduces-two-benchmark-datasets-for-evaluating-ai-agents-ability-on-code-migration/) — kanonik 2026 kıyaslaması
- [Moderne.io OpenRewrite platform](https://www.moderne.io) — deterministik alt-tabaka referansı
- [OpenRewrite documentation](https://docs.openrewrite.org) — reçete yazarlığı
- [Grit.io](https://www.grit.io) — alternatif kod modu DSL
- [OpenAI sandboxed migration cookbook](https://developers.openai.com/cookbook/examples/agents_sdk/sandboxed-code-migration/sandboxed_code_migration_agent) — Agents SDK referansı
- [Google App Engine Py2 to Py3 migrator](https://cloud.google.com/appengine) — alternatif taşıma kıyaslaması
- [libcst](https://github.com/Instagram/LibCST) — Python deterministik alt-tabaka
- [Daytona sandboxes](https://daytona.io) — referans dal-başına korumalı alan
