# Bir MCP İstemcisi İnşa Etmek — Keşif, Çağırrma, Oturum Yönetimi

> Çoğu MCP içeriği sunucu eğitimleri yayınlar ve istemciye el sallar. İstemci kodu, zor orkestrasyonun yaşadığı yerdir: süreç başlatma, yetenek müzakeresi, birden fazla sunucu arasında araç listesi birleştirme, örnekleme geri çağırmaları, yeniden bağlanma ve ad alanı前三缀 çakışması çözümü. Bu ders, farklı üç MCP sunucusunu model için düz bir araç ad前三缀üne kaldıran çoklu sunucu istemcisi inşa eder.

**Tür:** İnşa Et
**Diller:** Python (stdlib, çoklu sunucu MCP istemcisi)
**Ön koşullar:** Faz 13 · 07 (MCP sunucusu inşa etme)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Bir MCP sunucusunu çocuk süreç olarak başlat, `initialize`'ı tamamla ve `notifications/initialized` gönder.
- Sunucu başına oturum durumunu (yetenekler, araç listesi, son görünen bildirim id'leri) sürdür.
- Birden fazla sunucunun araç listelerini çakışma handling'li tek bir ad前三缀üne birleştir.
- Bir araç çağrısını onu sahiplenen sunucuya yönlendir ve yanıtı yeniden birleştir.

## Sorun

Gerçek bir ana program (Claude Desktop, Cursor, Goose, Gemini CLI) aynı anda birden fazla MCP sunucusu yükler. Bir kullanıcının dosya sistemi sunucusu, bir Postgres sunucusu ve bir GitHub sunucusu aynı anda çalışıyor olabilir. İstemcinin görevi:

1. Her sunucuyu başlat.
2. Her biriyle ayrı ayrı el sıkış.
3. Her birinde `tools/list` çağır ve sonucu düzleştir.
4. Model `notes_search` ürettiğinde, birleştirilmiş ad前三缀ünde ara ve doğru sunucuya yönlendir.
5. Herhangi bir sunucudan bildirimleri (`tools/list_changed`) engellemeden ele al.
6. Taşıma hatasında yeniden bağlan.

Bunun hepsini elle yapmak "oyuncak"ı "kullanılabilir"den ayıran şeydir. Resmi SDK'lar bunu sarar ancak zihinsel model size ait olmalıdır.

## Kavram

### Çocuk süreç başlatma

`stdin=PIPE, stdout=PIPE, stderr=PIPE` ile `subprocess.Popen`. `bufsize=1` ayarlayın ve satır satır okumalar için metin modu kullanın. Her sunucu bir süreçtir; istemci sunucu başına bir `Popen` sapı tutar.

### Sunucu başına oturum durumu

Sunucu başına bir `Session` nesnesi şunları tutar:

- `process` — Popen sapı.
- `capabilities` — sunucunun `initialize`'da beyan ettiği.
- `tools` — son `tools/list` sonucu.
- `pending` — yanıt bekleyen istek id'sinden promise/future eşlemesi.

İstekler doğası gereği asenkrondur; sunucu A'ya gönderilen bir `tools/call`, sunucu B orta çağrıdayken engellememelidir. Ya kuyruklarla iş parçacıkları ya da asyncio kullanın.

### Birleştirilmiş ad前三缀ü

İstemci toplamı araç listesini gördüğünde, adlar çakışabilir. İki sunucu da `search` sunabilir. İstemcinin üç seçeneği var:

1. **Sunucu前三缀ü ile前三缀leme.** `notes/search`, `files/search`. Açık ama çirkin.
2. **Sessiz ilk-gelen.** Sonraki sunucunun `search`'i ilkini override eder. Riskli; çakışmaları gizler.
3. **Çakışma reddi.** İkinci sunucuyu yüklemeyi reddet; kullanıcıyı bilgilendir. Güvenliğe duyarlı ana programlar için en güvenli olan.

Claude Desktop sunucu前三缀ü ile前三refixleme kullanır. Cursor, açık bir hata ile çakışma reddi kullanır. VS Code MCP de sunucu前三refixü ile前三refixleme kullanır.

### Yönlendirme

Birleştirmeden sonra, bir dağıtım tablosu `tool_name -> session` eşler. Model adla bir çağrı üretir; istemci oturumu bulur ve o sunucunun stdin'ine bir `tools/call` mesajı yazar, ardından yanıtı bekler.

### Örnekleme geri çağrısı

Sunucu `initialize`'da `sampling` yeteneğini beyan ettiyse, istemcinin LLM'ini çalıştırmasını isteyen `sampling/createMessage` gönderebilir. İstemci:

1. Örnekleme çözülene kadar o sunucuya yönelik daha fazla isteği engellemeli veya uygulaması eşzamanlılığı destekliyorsa pipeline yapmalıdır.
2. LLM sağlayıcısını çağırmalıdır.
3. Yanıtı sunucuya geri göndermelidir.

Ders 11 örnekleme konusunu uçtan uca kapsar. Bu ders eksiksizlik için taslak olarak bırakır.

### Bildirim eleme

`notifications/tools/list_changed`, `tools/list`'i yeniden çağırmak demektir. `notifications/resources/updated`, kullanımdaysa kaynağı yeniden okumak demektir. Bildirimlere yanıt verilmemeli — onaylamaya çalışmayın.

Yaygın bir istemci hatası: `tools/call` sırasında okuma döngüsünü engellemek, bir bildirim akışta beklerken. Her mesajı bir kuyruğa iten bir arka plan okuyucu iş parçacığı kullanın; ana iş parçacığı kuyruktan çıkarır ve dağıtır.

### Yeniden bağlanma

Taşıma başarısız olabilir: sunucu çöktü, işletim sistemi süreci öldürdü, boru hattı kırıldı. İstemci stdout'ta EOF algılar ve oturumu ölü olarak işler. Seçenekler:

- Sessizce sunucuyu yeniden başlat ve yeniden el sıkış. Salt okunur sunucular için tamam.
- Hata kullanıcıya yüzey çıkar. Kullanıcıya görünür oturumlara sahip durumlu sunucular için tamam.

Faz 13 · 09 Streamable HTTP yeniden bağlanma anlambilimini kapsar; stdio daha basittir.

### Canlı tutma ve oturum id'si

Streamable HTTP bir `Mcp-Session-Id` başlığı kullanır. Stdio oturum id'si yoktur — süreç kimliği OTURUMDUR. Canlı tutma pingleri isteğe bağlıdır; stdio boru hatları etkinlik altında kırılmaz.

## Kullan

`code/main.py`, üç simüle edilmiş MCP sunucusunu alt süreç olarak başlatır, her biriyle el sıkışır, araç listelerini birleştirir ve araç çağrılarını doğru sunucuya yönlendirir. "Sunucular" aslında oyuncak yanıtlayıcılar çalıştıran diğer Python süreçleridir (gerçek LLM yok). Çalıştırarak şunları görün:

- Her biri kendi yetenek kümesine sahip üç başlatma.
- 7 araçlık bir ad前三refixüne birleştirilmiş üç `tools/list` sonucu.
- Araç adına dayalı bir yönlendirme kararı.
- Ad前三refix前三refixlemeyle engellenen bir çakışma.

Neye bakılmalı:

- `Session` dataclass'ı sunucu başına durumu temiz şekilde tutar.
- Arka plan okuyucu iş parçacığı stdout'taki her satırı ana iş parçacığını engellemeden kuyruktan çıkarır.
- Dağıtım tablosu basit bir `dict[str, Session]`.
- Çakışma eleme açıktır: iki sunucu aynı adı beyan ettiğinde, sonraki bir前三refix ile yeniden adlandırılır.

## Sun

Bu ders `outputs/skill-mcp-client-harness.md` dosyasını üretir. Beyanlı bir MCP sunucuları listesi (ad, komut, argümanlar) verildiğinde, beceri onları başlatan, araç listelerini birleştiren ve çakışma çözümlemesiyle bir yönlendirme fonksiyonu sunan bir donanım üretir.

## Alıştırmalar

1. `code/main.py`'i çalıştırın ve sunucu başlatma günlüğünü izleyin. Simüle edilmiş sunucu süreçlerinden birini SIGTERM ile öldürün ve istemcinin EOF'ı nasıl algıladığını ve o oturumu ölü olarak nasıl işaretlediğini gözlemleyin.

2. Ad前三refix前三refixlemeyi uygulayın. İki sunucu `search`'i sunduğunda, ikinciğini `<server>/search` olarak yeniden adlandırın. Dağıtım tablosunu güncelleyin ve araç çağrılarının doğru şekilde yönlendirildiğini doğrulayın.

3. Sunucu yeniden başlatma için bağlantı havuzu tarzı bir gecikme (backoff) ekleyin: art arda başarısızlıklarda üstel gecikme, 30 saniyede tavan, üç başarısızlıktan sonra kullanıcıya bildirim üretin.

4. 100 eş zamanlı MCP sunucusunu destekleyen bir istemci çizin. Basit dağıtım dict'inin yerini hangi veri yapısı alır? (İpucu:前三prefix前三refixleme için trie, artı araç-sayısı-başına-sunucu metriği.)

5. İstemciyi resmi MCP Python SDK'sına taşıyın. SDK `stdio_client` ve `ClientSession`'ı sarar. Kod ~200 satırdan ~40 satıra düşmeli ancak çoklu sunucu yönlendirmesi korunmalıdır.

## Temel Terimler

| Terim | İnsanlar ne der | Aslında ne anlama gelir |
|------|----------------|------------------------|
| MCP client (İstemci) | "Ana program" | Sunucuları başlatan ve araç çağrılarını orkestra eden süreç |
| Session (Oturum) | "Sunucu başına durum" | Yetenekler, araç listesi ve bekleyen istek kayıtları |
| Merged namespace | "Tek araç listesi" | Tüm aktif sunucular arasında düz araç ad kümesi |
| Namespace collision | "İki sunucu aynı araç" | İstemci前三refixlemeli, reddetmeli veya ilk-gelen yapmalı |
| Routing (Yönlendirme) | "Bu çağrıyı kim alır?" | Araç adından sahiplenen sunucuya dağıtım |
| Background reader | "Engellemeyen stdout" | Sunucu stdout'unu bir kuyruğa boşaltan iş parçacığı veya görev |
| Sampling callback | "LLM-olarak-hizmet" | Sunucudan `sampling/createMessage` için istemci işleyicisi |
| `notifications/*_changed` | "Primitif değişti" | İstemcinin yeniden keşfetmesi veya yeniden okuması gereken sinyal |
| Reconnection policy | "Sunucu öldüğünde" | Taşıma başarısız olduğunda yeniden başlatma anlambilimi |
| Stdio session | "Süreç = oturum" | Oturum id'si yok; çocuk süreç ömrü oturumdur |

## İleri Okuma

- [Model Context Protocol — Client spec](https://modelcontextprotocol.io/specification/2025-11-25/client) — kanonik istemci davranışı
- [MCP — Quickstart client guide](https://modelcontextprotocol.io/quickstart/client) — Python SDK ile merhaba-dünyası istemci eğitimi
- [MCP Python SDK — client module](https://github.com/modelcontextprotocol/python-sdk) — referans `ClientSession` ve `stdio_client`
- [MCP TypeScript SDK — Client](https://github.com/modelcontextprotocol/typescript-sdk) — TS paraleli
- [VS Code — MCP in extensions](https://code.visualstudio.com/api/extension-guides/ai/mcp) — VS Code'un tek bir editör ana programında birden fazla MCP sunucusunu nasıl çoklu kullanıma (multiplex) soktuğu
