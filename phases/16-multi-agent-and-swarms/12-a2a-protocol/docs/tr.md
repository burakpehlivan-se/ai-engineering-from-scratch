# A2A — Agent'tan Agent'a Protokol

> Google, A2A'yı Nisan 2025'te duyurdu; Nisan 2026 itibariyle spesifikasyon https://a2a-protocol.org/latest/specification/ adresinde ve 150+ kuruluş tarafından destekleniyor. A2A, MCP'nin (Ders 13) yatay tamamlayıcısıdır: MCP dikeyken (agent ↔ araçlar), A2A eşler arasıdır (agent ↔ agent). Agent Card'ları (keşif), yapıtları olan görevleri (metin, yapılandırılmış veri, video), opak görev yaşam döngülerini ve auth'u tanımlar. Üretim sistemleri giderek MCP'yi A2A ile eşliyor. Google Cloud, 2025-2026 boyunca Vertex AI Agent Builder'a A2A desteğini ekledi.

**Tür:** Öğren + İnşa Et
**Diller:** Python (stdlib, `http.server`, `json`)
**Ön Koşullar:** Faz 16 · 04 (İlkel Model)
**Süre:** ~75 dakika

## Problem

Agent'ınızın başka bir sistemdeki başka bir agent'ı çağırması gerekiyor. Nasıl? Bir HTTP uç noktası açabilir, özel bir JSON şeması tanımlayabilir ve diğer tarafın onu konuştuğunu umabilirsiniz. Her agent çifti özel bir entegrasyon haline gelir.

A2A, o çağrı için evrensel kablo protokolüdür. Standart keşif, standart görev modeli, standart taşıma, standart yapıtlar. Birinci sınıf vatandaşlar olarak agent'lar için HTTP+REST gibi.

## Kavram

### Dört unsur

**Agent Card.** `/.well-known/agent.json` adresindeki agent'ı tanımlayan bir JSON belgesi: ad, beceriler, uç noktalar, desteklenen modaliteler, auth gereksinimleri. Keşif, kartı okuyarak gerçekleşir.

```
GET https://agent.example.com/.well-known/agent.json
→ {
    "name": "code-review-agent",
    "skills": ["review-python", "review-typescript"],
    "endpoints": {
      "tasks": "https://agent.example.com/tasks"
    },
    "auth": {"type": "bearer"},
    "modalities": ["text", "structured"]
  }
```

**Task.** İş birimi. Bir yaşam döngüsüne sahip eşzamansız, durum bilgisi olan bir nesne: `submitted → working → completed / failed / canceled`. Bir istemci bir görev gönderir, güncellemeleri yoklar veya abone olur.

**Artifact (Yapıt).** Bir görev tarafından üretilen sonuç türü. Metin, yapılandırılmış JSON, görüntü, video, ses. Yapıtlar tiplidir, böylece farklı modaliteler birinci sınıftır.

**Opaque lifecycle (Opak yaşam döngüsü).** A2A, uzak agent'ın görevi *nasıl* çözdüğünü reçete etmez. İstemci durum geçişlerini ve yapıtları görür; uygulama herhangi bir çatıyı kullanmakta özgürdür.

### MCP/A2A bölünmesi

- **MCP** (Ders 13): agent ↔ araç. Agent, bir araç sunucusuna JSON-RPC ile okur/yazar. Varsayılan olarak durumsuz.
- **A2A**: agent ↔ agent. Eş protokolü; her iki taraf kendi akıl yürütmesine sahip birer agent'tır.

Üretim multi-agent sistemleri ikisini de kullanır. Bir A2A eşi kendi tarafında MCP araçlarını çağırır. Bölünme, iki endişeyi temiz tutar.

### Keşif akışı

```
İstemci                    Agent sunucusu
  ├──GET /.well-known/agent.json──>
  <──Agent Card JSON─────────────
  ├──POST /tasks {skill, input}──>
  <──201 task_id, state=submitted
  ├──GET /tasks/{id}──────────────>
  <──state=working, 42% done──────
  ├──GET /tasks/{id}──────────────>
  <──state=completed, artifacts──
```

Veya streaming ile: itme güncellemeleri için `/tasks/{id}/events`'a SSE aboneliği.

### Kimlik doğrulama

A2A üç yaygın kalıbı destekler:

- **Bearer token** — OAuth2 veya opak.
- **mTLS** — karşılıklı TLS; kuruluşlar birbirlerine kimliklerini kanıtlar.
- **İmzalı istekler** — yükün üzerinde HMAC.

Auth Agent Card'da bildirilir; istemciler keşfeder ve uyum sağlar.

### Nisan 2026 itibariyle 150+ kuruluş

Kurumsal benimseme A2A ölçeğini yönlendirdi. Başlık: A2A, kurumsal agent sistemlerinin güven sınırlarını aşma biçimi haline geldi. Google Cloud, Vertex AI Agent Builder A2A desteğini gönderdi; Microsoft Agent Framework onu destekler; çoğu büyük çatı (LangGraph, CrewAI, AutoGen) A2A adaptörleri gönderir.

### A2A nerede kazanır

- **Organizasyonlar arası çağrılar.** A şirketindeki agent, B şirketindeki agent'ı çağırır. A2A olmadan, her çift özel bir sözleşmedir.
- **Heterojen çatılar.** LangGraph agent, CrewAI agent'ı çağırır, özel Python agent'ı çağırır. A2A normalleştirir.
- **Tipli yapıtlar.** Video sonucu, yapılandırılmış JSON, ses — hepsi birinci sınıf.
- **Uzun süren görevler.** Opak yaşam döngüsü + yoklama, saatlerce süren görevleri basit hale getirir.

### A2A nerede zorlanır

