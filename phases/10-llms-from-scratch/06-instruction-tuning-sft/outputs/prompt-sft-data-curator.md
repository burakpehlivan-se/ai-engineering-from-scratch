---
name: prompt-sft-data-curator
description: Denetimli ince ayar (SFT) için talimat veri kümelerini tasarlayın ve düzenleyin
version: 1.0.0
phase: 10
lesson: 6
tags: [sft, instruction-tuning, fine-tuning, data-curation, alignment]
---

# SFT Veri Düzenleyici

Belirli bir yetenek (kod üretimi, matematik, konuşma, güvenlik) için talimat-ayar veri kümesi tasarlarken, veri toplamayı planlamak, kalite kriterlerini tanımlamak ve eğitim işlem hattını yapılandırmak için bu çerçeveyi kullanın.

## Girdi Gereksinimleri

Sağlayın:
- **Hedef yetenek** (ör. "Python kod üretimi", "tıbbi S/C", "çok turlu konuşma")
- **Taban model** (ör. Llama 3 8B, Mistral 7B, Qwen 2.5 72B)
- **Bütçe** (etiketleme saatleri, sentetik üretim için API maliyetleri)
- **Format tercihi** (Alpaca, ShareGPT, ChatML)

## Adım 1: Veri Kümesi Tasarımı

### Boyut Kılavuzları

| Kalite Seviyesi | Gerekli Örnekler | Beklenen Sonuç |
|--------------|----------------|------------------|
| Araştırma prototipi | 1.000-5.000 | LIMA kalitesi: örnekler uzman yazımıysa daha büyük veri kümeleriyle karşılaştırılabilir |
| Üretim v1 | 10.000-50.000 | Stanford Alpaca seviyesi: yaygın görevlerde sağlam talimat takibi |
| Üretim v2 | 50.000-200.000 | Vicuna/Llama 2 Chat seviyesi: sağlam çok-turlu, alan kapsamı |

Kalite her zaman nicelikten iyidir. 1.000 uzman yazımı örnek (LIMA, Mayıs 2023) 50.000+ örnekle eğitilmiş modellerle eşleşti. Öncelik verin:
1. **Çeşitlilik** -- hedef yeteneklerin tam aralığını kapsayın
2. **Doğruluk** -- her yanıt olgusal olarak doğru olmalıdır
3. **Netlik** -- yanıtlar kısa ve iyi yapılandırılmış olmalıdır
4. **Zorluk gradyanı** -- kolay, orta ve zor örnekler dahil edin

### Çeşitlilik Kontrol Listesi

Genel amaçlı bir asistan için:
- Açık uçlu sorular (%20)
- Olgusal S/C (%20)
- Yaratıcı yazma (%10)
- Kod üretimi (%15)
- Akıl yürütme ve matematik (%15)
- Özetleme (%10)
- Kısıtlarla talimat takibi (%10)

Alana özgü modeller için yüzdeleri ayarlayın. Bir kodlama asistanı kod üretimine %60 ve kod açıklamasına %20 tahsis edebilir.

## Adım 2: Veri Formatı

### Alpaca Formatı (tek turlu)

```json
{
  "instruction": "Python'da bir diziyi tersine çeviren bir fonksiyon yaz.",
  "input": "",
  "output": "def reverse_string(s):\n    return s[::-1]"
}
```

Şu durumlarda kullanın: tek turlu görevler, basit talimat-yanıt çiftleri, hızlı prototipleme.

### ShareGPT Formatı (çok turlu)

```json
{
  "conversations": [
    {"from": "system", "value": "Sen bir Python uzmanısın."},
    {"from": "human", "value": "Bir diziyi nasıl tersine çeviririm?"},
    {"from": "gpt", "value": "Dilimlemeyi kullanın: s[::-1]"},
    {"from": "human", "value": "Peki ya bir liste için?"},
    {"from": "gpt", "value": "Aynı sözdizimi çalışır: my_list[::-1]"}
  ]
}
```

Şu durumlarda kullanın: konuşma uygulamaları, çok turlu bağlam önemlidir.

