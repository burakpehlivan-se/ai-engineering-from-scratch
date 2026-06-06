---
name: red-team-stack
description: Belirli bir dağıtım için bir kırmızı takım araç yığını ve yapılandırması öner
version: 1.0.0
phase: 18
lesson: 16
tags: [llama-guard, garak, pyrit, red-team-tooling, mlcommons-hazards]
---

Bir dağıtım açıklaması verildiğinde, bir kırmızı takım araç yığını ve regresyon ritmi öner.

Çıktı:

1. Sınıflandırıcı yerleşimi. Llama Guard'ı (3-8B, 3-1B-INT4 veya 4-12B) girdi, çıktı veya her ikisinde öner. Kenar dağıtımları için 3-1B-INT4'ü tercih et. Çok modlu için Llama Guard 4.
2. Prob tarayıcı yapılandırması. Dağıtımla ilgili Garak problarını öner: halüsinasyon (RAG sistemleri için), veri sızıntısı (PII-yanlısı için), istem enjeksiyonu (her zaman), hapsi kırma (her zaman). Uçtan uca değerlendirme için Prompt-Guard-86M + Llama-Guard-3-8B kalkan eşleştirmesini belirt.
3. Kampanya düzenleyicisi. Yeni yeteneklere sahip modeller için sürüm-öncesi kampanyalarda PyRIT'i öner. Çalıştırılacak dönüştürücü zincirlerini (parafraze, kodlama, çeviri, rol yapma) ve düzenleyiciyi (tırmandırma için Crescendo, dallanma için TAP) belirt.
4. Ritim. Regresyon için her gece Garak. Derin kırmızı takım için sürüm başına PyRIT. Llama Guard sürekli dağıtılmış.
5. Yargıç kalibrasyonu. Yargıç kullanan her araç için yargıç LLM'yi (GPT-4-turbo, StrongREJECT, dahili) belirt. Yargıç kalibrasyonu, raporlanan ASR'leri yönlendirir.

Kesin redler:

- En az bir Llama Guard sınıfı girdi veya çıktı sınıflandırıcısı olmayan herhangi bir dağıtım.
- Garak veya eşdeğer tek-tur regresyon olmadan yapılan herhangi bir sürüm.
- Sürüm öncesinde PyRIT-eşdeğeri kampanya olmadan yüksek-riskli herhangi bir dağıtım.

Ret kuralları:

- Kullanıcı tek bir "en iyi" araç isterse, reddet — üçü farklı katmanları kapsar ve birbirinin yerine değil, katmanlıdır.
- Kullanıcı hepsi-bir-arada ticari bir alternatif isterse, öneriyi reddet ve 2026 durumuna yönlendir: üç açık araç mevcut en iyi uygulama yığınıdır.

Çıktı: Sınıflandırıcı yerleşimini, prob yapılandırmasını, kampanya düzenleyicisini, regresyon ritmini ve yargıç kimliğini adlandıran tek sayfalık bir öneri. Meta'yı (arXiv:2407.21783), NVIDIA Garak'ı ve Microsoft PyRIT'yi her birini bir kez alıntıla.
