# Sunucusuz LLM'ler için Soğuk Başlatma Azaltma

> 20 GB'lık bir model imgesi, soğuktan sunmaya geçmek için 5-10 dakika (7B) ile 20+ dakika (70B) arasında sürer. Gerçek bir sunucusuz dünyada bu bir ısınma değil — bir kesintidir. Azaltmalar beş katmanda çalışır: önceden tohumlanmış düğüm imgeleri (AWS'de Bottlerocket, çift-birimli mimari), model akışı (NVIDIA Run:ai Model Streamer, vLLM'de yerel), GPU bellek anlık görüntüleri (Modal kontrol noktaları, 10x'e kadar daha hızlı yeniden başlatma), sıcak havuzlar (`min_workers=1`), katmanlı yükleme (ServerlessLLM'nin NVMe→DRAM→HBM boru hattı, 10-200x gecikme azalması) ve girdi tokenlerini (KB) taşıyan, KV cache'i (GB) değil, canlı geçiş. Modal 2-4s soğuk başlatmayı zemin olarak yayınlar; Baseten 5-10s varsayılan, ön ısıtma ile saniye altı. Bu ders beş katmanı ölçmeyi, bütçelemeyi ve yığmayı öğretir.

**Tür:** Öğrenme
**Diller:** Python (stdlib, oyuncak soğuk-başlatma yolu simülatörü)
**Önkoşullar:** Faz 17 · 02 (Inference Platform Ekonomisi), Faz 17 · 03 (GPU Otomatik Ölçekleme)
**Süre:** ~60 dakika

## Öğrenme Hedefleri

- Soğuk başlatma azaltmanın beş katmanını sıralayın ve her katmanda bir araç veya örüntü adlandırın.
- 70B model için toplam soğuk başlatma süresini (düğüm sağlama) + (ağırlık indirme) + (ağırlıkları HBM'e yükleme) + (motor başlatma) toplamı olarak hesaplayın.
- Canlı geçişin neden girdi tokenlerini (KB) değil KV cache'i (GB) aktardığını ve cezanın (yeniden hesaplama) ne olduğunu açıklayın.
- Sıcak-havuz ödünleşimini (boş GPU için öde veya soğuk-başlatma kuyruğunu kabul et) ve `min_workers > 0`'ın zorunlu hale geldiği SLA eşiğini adlandırın.

## Sorun

Sunucusuz LLM endpoint'iniz gece boyunca sıfıra ölçekleniyor. Sabah 8'de trafik sıçrıyor. İlk istek şunları beklerken:

1. Karpenter bir GPU düğümü sağlar: 45-60s.
2. Konteyner, 30 GB'lık bir imgeyi ağırlıklarla çeker: 120-300s.
3. Motor, ağırlıkları HBM'e yükler: model boyutuna ve depolama hızına bağlı olarak 45-120s.
4. vLLM veya TRT-LLM CUDA grafiklerini, KV cache havuzunu, tokenizer'ı başlatır: 10-30s.

Toplam: Bir token geri gelmeden önce 220-510s (kabaca 3-8 dakika). SLA'nız 2s. Bir sıcak havuz (`min_workers=1`) gönderiyorsunuz ve sorun kaybolmuş gibi görünüyor — ama artık 7/24 bir boş GPU için ödeme yapıyorsunuz. Servisiniz her birinde bir sıcak replika olmak üzere 5 ürüne sahipse, bu, tek bir kullanıcı çağırıp çağırmadığı fark etmeksizin 5 × 24 × 30 = 3.600 GPU-saat/ay demektir.

Soğuk başlatma azaltma, sunucusuz ekonomiyi korurken her-zaman-açık'in gecikmesini yaklaşıklandırmanın yoludur.

## Kavram

### Katman 1 — önceden tohumlanmış düğüm imgeleri (Bottlerocket)

AWS'de, Bottlerocket'in çift-birimli mimarisi işletim sistemini veriden ayırır. Konteyner imgeniz önceden çekilmiş veri biriminin anlık görüntüsünü alın; `EC2NodeClass` içinde anlık görüntü kimliğine başvurun. Yeni düğümler, ağırlıklar zaten yerel NVMe üzerinde olacak şekilde önyüklenir — 2. ve 3.'ün bir kısmı adımları kaybolur. Karpenter ile yerel olarak çalışır. Büyük modeller için tipik tasarruf: soğuk başlatma başına 2-4 dakika.

GCP'de eşdeğer: konteyner katmanları önceden pişirilmiş özel VM imgeleri. Azure'da: aynı örüntüyle yönetilen disk anlık görüntüleri.

### Katman 2 — model akışı (Run:ai Model Streamer)

İlk isteği yanıtlamadan önce tam dosyayı yüklemek yerine, ağırlıkları katman katman GPU belleğine akıtın ve ilk transformer bloğu yerleşik olur olmaz işlemeye başlayın. NVIDIA Run:ai Model Streamer, vLLM 2026'da yerel olarak gönderilir. S3, GCS ve yerel NVMe ile çalışır. Büyük modeller için I/O'yu hesaplama kurulumuyla örtüştürerek ağırlık yükleme süresini kabaca yarıya indirir.

### Katman 3 — GPU bellek anlık görüntüleri (Modal)

Modal, ilk yüklemeden sonra GPU durumunun (ağırlıklar, CUDA grafikleri, KV cache bölgesi) bir kontrol noktasını alır. Sonraki yeniden başlatmalar, doğrudan HBM'e deseralize eder — yeniden başlatmadan 10x daha hızlı. Bu, "2 saniyede sıcak bir GPU önyükle"ye en yakın şeydir. Ödünleşim: anlık görüntüler GPU-topolojisi başınadır, dolayısıyla Karpenter sizi farklı bir SKU'ya taşırsa, yeniden kontrol noktası alırsınız.

### Katman 4 — sıcak havuzlar (min_workers=1)

En basit azaltma: bir replikayı her zaman hazır tutun. Maliyet, 7/24 bir GPU'nun saatlik oranıdır. Aritmetik küçük modellerde acımasızdır (30s'lik bir soğuk başlatmayı önlemek için saatte 0,85-1,50$ ödersiniz) ve büyük modellere nazik olur (5 dakikalık bir soğuk başlatmayı önlemek için saatte 4$ ödersiniz). Sıcak havuzların zorunlu hale geldiği SLA eşiği: tipik olarak 70B+ modelde TTFT P99 < 60s.

### Katman 5 — katmanlı yükleme (ServerlessLLM)

ServerlessLLM depolamayı bir hiyerarşi olarak ele alır: NVMe (hızlı ama büyük), DRAM (orta ama katmanlı), HBM (küçük ama anında). Ağırlıklar DRAM'e önceden yüklenir; HBM'e talep-üzerine yükleyin. Makale, naif disk-HBM'e kıyasla soğuk yüklemelerde 10-200x gecikme azalması bildiriyor. Üretim benimsenmesi erken aşamada, ancak vLLM ile entegrasyonlar var.

### Katman 6 — canlı geçiş (bonus örüntü)

Bir düğüm kullanılamaz hale geldiğinde (spot eviction, düğüm drenajı), geleneksel örüntü başka bir replikayı soğuk başlatmak ve istek kuyruğunu boşaltmaktır. Canlı geçiş, girdi tokenlerini (kilobayt) modeli yüklü bir hedefe taşır ve hedef üzerinde KV cache'i yeniden hesaplar. Yeniden hesaplama, GB'larca KV cache'i ağ üzerinden aktarmaktan daha ucuzdur. Ayrıştırılmış dağıtımlar için uygulanabilir.

### Sıcak-havuz matematiği

P99 TTFT SLA'sı 2s olan bir servis için, soru "sıcak havuz evet/hayır" değil, "kaç tane sıcak replika ve hangi yollar onları alır"dir.

- Yüksek-değerli etkileşimli yollar (canlı sohbet, sesli agent): `min_workers=1-2`.
- Arka plan batch yolları (gece sınıflandırması): sıfıra ölçekleme kabul edilir, 5-10 dakikalık soğuk başlatma tolere edilebilir.
- Premium katman: ayrılmış kapasite ile kiracı başına `min_workers`.

### Optimize etmeden önce ölçün

Yeni bir düğümde 70B model için soğuk-başlatma anatomisi (gösterim amaçlı):

| Aşama | Süre | Azaltma |
|-------|------|---------|
| Düğüm sağlama | 50s | Bottlerocket + önceden tohumlanmış imge, sıcak havuz |
| İmge çekme | 180s | Önceden tohumlanmış veri birimi (ortadan kaldır) |
| Ağırlıkları HBM'e | 75s | Model streamer (yarıya indir); GPU anlık görüntüsü (ortadan kaldır) |
| Motor başlatma | 20s | Kalıcı CUDA grafik önbelleği |
| İlk forward | 3s | Min doğuştan gelen gecikme |
| **Toplam soğuk** | **328s** | |
| **Azaltmalarla toplam** | **~15s** | 22x azalma |

### Hatırlamanız gereken sayılar

- Modal soğuk başlatma: 2-4s (GPU anlık görüntüleriyle).
- Baseten varsayılan soğuk başlatma: 5-10s; ön ısıtma ile saniye altı.
- Ham 70B soğuk başlatma: 3-8 dakika.
- Run:ai Model Streamer: ~2x ağırlık yükleme hızlanması.
- ServerlessLLM katmanlı yükleme: 10-200x gecikme azalması (makale sayıları).

## Kullan

`code/main.py`, her azaltmayla ve azaltmasız bir soğuk-başlatma yolunu modeller. Toplam soğuk başlatma süresini, sıcak-havuz maliyetini ve sıcak replikayı ödeyen başabaş istek oranını raporlar.

## Üret

Bu ders `outputs/skill-cold-start-planner.md` üretir. SLA, model boyutu ve trafik şekli verildiğinde, hangi azaltmaların yığılacağını seçer.

## Alıştırmalar

1. `code/main.py`'yi çalıştırın. SLO'da ek istek düşüşleri ödeyerek soğuk başlatma vergisini ödemekten daha ucuz olan sıcak replika için başabaş istek oranını hesaplayın.
2. P99 TTFT SLA'sı 3s olan 13B bir model dağıtıyorsunuz. Onu başaran minimum azaltma yığınını (en az katman) seçin.
3. Bottlerocket ön-tohumlama, imge çekmeyi ortadan kaldırır, ancak ağırlıklar hâlâ anlık görüntüden HBM'e yüklenir. Anlık görüntü destekli NVMe 7 GB/s okuyorsa, 70B model için duvar saati süresini hesaplayın.
4. Sunucusuz sağlayıcınız GPU anlık görüntüleri sunuyor (Modal) ve ekibiniz "anlık görüntüler PII sızdırır" diye reddediyor. Her iki tarafı tartışın — gerçekçi risk nedir ve azaltma (efemeral anlık görüntüler, şifreleme, namespace izolasyonu) nedir?
5. Katmanlı bir sıcak-havuz politikası tasarlayın: ücretli kullanıcılar, deneme kullanıcıları ve batch iş yükleri için kaç sıcak replika? Matematiği gösterin.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|----------------------|----------------------------|
| Soğuk başlatma | "büyük duraklama" | Yeni bir replikada istekten ilk tokena kadar geçen süre |
| Sıcak havuz | "her-zaman-açık minimum" | En az bir replikayı hazır tutmak için `min_workers >= 1` |
| Önceden tohumlanmış imge | "pişmiş AMI" | Konteyner ağırlıkları önceden yerleşik düğüm imgesi |
| Bottlerocket | "AWS düğüm işletim sistemi" | Çift-birimli anlık görüntü desteği olan AWS konteyner-optimize işletim sistemi |
| Model streamer | "akış yükleme" | Ağırlıklar I/O'sunu hesaplama kurulumuyla örtüştür |
| GPU anlık görüntüsü | "HBM'e kontrol noktası" | Yükleme-sonrası GPU durumunu serileştir; yeniden başlatmada deseralize et |
| Katmanlı yükleme | "NVMe + DRAM + HBM" | Depolama katmanları hiyerarşisi; talep üzerine yükle |
| Canlı geçiş | "tokenleri taşı" | Girdiyi (KB) aktar, hedef üzerinde KV'yi yeniden hesapla |
| `min_workers` | "sıcak replikalar" | Sunucusuz minimum canlı tutma sayısı |
| Sıfıra ölçekleme | "tam sunucusuz" | Boştayken maliyet yok; tam soğuk başlatma vergisini kabul et |

## İleri Okuma

- [Modal — Cold start performance](https://modal.com/docs/guide/cold-start) — Modal'ın yayınlanan kıyaslamaları ve kontrol noktası mimarisi.
- [AWS Bottlerocket](https://github.com/bottlerocket-os/bottlerocket) — önceden tohumlanmış veri birimi anlık görüntü örüntüsü.
- [NVIDIA Run:ai Model Streamer](https://github.com/run-ai/runai-model-streamer) — ağırlık yüklemeyi hesaplama kurulumuyla örtüştür.
- [Baseten — Cold-start mitigation](https://www.baseten.co/blog/cold-start-mitigation/) — ön ısıtma oyun kitabı.
- [ServerlessLLM paper (USENIX OSDI'24)](https://www.usenix.org/conference/osdi24/presentation/fu) — katmanlı yükleme tasarımı.
- [NVIDIA — Disaggregated LLM Inference on Kubernetes](https://developer.nvidia.com/blog/deploying-disaggregated-llm-inference-workloads-on-kubernetes/) — ayrıştırılmış dağıtımlar için canlı geçiş.
