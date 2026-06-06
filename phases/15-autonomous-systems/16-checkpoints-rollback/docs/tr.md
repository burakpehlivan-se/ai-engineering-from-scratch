# Kontrol Noktaları ve Geri Alma (Checkpoints and Rollback)

> Her grafik durumu (graph-state) geçişi kalıcı hale gelir. Bir işçi (worker) çöktüğünde kirası (lease) sona erer ve başka bir işçi en son kontrol noktasından (checkpoint) devam alır. Cloudflare Durable Objects saatlerce veya haftalarca durumu tutar. Öner-sonra-uygula (Ders 15) eylem başına bir geri alma planı tanımlar. Eylem sonrası doğrulama döngüyü kapatır. EU AI Act Madde 14, yüksek riskli sistemler için etkili insan gözetimini zorunlu kılar — pratikte bu, kontrol noktalarının sorgulanabilir, geri almaların provadan geçirilmiş ve denetim izinin (audit trail) bir deploy'dan sağ kalması gerektiği anlamına gelir. Keskin başarısızlık modu: özdeşlik anahtarı ve ön koşul kontrolleri olmadan, geçici bir hatadan sonra yeniden deneme, zaten onaylanmış bir eylemi iki kez çalıştırabilir. Eylem sonrası doğrulama tam da bunu yakalar.

**Tür:** Öğrenme
**Diller:** Python (stdlib, kontrol noktası ve geri alma durum makinesi)
**Önkoşullar:** Faz 15 · 12 (Dayanıklı çalıştırma), Faz 15 · 15 (Öner-sonra-uygula)
**Süre:** ~60 dakika

## Sorun

Dayanıklı çalıştırma (Ders 12), çökmüş bir agent'ın devam edilebilir olmasını sağlar. Öner-sonra-uygula (Ders 15), onaylanmış bir eylemin denetlenebilir olmasını sağlar. Bu ders onları birleştirir: onaylanmış bir eylem kısmen çalıştırıldığında, çöktüğünde ve devam ettiğinde ne olur? Geri alma ne zaman çalışır ve hangi duruma karşı çalışır?

Gerçek sistemler bunu farklı bağlar:

- **LangGraph** her grafik durumu geçişini PostgreSQL'e kontrol noktası alır. İşçi çöktüğünde kira serbest kalır ve başka bir işçi en son kontrol noktasından devam eder. İş akışları `interrupt()` ile durur ki bu da kalıcıdır.
- **Cloudflare Durable Objects** anahtar başına durumu saatlerce veya haftalarca tutar. Hesaplamayı onaylı eylemin depolamasıyla aynı yere yerleştirir.
- **Microsoft Agent Framework** iş akışı API'sinde `Checkpoint` ilkel elementlerini sunar; yeniden oynatma artı özdeşlik yeniden denemeleri kapsar.

Her durumda gerçekten çalışan kombinasyon: özdeşlik anahtarı (çift uygulamayı önler) + ön koşul kontrolü (durum hala onayladığımız durumda mı) + eylem sonrası doğrulama (yan etki gerçekten oldu mu) + doğrulama başarısızlığında geri alma.

## Kavram

### Her geçiş kalıcı hale gelir

Bir grafik durumu geçişi, iş akışını bir adlandırılmış durumdan diğerine taşıyan her adımdır. Basit uygulamalar sadece belirli uygulama noktalarında kalıcı hale getirir; üretim uygulamaları her geçişi kalıcı hale getirir. Maliyet (birkaç ekstra yazma) güvenilirlik kazancına göre küçüktür (yeniden oynatma herhangi bir yere iner, kira kurtarma hassastır).

### Kira kurtarma

Bir işçi çöktüğünde iş akışı kaybolmaz; kira (bu işçinin bu çalışmayı yürüttüğüne dair kısa süreli iddia) sona erer. Başka bir işçi en son kontrol noktasını alır ve devam eder. Kira mekanizması, üretim sistemlerinin devam eden çalışmaları kaybetmeden yuvarlanan deploy'lardan (rolling deploys) sağ kalmasını sağlar.

### Özdeşlik artı ön koşullar

