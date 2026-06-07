# Capstone 06 — Kubernetes için DevOps Sorun Giderme Ajanı

> AWS'nin DevOps Agent'ı GA oldu, Resolve AI K8s oyun kitaplarını yayınladı, NeuBird anlamsal izlemeyi gösterdi ve Metoro yapay zekâ SRE'sini hizmet-başına SLO'lara bağladı. 2026'nın üretim şekli yerleşti: bir uyarı webhook'ı tetiklenir, bir ajan telemetriyi okur, K8s nesneleri grafiğinde yürür, kök-neden hipotezlerini sıralar ve onay düğmeleriyle bir Slack özeti gönderir. Varsayılan olarak salt-okunur. Her iyileştirme (remediation) bir insan tarafından geçitlenir. Bu capstone o ajandır; 20 sentetik olay üzerinde değerlendirilir ve üç ortak vakada AWS'nin Agent'ına karşı kıyaslanır.

**Type:** Capstone
**Languages:** Python (agent), TypeScript (Slack entegrasyonu)
**Prerequisites:** Phase 11 (LLM engineering), Phase 13 (tools and MCP), Phase 14 (agents), Phase 15 (autonomous), Phase 17 (infrastructure), Phase 18 (safety)
**Phases exercised:** P11 · P13 · P14 · P15 · P17 · P18
**Time:** 30 saat

## Problem

2025-2026'nın SRE anlatısı şu oldu: "Yapay zekâ ajanları olayları triyaj yapar, insanlar iyileştirmeleri onaylar." AWS DevOps Agent, Resolve AI, NeuBird, Metoro, PagerDuty AIOps hepsi bu şekli üretimde yayınladı. Ajan Prometheus metriklerini, Loki günlüklerini, Tempo izlerini, kube-state-metrics'i ve K8s nesnelerinin bir bilgi grafını okur. Beş dakikanın altında, telemetri alıntıları ile sıralanmış bir kök-neden hipotezi üretir. Açık insan onayı olmadan Slack üzerinden yıkıcı komutları asla yürütmez.

Zor işin çoğu akıl yürütme değil, kapsam ve güvenliktir. Ajanın varsayılan olarak salt-okunur bir RBAC yüzeyine, sertleştirilmiş bir MCP tool sunucusuna ve değerlendirilen vs yürütülen her komutun denetim günlüğüne ihtiyacı vardır. Yetkinliğinin dışında olduğunda bilmesi ve yükseltmesi gerekir. Ve OOM-kill kaskadlarının $5k'lik bir ajan faturası üretmediği kadar ucuza çalışmalıdır.

## Concept

Ajan bir bilgi grafı üzerinde çalışır. Düğümler K8s nesneleridir (Pod'lar, Deployment'lar, Service'ler, Node'lar, HPA'lar, PVC'ler) artı telemetri kaynakları (Prometheus serileri, Loki akışları, Tempo izleri). Kenarlar sahipliği (Pod -> ReplicaSet -> Deployment), zamanlamayı (Pod -> Node) ve gözlemi (Pod -> Prometheus serisi) kodlar. Graf, bir kube-state-metrics senkronizasyonu ile taze tutulur ve her uyarıda yeniden örneklenir.

Bir uyarı tetiklendiğinde, ajan etkilenen nesneden kök-neden çıkarır. Kenarlarda yürür, ilgili telemetri dilimlerini (son 15 dakika) çeker ve bir hipotez taslağı oluşturur. Hipotez, kanıtla sıralanır: kaç telemetri alıntısı destekliyor, ne kadar yeni, ne kadar spesifik. İlk 3 hipotez, graf-yol görselleştirmeleri ve iyileştirme eylemleri için onay düğmeleriyle Slack'e gider.

İyileştirme geçitlenir. İzin verilen varsayılan eylemler salt-okunurdur. Yıkıcı eylemler (küçültme, geri sarma, Pod silme) Slack onayı gerektirir; ArgoCD geri sarma kancaları ajanın hiç tutmadığı bir kimlik doğrulama belirteci gerektirir. Denetim günlüğü, ajanın *düşündüğü* her komutu — yalnızca yürütülenleri değil — kaydeder, böylece inceleme süreci yakın-kaçırmaları yakalar.

## Architecture

```
PagerDuty / Alertmanager webhook
 |
 v
 FastAPI receiver
 |
 v
 LangGraph root-cause agent
 |
 +---- read-only MCP tools ----+
 | |
 v v
 K8s knowledge graph telemetry slices
 (Neo4j / kuzu) Prometheus, Loki, Tempo
 ownership + scheduling last 15m, scoped
 |
 v
 hypothesis ranking (evidence weight)
 |
 v
 Slack brief + approval buttons
 |
 v (approved)
 ArgoCD rollback hook / PagerDuty escalate
 |
 v
 audit log: considered vs executed, every command
```

#### Açıklama

