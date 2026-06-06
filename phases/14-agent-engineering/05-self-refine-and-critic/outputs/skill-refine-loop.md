---
name: refine-loop
description: Task, verifier mevcudiyeti ve iterasyon budget'ı verildiğinde bir evaluator-optimizer (Self-Refine / CRITIC) loop konfigüre et.
version: 1.0.0
phase: 14
lesson: 05
tags: [self-refine, critic, evaluator-optimizer, guardrails, iteration]
---

Bir task, bir iterasyon budget'ı ve hangi verifier'ın mevcut olduğu (tool-grounded veya yalnızca self-eval) verildiğinde, bir evaluator-optimizer loop için prompt'lar ve bir stop policy yay.

Şunları üret:

1. Generator prompt'u. İlk çıktı için deterministik üretici. Task'ı, output format'ını ve kısıtları açıkça belirt.
2. Evaluator/verifier prompt'u. Tool'lar mevcutsa (search, code run, test'ler, calculator, type check), onları nasıl çağıracağını ve nasıl yapılandırılmış bir eleştiri üreteceğini (JSON ile: pass/fail, violations[], suggested_fixes[]) belirt. Yalnızca self-eval mevcutsa, Self-Refine rubber-stamp riskini açıkça işaretle ve yapısal olarak farklı bir prompt stili kullan (örn. çekişmeli "en az bir kusur bul").
3. Refiner prompt'u. Önceki çıktılara ve eleştirilere (history) atıfta bulunmalıdır. "Önceki iterasyonlarda işaretlenen bir başarısızlık modunu tekrarlama"nın zorunlu olduğunu belirt.
4. Stop policy. Birleşim: verifier geçer VEYA (self-eval iyi diyor VE iterasyonlar >= 2) VEYA iterasyonlar >= max_iterations. Asla tek koşul.
5. Observability hook'ları. Her iterasyonu Ders 23'e göre bir OpenTelemetry GenAI span'ı olarak (evaluate, optimize) log'la, böylece tam refine trajectory'si denetlenebilir olsun.

Sert reject sebepleri:

- Generator ve critic için aynı prompt. Rubber-stamp riski — model kendisiyle aynı fikirde olur.
- İterasyon cap'i yok. Sonsuz refine loop'lar token yakar; her zaman varsayılan olarak 4'te cap'le.
- Serbest formatlı nesir geri bildirimi isteyen verifier prompt'u. Yalnızca yapılandırılmış JSON — pass/fail artı maddelendirilmiş violations.
- Refiner prompt'undan history'yi düşürmek. Makale, onsuz kalitenin çöktüğünü gösterir.

Refusal kuralları:

- Task'ın verifier'ı yoksa ve birini inşa etmenin yolu yoksa, CRITIC'i reddet ve Self-Refine'ın mevcut zayıf seçenek olduğunu not et — kullanıcıyı rubber-stamp riski hakkında uyar.
- max_iterations >= 10 ise, reddet ve task'ı yeniden mimarileştirmeyi öner. 3-4 geçişin ötesinde yakınsamaya kadar refine, genellikle generator prompt'unun yanlış olduğunun bir sinyalidir.
- Verifier yıkıcı tool'lar çağırıyorsa (shell, git write), reddet ve bir sandbox sınırı talep et (Ders 09).

Çıktı: tüm prompt'lar, stop policy ve tool listesini içeren tek bir konfigürasyon block'u, artı deployment hedefine göre Ders 16'ya (OpenAI Agents SDK guardrails), Ders 12'ye (Anthropic evaluator-optimizer) veya Ders 30'a (eval-driven agent development) işaret eden bir "sırada ne okumalı" notu.
