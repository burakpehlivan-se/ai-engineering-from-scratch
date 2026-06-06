---
name: failure-detector
description: Bir trace store'a bağlı, endüstri-tekrarlayan beş modu artı domain-spesifik imzaları etiketleyen agent failure mode detector'ları üret.
version: 1.0.0
phase: 14
lesson: 26
tags: [failure-modes, masft, detection, observability]
---

Bir ürün domain'i ve bir trace store verildiğinde, agent failure mode'ları için detector'lar üret.

Şunları üret:

1. Mod başına detector: `hallucinated_action`, `scope_creep`, `cascading_errors`, `context_loss`, `tool_misuse`, `success_hallucination`.
2. Domain-spesifik detector'lar (örn. "issue bağlamadan PR oluşturdu" bir dev tool için, ">5 alıcıya confirmation olmadan e-posta gönderdi" bir pazarlama tool'u için).
3. Tüm detector'ları her trace'e uygulayan ve bir dağılım yayan tagger.
4. Threshold-based alerting: bugünün trace'lerinin >=%5'i bir modu etiketlerse, page aç veya ticket aç.
5. Sample retention: etiketlenen her trace için, operatör incelemesi için input + output + state snapshot'larını tut.

Sert reject sebepleri:

- Production'da trace başına LLM çağrıları gerektiren detector'lar. Pattern-based detector'lar kullan; LLM-judge'u örneklenen inceleme için sakla.
- Sadece crash'te etiketleme. Çoğu başarısızlık geçerli görünen çıktı üretir. İçerik + state üzerinde imza check'leri zorunludur.
- PII redaction olmadan etiketlenmiş trace'leri depolamak. Başarısızlık örnekleri en kötü içeriği taşır; depolamadan önce temizle.

Refusal kuralları:

- Kullanıcı "tüm trace'ler sonsuza kadar depolanır" isterse, maliyet + compliance nedenleriyle reddet. Tag + oranına göre örnekle.
- Ürünün "bilinen iyi" baseline'ı yoksa, drift alert'lerini reddet. Drift referansa ihtiyaç duyar.
- Detector'lar versiyonlanmamışsa, reddet. Detector regresyonları sinyalini fark etmeden kırar.

Çıktı: `detectors.py`, `tagger.py`, `alerts.py`, `retention.py`, threshold'ları, retention policy'sini ve alert routing'i açıklayan `README.md`. Ders 24'e (observability backends) veya adversarial failure mode'ları için Ders 27'ye (prompt injection) işaret eden bir "sırada ne okumalı" ile bitir.
