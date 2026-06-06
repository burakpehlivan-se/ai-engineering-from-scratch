---
name: engine-picker
description: Donanım, ölçek ve iş yükü verildiğinde self-hosted bir LLM motoru (llama.cpp, Ollama, TGI, vLLM, SGLang) seç. 2026 TGI bakım modunu bir geçiş tetikleyicisi olarak adlandır.
version: 1.0.0
phase: 17
lesson: 28
tags: [self-hosted, vllm, sglang, llama-cpp, ollama, tgi, trt-llm, engine-selection]
---

Donanım (CPU / Apple Silicon / AMD / NVIDIA Hopper / NVIDIA Blackwell), ölçek (tek-kullanıcı / küçük ekip / üretim / kurumsal) ve iş yükü (genel sohbet / agentic / RAG / uzun-bağlam / kod) verildiğinde bir motor önerisi üret.

Üretilecekler:

1. **Motor.** Belirli motoru adlandır. Donanım-önce, ölçek-ikinci, iş yükü-üçüncü ağacına atıf.
2. **Alternatifler neden değil.** Her alternatif motor için neden tercih edilmediğini belirt (TGI bakım modu, AMD TRT-LLM'yi dışlar, Ollama yalnızca geliştirme).
3. **Boru hattı.** Üretimde ise, boru hattı kalıbını (geliştirmede Ollama → staging'de llama.cpp → üretimde vLLM/SGLang) adlandır ve ağırlık biçiminin (GGUF veya HF) aktığını doğrula.
4. **Üretim yığınlaması.** Üretim ölçeğinde, kompozisyon için Phase 17 · 18 (production-stack), · 17 (ayrıştırılmış), · 11 (önbellek-farkında yönlendirici) konularına yönlendir.
5. **TGI geçişi.** Mevcutsa TGI ise, geçiş planını ve zaman çizelgesini belirt — acil değil ama 6 ay içinde başlanmalı.
6. **Donanım tuzağı.** İki sert kısıtı belirt: yalnızca CPU → llama.cpp; AMD → TRT-LLM yok.

**Hard rejects (zorunlu redler):**
- 2026'da yeni projeleri varsayılan olarak TGI yapmak. Reddet — bakım modu.
- >1 eşzamanlı kullanıcıda paylaşılan üretim için Ollama. Reddet — iş geçişi boşluğu.
- NVIDIA-onayını doğrulamadan TRT-LLM önermek. Reddet — AMD / NVIDIA-dışı sert bir engeldir.

**Reddetme kuralları:**
- Donanım karışıksa (bazı AMD, bazı NVIDIA), küme başına motor kararı zorunlu; tek bir motor zorlama.
- İş yükü üretim ölçeğinde "bilinmiyor/genel" ise, varsayılan olarak vLLM ve 3 aylık trafik verisinden sonra yeniden değerlendirme planla.
- Ekip "GPU başına en hızlı, Blackwell yok" istiyor ve yalnızca Hopper'da ısrar ediyorsa, doğrula — TRT-LLM veya vLLM'nin ikisi de kabul edilebilir.

**Çıktı:** Motor, elenen alternatifler, boru hattı, üretim yığınlaması, TGI geçiş duruşu içeren tek sayfalık bir öneri. Tek bir üç aylık incelemeyle bitir: iş yükü şekli maddi olarak değiştiğinde motor seçimini yeniden değerlendir.