Tek başına özdeşlik yeterli değildir. Düşünün: bir iş akışı "bakiye > 1000$ olduğunda A'dan B'ye 100$ aktar" için onaylanmıştır. İş akışı uygulanır, çalıştırma ortasında çöker ve devam eder. Sadece özdeşlik anahtarı kontrol edilip çalıştırma devam ederse, aktarma bir kez çalışır (doğru). Ancak çökme ile devam arasında A'nın bakiyesi farklı bir iş akışı aracılığıyla 500$'a düşerse. Özdeşlik kontrolü hala geçer; ön koşul geçemez. Ön koşul kontrolü olmadan, fazla çekim (overdraft) göndeririz.

Her sonuç eylemi ikisini de gerektirir:

- **Özdeşlik anahtarı:** çift uygulamayı önler.
- **Ön koşul kontrolü:** durumun hala onaylandığı durumla tutarlı olduğunu doğrular.

### Eylem sonrası doğrulama

"Araç 200 döndürdü" doğrulama değildir. Gerçek doğrulama hedef durumu tekrar okur ve yan etkinin gerçekten gerçekleştiğini doğrular. Kalıplar:

- Veritabanı güncelleme: `UPDATE ... RETURNING *` ardından döndürülen satırın hedeflenen durumla eşleştiğini doğrula.
- E-posta gönderme: gönderdikten sonra giden kutusunda mesaj kimliğini kontrol et.
- Dosya yazma: dosyayı geri oku ve hash'le.
- API çağrısı: hedef kaynak üzerinde takip `GET`.

Doğrulama başarısız olursa iş akışı bilinen kötü durumdadır. Geri alma devreye girer.

### Geri alma planları

Öner-sonra-uygula'daki (Ders 15) her sonuç eylemi bir geri alma planı taşır. Türler:

- **Band içi geri alma (In-band rollback):** yan etkiyi doğrudan tersine çevir (`INSERT` sonrası `DELETE`, gönderme sonrası düzeltme e-postası gönderme).
- **Telafi edici işlem (Compensating transaction):** orijinali etkisiz hale getiren yeni bir eylem (standart SAGA kalıbı).
- **Bant dışı geri alma (Out-of-band rollback):** bir insana uyarı, iş akışını durdurma, kötü durumu soruşturma için bırakma.

Boşuna geri alma ("bunu geri alamıyoruz") önermede adlandırılmalıdır. Geri alması olmayan eylemler, uygulamada daha güçlü HITL gerektirir (Ders 15 meydan okuma-yanıtı).

### EU AI Act Madde 14 işletme okuması

Madde 14, yüksek riskli sistemler için "etkili insan gözetimi" gerektirir. İşletme dilinde, uygulayıcılar bunu şu şekilde okur:

- Kontrol noktaları bir denetçi tarafından sorgulanabilir.
- Geri almalar provadan geçirilmiştir (en az bir kez uçtan uca test edilmiştir).
- Denetim izi bir deploy'dan sağ kalır (kontrol noktası arka planı geçici değildir).
- Başarısız doğrulamalara uyarı verilir, sessizce loglanmaz.

Uygulama ortasında çöken, devam eden ve verify + geri alma yolu olmadan yan etkiyi tamamlayan bir iş akışı Madde 14 testinden geçemez.

### Keskin başarısızlık modu: çift uygulama

Bu alandaki en yaygın üretim olayı (incident):

1. Eylem onaylandı, özdeşlik anahtarı k.
2. Uygulama başladı, çalıştırıldı, 200 döndürdü.
3. İş akışı "uygulandı" durumunu kalıcı hale getirmeden önce çöktü.
4. İş akışı devam etti; "onaylanmış ama uygulanmamış" gördü; tekrar çalıştırdı.
5. Yan etki iki kez tetiklendi.

Azaltma: çalıştırma öncesinde "yolda" (in-flight) bir niyet kaydedin, özdeşlik anahtarıyla çalıştırın, ardından eylem sonrası doğrulama başarısız olursa "uygulandı" olarak işaretleyin. Eylem tetiklenip durum yazımı başarısız olursa, doğrulamanız ve (gerekirse) tekrar tetiklemeniz gerektiğini bilirsiniz. Durum yazımı başarılı olup eylem başarısız olursa, kurtarma yolu aracılığıyla tam olarak bir kez doğrular ve tetiklersiniz.

