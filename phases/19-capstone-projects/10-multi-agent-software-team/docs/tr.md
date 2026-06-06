# Capstone 10 — Çok Ajanlı Yazılım Mühendisliği Ekibi

> SWE-AF'nin fabrika mimarisi, MetaGPT'nin rol-tabanlı istemleri, AutoGen 0.4'ün tipli aktör grafı, Cognition'ın Devin'i ve Factory'nin Droids'leri 2026'da aynı şekilde birleşti: bir mimar plan yapar, N kodlayıcı paralel çalışma ağaçlarında (worktree) çalışır, bir incelemeci geçitler, bir testçi doğrular. Paralel çalışma ağaçları duvar-saati çıktıya (throughput) dönüştürür. Paylaşılan durum ve devir protokolleri hata yüzeyi olur. Capstone ekibi inşa etmek, SWE-bench Pro üzerinde değerlendirmek ve hangi devirlerin ne sıklıkta kırıldığını raporlamaktır.

**Type:** Capstone
**Languages:** Python / TypeScript (agents), Shell (worktree scripts)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools), Phase 14 (agents), Phase 15 (autonomous), Phase 16 (multi-agent), Phase 17 (infrastructure)
**Phases exercised:** P11 · P13 · P14 · P15 · P16 · P17
**Time:** 40 saat

## Problem

Tek-ajanlı kodlama çatıları büyük görevlerde bir tavana ulaşıyor. Bunun nedeni herhangi bir bireysel ajanın zayıf olması değil, 200k-token bir bağlamın bir mimari planı artı dört paralel kod tabanı dilimini artı incelemeci yorumlarını artı test çıktısını tutamamasıdır. Çok-ajanlı fabrikalar sorunu böler: bir mimar plan sahibidir, kodlayıcılar paralel çalışma ağaçlarında uygulama sahibidir, bir incelemeci geçitler, bir testçi doğrular. SWE-AF'nin "fabrika" mimarisi, MetaGPT'nin rolleri, AutoGen'nin tipli aktör grafı — üç çerçeve de aynı şekli tanımlar.

Hata yüzeyi devirdir. Mimar, kodlayıcıların uygulayamayacağı bir şey planlar. Kodlayıcılar çakışan diff'ler üretir. İncelemeci halüsinasyonlanmış bir düzeltmeyi onaylar. Testçi hâlâ yazan bir kodlayıcıyla yarışır. Bu ekiplerden birini inşa edecek, 50 SWE-bench Pro sorusu üzerinde çalıştıracak, her devri izleyecek ve post-mortem yayınlayacaksınız.

## Concept

Roller tipli ajanlardır. **Mimar** (Claude Opus 4.7) sorunu okur, bir plan yazar ve onu açık arayüzlerle alt görevlere ayırır. **Kodlayıcılar** (Claude Sonnet 4.7, N paralel örnek, her biri bir `git worktree` + Daytona korumalı alanında) alt görevleri bağımsız olarak uygular. **İncelemeci** (GPT-5.4) birleştirilmiş diff'i okur ve onaylar veya belirli değişiklikler ister. **Testçi** (Gemini 2.5 Pro) test paketini yalıtımda çalıştırır ve yapılarla birlikte geçme/başarısızlık raporlar.

İletişim paylaşılan bir görev panosu (dosya tabanlı veya Redis) aracılığıyladır. Her rol, işlemesine izin verilen görevleri tüketir. Devirler A2A-protokol-tipli mesajlardır. Koordinasyon endişeleri: birleştirme-çakışması çözümü (koordinatör rol veya otomatik üç-yönlü birleştirme), paylaşılan durum senkronizasyonu (plan, kodlayıcılar başladığında dondurulur; yeniden planlamalar ayrı olaylardır) ve incelemeci geçitleme (incelemeci kendi değişikliklerini veya önerdiği değişiklikleri onaylayamaz).

Token çoğaltma gizli maliyettir. Her rol sınırı özet istemleri ve devir bağlamı ekler. 40 dönüşlük bir tek-ajanlı çalıştırma, dört rol boyunca toplam 160 dönüş olur. Rubrik, dolar başına kazanıp kazanmadığı sorusu olduğu için, token verimliliğini tek-ajan temel çizgisine karşı özellikle tartar.

## Architecture

```
GitHub issue URL
      |
      v
Architect (Opus 4.7)
   reads issue, produces plan with subtasks + interfaces
      |
      v
Task board (file / Redis)
      |
   +-- subtask 1 ---+-- subtask 2 ---+-- subtask 3 ---+-- subtask 4 ---+
   v                v                v                v                v
Coder A          Coder B          Coder C          Coder D          (4 parallel)
 (Sonnet)         (Sonnet)         (Sonnet)         (Sonnet)
 worktree A       worktree B       worktree C       worktree D
 Daytona          Daytona          Daytona          Daytona
      |                |                |                |
      +--------+-------+-------+--------+
               v
           merge coordinator  (three-way merge + conflict resolution)
               |
               v
           Reviewer (GPT-5.4)
               |
               v
           Tester  (Gemini 2.5 Pro)  -> passes? -> open PR
                                     -> fails?  -> route back to coder
```

