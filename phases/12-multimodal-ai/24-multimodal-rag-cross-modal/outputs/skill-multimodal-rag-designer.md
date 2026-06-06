---
name: multimodal-rag-designer
description: Metin, görüntü, ses, video genelinde geri getiriciler, füzyon stratejisi ve temellendirilmiş jeneratör ile üretim multimodal bir RAG tasarlayın.
version: 1.0.0
phase: 12
lesson: 24
tags: [multimodal-rag, cross-modal-retrieval, fusion, grounded-generation]
---

Bir multimodal ürün sorgu akışı (sorguda hangi modaliteler, derlemde hangi modaliteler) verildiğinde, geri getiriciler, füzyon ve üretim tasarlayın.

Üretin:

1. Modalite başına geri getiriciler. Metin+görüntü için CLIP / SigLIP 2, metin+ses için CLAP, diğer her şey için VLM gizli durumları.
2. Füzyon seçimi. Puan füzyonu varsayılan; sorgu başına yönlendirme gerekirse MoE füzyonu; ölçekte dikkat füzyonu.
3. Temellendirilmiş jeneratör. Kaynak-etiketli çıktılar üzerinde eğitilmiş Qwen2.5-VL veya Claude 4.7.
4. Değerlendirme. Modalite başına Recall@k + füze edilmiş top-k doğruluğu + insan-yargıçlı uçtan uca.
5. Aantik çok-adımlı. Ne zaman yeniden sorgulanacağı; tetiklemek için güven eşiği.
6. Depolama tahmini. Modalite başına vektör sayıları ve sıkıştırma.

Sert reddetmeler:
- Paylaşılan uzay (CLIP / CLAP) olmadan modaliteler arasında bi-kodlayıcı geri getirme kullanmak. Puanlar anlamsızdır.
- Eğitim verisi olmadan MoE füzyonu önermek. MoE doğru yönlendirmek için denetim gerektirir.
- Puan füzyonu ağırlıklarının alanlar arasında aktarıldığını iddia etmek. Aktarılmazlar.

Ret kuralları:
- Derlemin eğitim geri getiricileri için görüntü-altyazı çifti verisi yoksa, özel ince ayarı reddedin ve hazır CLIP / SigLIP 2 önerin.
- Sorgu gecikme bütçesi <200ms ve çok-adımlı gerekliyse, reddedin; daha iyi geri getiricilerle tek atış önerin.
- Temellendirilmiş atıflar düzenleyici bir gereksinimse ve hiçbir jeneratör onları desteklemiyorsa, reddedin ve Anthropic / OpenAI atıf API'lerini veya açık bir son işlem atıf katmanını önerin.

Çıktı: Geri getiriciler, füzyon, jeneratör, değerlendirme, ajantik strateji, depolama ile tek sayfalık bir RAG tasarımı. arXiv 2502.08826, 2504.08748, 2503.18016 ile bitirin.
