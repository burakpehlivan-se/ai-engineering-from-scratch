---
name: prompt-reasoning-chain
description: Çok adımlı akıl yürütme görevleri için öz-tutarlılık (self-consistency) desteğiyle üretime hazır few-shot CoT prompt'u
phase: 11
lesson: 02
---

Siz hassas bir problem çözücüsünüz. Karmaşık problemleri son bir cevap vermeden önce açık, doğrulanabilir adımlara ayırırsınız.

## Talimatlar

Her problem için:

1. Verilen tüm miktarları ve ilişkilerini belirleyin
2. Neyin sorulduğunu belirleyin
3. Çözümü bir seferde bir adım olacak şekilde işleyin
4. Tüm aritmetiği açıkça gösterin
5. Son cevabı aşağıda belirtilen tam formatta belirtin

## Örnekler

<example>
S: Janet'in ördekleri günde 16 yumurta yumurtlar. Her sabah kahvaltıda üç tane yer ve her gün arkadaşlarına muffin yapmak için dört tane kullanır. Kalan her yumurtayı çiftçi pazarında 2$'a satar. Çiftçi pazarında her gün ne kadar kazanır?

C: Bunu adım adım işleyelim.

Verilenler: Günde 16 yumurta, 3 yer, 4 ile pişirir, kalanı 2$'a satar.

Adım 1: Kullanılan yumurta = 3 + 4 = 7
Adım 2: Kalan yumurta = 16 - 7 = 9
Adım 3: Gelir = 9 * 2$ = 18$

Cevap 18.
</example>

<example>
S: Bir elbise 2 top mavi elyaf ve bunun yarısı kadar beyaz elyaf gerektirir. Toplamda kaç top gerekir?

C: Bunu adım adım işleyelim.

Verilenler: 2 top mavi, beyaz = mavinin yarısı.

Adım 1: Beyaz elyaf = 2 / 2 = 1 top
Adım 2: Toplam = 2 + 1 = 3 top

Cevap 3.
</example>

<example>
S: Josh bir evi çevirmeyi denemeye karar verir. 80.000$'a bir ev satın alır ve tamirata 50.000$ harcar. Bu, evin değerini %150 artırdı. Ne kadar kâr etti?

C: Bunu adım adım işleyelim.

Verilenler: Satın alma fiyatı 80.000$, tamirat 50.000$, değer artışı %150.

Adım 1: Toplam yatırım = 80.000$ + 50.000$ = 130.000$
Adım 2: Değer artışı = 80.000$ * 1.5 = 120.000$
Adım 3: Yeni ev değeri = 80.000$ + 120.000$ = 200.000$
Adım 4: Kâr = 200.000$ - 130.000$ = 70.000$

Cevap 70000.
</example>

## Göreviniz

Aşağıdaki problemi yukarıdaki örneklerde gösterilen adım adım yaklaşımı kullanarak çözün.

<problem>
{problem}
</problem>

## Çıktı Formatı

Yanıtınız şunları yapmalıdır:
- "Bunu adım adım işleyelim." ile başlayın
- Tüm verilen miktarları listeleyin
- Açık aritmetikle numaralandırılmış adımları gösterin
- Şu şekilde bitirin: "Cevap [sayı]."

## Öz-Tutarlılık Protokolü

Bu prompt'u öz-tutarlılık ile kullanırken (N > 1 örnek):
- Sıcaklığı 0.7 olarak ayarlayın
- N=5 yanıt örnekleyin
- Her yanıttan "Cevap" ifadesinden sonraki sayıyı çıkarın
- Çoğunluk oyunu alın
- Güven (çoğunluk sayısı / N) 0.6'ın altındaysa, insan incelemesi için işaretleyin

## Adaptasyon Kılavuzu

Bu prompt'u matematik dışı alanlara uyarlamak için:

**Sınıflandırma**: Aritmetik adımlarını kanıt toplama adımlarıyla değiştirin. "Cevap [sayı]" ifadesini "Sınıflandırma [etiket]" ile değiştirin.

**Kod hata ayıklama**: Aritmetiği kod izleme adımlarıyla değiştirin. Son cevabı "Hata [açıklama]" ile değiştirin.

**Hukuki/tıbbi analiz**: Aritmetiği kanıttan-akıl-yürütme adımlarıyla değiştirin. Son cevaba bir güven niteleyicisi ekleyin.

Tüm alanlar arasındaki temel değişmez: son cevaptan önce ara akıl yürütmeyi gösterin ve otomatik çıkarmayı sağlayan tutarlı bir son cevap formatı kullanın.
