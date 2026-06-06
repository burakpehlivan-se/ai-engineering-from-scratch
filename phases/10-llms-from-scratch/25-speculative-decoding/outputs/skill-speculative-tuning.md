---
name: speculative-tuning
description: Bir kod çözme iş yükünü profilleyin ve spekülatif kod çözme için taslak modeli, taslak uzunluğu K'yı, sıcaklık geçidini ve geri dönüş politikasını seçin.
version: 1.0.0
phase: 10
lesson: 25
tags: [speculative-decoding, draft-model, alpha, throughput, inference, decode-latency]
---

Hedef model (boyut, aile, tokenizer), iş yükü telemetrisi (görev karışımı, prompt-vs-kod çözme token oranı, p50/p99 kod çözme gecikmesi, hızlandırıcı ve HBM yedek alanı, ortalama parti boyutu, örnekleme sıcaklığı dağılımı) ve mevcut taslak kontrol noktaları verildiğinde, çıktı:

1. Taslak seçimi. Aynı aile küçük (Llama-3.2-1B for Llama-70B), damıtılmış taslak (Qwen3-0.6B-spec), hedefe monte edilmiş Medusa kafaları veya hiçbir taslak %30 FLOP maliyet oranına yakın değilse "spec decode yok" arasından seçin. Hedefe karşı bayt bayt tokenizer eşleşmesini doğrulayın; uyumsuz bir tokenizer'ı reddedin.
2. Taslak uzunluğu K. c taslak-hedef maliyet oranı olmak üzere E[tokens] / (1 + K x c) argmax'ı. Dağılım-içi verilerin 5_000 tokeni üzerinde bir kalibrasyon çalıştırmasından ölçülen alfayı kullanarak K için 2, 3, 4, 5, 6 üzerinden çalışmayı gösterin. Sohbet için varsayılan K=4, kod için K=6, yüksek sıcaklıklı yaratıcı yazı için K=2.
3. Sıcaklık geçidi. Spec decode'un devre dışı bırakıldığı bir sıcaklık eşiği belirleyin. Varsayılan 0.8; kalibrasyon alfayı daha erken çökertiyorsa 0.6'a düşürün. 50 mikrosaniyeden fazla ekleyen istek başına incelemeye bağlı herhangi bir sıcaklık geçidini reddedin.
4. Ağaç bütçesi. Sunma yığını ağaç taslağını destekliyorsa, 8'in altındaki parti için küçük sabit bir ağaç (derinlik 2, dal 3-2) seçin; 32'nin üzerindeki parti için düz zincir. Doğrulayıcının KV scratch boyutunu bayt olarak belirtin ve HBM yedek alanına sığdığını doğrulayın.
5. Geri dönüş politikası. Metriği (son 1_000 doğrulama üzerinde kayan pencere ölçülen alfa) ve eşiği (0.4'ün altındaki alfa) adlandırın; bu eşikte sunucu, o istek akışı için düz otoregresif kod çözmeye geri döner. Geri dönüş kararının istek başına ömrünü dahil edin.

Doğrulayıcının hesaplama bağımlı olduğu noktanın üzerindeki parti boyutunda spec decode'u reddedin. Bu noktanın üzerinde, spekülatörün emmesi gereken kullanılmayan FLOP'lar artık mevcut değildir; verim düşer. Ölçülen alfayı 0.4'ün altında olan herhangi bir görev ailesi için spec decode'u reddedin; taslak ek yükü baskındır ve duvar saati gecikmesi kötüleşir. Hedefe karşı tutulan 1_000 tokenlik bir örneklem üzerinde doğrulanmamış bir taslağı reddedin: doğrulanmamış bir taslak sessiz bir KL sapmasıdır.

Örnek girdi: "Llama-3.3-70B on 8xH100, chat workload, batch 16, p50 decode 28 ms, p99 60 ms, temperature distribution mean 0.4 / max 1.2, calibration shows alpha 0.78 on chat, 0.61 on code."

Örnek çıktı:
- Taslak: Llama-3.2-1B-Instruct-spec. Aynı tokenizer, aynı aile, c oranı yaklaşık 0.03.
- K: 4. E[tokens/verify] = 3.4 sohbet, 2.5 kod. K=5 sohbet için 0.1 token kazanır ve 0.03 ekstra c öder; reddedildi.
- Sıcaklık geçidi: 0.8. 0.8'in üzerinde alfa kalibrasyon setinde 0.45'in altına düşer.
- Ağaç bütçesi: derinlik 2 dal (3, 2). KV scratch parti 16'da 480 MB sığar.
- Geri dönüş: son 1_000 doğrulama üzerinde kayan pencere alfayı 0.40'ın altında, o akış için spec decode'u 30 saniye devre dışı bırakır, sonra tekrar dener.
