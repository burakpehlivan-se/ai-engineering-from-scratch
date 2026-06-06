---
name: wmdp-eval
description: Çift-kullanım yetenek iddiasını WMDP, unlearning değerlendirmesi ve çıkarma çalışmalarına karşı denetle
version: 1.0.0
phase: 18
lesson: 17
tags: [wmdp, rmu, dual-use, biosecurity, cybersecurity, chemistry]
---

Çift-kullanım yetenek iddiası ("modelimiz biyolojik silahlar / siber saldırı / kimya konusunda anlamlı yardım sağlamıyor") verildiğinde, destekleyici değerlendirmeyi denetle.

Çıktı:

1. Kıyaslama kapsamı. WMDP (veya eşdeğeri sarı-bölge kıyaslaması) çalıştırıldı mı? Alan başına puanları raporla (biyo, siber, kim). Alan başına sayılar olmadan herhangi bir iddia değerlendirilemez.
2. Unlearning izi. Unlearning uygulandıysa (RMU veya alternatif), genel yetenek deltasını raporla (MMLU, HELM, HumanEval). Genel yetenek raporu olmayan unlearning inandırıcı değildir.
3. Reddetme yolu denetimi. Kıyaslama ham tamamlama yoluyla mı yoksa üretim güvenlik yığını yoluyla mı uygulandı? Yalnızca güvenlik yığını nedeniyle düşük puan alan bir model, yığın atlandığında hâlâ çift-kullanım yeteneğine sahiptir.
4. Çıkarma çalışması. Çoktan-seçmeli yetenek, çıkarmaya dayanıklı hale getirilmiş yetenekle eşit değildir. Anthropic tarzı edinme denemeleri veya eşdeğeri acemi-döngüde çalışma referans verildi mi? Verilmediyse, iddia WMDP-tarzı kanıtla sınırlıdır.
5. Acemi-vs-uzman bölünmesi. Acemi-göreli gelişim ve uzman-mutlak yetenek farklı niceliklerdir. Her ikisi de ele alındı mı?

Kesin redler:

- WMDP-eşdeğeri yetenek ölçümü olmadan herhangi bir çift-kullanım güvenlik iddiası.
- Genel yetenek deltası olmadan herhangi bir unlearning iddiası.
- Acemi-döngüde çalışma olmadan "anlamlı gelişim yok" iddiası.

Ret kuralları:

- Kullanıcı modelinin ASL-3'ü aşıp aşmadığını sorarsa, doğrudan yanıt vermeyi reddet; eşikler laboratuvara özgüdür (Ders 18) ve çıkarmaya bağlıdır.
- Kullanıcı "güvenli" olan bir WMDP kesim noktası sorarsa, reddet — eşik, çıkarma direncine, örtük bilgi engellerine ve dağıtım yüzeyine bağlıdır.

Çıktı: Yukarıdaki beş bölümü dolduran, en önemli eksik kanıtı işaretleyen ve iddianın WMDP-düzeyinde mi yoksa dağıtım-düzeyinde mi olduğunu belirleyen tek sayfalık bir denetim. Li ve diğerlerini (arXiv:2403.03218) kıyaslama kaynağı olarak bir kez alıntıla.