#### Açıklama

Bu mimari bir GitHub sorunundan hazır PR'a kadar çok-ajanlı veri akışını gösterir. Mimari (Opus 4.7) sorunu okur, açık arayüzlerle bir plan yazar ve alt görevlerden oluşan bir DAG üretir. Görev panosu (dosya veya Redis) alt görevleri dört paralel kodlayıcıya dağıtır. Her kodlayıcı kendi `git worktree`'sinde ve Daytona korumalı alanında çalışır. Tüm kodlayıcılar bitirdiğinde, birleştirme koordinatörü üç yönlü birleştirme yapar ve çakışmaları çözer. İncelemeci (GPT-5.4) birleştirilmiş diff'i okur; onaylarsa testçiye (Gemini 2.5 Pro) geçer, yoksa belirli değişikliklerle ilgili kodlayıcıya geri yönlendirir. Testçi testleri çalıştırır, geçerse PR açılır, başarısız olursa yine ilgili kodlayıcıya yönlendirilir.

## Stack

- Orkestrasyon: Paylaşılan durum + ajan-başına alt-grafikler ile LangGraph
- Mesajlaşma: Tipli ajan-arası mesajlar için A2A protokolü (Google 2025)
- Modeller: Opus 4.7 (mimar), Sonnet 4.7 (kodlayıcılar), GPT-5.4 (incelemeci), Gemini 2.5 Pro (testçi)
- Worktree yalıtımı: Kodlayıcı başına `git worktree add` + Daytona korumalı alanı
- Birleştirme koordinatörü: Özel üç-yönlü birleştirme + LLM-aracılı çakışma çözümü
- Değerlendirme: SWE-bench Pro (50 soru), SWE-AF senaryoları, birim testler için HumanEval++
- Gözlemlenebilirlik: Rol-etiketli span'lerle Langfuse, ajan başına token hesabı
- Dağıtım: Her rol ayrı bir Deployment + backlog üzerinde HPA ile K8s

## Build It

1. **Görev panosu.** Tipli mesajlarla dosya tabanlı JSONL: `plan_request`, `subtask`, `diff_ready`, `review_needed`, `test_needed`, `approved`, `rejected`, `replan_needed`. Ajanlar etiketlere abone olur.

2. **Mimar.** GitHub sorununu okur, açık alt görev arayüzleri gerektiren bir plan şablonu ile Opus 4.7 çalıştırır (değiştirilen dosyalar, genel fonksiyonlar, test etkisi). Alt görevlerin bir DAG'ı ile bir `plan_request` yayar.

3. **Kodlayıcılar.** N paralel işçi, her biri panodan bir alt görev talep eder. Her biri taze bir `git worktree add` dalı artı bir Daytona korumalı alanı başlatır. Alt görevi uygular. Yama + test deltaları ile `diff_ready` yayar.

4. **Birleştirme koordinatörü.** Tüm-kodlayıcılar-bitti üzerine, N dalını üç yönlü olarak bir hazırlama dalına birleştirir. Yalnızca dosya-düzey çakışma olduğunda LLM-aracılı çakışma çözümü.

5. **İncelemeci.** GPT-5.4 birleştirilmiş diff'i okur. Kendi yazdığı diff'leri onaylayamaz. `approved` (no-op) veya belirli değişiklik istekleriyle ilgili kodlayıcıya yönlendirilen `review_feedback` yayar.

6. **Testçi.** Gemini 2.5 Pro test paketini temiz bir korumalı alanda çalıştırır. Yapıtları yakalar. `test_passed` veya yığın izleriyle `test_failed` yayar. Başarısız testler başarısız alt görevin sahibi kodlayıcıya geri döner.

7. **Devir hesabı.** Rol sınırını geçen her mesaj, yük boyutu ve kullanılan model ile Langfuse'ta bir span alır. Alt görev başına token çoğaltmayı hesaplayın (kodlayıcı_tokenleri + incelemeci_tokenleri + testçi_tokenleri + mimar_payı / kodlayıcı_tokenleri).

