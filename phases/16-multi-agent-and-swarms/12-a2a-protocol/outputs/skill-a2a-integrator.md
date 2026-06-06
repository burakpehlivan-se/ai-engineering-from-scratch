---
name: a2a-integrator
description: İki agent arasında bir A2A entegrasyonu tasarlayın — Agent Card, görev şemaları, kimlik doğrulama, akış veya yoklama.
version: 1.0.0
phase: 16
lesson: 12
tags: [multi-agent, a2a, protocol, interoperability, google]
---

Birlikte çalışması gereken iki agent sistemi verildiğinde, A2A entegrasyon planını üretin: Agent Card içerikleri, görev şemaları, kimlik doğrulama, taşıma modu.

Üretin:

1. **Agent Card.** Ad, versiyon, beceriler, endpoint'ler, desteklenen modaliteler (metin, yapılandırılmış, görüntü, ses, video), protocol_version, kimlik doğrulama beyanı.
2. **Beceri başına görev şemaları.** Girdi JSON şeması + artefakt JSON şeması. Açık olun — istemciler doğrulayacak.
3. **Kimlik doğrulama seçimi.** Bearer token (OAuth2 veya opak), mTLS veya imzalı istekler. Tehdit modeli göz önüne alınarak gerekçelendirin (genel internet, VPC, karışık).
4. **Taşıma modu.** Yoklama vs SSE akışı vs webhook callback'leri. Uzun-süren veya ilerleme-ağır görevler için akış; kısa görevler için yoklama.
5. **Hız sınırları.** İstemci başına ve görev başına sınırlar. Kötüye kullanımdan korunma.
6. **Idempotency (Tekrar-koruma).** Yinelenen `POST /tasks` istekleri için strateji (istemci tarafı görev-anahtarı, sunucu tarafı tekilleştirme).
7. **Başarısızlık yönetimi.** `failed`'ın ötesinde görev durumları (yeniden-denebilir mi yoksa ölümcül mü), dead-letter (ölü-mektup) politikası, hata artefaktı şeması.
8. **MCP vs A2A bölünmesi.** Uzak agent dahili olarak MCP kullanıyorsa, hangi araçların açığa çıkarıldığını ve hangilerinin dahili tutulduğunu not edin.

Keskin redler:

- Beyan edilmiş protokol versiyonu olmayan Agent Card'lar.
- Kullanım durumu yapıyı haklı kılarken serbest-biçimli metin olan görev şemaları.
- Genel-internet deployment'larında auth=yok.

Ret kuralları:

- Her iki agent aynı proseste çalışıyorsa, A2A'yı reddedin ve doğrudan Python/JS çağrıları önerin. A2A, sistem-sınır-ötesi sınırlar içindir.
- Gecikme gereksinimleri 100ms altı gidiş-dönüş ise, A2A'yı reddedin ve paylaşılan şemayla doğrudan RPC önerin.
- Uzak agent bir Agent Card beyan etmiyorsa, entegrasyonu reddedin ve önce bir tane yayınlamasını önerin.

Çıktı: Tek sayfalık entegrasyon özeti. Mühendisliğin `/.well-known/agent.json`'a yapıştırması için satır içinde yapıştırılmış Agent Card JSON'ıyla kapatın.
