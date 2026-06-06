---
name: moderation-stack
description: Bir üretim dağıtımı için moderasyon yığını yapılandırması öner
version: 1.0.0
phase: 18
lesson: 29
tags: [openai-moderation, perspective, llama-guard, layered-moderation, azure-content-safety]
---

Bir üretim dağıtımı verildiğinde, üç katman boyunca moderasyon yığını yapılandırması öner.

Çıktı:

1. Girdi sınıflandırıcısı. OpenAI Moderation, Llama Guard 3/4 veya Perspective API arasından seç. Politika sınıflandırmasıyla eşle. Çok modlu dağıtımlar için Llama Guard 4 veya OpenAI omni-moderation.
2. Çıktı sınıflandırıcısı. Girdi sınıflandırıcısıyla aynı veya farklı. Eşikleri aşağı yöndeki risk modeliyle eşle.
3. Özel alan kuralları. Genel sınıflandırıcıların yakalayamayacağı alana özgü kuralları sırala: finansal-tavsiye feragatnameleri, tıbbi-tavsiye reddetmeleri, yasal-feragatname kalıpları.
4. Kenar durumlar için yargıç. İnsan-eskalasyon yolunu belirt. Sert reddetmeler kesindir; belirsiz durumlar SLA dahilinde insan incelemesine gider.
5. Geçiş planı. Azure Content Moderator yığında ise, Şubat 2027 emekliliğinden önce Azure AI Content Safety'ye geçişi planla.

Kesin redler:

- Çıktı moderasyonu olmadan herhangi bir dağıtım (yalnızca girdi yeterli değildir).
- Düzenlenmiş yüzeylerde (finans, sağlık, yasal) özel alan kuralları olmadan herhangi bir dağıtım.
- Modern sohbet uygulamaları için yalnızca LLM-öncesi sınıflandırıcılara (Perspective) dayanan herhangi bir dağıtım.

Ret kuralları:

- Kullanıcı tek en iyi sınıflandırıcıyı sorarsa, reddet — sınıflandırıcı seçimi politika-sınıflandırmasına özgüdür.
- Kullanıcı eşikleri isterse, tek sayıları vermeyi reddet — eşikler risk toleransına ve aşağı yöndeki etkiye bağlıdır.

Çıktı: Beş bölümü dolduran, her katmanda sınıflandırıcıyı adlandıran ve geçiş yükümlülüklerini işaretleyen tek sayfalık bir öneri. OpenAI Moderation belgelerini ve Llama Guard 3/4 referanslarını her birini bir kez alıntıla.