8. **Değerlendirme.** 50 SWE-bench Pro sorusu üzerinde çalıştırın. pass@1 ve $-başına-çözülen-soruyu tek-ajan temel çizgisine (tek bir worktree'de tek bir Sonnet 4.7) karşı karşılaştırın.

9. **Post-mortem.** Başarısız her soru için, kırılan devri belirleyin (çok belirsiz plan, birleştirme çakışması, incelemeci yanlış-onayı, testçi tüyü). Bir devir-başarısızlık histogramı üretin.

## Use It

```
$ team run --issue https://github.com/acme/widget/issues/842
[architect] plan: 4 subtasks (parser, cache, api, migration)
[board]     dispatched to 4 coders in parallel worktrees
[coder-A]   subtask parser  -> 42 lines, tests pass locally
[coder-B]   subtask cache   -> 88 lines, tests pass locally
[coder-C]   subtask api     -> 31 lines, tests pass locally
[coder-D]   subtask migration -> 19 lines, tests pass locally
[merge]     3-way merge: 0 conflicts
[reviewer]  comments on cache (thread pool sizing); routed to coder-B
[coder-B]   revision: 92 lines; submits
[reviewer]  approved
[tester]    all 412 tests pass
[pr]        opened #3382   4 coders, 1 revision, $4.90, 18m
```

#### Açıklama

Bu oturum tipik bir çok-ajanlı sorun çözümünü gösterir. Mimari 4 alt görevlik bir plan çıkarır: parser, cache, api, migration. Pano her görevi paralel bir kodlayıcıya atar. Her kodlayıcı kendi worktree'sinde bağımsız çalışır; tüm yerel testler geçer. Birleştirme koordinatörü sıfır çakışmayla üç yönlü birleştirme yapar. İncelemeci cache alt görevi hakkında thread pool boyutlandırması konusunda yorum yapar; ilgili kodlayıcı revizyon yapar ve yeniden gönderir. İncelemeci onaylar, testçi 412 testin tümünü geçirir. Sonuç: 18 dakikada, 4.90 dolarla, 1 revizyonla açılan PR.

## Ship It

`outputs/skill-multi-agent-team.md` teslim edilen şeydir. Bir sorun URL'si ve paralellik düzeyi verildiğinde, ekip rol başına token hesabı ile birleştirmeye hazır bir PR üretir.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | SWE-bench Pro pass@1 | Eşleşmiş 50-soruluk alt küme, pass@1 |
| 20 | Paralel hızlanma | Tek-ajan temel çizgisine karşı duvar-saati |
| 20 | İnceleme kalitesi | Enjekte-hata sondası üzerinde yanlış-onay oranı |
| 20 | Token verimliliği | Tek-ajan başına çözülen sorun başına toplam token |
| 15 | Koordinasyon mühendisliği | Birleştirme-çakışması çözümü, devir-başarısızlık histogramı |
| **100** | | |

## Exercises

1. Bir diff'in ortasına bariz bir hata enjekte edin (ana gövdeden önce ekstra `return None`). İncelemeci yanlış-onay oranını ölçün. Yanlış-onay %5'in altına düşene kadar incelemeci istemini ayarlayın.

2. İki kodlayıcıya indirgeyin (mimar + kodlayıcı + incelemeci + testçi, kodlayıcı iki alt görevi sıralı çalıştırır). Duvar-saati ve geçme oranını karşılaştırın.

3. Birleştirme koordinatörünü tek-yazıcı kısıtı ile değiştirin (alt görevler ayrık dosya kümelerine dokunur). Mimar üzerindeki planlama yükünü ölçün.

4. İncelemeciyi GPT-5.4'ten Claude Opus 4.7'ye değiştirin. Yanlış-onay oranını ve token maliyeti deltasını ölçün.

5. Beşinci bir rol ekleyin: belgelemeci (Haiku 4.5). İncelemeden sonra, bir değişiklik günlüğü girdisi üretir. Dokümantasyon kalitesinin ekstra token harcamayı haklı çıkarıp çıkarmadığını ölçün.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| Paralel çalışma ağacı | "Yalıtılmış dal" | Kodlayıcı başına taze bir çalışma ağacı üreten `git worktree add` |
| Görev panosu | "Paylaşılan mesaj veri yolu" | Ajanların abone olduğu tipli mesajların dosya veya Redis deposu |
| Devir | "Rol sınırı" | Bir rolün bağlamından diğerininkine geçen herhangi bir mesaj |
| Token çoğaltma | "Çok-ajanlı ek yük" | Aynı görev için roller arası toplam token / tek-ajanlı token |
| A2A protokolü | "Ajan-arası" | Google'ın 2025 spesifikasyonu, tipli ajan-arası mesajlar için |
| Birleştirme koordinatörü | "Entegratör" | Üç yönlü birleştirmeyi çalıştıran ve çakışmaları aracılık eden bileşen |
| Yanlış onay | "İncelemeci halüsinasyonu" | İncelemeci, bilinen hataları olan bir diff'i onaylar |

## Further Reading

- [SWE-AF factory architecture](https://github.com/Agent-Field/SWE-AF) — referans 2026 çok-ajanlı fabrika
- [MetaGPT](https://github.com/FoundationAgents/MetaGPT) — rol-tabanlı çok-ajanlı çatı
- [AutoGen v0.4](https://github.com/microsoft/autogen) — Microsoft'un tipli aktör çatısı
- [Cognition AI (Devin)](https://cognition.ai) — referans ürün
- [Factory Droids](https://www.factory.ai) — alternatif referans ürün
- [Google A2A protocol](https://developers.google.com/agent-to-agent) — ajan-arası mesajlaşma spesifikasyonu
- [git worktree documentation](https://git-scm.com/docs/git-worktree) — yalıtım alt-tabakası
- [SWE-bench Pro](https://www.swebench.com) — değerlendirme hedefi