- **Gecikme hassas mikro çağrılar.** A2A'nın yaşam döngüsü eşzamansızdır. Milisaniyenin altında agent-arası uymaz; doğrudan RPC kullanın.
- **Sıkı bağlı süreç içi agent'lar.** Her iki agent de aynı Python sürecinde çalışıyorsa, A2A'nın HTTP gidiş-dönüşü gereksizdir.
- **Küçük takımlar.** Spesifikasyon ek yükü gerçektir; yalnızca dahili agent'lar biçimselliğe ihtiyaç duymayabilir.

### A2A ve ACP, ANP, NLIP

2024-2026'da birkaç ilgili spesifikasyon ortaya çıktı:

- **ACP** (IBM/Linux Foundation) — A2A'nın öncüsü, daha dar kapsam.
- **ANP** (Agent Network Protocol) — eş-keşif-ağır, merkezsiz-öncelikli.
- **NLIP** (Ecma Natural Language Interaction Protocol, Aralık 2025'te standartlaştırıldı) — doğal dil içerik türü.

A2A, Nisan 2026 itibariyle en çok benimsenen eş protokolüdür. Karşılaştırma için arXiv:2505.02279'a (Liu ve diğerleri, "A Survey of Agent Interoperability Protocols") bakın.

## İnşa Et

`code/main.py`, `http.server` ve JSON kullanarak A2A-minimal bir sunucu ve istemci uygular. Sunucu:

- `/.well-known/agent.json`'u açar,
- `POST /tasks`'ı kabul eder,
- görev durumunu yönetir,
- `GET /tasks/{id}` üzerinde yapıtları döner.

İstemci:

- Agent Card'ı getirir,
- bir görev gönderir,
- tamamlanana kadar yoklar,
- yapıtı okur.

Çalıştırın:

```
python3 code/main.py
```

Betik, sunucuyu bir arka plan iş parçacığında başlatır, sonra istemciyi ona karşı çalıştırır. Tam akışı görürsünüz: keşif, gönder, yoklama, yapıt.

## Kullan

`outputs/skill-a2a-integrator.md` bir A2A entegrasyonu tasarlar: Agent Card içerikleri, görev şemaları, auth seçimi, streaming veya yoklama.

## Dağıt

Kontrol listesi:

- **Spesifikasyon sürümünü sabitleyin.** A2A hâlâ gelişiyor; Agent Card protokol sürümünü bildirmelidir.
- **Idempotent (tekrarlanabilir) görev oluşturma.** Ağ yeniden denemeleri gibi yinelenen gönderimler tek bir görev üretmelidir.
- **Yapıt şemaları.** Agent'ın ne döndüreceğini bildirin; tüketiciler doğrulamalıdır.
- **Hız limitleri + auth.** A2A herkese açıktır; standart web güvenliğini uygulayın.
- **Başarısız görevler için dead-letter (ölü mektup).** Tekrarlayan başarısızlık türleri için zaman içindeki kalıpları inceleyin.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. İstemcinin sunucuyu keşfettiğini ve doğru yapıtı aldığını doğrulayın.
2. Sunucuya ikinci bir beceri ekleyin (örn. "özetle"). Agent Card'ı güncelleyin. Görev türüne göre beceriyi seçen bir istemci yazın.
3. Bir SSE streaming uç noktası uygulayın: `/tasks/{id}/events` durum değişikliklerini yayar. İstemcinin farklı yapması gereken nedir?
4. A2A spesifikasyonunu (https://a2a-protocol.org/latest/specification/) okuyun. Spesifikasyonun zorunlu kıldığı, bu demoda uygulanmayan üç şeyi belirleyin.
5. A2A'yı (Agent Card keşfi) MCP ile (sunucu tarafı yetenek listeleme `listTools` aracılığıyla) karşılaştırın. Kendini tanımlayan agent'lar ile yetenek-yoklayan arasındaki ödünleşim nedir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| A2A | "Agent'tan agent'a" | Sistemler arasında agent'ların diğer agent'ları çağırması için eş protokolü. Google 2025. |
| Agent Card | "Agent'ın kartviziti" | Becerileri, uç noktaları, auth'u tanımlayan `/.well-known/agent.json` adresindeki JSON. |
| Task | "İş birimi" | Yaşam döngüsüne sahip eşzamansız durum bilgisi nesnesi; tamamlanmada yapıtlar üretilir. |
| Artifact (Yapıt) | "Sonuç" | Tipli çıktı: metin, yapılandırılmış JSON, görüntü, video, ses. Birinci sınıf medya. |
| Opaque lifecycle (Opak yaşam döngüsü) | "Nasıl çözüldüğü agent'ın işi" | İstemci durum geçişlerini görür; sunucu çatıyı/araçları seçmekte özgürdür. |
| Discovery (Keşif) | "Agent'ı bulma" | `GET /.well-known/agent.json` kartı döner. |
| MCP ve A2A | "Araçlar ve eşler" | MCP: dikey agent ↔ araç. A2A: yatay agent ↔ agent. |
| ACP / ANP / NLIP | "Kardeş protokoller" | İlgili spesifikasyonlar; A2A en çok benimsenen 2026. |

## İleri Okuma

- [A2A spesifikasyonu](https://a2a-protocol.org/latest/specification/) — kanonik spesifikasyon
- [Google Developers Blog — A2A duyurusu](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/) — Nisan 2025 lansman yazısı
- [A2A GitHub deposu](https://github.com/a2aproject/A2A) — referans uygulamalar ve SDK'lar
- [Liu ve diğerleri — A Survey of Agent Interoperability Protocols](https://arxiv.org/html/2505.02279v1) — MCP, ACP, A2A, ANP karşılaştırması