## Kullan

`code/main.py`, özdeşlik, ön koşullar, doğrulama ve geri almayla kontrol noktası alınmış bir iş akışı uygular. Sürücü dört senaryoyu simüle eder: temiz çalışma, çökmeden sonra yeniden deneme (özdeşlik yakalar), ön koşul başarısızlığı (eylem tetiklenmeden iptal), doğrulama başarısızlığı (geri alma tetiklenir).

## Üret

`outputs/skill-rollback-rehearsal.md`, önerilen bir iş akışı için geri alma provası testi tasarlar ve kontrol noktası arka planını denetim izi kalıcılığı için denetler.

## Alıştırmalar

1. `code/main.py` çalıştırın. Dört senaryoyu doğrulayın. Uygulama sırasında çökme durumunda, eylemin yeniden denemeler boyunca tam olarak bir kez tetiklendiğini doğrulayın.

2. "Önce bitmiş olarak işaretle, sonra yap" kalıbını, durum yazımının eylemden sonra tetiklenmesi için değiştirin. Çökme senaryosunu tekrar çalıştırın. Kaç çift eylemin tetiklendiğini ölçün.

3. Belirli bir üretim eylemi için (ör. "Slack kanalında paylaşım") bir geri alma planı tasarlayın. Band içi, telafi edici veya bant dışı olarak sınıflandırın. Seçimi gerekçelendirin.

4. Bildiğiniz bir iş akışını seçin. Her durum geçişini belirleyin. Her birini bir dayanıklılık gereksinimiyle (kalıcı / kalıcı değil) işaretleyin. Şu anda kalıcı hale getirmediğinizlerin sayısını bulun.

5. Provadan geçirilmiş geri alma testi: gerçek bir iş akışını çalıştıran, çöktüren ve geri alma yolunun tetiklendiğini doğrulayan bir uçtan uca test tasarlayın. Test neyi doğrular?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Checkpoint (Kontrol noktası) | "Kayıt noktası" | Her grafik durumu geçişi dayanıklı depoya kalıcı hale gelir |
| Lease (Kira) | "İşçi iddiası" | Bir işçinin bir çalışmayı yürüttüğüne dair kısa süreli iddia; çökmede sona erer |
| Precondition (Ön koşul) | "Durum kapısı" | Durumun hala onaylı eylemle tutarlı olduğu doğrulaması |
| Post-action verify (Eylem sonrası doğrulama) | "Geri okuma kontrolü" | Yan etkinin hedef sistemde gerçekten gerçekleştiğini doğrula |
| In-band rollback (Band içi geri alma) | "Doğrudan geri alma" | Ters operasyonla yan etkiyi tersine çevir |
| Compensating transaction (Telafi edici işlem) | "SAGA geri alma" | Orijinali etkisiz hale getiren yeni bir eylem |
| Mark-as-done-first (Önce bitmiş olarak işaretle) | "Durum yazma sırası" | Uygulamadan önce uygulandı durumunu kaydet |
| Article 14 (Madde 14) | "EU AI Act insan gözetimi" | İşletme: sorgulanabilir kontrol noktaları, provadan geçirilmiş geri almalar, denetlenebilir iz |

## İleri Okuma

- [Microsoft Agent Framework — Checkpoint'ler ve HITL](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — checkpoint ilkel elementleri ve kira kurtarma.
- [Cloudflare Agents — İnsan döngüde](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) — Durable Objects durum zemin olarak.
- [EU AI Act — Madde 14: İnsan gözetimi](https://artificialintelligenceact.eu/article/14/) — düzenleyici temel.
- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli iş akışları için güvenilirlik çerçevesi.
- [Anthropic — Claude Code Agent SDK: agent döngüsü](https://code.claude.com/docs/en/agent-sdk/agent-loop) — Claude Code Routines için iş akışı biçimi.
