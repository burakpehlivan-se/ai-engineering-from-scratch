---
name: lm-eval-harness
description: JSONL görev şartnamesi, beş metrik, değiştirilebilir adaptör ve liderlik tablosu JSON çıktısı ile minimal bir dil modeli değerlendirme iskeleti
version: 1.0.0
phase: 19
lesson: 49
tags: [evaluation, metrics, leaderboard, harness]
---

## Ne Zaman Kullanılır

Sabit bir görev kümesine karşı iki modeli, iki kontrol noktasını veya iki istem şablonunu karşılaştır. Zaman içinde gönderdiğiniz ve izlemeniz gereken her şey.

## Görev Şartnamesi

Örnek başına bir JSONL satırı:

```json
{"id": "ex-001", "prompt": "...", "targets": ["..."], "metric": "exact_match", "extras": {}}
```

Bir dosyadaki tüm örnekler bir metriği paylaşır. Dosya adı görev adıdır.

## Metrikler

| Metrik | İmza | Kullanım |
|--------|-----------|---------|
| exact_match | küçük harf + boşluk normalleştir, eşitlik | Aritmetik, kısa-yanıt gerçekleri |
| substring_contains | hedef normalleştirilmiş tahminde geçmeli | Çapa sözcüklü serbest biçim üretim |
| multiple_choice | ilk harf eşleşmesi | A/B/C/D tarzı sorular |
| rouge_l | tokenleştirilmiş metin üzerinde LCS F1 | Özetleme, parafraze |
| code_exec | tahminin `f`'sini io_pairs üzerinde çalıştır, eşleşmeleri say | Kod üretimi |

Tüm metrikler [0,0, 1,0] aralığında float döner. Görev puanı ortalamadır.

## Adaptör

```python
class Adapter(Protocol):
 name: str
 def generate(self, prompts: list[str]) -> list[str]: ...
```

Adaptör, tek modele özgü koddur.

## Liderlik Tablosu JSON

Şema dizesi, zaman damgası, görev başına puanlar ve gecikme, genel ortalama. Çalıştırmaları karşılaştırırken tahmin-düzeyinde regresyonların görünür olması için örnek başına kayıtları dahil et.

## Başarısızlık Kipleri

- Metrik [0, 1] dışında dönüyor: genel puan yorumlanamaz hale gelir.
- Bir görev dosyasında karışık metrikler: onaylama tetiklenir; dosya başına bir metrik tut.
- Kısıtlı ad alı olmadan code_exec: keyfi kod yürütme.
- Şema dizesi yok: format evrimi aşağı yöndeki panoları bozar.