Bu mimari bir PagerDuty uyarısından Slack onayına kadar tam veri akışını gösterir. Uyarı, PagerDuty veya Alertmanager'dan gelen bir webhook'tur. FastAPI alıcı olayı ayrıştırır ve LangGraph kök-neden ajanını başlatır. Ajan iki paralel kanaldan veri toplar: K8s bilgi grafı (Neo4j veya kuzu'da) ve telemetri dilimleri (Prometheus, Loki, Tempo'dan son 15 dakika). Hipotezler kanıt ağırlığına göre sıralanır, ilk 3'ü bir graf-yol görselleştirmesi ve onay düğmeleriyle Slack'e gönderilir. Onay geldiğinde ArgoCD geri sarma veya PagerDuty yükseltme tetiklenir. Tüm süreç, ajanın düşündüğü ve yürüttüğü her komutu kaydeden bir denetim günlüğü tarafından izlenir.

## Stack

- Gözlemlenebilirlik kaynakları: Prometheus, Loki, Tempo, kube-state-metrics
- Bilgi grafı: K8s nesneleri + telemetri kenarları için Neo4j (yönetilen) veya kuzu (gömülü)
- Ajan: Tool başına izin-listesi ile LangGraph, varsayılan olarak salt-okunur
- Tool taşıma: StreamableHTTP üzerinden FastMCP; onay kapısının arkasındaki yıkıcı tool'lar için ayrı sunucu
- Modeller: Kök-neden akıl yürütmesi için Claude Sonnet 4.7, günlük özetleme için Gemini 2.5 Flash
- İyileştirme: ArgoCD geri sarma webhook'u, PagerDuty yükseltme, Slack onay kartı
- Denetim: Salt-ekleme yapılandırılmış günlük (düşünülen, yürütülen, onaylanan, sonuç)
- Dağıtım: Kendi dar RBAC rolüne sahip K8s deployment; ayrı namespace

## Build It

1. **Graf hazmetme.** kube-state-metrics'i her 30 saniyede Neo4j/kuzu'ya senkronize edin. Düğümler: Pod, Deployment, Node, Service, PVC, HPA. Kenarlar: OWNED_BY, SCHEDULED_ON, EXPOSES, MOUNTS, SCALES. Telemetri yerleşim kenarları: OBSERVED_BY (bir Pod bir Prometheus serisi tarafından gözlemlenir).

2. **Uyarı alıcısı.** PagerDuty veya Alertmanager webhook'larını kabul eden FastAPI uç noktası. Etkilenen nesneyi (nesneleri) ve SLO ihlalini çıkarın.

3. **Salt-okunur tool yüzeyi.** kubectl, Prometheus sorgusu, Loki logql, Tempo traceql'yi FastMCP üzerinden sarın. Her tool'un dar bir RBAC fiili vardır ("get", "list", "describe"). Varsayılan sunucuda "delete", "exec", "scale" yoktur.

4. **Kök-neden ajanı.** Üç düğümlü LangGraph: `sample` son-15-dakika telemetri dilimini çeker, `walk` grafı komşu nesneler için sorgular, `hypothesize` telemetri alıntıları ile sıralanmış kök-neden adayları taslağını oluşturur.

5. **Kanıt puanlaması.** Her hipotez bir skora sahiptir = yenilik * özgüllük * graf-yol uzunluğu tersi * alıntı sayısı. İlk 3'ü döndürün.

6. **Slack özeti.** Hipotez, graf-yol görselleştirmesi (sunucu tarafında işlenmiş bir alt-graf görüntüsü) ve en fazla bir iyileştirme eylemi için onay düğmeleriyle bir ek gönderin.

7. **İyileştirme kapısı.** Yıkıcı tool'lar (küçültme, geri sarma, silme) onay belirtecinin arkasındaki ikinci bir MCP sunucusunda yaşar. Ajan bunları yalnızca Slack kartı bir insan tarafından onaylandıktan sonra çağırabilir.

8. **Denetim günlüğü.** Salt-ekleme JSONL: her aday komut için, düşünülüp düşünülmediğini, yürütülüp yürütülmediğini, kimin onayladığını günlüğe kaydedin. Günlük olarak S3'e gönderin.

9. **Sentetik olay paketi.** 20 senaryo inşa edin: OOMKill kaskadı, DNS flap, HPA thrash, PVC dolma, gürültülü komşu, hatalı sidecar, kötü ConfigMap dağıtımı, sertifika rotasyonu, görüntü-çekme geri-izlemesi vb. Ajanı kök-neden doğruluğu ve hipotez süresi üzerinde puanlayın.

## Use It

```
webhook: alert.pagerduty.com -> checkout-api SLO breach, error rate 14%
[graph] affected: Deployment checkout-api (3 Pods, Node ip-10-2-3-4)
[walk] neighbors: ReplicaSet checkout-api-abc, Service checkout-api,
 recent rollout 14m ago
[sample] prometheus error_rate 14%, up-trend; loki 500s on /api/v2/pay
[hypo] #1 bad rollout: latest image checkout-api:v2.41 fails /healthz
 citations: deploy.yaml (rev 42), prometheus errorRate, loki 500 stack
[slack] [ROLL BACK to v2.40] [ESCALATE] [IGNORE]
 (approval required; agent does not roll back unilaterally)
```

#### Açıklama

