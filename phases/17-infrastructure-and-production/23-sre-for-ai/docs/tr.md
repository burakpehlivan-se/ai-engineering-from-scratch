# AI için SRE — Çok-Ajanlı Olay Müdahalesi, Runbook'lar, Tahmine Dayalı Tespit

> AI SRE, altyapı verisine (günlükler, runbook'lar, servis topolojisi) RAG (Retrieval-Augmented Generation — getirilmiş içerikle zenginleştirilmiş üretim) ile temellendirilmiş LLM'leri soruşturma, dokümantasyon ve koordinasyon aşamalarını otomatikleştirmek için kullanır. 2026 mimari kalıbı çok-ajanlı (multi-agent) orkestrasyondur — uzman ajanlar (günlükler, metrikler, runbook'lar) bir gözetmen (supervisor) tarafından koordine edilir; AI hipotez ve sorguları önerir, insanlar yargı çağrılarını onaylar. Datadog Bits AI ve Azure SRE Agent bunu yönetilen ürünler olarak sunar. Runbook'lar gelişiyor: NeuBird Hawkeye, hasım değerlendirmesi (adversarial evaluation) kullanır — iki model aynı olayı analiz eder; anlaşma = güven, anlaşmazlık = belirsizlik); operasyonel bellek ekip değişikliklerinde kalıcıdır. Otomatik düzeltme (auto-remediation) temkinli kalır: AI önerir, insanlar onaylar. Tamamen özerk eylem dardır (pod'u yeniden başlat, belirli dağıtımı geri al) sıkı koruyucularla — "kur ve unut" satan herkes abartıyor. Yükselen sınır: olay-öncesi tahmin. MIT araştırması, GPU sıcaklıkları + API hata kalıpları + tarihsel günlükler üzerinde eğitilmiş bir LLM'nin, test setinde olayların %89'unu 10-15 dakika önceden tahmin ettiğini bildiriyor. Projeksiyon: 2026 sonuna kadar kurumsal LLM'lerin %95'inin otomatik yük devretmesi olacak.

**Tür:** Öğren
**Diller:** Python (stdlib, basit çok-ajanlı olay triyajı simülatörü)
**Önkoşullar:** Phase 17 · 13 (Gözlemlenebilirlik), Phase 17 · 24 (Kaos Mühendisliği)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Çok-ajanlı AI SRE mimarisini şematize edin: gözetmen + uzman ajanlar (günlükler, metrikler, runbook'lar) + insan onay geçidi.
- Otomatik düzeltmenin neden dar (pod'u yeniden başlat, dağıtımı geri al) değil geniş (servisi yeniden mimarile) olduğunu açıklayın.
- Hasım değerlendirme kalıbını (NeuBird Hawkeye) sayın: iki model anlaşır = güven; anlaşmaz = yükseltme.
- MIT %89 erken tespit sonucunu ve operasyonel kısıtı alıntılayın: tahminler olmadan hareket geçmek sadece panodur.

## Problem

Nöbetçi mühendis saat 3'te sayfa alıyor: "Ödeme akışında yüksek hata oranı." Datadog, Loki, üç runbook, dağıtım günlüğünü kontrol ediyor. 30 dakika sonra kök nedenin bir KV cache sıçramasından kaynaklanan vLLM OOM olduğunu anlıyor. Pod'u yeniden başlatıyor; hata temizleniyor.

2026'da bu soruşturmanın ilk 20 dakikası otomatikleştirilebilir. Günlükleri servise göre gruplama, son dağıtımlarla ilişkilendirme, runbook'larla eşleştirme — hepsi RAG + araç kullanımı. Gözetilen bir ajan, insan Datadog'u açmadan önce ilk geçiş triyajını yapıp bir hipotez sunabilir.

Tamamen özerk düzeltme farklı bir sorundur. Pod'u yeniden başlat: güvenli. GPU havuzunu ölçekle: politika izin veriyorsa güvenli. Servisi yeniden mimarile: kesinlikle hayır. Disiplin, dar çizgiyi çizmektir.

## Kavram

### Çok-ajanlı mimari

```mermaid
flowchart TB
    O[Olay] --> S[Gözetmen]
    S --> LA[Günlük ajanı]
    S --> MA[Metrik ajanı]
    S --> RA[Runbook ajanı]
    LA --> H[Hipotez + kanıt]
    MA --> H
    RA --> H
    H --> I[İnsan onayı]
    I --> A[Eylem (dar set)]
```

#### Açıklama

Bu diyagram çok-ajanlı (multi-agent) AI SRE akışını gösterir: bir olay gözetmen tarafından alınır, üç uzman ajana (günlükler, metrikler, runbook'lar) dağıtılır, sentezlenen hipotez + kanıt insan onayına sunulur ve onaylanan eylem dar bir eylem kümesiyle sınırlıdır.

Gözetmen olayı alt sorgulara böler. Uzman ajanlar araç erişimine sahiptir (günlük arama, PromQL — Prometheus Sorgu Dili, doküman alma). Gözetmen sentezler, hipotez + kanıtı insana sunar. İnsan onaylar veya yeniden yönlendirir.

### Otomatik düzeltme kapsamı

**Güvenli (dar)**: pod'u yeniden başlat, belirli dağıtımı geri al, havuzu önceden onaylanmış sınırlar içinde ölçekle, önceden onaylanmış özellik flag'ini etkinleştir.

**Güvenli değil (geniş)**: servis topolojisini değiştir, kaynak sınırlarını değiştir, yeni kod dağıt, IAM'i değiştir, veritabanlarını değiştir.

"Kur ve unut" satan herkes abartıyor. Güvenli set, AI SRE olgunlaştıkça büyür, ama sınır gerçektir.

### Hasım değerlendirme (NeuBird Hawkeye)

İki model aynı olayı bağımsız olarak analiz eder. Kök neden üzerinde anlaşırlarsa, güven yüksektir. Anlaşmazlarsa, her iki hipotez görünür şekilde insana yükseltin. Basit kalıp, halüsinasyon kök nedenlerine karşı etkili filtre.

### Operasyonel bellek

Ekip devri geleneksel SRE'nin sessiz ölümüdür — kabile bilgisi gider. AI SRE, runbook'ları ve post-mortem'leri bir vektör veritabanında depolar; ajanlar her yeni olayda alır. Yeni mühendisler katıldığında, AI tam tarihe sahiptir.

### Olay-öncesi tahmin

MIT 2025 araştırması: tarihsel günlükler, GPU sıcaklıkları ve API hata kalıpları üzerinde eğitilmiş LLM, test setinde olayların %89'unu 10-15 dakika önceden, gerçekleşmeden önce tahmin etti.

Gerçeklik kontrolü: tahminler olmadan hareket geçmek panolardır. Operasyonel soru "tahmin ettiğimizde ne yaparız?" Önleyici tahliye? Çağrı cihazı? Otomatik ölçekleme? Cevap politika-özgüdür.

### 2026'da ürünler

- **Datadog Bits AI** — Datadog içinde yönetilen SRE yardımcı pilotu (copilot).
- **Azure SRE Agent** — Azure-native.
- **NeuBird Hawkeye** — hasım değerlendirme + operasyonel bellek.
- **PagerDuty AIOps** — triyaj + tekilleştirme.
- **Incident.io Autopilot** — olay komutanı + koordinasyon.

### Kod olarak runbook'lar

Runbook'lar Confluence sayfalarından yapılandırılmış bölümlere sahip versiyonlanmış markdown'a evriliyor (semptom, hipotez, doğrula, hareket et). Yapılandırılmış runbook'lar daha iyi RAG alımı besler. AI-SRE yayılımına yapılandırılmamış runbook'ları yapılandırılmışa çevirerek başlayın.

### Hatırlamanız gereken sayılar

- MIT erken tespiti: olayların %89'u, 10-15 dakika kurşun süresi.
- Çok-ajanlı triyaj: gözetmen + (günlükler, metrikler, runbook'lar) + insan.
- Güvenli otomatik düzeltme seti: pod'u yeniden başlat, dağıtımı geri al, sınırlar içinde ölçekle.
- Hasım değerlendirme: iki model bağımsız; anlaşma = güven.

## Kullanım

`code/main.py` çok-ajanlı triyajı simüle eder: günlük ajanı hatayı bulur, metrik ajanı CPU sıçramasını bulur, runbook ajanı bilinen sorunla eşleşir. Gözetmen hipotezleri sıralar.

## Yaygınlaştırma

Bu ders `outputs/skill-ai-sre-plan.md` üretir. Mevcut nöbet, olay hacmi, ekip olgunluğu verildiğinde, bir AI SRE yayılımı tasarlar.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. Günlük ve metrik ajanları anlaşmazsa ne olur? Gözetmen nasıl çözer?
2. Servisiniz için üç "güvenli" otomatik düzeltme eylemi tanımlayın. Her birini gerekçelendirin.
3. Yapılandırılmış runbook şablonu yazın: bölümler, gerekli alanlar, doğrulama komutları.
4. Tahmine dayalı tespit 12 dakika kurşunla ateşleniyor. Politikanız nedir — çağrı cihazı, ön-tahliye veya ikisi?
5. 3 kişilik bir ekibin 2026'da AI SRE benimseyip benimsemeyeceğini tartışın. Olgunluk, hacim, riski göz önünde bulundurun.

## Anahtar Terimler

| Terim | İnsanların söylediği | Gerçek anlamı |
|-------|----------------------|---------------|
| AI SRE | "nöbet için ajan" | LLM destekli olay soruşturması + koordinasyon |
| Gözetmen ajanı | "orkestratör" | Olayları alt sorgulara bölen üst-düzey ajan |
| Uzman ajan | "alan ajanı" | Araç erişimli alt ajan (günlükler, metrikler, runbook'lar) |
| Otomatik düzeltme | "AI düzeltir" | Dar önceden onaylanmış eylem; geniş yeniden mimari DEĞİL |
| Operasyonel bellek | "vektör runbook'lar" | RAG için vektör veritabanında post-mortem'ler + runbook'lar |
| Hasım değerlendirme | "iki-model kontrolü" | Bağımsız analizler; anlaşma = güven |
| NeuBird Hawkeye | "hasım olan" | Hasım değerlendirme + bellek kalıbı olan ürün |
| Bits AI | "Datadog'un SRE ajanı" | Datadog yönetilen AI SRE |
| Olay-öncesi tahmin | "erken tespit" | Olay tahmininde 10-15 dakika kurşun süresi |

## Ek Okuma

- [incident.io — AI SRE Tam Kılavuz 2026](https://incident.io/blog/what-is-ai-sre-complete-guide-2026)
- [InfoQ — SRE için İnsan-Merkezli AI](https://www.infoq.com/news/2026/01/opsworker-ai-sre/)
- [DZone — SRE'de AI 2026](https://dzone.com/articles/ai-in-sre-whats-actually-coming-in-2026)
- [Datadog Bits AI](https://www.datadoghq.com/product/bits-ai/)
- [NeuBird Hawkeye](https://www.neubird.ai/)
- [awesome-ai-sre](https://github.com/agamm/awesome-ai-sre)
