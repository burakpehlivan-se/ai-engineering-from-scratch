# Hafıza Blokları ve Sleep-Time Compute (Letta)

> MemGPT 2024'te Letta oldu. 2026 evrimi iki fikir ekler: modelin doğrudan düzenleyebildiği ayrışmış (discrete) işlevsel hafıza blokları ve birincil agent boşta iken hafızayı birleştiren asenkron bir sleep-time agent'ı. Konuşma sınırını aşarak hafızayı nasıl ölçeklersiniz işte budur.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 07 (MemGPT)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Letta'nın kullandığı üç hafıza katmanını (core, recall, archival) ve her birinin rolünü adlandırın.
- Hafıza bloğu kalıbını açıklayın: İnsan bloğu, Persona bloğu ve birinci sınıf tip nesneleri olarak kullanıcı tanımlı bloklar.
- Sleep-time compute'in ne olduğunu, neden kritik yolun dışında olduğunu ve neden birincil agent'dan daha güçlü bir model çalıştırabileceğini açıklayın.
- Birincil agent'ın yanıtlar sunduğu ve sleep-time agent'ın turlar arasında blokları birleştirdiği betiklenmiş bir iki-agent döngüsü uygulayın.

## Problem

MemGPT (Ders 07) sanal bellek kontrol akışını çözdü. Üç production sorunu ortaya çıktı:

1. **Gecikme (latency).** Her hafıza işlemi kritik yolun üzerindedir. Agent'ın kullanıcı beklerken kıstırması, özetlemesi veya uzlaştırması gerekirse, kuyruk gecikmesi patlar.
2. **Hafıza çürümesi.** Yazmalar birikir. Çelişen olgular kalır. Arama eski içerikte boğulur.
3. **Yapı kaybı.** Düz bir arşiv deposu "İnsan bloğu her zaman prompt'ta; Persona bloğu her zaman prompt'ta; Görev bloğu oturum başına takaslanır" ifadesini açıklayamaz.

Letta (letta.com) 2026 yeniden yazımıdır. Hafıza bloklarını yapıyı açık hale getirir; sleep-time compute birleştirmeyi kritik yolun dışına taşır.

## Kavram

### Üç katman

| Katman | Kapsam | Nerede yaşıyor | Kimin tarafından yazılır |
|--------|-------|----------------|--------------------------|
| Core | Her zaman görünür | Ana prompt içinde | Agent aracı + sleep-time yeniden yazmaları |
| Recall | Konuşma geçmişi | Alınabilir | Otomatik tur kaydı |
| Archival | Keyfi olgular | Vektör + KV + graf | Agent aracı + sleep-time işleme |

Core MemGPT core'udur. Recall, kovulan kuyruğuyla konuşma tamponudur. Archival harici depodur. Ayrım, MemGPT'nin iki katmanlı aşırı yüklemesini temizler.

### Hafıza blokları

Bir blok, core katmanının tipli, kalıcı, düzenlenebilir bir bölümüdür. Orijinal MemGPT makalesi ikisini tanımladı:

- **İnsan bloğu** — kullanıcı hakkında olgular (isim, rol, tercihler, hedefler).
- **Persona bloğu** — agent'ın öz-kavramı (kimlik, ton, kısıtlamalar).

Letta keyfi kullanıcı tanımlı bloklara genelleştirir: mevcut hedef için bir `Task` bloğu, kod tabanı olguları için bir `Project` bloğu, katı kısıtlamalar için bir `Safety` bloğu. Her bloğun `id`, `label`, `value`, `limit` (karakter sınırı), `description`'ı (modelin ne zaman düzenleyeceğini bilmesi için) vardır.

Bloklar araç yüzeyiyle düzenlenebilir:

- `block_append(label, text)`
- `block_replace(label, old, new)`
- `block_read(label)`
- `block_summarize(label)` — limitine yaklaşan bir bloğu yoğunlaştır.

### Sleep-time compute

2025 Letta eklemesi: arka planda, kritik yolun dışında bir ikinci agent çalıştırın. Sleep-time agent'ları konuşma dökümlerini ve kod tabanı bağlamını işler, `learned_context`'i paylaşılan bloklara yazar ve arşiv kayıtlarını birleştirir veya geçersiz kılar.

Ortaya çıkan özellikler:

- **Gecikme maliyeti yok.** Birincil yanıtlar hafıza işlemlerini beklemez.
- **Daha güçlü modele izin.** Sleep-time agent daha pahalı, daha yavaş bir model olabilir çünkü gecikmeyle sınırlı değildir.
- **Doğal birleştirme penceresi.** Kullanıcı beklemedeyken duplikasyonu azaltın, özetleyin, çelişen olguları geçersiz kılın.

Şekil insanların çalışma şekline benzer: görevi yaparsınız, üzerine uyursunuz, uzun vadeli hafıza gece boyunca yerleşir.

### Letta V1 ve native reasoning

