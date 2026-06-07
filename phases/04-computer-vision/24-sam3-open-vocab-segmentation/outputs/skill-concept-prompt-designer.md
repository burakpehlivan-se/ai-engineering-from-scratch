---
name: skill-concept-prompt-designer
description: Kullanıcı ifadelerini bölme, belirsizlik giderme ve geri dönüşlerle iyi biçimlendirilmiş SAM 3 kavram istemlerine dönüştürün
version: 1.0.0
phase: 4
lesson: 24
tags: [sam3, açık-kelimelik, istem-mühendisliği, segmentasyon]
---

# Kavram İstem Tasarımcısı

SAM 3'ün doğruluğu büyük ölçüde kavram isteminin nasıl ifade edildiğine bağlıdır. Bu beceri, serbest biçimli kullanıcı ifadelerini SAM 3'ün iyi ele aldığı istemlere normalleştirir.

## Ne zaman kullanılır

- Doğal dil nesne sorgularını kabul eden bir UI inşa ederken.
- Yukarı akış arayanların cümleler gönderdiği SAM 3'ü bir API aracılığıyla sunarken.
- Zayıf SAM 3 eşleşmelerini ayıklarken — genellikle model değil, istem hatalı biçimlendirilmiştir.

## Girdiler

- `utterance`: ham kullanıcı dizesi.
- `context`: isteğe bağlı alan ipucu (örn. "gözetim", "tıbbi", "perakende").
- `max_concepts`: ifade başına çıkarılacak maksimum kavram; varsayılan 5.

## SAM 3'ün tercih ettiği kurallar

- **Cümle değil, kısa isim öbekleri.** `"kedi"`, `"bir kedi var"`'dan kazanır.
- **Somut isimler.** `"kaykay"`, `"üzerinde binilecek şey"`'den kazanır.
- **Nitelipler isimden hemen önce.** `"kırmızı araba"`, `"kırmızı olan araba"`dan kazanır.
- **Küçük harf.** SAM 3 sağlamdır ancak deneysel olarak küçük harfli girdilerde biraz daha iyidir.
- **Tekil veya çoğul.** İkisi de çalışır; birden fazla örnek beklendiğinde çoğul yardımcı olur.

## Adımlar

1. **Yaygın ayraçlarla belgeleme** — virgül, noktalı virgül, "ve", "veya", "&".
2. **Dolgu öneklerini bırakın** — "bul", "bana göster", "bölütle", "tespit et", "konumlandır", "bir", "an", "şu".
3. **Edat niteleyicilerini yalnızca görsel iseler koruyun** — `"çizgili kırmızı şemsiye"` evet, `"dünkü şemsiye"` hayır (`"dünkü"` görüntüde değil).
4. **Çakışmaları belirsizlikten kurtarın** isteğe bağlı `context` kullanarak:
 - gözetim bağlamında `"pencere"` -> `"bina penceresi"`.
 - tıbbi bağlamda `"pencere"` -> genellikle hata; kullanıcının netleştirmesini önerin.
5. Bölme sıfır kavram veriyorsa *ve* ifade en az bir somut isim içeriyorsa, **tam dizeye geri dönün**. Hiçbir somut isim çıkarılamıyorsa, bir kavram yayınlamayın — yalnızca uyarılar döndürün ve kullanıcıdan netleştirmesini isteyin (Kurallara bakın).
6. **`max_concepts` ile sınırlayın.** Arayanın istediğinden daha fazla kavram çıkarıldıysa, ilk `max_concepts`'i ifade sırasında tutun ve geri kalanını `"exceeded max_concepts"` nedeniyle `dropped` altında yayınlayın. Bu, kullanıcı uzun bir sıralama yapıştırdığında gecikmeyi sınırlı tutar.

## Çıktı biçimi

```
[designed prompts]
 utterance: <orijinal>
 concepts: ["concept_1", "concept_2", ...]
 dropped: ["filler_1", ...]
 warnings: ["concept too abstract", "may match many classes", ...]

[sam3 calls]
 Her kavram için çalıştır: sam3.detect(image, concept)
 Çıktıları tespit başına ayrı kavram etiketleri ile birleştirin.
```

## Örnekler

```
in: "can you find me a cat or two dogs?"
out: ["cat", "dogs"]
dropped: ["can you find me", "a", "or two", "?"]
note: "dogs" çoğul tutuldu çünkü ifade "two dogs" diyor — çoğul ipucu korundu.

in: "segment the big red truck and the blue sedan"
out: ["big red truck", "blue sedan"]
dropped: ["segment", "the", "and"]

in: "thing near the door"
out: ["door"]
warnings: ["'thing' SAM 3 için çok soyut; 'door'a geri dönüldü"]

in: "striped red umbrella, green hat, pink balloon"
out: ["striped red umbrella", "green hat", "pink balloon"]
```

## Kurallar

- 8 kelimeden uzun cümleleri asla SAM 3'e geçirmeyin — doğruluk bunun üzerinde düşer.
- Bir ifade çıkarılabilir somut isim içermiyorsa, SAM 3'ü çalıştırmayın; uyarıları döndürün ve netleştirme isteyin.
- Tırnak içindeki dizelerde noktalamaya göre bölmeyin; `"siyah beyaz kedi"` tırnak içindeyse tek kavram olarak koruyun.
- Üretim hata ayıklaması için orijinal ifadeyi ve türetilmiş kavramları her zaman kaydedin.
