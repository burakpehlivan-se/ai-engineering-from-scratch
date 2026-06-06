---
name: skill-fine-tuning-guide
description: LLM'leri ne zaman ve nasıl LoRA ve QLoRA ile ince ayar yapacağınıza dair karar ağacı
version: 1.0.0
phase: 11
lesson: 8
tags: [fine-tuning, lora, qlora, peft, llm-engineering]
---

# İnce Ayar Karar Kılavuzu

İnce ayardan önce, bunları sırayla deneyin:

```
1. Prompt mühendisliği (dakikalar, 0$)
2. Prompt'ta few-shot örnekleri (dakikalar, 0$)
3. Bilgi getirmesi için RAG (günler, 10-100$/ay)
4. LoRA/QLoRA ile ince ayar (günler, deney başına 5-50$)
5. Tam ince ayar (haftalar, çalıştırma başına 100-10.000$)
```

Yalnızca önceki adım ölçülebilir şekilde yetersizse bir sonraki adıma geçin.

## Ne Zaman İnce Ayar Yapılır

- Model, prompting ile başarılamayan tutarlı bir çıktı stiline veya formatına ihtiyaç duyuyor
- Daha büyük bir modeli damıtıyorsunuz (8B modelden GPT-4 kalitesi)
- Gecikme önemli ve few-shot örnekleri çok fazla token ekliyor
- Modelin karmaşık bir akıl yürütme kalıbını güvenilir bir şekilde takip etmesini istiyorsunuz
- İstenen girdi-çıktı davranışının 1.000+ yüksek kaliteli örneğine sahipsiniz

## Ne Zaman İnce Ayar YAPILMAZ

- Model, doğru prompt ile zaten istediğinizi yapıyor
- Modelin gerçekleri bilmesini istiyorsunuz (bunun yerine RAG kullanın)
- 500'den az eğitim örneğiniz var (muhtemelen aşırı uyum sağlar)
- Görev sık sık değişiyor (yeniden eğitim pahalıdır)
- Belirli bir çıktıyı hangi verilerin etkilediğini denetlemeniz gerekiyor (ince ayar kara kutudur)

## Yöntem Seçimi

| GPU VRAM | 7B model | 13B model | 70B model |
|----------|----------|-----------|-----------|
| 16GB (T4) | QLoRA | Mümkün değil | Mümkün değil |
| 24GB (3090/4090) | QLoRA veya LoRA | QLoRA | Mümkün değil |
| 40GB (A100) | LoRA veya Tam | QLoRA veya LoRA | QLoRA |
| 80GB (A100/H100) | Tam | LoRA veya Tam | QLoRA veya LoRA |

## LoRA Yapılandırma Kontrol Listesi

1. r=16, alpha=32 ile başlayın (çoğu görev için güvenli varsayılan)
2. Önce q_proj ve v_proj'yi hedefleyin (asgari uygulanabilir LoRA)
3. QLoRA için öğrenme oranı 2e-4, LoRA fp16 için 5e-5 kullanın
4. lora_dropout=0.05 ayarlayın
5. 1-3 epoch eğitin (daha fazlası aşırı uyum riski taşır)
6. Tutulan bir set üzerinde her 100 adımda bir değerlendirin
7. Kontrol noktalarını kaydedin ve en iyiyi değerlendirme kaybına göre seçin

## Yaygın Hatalar

- Çok fazla epoch eğitmek (küçük veri kümelerinde epoch 2-3'ten sonra aşırı uyum)
- Tam ince ayarla aynı öğrenme oranını kullanmak (LoRA daha yüksek LR gerektirir)
- Pad token'ını ayarlamayı unutmak (Llama modellerinde NaN kayıplarına neden olur)
- Temel modeli dondurmamak (LoRA'nın amacını bozar)
- Yalnızca eğitim verisinde değerlendirmek (değerlendirme için her zaman %10-20 tutun)
- Prompt mühendisliği temelini atlamak (prompting'in zaten çözdüğü bir sorunu ince ayar yapmak)

## Kalite Doğrulama

Eğitimden sonra, 200+ tutulan örnek üzerinde karşılaştırın:
1. En iyi prompt ile temel model (temel)
2. LoRA adaptörü ile temel model (ince ayarlı modeliniz)
3. Aynı prompt ile GPT-4 veya Claude (tavan)

LoRA modeli, promptlanmış temeli yenemezse, eğitim verileriniz veya yapılandırmanız daha fazla hesaplama değil, çalışma gerektirir.

## Adaptör Yönetimi

- Çoklu görev sunma için adaptörleri ayrı tutun (istek başına adaptör değiştirin)
- Tek görev dağıtımı için adaptörleri temel ağırlıklarla birleştirin
- Adaptörleri Hugging Face Hub'da depolayın (10-100MB, sürümlemesi ve paylaşması kolay)
- Birleştirilmiş model çıktılarının birleştirilmemiş çıktılarla eşleştiğini dağıtmadan önce test edin
- Birden fazla adaptörü tek bir adaptörde birleştirmek için TIES-Merging veya DARE kullanın

## Eğitimde Hata Ayıklama

Kayıp azalmıyorsa:
1. Öğrenme oranını kontrol edin (LoRA için çok düşük, 2e-4 deneyin)
2. LoRA katmanlarının gerçekten gradyan aldığını doğrulayın
3. Temel model ağırlıklarının dondurulmuş olduğunu onaylayın
4. Veri formatını kontrol edin (tokenizer, modelin beklenen formatıyla eşleşmelidir)

Kayıp azalıyor ancak değerlendirme kalitesi kötüyse:
1. Eğitim verisi kalite sorunu (çöp girer, çöp çıkar)
2. Aşırı uyum (epoch'ları azaltın, dropout'ı artırın, daha fazla veri ekleyin)
3. Yanlış hedef modüller (karmaşık görevler için MLP katmanları ekleyin)
4. Rank çok düşük (r=32 veya r=64'ü deneyin)
