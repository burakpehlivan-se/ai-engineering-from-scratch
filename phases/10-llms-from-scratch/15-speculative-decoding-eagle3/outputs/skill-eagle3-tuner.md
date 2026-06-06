---
name: eagle3-tuner
description: Yeni bir çıkarım iş yükü için spekülatif kod çözme stratejisi (vanilla / Medusa / EAGLE-1/2/3 / lookahead) seçin ve ayarlayın.
version: 1.0.0
phase: 10
lesson: 15
tags: [speculative-decoding, eagle, eagle-3, medusa, inference, vllm, sglang, tensorrt-llm]
---

Üretim çıkarım hedefi (doğrulayıcı model, parti boyutu, dizi uzunluğu profili, hedef p50/p99 kod çözme gecikmesi, hızlandırıcı, telemetriden beklenen alfa aralığı, görev karışımı) verildiğinde, bir spekülatif kod çözme stratejisi ve ayarlama parametreleri önerin. Öneri, doğrulayıcının çıktı dağılımını tam olarak korumalıdır — açık onay olmadan hiçbir kalite ödünleşimi kabul edilemez.

Şunu üretin:

1. Taslak ailesi. Vanilla, Medusa, EAGLE-1, EAGLE-2, EAGLE-3 veya lookahead arasından seçin. Alfa telemetrisini (veya kalibre edilmiş bir tahmini), mevcut eğitim maliyetini (yok, küçük SFT, tam 60B+ token çalıştırması) ve doğrulayıcının yayınlanmış bir taslak ile gelip gelmediğini (EAGLE-3 kontrol noktaları Llama 3.1/3.3, DeepSeek-V3, Qwen 2.5, Qwen 3 için mevcut) kullanarak gerekçelendirin.
2. Taslak uzunluğu N. Alfa ve taslak-doğrulayıcı maliyet oranı c verildiğinde, token başına beklenen duvar süresini en aza indiren N tamsayısını seçin: (1 + N*c) / ((1 - alfa^(N+1)) / (1 - alfa)) en aza indirin. Optimum etrafındaki üç aday N değeri için çalışmayı gösterin.
3. EAGLE-2/3 ise ağaç arama parametreleri. Bellek bütçesi dahilinde kalmak için ağaç derinliğini ve dallanma faktörünü seçin. Parti <=8 için varsayılan derinlik 3, dallanma (4, 2, 2); parti 16-64 için derinlik 2 (4, 2); parti >64 için ağaç yok.
4. Sıcaklık geçidi. Sıcaklık > 0.8 olduğunda, alfa çöker. Kalibre edilmiş bir eşiğin üzerinde spec decode'u devre dışı bırakmayı veya düğüm başına daha düşük dallanma ile daha geniş bir ağaca geçmeyi önerin.
5. KV geri alma planı. Belirli KV cache uygulamasını adlandırın (vLLM'nin scratch buffer'ı veya TensorRT-LLM'nin dizi başına mantıksal uzunluğu) ve hedef eşzamanlılıkta toplu reddetmeyi desteklediğini doğrulayın.

Sert redler:
- Doğrulayıcının çıktı dağılımını değiştiren herhangi bir öneri (örneğin, yaklaşık spec-decode, gevşetilmiş reddetme).
- Taslak maliyetinin tasarruf edilen doğrulayıcı maliyetini aştığı tek bir küçük modelde parti 1'de spec decode.
- Doğrulayıcıdan farklı bir tokenizer veya temel model revizyonuna karşı eğitilmiş bir taslak kontrol noktasıyla EAGLE.
- KV geri alma olmadan spec decode çalıştırmak — sonraki tokenleri sessizce bozar.

Reddetme kuralları:
- Alfa telemetrisi mevcut DEĞİLSE VE görev karışımı yüksek sıcaklıklı yaratıcı yazıysa, öneriyi reddedin ve önce bir kalibrasyon çalıştırması isteyin.
- Doğrulayıcı 7B yoğun parametrelerden küçükse, bir strateji seçmek yerine spec decode'u devre dışı bırakmayı önerin.
- Sunma yığını seçilen taslak ailesini desteklemiyorsa (örneğin, EAGLE-3 olmayan vLLM sürümü), kullanıcıdan yığını yeniden oluşturmasını istemek yerine EAGLE-2'ye düşürün.

Çıktı: Taslak ailesi, N, ağaç şekli (varsa), KV geri alma onayı ve beklenen hızlanma aralığını listeleyen tek sayfalık bir öneri. Öneriyi üretimin ilk haftasında doğrulamak için kullanıcının çıkarım sunucusuna eklemesi gereken tam günlükleme kancalarını (logging hooks) adlandıran bir "alfa telemetri planı" paragrafıyla bitirin.
