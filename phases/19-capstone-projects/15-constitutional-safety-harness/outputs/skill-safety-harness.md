---
name: safety-harness
description: Bir hedef LLM uygulamasının etrafına katmanlı bir güvenlik hattı bağla, altı-aile kırmızı takım aralığı çalıştır ve ölçülebilir bir zararsızlık deltası için anayasal bir öz-eleştiri çalıştır
version: 1.0.0
phase: 19
lesson: 15
tags: [capstone, safety, red-team, llama-guard, x-guard, garak, pyrit, constitutional-ai]
---

Bir hedef LLM uygulaması (8B talimat-ayarı modeli veya bir RAG sohbet botu) verildiğinde, katmanlı bir güvenlik hattıyla sertleştir ve altı saldırı ailesi boyunca otonom bir kırmızı takım aralığı çalıştır. Önce/sonra bir zararsızlık raporu üret.

İnşa planı:

1. Beş-katmanlı hat: girdi temizleme (sıfır-genişlik soyma, kodlama çözme, Unicode normalleştirme) -> NeMo Guardrails v0.12 rayları -> sınıflandırıcı geçidi (Llama Guard 4 / X-Guard / ShieldGemma-2 / Nemotron 3) -> hedef LLM -> çıktı filtresi (Llama Guard 4 + Presidio PII + alıntı kontrolü). Bayraklanan çıktılar bir Slack HITL kuyruğuna gider.
2. Uçtan uca gözlemlenebilirlik için katman başına bir Langfuse span'i yay.
3. garak, PyRIT, PAIR, TAP, GCG, çok-turlu persona ve çok-dilli kod-değiştirme saldırılarını bir cron üzerinde çalıştıran kırmızı takım zamanlayıcısı.
4. Her başarılı hapis kırma: CVSS 4.0 puanı, yeniden-üretim, hafifletme planı, ifşa zaman çizelgesi.
5. Zararsız-istek gerilemesini yakalamak için sürekli çalışan XSTest zararsız-istek sondası.
6. Anayasal öz-eleştiri çalıştırması: 1k zararlı-girişim istemi -> hedef taslak -> yazılı bir anayasaya karşı yargıç puanları -> yeniden yazılmış çiftler -> SFT. Önce/sonra, elenmiş zararsızlık değerlendirmesinde ölç.
7. Uyarılar: zararsız-regresyonda Slack uyarısı, yeni hapis-kırma ailesinde PagerDuty kritik.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Saldırı-yüzeyi kapsamı | 6+ saldırı ailesi, 2+ dil çalıştırılmış |
| 20 | Gerçek-pozitif / yanlış-pozitif ödünleşimi | Saldırı engelleme oranı vs XSTest zararsız geçme oranı |
| 20 | Öz-eleştiri deltası | Elenmiş değerlendirmede önce/sonra zararsızlık |
| 20 | Dokümantasyon ve ifşa | Zaman çizelgesiyle CVSS puanlı bulgular |
| 15 | Otomasyon ve tekrarlanabilirlik | Cron-tahrikli, uçtan uca çalıştırılmış uyarılar |

Kesin redler:

- Tek-katmanlı güvenlik yığınları. Bu capstone'ın tezi derinlikte savunmadır.
- XSTest aşırı-reddetme sayıları olmadan başarı oranı raporlayan kırmızı takım çalıştırmaları.
- Elenmiş değerlendirme olmadan anayasal öz-eleştiri (eğitim kümesi doğruluğunu raporlar, genelleştirmeyi değil).
- Hapis-kırma bulgularında eksik CVSS puanlaması.

Ret kuralları:

- Zararsız-sonda karşı-noktası olmadan bir güvenlik sayısı raporlamayı reddet. Biri diğeri olmadan yanıltıcıdır.
- Eleştiri çiftlerinin insan küratörlüğü olmadan kırmızı takım başarıları üzerinde otomatik olarak yeniden eğitmeyi reddet.
- En az iki İngilizce-olmayan dilde X-Guard çalıştırmadan çok-dilli kapsamı iddia etmeyi reddet.

Çıktı: Beş-katmanlı hattı, kırmızı takım zamanlayıcısını, PAIR/TAP/GCG çalıştırıcılarını, anayasal-öz-eleştiri eğitim iskeletini, XSTest aşırı-reddetme panosunu, CVSS bulgular izleyicisini ve sertleştirme öncesinde en yüksek başarı oranına sahip üç saldırı ailesini ve her birini hafifleten spesifik hat katmanını adlandıran bir yazıyı içeren bir depo.
