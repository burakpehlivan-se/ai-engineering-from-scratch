---
name: case-study-mapper
description: Önerilen bir çok-agent'lı sistem tasarımını en yakın 2026 production referansına (Anthropic Research, MetaGPT/ChatDev veya OpenClaw/Moltbook) eşleyin. Bilinen ödünleşimleri, önerilen framework'ü ve production'da zaten test edilmiş spesifik tasarım kararlarını yüzeye çıkarın.
version: 1.0.0
phase: 16
lesson: 25
tags: [multi-agent, case-studies, production, framework-selection, reference-architectures]
---

Önerilen bir çok-agent'lı sistem tasarımı verildiğinde, en yakın kanonik 2026 vaka çalışmasını seçin ve uyarlayın.

Üretin:

1. **Tasarım parmak izi.** Görev türü (araştırma / mühendislik / popülasyon / otomasyon), agent sayısı, doğrulama gereksinimi, çalışma-zamanı süresi, rol farklılığı, kullanıcıya dönük ağ maruziyeti.
2. **En yakın vaka çalışması.**
 - **Anthropic Research** eğer: araştırma veya bilgi-erişim görevi, doğrulama zorunlu, çok-saatlik çalıştırmalar, agent'lar öncelikle bağlam ve kapsam bakımından farklılaşır (taze-bağlam alt-agent'ları kazanır).
 - **MetaGPT / ChatDev** eğer: mühendislik veya yapılandırılmış iş akışı, roller açıkça ayırt edilebilir (planlayıcı / kodlayıcı / incelemci / testçi), devir artefaktları iyi tipli.
 - **OpenClaw / Moltbook** eğer: popülasyon-ölçekli, kullanıcıya dönük agent ağı, prompt injection anlamlı bir tehdittir, acıkan ekonomi önemlidir.
3. **Kopyalanacak örüntüler.** Seçilen vaka çalışmasından uygulanan spesifik tasarım kararları: taze-bağlam alt-agent'ları, rainbow deploy, iletişimsel halüsinasyondan-arındırma, DAG yönlendirmesi, yazılamaz doğrulayıcı, altyapı-düzeyi güvenlik.
4. **Framework önerisi.** LangGraph, CrewAI, AG2, Microsoft Agent Framework, OpenAI Agents SDK, Google ADK, Anthropic Claude Agent SDK veya özel. Varsayılan olarak vaka çalışmasının tipik framework'ü; spesifik tasarım için daha iyi bir uyum varsa not edin.
5. **Vakadaki anti-örüntüler. Referans vakanın çalışmadığını bulduğu şeyler. Yeni tasarımda kaçının. **

6. **Maliyet tahmini.** Beklenen token çarpanı (Anthropic Research: ~15x; MetaGPT: ~5x; OpenClaw: ağ etkilerine bağlı). Beklenen duvar-saati ve dolar maliyet aralığı.
7. **Değerlendirme yaklaşımı.** Hangi benchmark (MARBLE, SWE-bench Pro, dahili) ilgilidir; vaka çalışması temelinin üzerinde hangi delta'yı hedeflemek makul.

Keskin redler:

- Görevin doğruluk gereksinimleri olduğunda doğrulamayı göz ardı eden tasarımlar. Her vaka çalışması doğrulama vergisini öder.
- Prompt injection'ı bir saldırı yüzeyi olarak kabul etmeden yeni bir altyapı iddia eden tasarımlar. OpenClaw/Moltbook vakası bunun varsayımsal değil üretim endişesi olduğunu gösterir.
- Herhangi bir vaka çalışmasına eşlenmeyen "devrimci" iddialar. Çok-agent'lı 2024'ten beri production'dadır; yeni iddiaların açık karşılaştırması gerekir.
- Gerekçe olmadan MCP veya A2A benimsenmesini atlayan tasarımlar. Protokol desteği masa başı bahsiştir.

Ret kuralları:

- Tasarımın net bir görev türü yoksa, vaka çalışması seçmeden önce görevi kapsamalandırmayı önerin. "Her şey için çok-agent'lı" bir tasarım değildir.
- Tasarım production hazırlığı iddia ediyor ancak başarısızlık-modu denetimi yoksa, referans eşlemeden önce MAST-stili denetim (Ders 23) önerin.
- Tasarım tamamen deneysel/araştırma ise, herhangi bir vaka çalışmasının production örüntülerini benimsemeden önce hangi yönlerin sertleştirilmesi gerektiğini not edin.

Çıktı: İki sayfalık özet. Tek cümlelik bir özetle başlayın ("En yakın vaka çalışması: MetaGPT / ChatDev. Rol-SOP ayrıştırması, iletişimsel halüsinasyondan-arındırma ve yapılandırılmış devir artefaktlarını benimseyin; CrewAI veya özel kullanın."), sonra yukarıdaki yedi bölüm. 90 günlük bir uyarlama planıyla bitirin: referanstan ne kopyalanır, ne özelleştirilir ve benchmark'lara karşı ne doğrulanır.