Bu zaman çizelgesi tipik bir SRE olay müdahalesini gösterir. PagerDuty, checkout-api için %14 hata oranı SLO ihlali bildirir. Ajan bilgi grafından Deployment'ı, 3 Pod'unu ve Node'u bulur, komşu ReplicaSet ve Service'i, 14 dakika önceki dağıtımı tespit eder. Prometheus yükselişi ve Loki 500'leri örnekler. Birinci hipotez "kötü dağıtım: checkout-api:v2.41 görüntüsü /healthz'yi başarısız kılıyor" olur ve üç alıntıyla desteklenir. Slack kartı üç düğmeyle gelir: geri sarma, yükseltme veya yok sayma. Ajan hiçbirini tek taraflı yapmaz.

## Ship It

`outputs/skill-devops-agent.md` teslim edilen şeydir. Bir K8s kümesi ve uyarı kaynağı verildiğinde, ajan sıralanmış kök-neden hipotezleri ve Slack geçitli bir iyileştirme akışı üretir.

| Ağırlık | Ölçüt | Nasıl ölçülür |
|:-:|---|---|
| 25 | Senaryo paketi üzerinde RCA doğruluğu | 20 sentetik olayda ≥ %80 doğru kök neden |
| 20 | Güvenlik | Yıkıcı-eylem koruması denetim günlüğünde Slack onayı olmadan asla tetiklenmez |
| 20 | Hipotez süresi | Uyarıdan Slack özetine p50 5 dakika altında |
| 20 | Açıklanabilirlik | Her hipotez graf yollarına ve telemetri alıntılarına sahiptir |
| 15 | Entegrasyon tamlığı | PagerDuty, Slack, ArgoCD, Prometheus uçtan uca çalışıyor |
| **100** | | |

## Exercises

1. Ajanınızı AWS'nin DevOps Agent'ının demo yapıldığı aynı üç olay üzerinde çalıştırın. Yan yana karşılaştırmayı yayınlayın. Ajanın nerede ayrıştığını raporlayın.

2. Ajanın onay olmadan yıkıcı olacak *düşündüğü* her komutu işaretleyen bir "yakın-kaçırma" denetimi ekleyin. Bir hafta boyunca yakın-kaçırma oranını ölçün.

3. Hipotez modelini Claude Sonnet 4.7'den self-hosted Llama 3.3 70B'ye değiştirin. RCA doğruluğu farkını ve olay başına doları ölçün.

4. Nedensel bir süzgeç inşa edin: ilişkili telemetri artışlarını gerçek bir kök nedenden ayırt edin. 20-senaryo etiketleri üzerinde küçük bir sınıflandırıcı eğitin.

5. Geri sarma kuru-çalıştırması ekleyin: aynı manifest ile bir hazırlık kümesine ArgoCD geri sarma. Slack onay düğmesinden önce canlı kümede geri sarma planını doğrulayın.

## Key Terms

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|------|----------------------|----------------------------|
| K8s bilgi grafı | "Küme grafı" | Düğümler = K8s nesneleri + telemetri serileri; kenarlar = sahiplik, zamanlama, gözlem |
| Varsayılan olarak salt-okunur | "Kapsamlı RBAC" | Ajanın hizmet hesabı yalnızca get/list/describe fiillerine sahiptir; yıkıcı fiiller onayın arkasındaki ayrı bir sunucuda yaşar |
| Denetim günlüğü | "Düşünülen vs yürütülen" | Her aday komutun, çalışıp çalışmadığının, kimin onayladığının salt-ekleme kaydı |
| Hipotez sıralaması | "Kanıt skoru" | Yenilik × özgüllük × graf-yol uzunluğu tersi × alıntı sayısı |
| Slack onay kartı | "HITL kapısı" | İyileştirme düğmeleriyle etkileşimli Slack mesajı; ajan bir insan tıklayana kadar ilerleyemez |
| Telemetri alıntısı | "Kanıt işaretçisi" | Bir iddiayı destekleyen Prometheus sorgusu, Loki seçicisi veya Tempo iz URL'si |
| MTTR | "Çözüm süresi" | Uyarı tetiklenmesinden SLO kurtarmaya kadar geçen duvar-saati |

## Further Reading

- [AWS DevOps Agent GA](https://aws.amazon.com/blogs/aws/aws-devops-agent-helps-you-accelerate-incident-response-and-improve-system-reliability-preview/) — kanonik 2026 referansı
- [Resolve AI K8s troubleshooting](https://resolve.ai/blog/kubernetes-troubleshooting-in-resolve-ai) — rakip referansı
- [NeuBird semantic monitoring](https://www.neubird.ai) — anlamsal-graf yaklaşımı
- [Metoro AI SRE](https://metoro.io) — SLO-öncelikli üretim çerçevesi
- [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics) — küme-durum kaynağı
- [LangGraph](https://langchain-ai.github.io/langgraph/) — referans ajan orkestratörü
- [FastMCP](https://github.com/jlowin/fastmcp) — Python MCP sunucu çatısı
- [ArgoCD rollback](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd_app_rollback/) — geçitlenen iyileştirme hedefi