Letta V1 (`letta_v1_agent`, 2026) `send_message`/heartbeat ve inline `Thought:` token'larını native reasoning lehine terk eder. Responses API (OpenAI) ve extended thinking ile Messages API (Anthropic) ayrı bir kanalda reasoning üretir, turlar arası iletilir (production'da sağlayıcılar arası şifreli). Kontrol hâlâ ReAct'tır. Thought trace'i yapısal, prompt şeklinde değil.

### Bu kalıp nerede yanlış gider

- **Blok şişmesi.** Sonsuz `block_append` limiti çabuk doldurur. Yazmadan önce blok sıkıştırıcısı bağlayın.
- **Sessiz kayma.** Sleep-time agent bir bloğu yeniden yazar ve birincil agent fark etmez. Blokları versiyonlayın ve trace'de farkları (diff) gösterin.
- **Zehirlenmiş birleştirme.** Sleep-time agent saldırganın erişebileceği içeriği core'a işler. Ders 27 sleep-time yüzeyi için de geçerlidir.

## İnşa Et

`code/main.py` şunları uygular:

- `Block` — id, label, value, limit, description.
- `BlockStore` — CRUD + `near_limit(label)` yardımı.
- İki betiklenmiş agent — `PrimaryAgent` bir tur sunar, `SleepTimeAgent` turlar arasında birleştirir.
- Blok yazmalarıyla üç turluk bir konuşma ve bir bloğu özetleyen ve eski bir olguyu geçersiz kılan bir pass gösteren bir trace.

Çalıştırın:

```bash
python3 code/main.py
```

Transkript ayrımı gösterir: birincil turlar hızlı ve ham yazarlar üretir; sleep pass sıkıştırır ve temizler.

## Kullan

- **Letta** (letta.com) referans uygulaması için. Self-hosted veya yönetilen bulut.
- **Claude Agent SDK yetenekleri** blok şeklinde bilgi olarak — bir yetenek, agent'ın talep üzerine yüklediği adlandırılmış, versiyonlanmış, alınabilir bir talimat bloğudur.
- **Özel inşaatlar** depolama arka ucunda kontrol isteyen ekipler için. Sonradan geçiş yapabilmeniz için Letta API sözleşmesini kullanın.

## Teslim Et

`outputs/skill-memory-blocks.md`, güvenlik kuralları ve alıntı tesisatıyla herhangi bir runtime için Letta şeklinde bir blok sistemi üretir.

## Alıştırmalar

1. `near_limit` döndüğünde blok değerini model tarafından üretilen bir özetle değiştiren `block_summarize` aracı ekleyin. Hem özetleme çağrılarını hem blok taşmasını en aza indiren tetikleme eşiği nedir?
2. Arşiv üzerinde uyku zamanı ayıklaması (dedup) uygulayın: metinleri >90% token örtüşen iki kayıt tek birine çöker. Bunu yalnızca sleep pass'te, asla kritik yolda yapın.
3. Blokları versiyonlayın. Her yazımda eski değeri ve bir diff'i kaydedin. Operatörlerin "agent neden X'i unuttu" sorusunu hata ayıklaması için `block_history(label)` sunun.
4. Sleep-time agent'ları güvenilmez yazarlar olarak kabul edin. Persona veya Safety bloğuna dokunduklarında, commit'ten önce ikinci bir agent incelemesi gerektirin.
5. Örneği Letta API'sini (`letta_v1_agent`) kullanacak şekilde taşıyın. Blok şemasında ne değişir ve native reasoning trace şeklini nasıl değiştirir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Memory block | "Düzenlenebilir prompt bölümü" | Core hafızasının tipli, kalıcı, LLM tarafından düzenlenebilir segmenti |
| Human block | "Kullanıcı hafızası" | Kullanıcı hakkında olgular, core'da sabitlenmiş |
| Persona block | "Agent kimliği" | Öz-kavram, ton, kısıtlamalar, core'da sabitlenmiş |
| Sleep-time compute | "Asenkron hafıza çalışması" | Kritik yolun dışında birleştirme yapan ikinci agent |
| Core / Recall / Archival | "Katmanlar" | Üç katmanlı hafıza ayrımı: her zaman görünür / konuşma / harici |
| Block limit | "Sınır" | Blok başına karakter sınırı; zorlamalı özetleme |
| Native reasoning | "Düşünme kanalı" | Sağlayıcı düzeyinde reasoning çıktısı, prompt düzeyinde `Thought:` değil |
| Learned context | "Uyku çıktısı" | Sleep-time agent'ın paylaşılan bloklara yazdığı olgular |

## İleri Okuma

- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) — blok kalıbı
- [Letta, Sleep-time Compute blog](https://www.letta.com/blog/sleep-time-compute) — asenkron birleştirme
- [Letta, Rearchitecting the Agent Loop](https://www.letta.com/blog/letta-v1-agent) — native reasoning yeniden yazımı
- [Packer ve diğerleri, MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — köken
