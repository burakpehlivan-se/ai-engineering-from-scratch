---
name: devops-agent
description: Bir küme bilgi grafiğini gezen, kök nedenleri sıralayan ve her iyileştirmeyi Slack üzerinden geçitlendiren bir Kubernetes sorun giderme ajanı inşa et
version: 1.0.0
phase: 19
lesson: 06
tags: [capstone, devops, sre, kubernetes, langgraph, fastmcp, aiops]
---

Bir K8s kümesi ve bir uyarı kaynağı (PagerDuty veya Alertmanager) verildiğinde, beş dakika altında sıralanmış kök-neden hipotezleri üreten ve her iyileştirmeyi bir Slack onay kartıyla geçitlendiren bir ajan inşa et.

İnşa planı:

1. kube-state-metrics'i her 30 saniyede Neo4j veya kuzu'ya al. Pod'lar, Deployment'lar, Service'ler, Node'lar, PVC'ler, HPA'lar artı Prometheus, Loki ve Tempo kaynaklarına telemetri-örtüşüm kenarları grafiğini kur.
2. PagerDuty ve Alertmanager için bir FastAPI webhook alıcısı kur.
3. FastMCP aracılığıyla StreamableHTTP taşıma ile salt-okunur araçları aç: kubectl get/describe, promql, logql, traceql.
4. Üç düğümlü bir LangGraph kök-neden ajanı inşa et: `sample` (15 dakika telemetri çek), `walk` (grafik komşularını dolaş), `hypothesize` (adayları yakınlık × özgüllük × alıntı sayısı ile sırala).
5. İlk-3 sıralanmış hipotezi grafik-yolu görselleştirmesiyle onay düğmeleriyle Slack'e gönder.
6. Yıkıcı araçları (scale, rollback, delete) Slack onayından sonra ajanın yalnızca onay aldığı bir onay belirteci gerektiren ayrı bir FastMCP sunucusunun arkasına koy.
7. Sadece-ekleme (append-only) bir denetim günlüğü tut: değerlendirilen her komut, onaylanıp onaylanmadığı, yürütülüp yürütülmediği, kimin onayladığı.
8. 20 sentetik olay senaryosu inşa et (OOMKill, DNS flap, HPA thrash, PVC dolu, gürültülü komşu, hatalı yan-konteyner, kötü ConfigMap yayılımı, sertifika döndürme, görüntü-çekme geri-çevrimi, prob başarısızlığı ve 10 tane daha). Ajanı RCA doğruluğu ve hipotez-zamanı için puanla.

Değerlendirme rubriği:

| Ağırlık | Kriter | Ölçüm |
|:-:|---|---|
| 25 | Senaryo paketinde RCA doğruluğu | 20 sentetik olayda en az %80 doğru kök neden |
| 20 | Güvenlik | Yıkıcı-eylem koruyucusu, denetim günlüğünde Slack onayı olmadan asla tetiklenmez |
| 20 | Hipotez-zamanı | Uyarıdan Slack brifingine p50 5 dakika altında |
| 20 | Açıklanabilirlik | Her hipotezin grafik yolları ve telemetri alıntıları vardır |
| 15 | Entegrasyon tamlığı | PagerDuty, Slack, ArgoCD, Prometheus uçtan uca çalışır |

Kesin redler:

- Salt-okunur ve yıkıcı araçları karıştıran tek bir MCP sunucusu olan ajanlar.
- Telemetri alıntıları olmadan üretilen herhangi bir RCA. Alıntısız hipotezler reddedilmelidir.
- Yalnızca yürütmeleri kaydeden denetim günlükleri. Değerlendirilen her komutu kaydetmelidir.
- Tohumlarla senaryo paketine karşı ajanı çalıştırmadan yapılan doğruluk iddiaları.

Ret kuralları:

- İnsan çağrıdaki birinden Slack onayı olmadan iyileştirme yapmayı reddet. Hipotez ne kadar açık olursa olsun.
- Salt-okunur MCP üzerinden `kubectl exec`, `kubectl port-forward` veya herhangi bir etkileşimli aracı açmayı reddet. Bunlar fiilen yıkıcıdır.
- Birden çok dağıtımda iyileştirmeleri toplu olarak uygulamayı reddet; dağıtım başına onay kartları kullan.

Çıktı: FastAPI alıcıyı, LangGraph ajanını, salt-okunur ve yıkıcı MCP sunucularını, Slack entegrasyonunu, 20-senaryoluk test paketini, AWS DevOps Agent ile üç paylaşılan olayda yan yana karşılaştırmayı ve bir haftalık gözlem penceresinde ajanın *değerlendirdiği* ancak yürütmediği yakın-kaçırma komutlarını açıklayan bir yazıyı içeren bir depo.