### ChatML Formatı (özel token'larla)

```
<|im_start|>system
Sen bir Python uzmanısın.<|im_end|>
<|im_start|>user
Bir diziyi nasıl tersine çeviririm?<|im_end|>
<|im_start|>assistant
Dilimlemeyi kullanın: s[::-1]<|im_end|>
```

Şu durumlarda kullanın: ChatML'yi yerel olarak kullanan modelleri hedefleme (Qwen, Yi).

## Adım 3: Kalite Kriterleri

### Örnek Başına Kontroller

1. **Yanıt ilgililiği**: Yanıt gerçekten talimatı yanıtlıyor mu?
2. **Olgusal doğruluk**: Tüm iddialar doğrulanabilir ve doğru mu?
3. **Tamlık**: Yanıt talimatı tam olarak ele alıyor mu?
4. **Kısalık**: Aynı bilgi daha az kelimeyle aktarılabilir mi?
5. **Format tutarlılığı**: Yanıt beklenen stili takip ediyor mu?

### Kırmızı Bayraklar (örneği reddedin)

- Yanıt kendi kendiyle çelişiyor
- Yanıt reddetme olmadan zararlı içerik içeriyor
- Yanıt olgu veya atıf halüsinasyonları yapıyor
- Talimat belirsiz ve yanıt netleştirmiyor
- Yanıt talimatın yeniden ifade edilmiş bir kopyası

### Veri Kümesi Düzeyinde Kontroller

- Herhangi bir tek kaynaktan/şablondan örneklerin %5'inden fazlası yok
- Yanıt token'larının en az %80'i anlamlı (doldurucu değil)
- Ortalama yanıt uzunluğu 50-200 token (çok kısa veya çok uzun kaçının)
- Sistem prompt çeşitliliği: en az 10 farklı sistem prompt temsil edilmiş

## Adım 4: Eğitim Yapılandırması

| Parametre | Önerilen Aralık | Notlar |
|-----------|------------------|-------|
| Öğrenme hızı | 1e-5 ila 5e-5 | Daha büyük modeller için daha düşük (70B için 1e-5, 7B için 5e-5) |
| Epoklar | 1-3 | Doğrulama kaybını izleyin, ilk artış belirtisinde durun |
| Batch boyutu | 32-128 | GPU kısıtlıysa gradyan birikimi ile ölçeklendirin |
| Isınma | Adımların %0-5'i | Ön-eğitimden daha az kritik |
| Ağırlık azalması | 0.0-0.1 | Kısa ince ayar çalıştırmaları için isteğe bağlı |
| Kayıp maskeleme | Yalnızca yanıt token'ları | Talimat ve sistem prompt token'larını maskeleyin |
| Ön-eğitim verisi karıştırma | %2-5 | Felaket unutmayı önlemek için ham metin karıştırın |

## Adım 5: Değerlendirme Protokolü

Eğitimden sonra, şunlar üzerinde değerlendirin:

1. **Talimat takip oranı**: Modelin ilgili, eksiksiz bir yanıt ürettiği test prompt'larının yüzdesi
2. **Unutma puanı**: Taban modelle karşılaştırıldığında tutulan genel metin derlemi üzerinde karmaşıklık
3. **Format uyumluluğu**: Beklenen sohbet formatını takip eden yanıtların yüzdesi
4. **MT-Bench veya AlpacaEval**: Talimat-ayarlı modeller için standart kıyaslamalar
5. **Alana özgü değerlendirme**: Hedef yeteneğiniz için özel değerlendirme

### Uyarı İşaretleri

- 1. epoktan sonra doğrulama kaybı artıyor: aşırı uyuyorsunuz, epokları azaltın veya veriyi artırın
- Unutma puanı > %15 artıyor: öğrenme hızı çok yüksek veya çok fazla epok
- Model eğitim örneklerini aynen yeniden üretiyor: ciddi aşırı uyum, daha çeşitli veri gerekiyor
- Model zararsız talimatları reddediyor: güvenlik verisi üzerinde aşırı eğitilmiş, veri kümesini yeniden dengeleyin
