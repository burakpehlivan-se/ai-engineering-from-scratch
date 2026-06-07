---
name: vllm-stack-decider
description: vLLM dağıtım düzenini kararla — production-stack Helm şeması, KV offload (yerel CPU veya LMCache), yönlendirici/gözlemlenebilirlik entegrasyonu — iş yükü ve filo büyüklüğüne göre.
version: 1.0.0
phase: 17
lesson: 18
tags: [vllm, production-stack, lmcache, kv-offload, connector-api]
---

İş yükü (istem şekli, eşzamanlılık, önek yeniden kullanım kalıbı), filo (motor sayısı, GPU türü) ve operasyonel bağlam (Kubernetes-native, çok-kiracılı, bütçe) verildiğinde bir vLLM yığın planı üret.

Üretilecekler:

1. **Yığın.** vLLM production-stack Helm şemasını (yeni dağıtımlar için önerilen) kullan veya kendininkini kur. Hangi operatörlerin/CRD'lerin geçerli olduğunu belirt.
2. **KV offload.** Şunlardan seç:
 - Yok (kısa istemler, düşük eşzamanlılık — yükü faydayı aşar).
 - Yerel vLLM CPU offload (tek motorlu HBM baskısı, basit).
 - LMCache bağlayıcısı (çok motorlu önek yeniden kullanımı, yoğun önceleme veya çok-kiracılı paylaşılan istemler).
3. **HBM kullanımı izleme.** Başlık payıyla `--gpu-memory-utilization` ayarla; %92+ sürekli izlemde, önceleme-öncesi sinyal olarak uyar.
4. **Yönlendirici entegrasyonu.** Önbellek-farkında yönlendirici (Phase 17 · 11). KV-olay kanalının yapılandırıldığını doğrula.
5. **Gözlemlenebilirlik.** Prometheus her motor için scrape, OTel GenAI öznitelikleri (Phase 17 · 13), production-stack'ten Grafana pano şablonu.
6. **Beklenen etki.** Mevcut duruma karşı beklenen iş geçişi kazanımını nicelleştir — 16x H100 kıyaslama şekline atıf (KV ayak izi HBM'i aştığında LMCache yardımcı olur).

**Hard rejects (zorunlu redler):**
- Paylaşılan önekler veya önceleme olmadan LMCache dağıtmak. Reddet — yük, fayda yok.
- HBM baskısı izlemesi olmadan vLLM çalıştırmak. Reddet — ilk önceleme sürpriz olacaktır.
- Helm şeması kullanım senaryosunu karşılıyorsa kendi production-stack'ini kurmak. Reddet — yeniden-icat maliyeti.

**Reddetme kuralları:**
- Filo <2 motordan oluşuyorsa, LMCache'i reddet — motorlar-arası yeniden kullanım asıl noktadır; tek motorda yerel offload kullan.
- İş yükünde istemler < 1K token ve eşzamanlılık < 100 ise, herhangi bir offload türünü reddet — HBM başlık payı yeterlidir.
- Ekipte K8s yetkinliği yoksa, production-stack'i reddet — tek motorlu vLLM + basit proxy ile başla.

**Çıktı:** Yığın, KV offload seçimi, HBM izleme, yönlendirici entegrasyonu, gözlemlenebilirlik, beklenen etki içeren tek sayfalık bir plan. Tek bir kapıyla bitir: son 24 saat üzerinden HBM kullanımı P99.
