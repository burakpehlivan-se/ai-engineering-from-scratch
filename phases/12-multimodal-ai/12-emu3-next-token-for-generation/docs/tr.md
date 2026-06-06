# Emu3: Görüntü ve Video Üretimi için Sonraki-Token Tahmini

> BAAI'nin Emu'su (Wang ve diğerleri, Eylül 2024), difüzyon ile otoregresif tartışmasını bitirmesi gereken 2024 sonucudur. Tek bir Llama tarzı yalnızca çözümleyici transformer, yalnızca sonraki-token tahmini hedefiyle, metin + VQ görüntü token'ları + 3B VQ video token'larından oluşan birleşik bir sözlük üzerinde eğitilir, görüntü üretiminde SDXL'i, algılamada LLaVA-1.6'yı yener. CLIP kaybı yok. Difüzyon takvimi yok. Sınıflandırıcı-rehbersiz (classifier-free) rehberlik kalite için kullanılır ama temel eğitim hedefi öğretmen zorlamalı (teacher forcing) sonraki-token tahminidir. Nature'da yayınlandı. Bu ders Emu3 tezini inceler — neden daha iyi bir tokenize edici + ölçek her şey için yeterlidir — ve difüzyon yaklaşımlarıyla karşılaştırır.

**Tür:** Öğren
**Diller:** Python (stdlib, 3B video tokenize edici matematiği + otoregresif örnekleme iskeleti)
**Önkoşullar:** Faz 12 · 11 (Chameleon)
**Süre:** ~120 dakika

## Öğrenme Hedefleri

- Emu3'ün tek-kayıplı sonraki-token hedefinin, görüntü kalitesi için difüzyonun gerekli olduğu uzun süredir devam eden varsayımına rağmen neden çalıştığını açıklama.
- 3B video tokenize edicisini tasvir etme: uzamsal-zamansal VQ sözlüğü nasıl görünür, yamalar neden zamanı kapsar.
- Emu3'ü (eğitim hesaplama, çıkarım maliyeti, kalite tavanı) açısından Stable Diffusion XL ile karşılaştırma.
- Aynı Emu3 modelinin oynadığı üç rolü adlandırma: Emu3-Gen (görüntü üretimi), Emu3-Chat (algılama), Emu3-Stage2 (video üretimi).

## Sorun

2024'e kadar geleneksel bilgelik: görüntü üretimi difüzyon gerektirir. Argument: disket görüntü token'ları ayrıntıyı yeniden oluşturmak için çok fazla bilgi kaybeder ve otoregresif örnekleme binlerce token boyunca hata biriktirir. Stable Diffusion, DALL-E 3, Imagen, Midjourney hepsi bir tür difüzyon kullanır. Chameleon (Ders 12.11) küçük ölçekte bunu kısmen yanlışladı ama SDXL ile kalitede eşleşemedi.

Emu3 argümana doğrudan saldırdı. İddia: daha iyi görsel tokenize edici + yeterli ölçek + sonraki-token kaybı = aynı modelde difüzyonu yenen görüntü üretimi, aynı zamanda algılama da yapar.

Yayınlandığında tartışma konusuydu. İki yıl sonra açık kaynak birleşik-üretim ailesi (Emu3, Show-o, Janus-Pro, Transfusion) araştırma için varsayılan yoldur; üretim çığır açan modelleri bazı çeşidini kullanıyor görünmektedir.

## Kavram

### Emu3 tokenize edici

Kilit malzeme görsel tokenize edicidir. Emu3, token başına 8x8 çözünürlük azaltmasıyla özel bir IBQ sınıfı tokenize edici (Ters Darboğaz Nicelleştirici, SBER-MoVQGAN ailesi) eğitir. 512x512 görüntü 32768 sözlük boyutuyla 64x64 = 4096 token olur.

Bu, Chameleon'ın K=8192 ile 512x512 için 1024 token'ından daha büyüktür ama token başına daha ucuzdur (daha küçük sözlük aramaları, daha basit codec). Kilit metrik: 30.5 dB yeniden oluşturma PSNR'si, 32 dB'lik Stable Diffusion'ın sürekli gizli uzayıyla rekabetçidir.

Video için: 3B VQ tokenize edicisi bir uzamsal-zamansal yamayı (4x4x4 piksel) bir tamsayıya kodlar. 8 FPS'te 4 saniyelik bir klip 32 karedir; 256x256'da 4x uzamsal ve 4x zamansal azaltmayla token sayısı (256/4) * (256/4) * (32/4) = 64 * 64 * 8 = 32.768 token'dır.

Tokenize edici kalitesi tavanıdır. Emu3'ün katkısının bir kısmı "çok iyi bir tokenize edici eğittik"tir.

### Tek-kayıplı eğitim

Emu3 tek bir hedef kullanır: metin token'ları, 2B görüntü token'ları ve 3B video token'larından oluşan paylaşımlı sözlükte sonraki-token tahmini. Eğitim sırasında katkıyı dengelemek için ağırlıklar modaliteye özel çarpanlarla çarpılır ama kayıp fonksiyonu özdeştir.

Karışık üzerinde eğitilir:
- Görüntü üretimi: `<text caption> <image> image_tokens </image>`
- Görüntü algılama: `<image> image_tokens </image> <question> text_tokens`
- Video üretimi: `<text caption> <video> video_tokens </video>`
- Video algılama: benzer.
- Yalnızca metin: standart NTP.

Model, görüntü token'larını ne zaman üreteceğini metin dağılımından öğrenir. Üretim, modelin `<image>` etiketinden sonra görüntü token'larını tahmin etmesinden ortaya çıkar.

### Sınıflandırıcı-rehbersiz rehberlik ve sıcaklık

Otoregresif görüntü üretimi, çıkarımda sınıflandırıcı-rehbersiz rehberlik (classifier-free guidance, CFG) ile çok daha iyi hale gelir. Emu3 bunu kullanır: iki kez üret, birinde tam açıklama, diğerinde boş açıklama, logit'leri rehberlik ağırlığıyla (tipik 3.0-7.0) karıştır. Bu difüzyonun kullandığı aynı CFG hilesi, otoregresif duruma aktarılmıştır.

Sıcaklık önemlidir: çok yüksek, artefaktlar; çok düşük, mod çökmesi (mode collapse). Emu3'ün önerilen sıcaklığı algılama için 1.0, görüntü üretimi için 0.8'dir.

### Üç rol, tek model

Emu3 işlevsel olarak üç ayrı API olarak sunulur ama tek bir temel ağırlık kümesi:

- Emu3-Gen. Görüntü üretimi. Metin girdisi, görüntü token'ları çıktısı.
- Emu3-Chat. VQA ve açıklama. Görüntü (token) girdisi, metin çıktısı.
- Emu3-Stage2. Video üretimi ve video VQA. Metin veya video girdisi, metin veya video çıktısı.

Görev özel kafa yok. Yalnızca farklı istem şablonları. Aynı kontrol noktası.

### Kıyaslama testleri

Emu3 makalesinden (Eylül 2024):

- Görüntü üretimi: MJHQ-30K FID'de SDXL'i yener (5.4 vs 5.6), GenEval genelinde (0.54 vs 0.55 — istatistiksel berabere) ve Deep-Eval bileşiğinde eş değer.
- Görüntü algılama: VQAv2'de LLaVA-1.6'yı yener (75.1 vs 72.4) ve MMMU'da yaklaşık olarak eşleşir.
- Video üretimi: Sora dönemi herkese açık kıyaslama testi yapılan modellerle rekabetçi FVD ile 4 saniyelik klip kalitesi.

Sayılar her zaman kazanmıyor — Emu3 bir yerde bir puan takası yapıyor — ama "sonraki-token tahmini her şey için yeterlidir" iddiası modaliteler boyunca savunulabilir.

### Hesaplama maliyeti

Emu3, 7B parametrelik bir modelle yaklaşık 300 milyar multimodal token üzerinde eğitildi. GPU-saatleri yaklaşık olarak Llama-2-7B ön-eğitimiyle karşılaştırılabilir (A100 sınıfı çip üzerinde 2k-4k GPU-yılı). Stable Diffusion 3 gibi difüzyon modelleri benzer bütçelerde eğitilir ama ayrı metin kodlayıcılarına ve daha karmaşık hatlara ihtiyaç duyar.

Çıkarımda Emu3 görüntü başına SDXL'den daha yavaştır: 30 tok/s'te 4096 görüntü token'ı 512x512 görüntü için ~2 dakika, SDXL için 2-5 saniye. Spekülatif çözümleme ve KV-önbellek optimizasyonları farkı daraltır ama kapatmaz. Otoregresif görüntü üretimi hesaplama ağırdır; bu kalıcı uzlaşmadır.

### Neden önemli

Emu3'ün derin katkısı kavramsaldır. Sonraki-token tahmini görüntü üretiminde difüzyonla eşleşecek şekilde ölçeklenirse, birleşik-model yolu (tek kayıp, tek omurga, herhangi bir modalite) uygulanabilir. Gelecek modeller ayrı metin kodlayıcılarına, ayrı difüzyon takvimlerine, ayrı VAE'lere ihtiyaç duymaz. Tek transformer, modalite başına tek tokenize edici, ölçek.

Show-o, Janus-Pro ve InternVL-U hep bu tezi inşa eder veya meydan okur. Çin laboratuvarları (BAAI, DeepSeek) 2025'e kadar bu yönde ABD laboratuvarlarından daha agresif yayın yapar.

## Kullan

`code/main.py` iki oyuncu parça inşa eder:

- 2B vs 3B VQ tokenize edici sayacı: (çözünürlük, yama, klip_uzunluğu, FPS) verildiğinde görüntü için token sayılarını videoyla karşılaştırın.
- Sınıflandırıcı-rehbersiz rehberlikli sıcaklıkta otoregresif görüntü-token örnekleme.

CFG uygulaması Emu3 tarifini eşleştirir — koşulsuz ve koşullu logit'leri rehberlik ağırlığıyla karıştırır.

## Teslimat

Bu ders `outputs/skill-token-gen-cost-analyzer.md` dosyasını üretir. Bir üretim ürün şartnamesi (görüntü veya video, hedef çözünürlük, kalite katmanı, gecikme bütçesi) verildiğinde token sayılarını, çıkarım maliyetini hesaplar ve Emu3 ailesi ile difüzyon arasında seçim yapar.

## Alıştırmalar

1. Emu3 8x8 azaltmayla 512x512 görüntü başına 4096 token üretir. 1024x1024 ve 2048x2048 için eşdeğeri hesaplayın. Çıkarım gecikmesine ne olur?

2. Emu3 Bölüm 3.3'ü okuyun, video tokenize edicisini. 3B VQ yama şeklinin ne olduğunu ve neden 4x4x4 de 8x8x1 olmadığını açıklayın.

3. Sınıflandırıcı-rehbersiz rehberlik ağırlığı 5.0 vs 3.0: hangi görsel etki? `code/main.py`'de matematiği izleyin.

4. Emu3-7B'nin 300B token ile eğitim FLOPs'larını hesaplayın ve Stable Diffusion 3 ile karşılaştırın. Hangisi eğitmek daha pahalıydı?

5. Emu3 FID'de SDXL'i yener ama VQAv2'de uzman VLM'lerle yemez. Birleşik-kayıp yaklaşımının farklı kıyaslama testlerinde uzmanlara göre farklı güçlü yönler gösterdiğini açıklayın.

## Temel Terimler

| Terim | İnsanların söylediği | Gerçekte ne anlama geldiği |
|-------|---------------------|--------------------------|
| Sonraki-token tahmini | "NTP" | Standart otoregresif kayıp: token[0..i] verildiğinde token[i+1] tahmin etme; tokenizasyondan sonra her modalite için çalışır |
| IBQ tokenize edici | "Ters darboğaz nicelleştirici" | Chameleon'dan daha büyük sözlüklerle (32768+) ve daha iyi yeniden oluşturma yeteneğine sahip bir VQ-VAE sınıfı |
| 3B VQ | "Uzamsal-zamansal nicelleştirici" | (zaman, satır, sütun) ile indekslenen sözlük; bir token 4x4x4 piksel küpünü kapsar |
| Sınıflandırıcı-rehbersiz rehberlik | "CFG" | Koşullu ve koşulsuz logit'leri gamma ağırlığıyla karıştırır; çıkarımda görüntü kalitesini artırır |
| Birleşik sözlük | "Paylaşımlı token'lar" | Metin + görüntü + video hepsi aynı tamsayı uzayından çeker; model bir sonraki hangi modalite gelirse onu tahmin eder |
| MJHQ-30K | "Görüntü üretimi kıyaslama testi" | 30k istemle orta yol kalitesinde kıyaslama testi; Emu3 burada FID rapor eder |

## İleri Okuma

- [Wang ve diğerleri — Emu3: Sonraki-Token Tahmini Her Şey İçin Yeterlidir (arXiv:2409.18869)](https://arxiv.org/abs/2409.18869)
- [Sun ve diğerleri — Emu: Multimodalitada Üretici Ön-Eğitim (arXiv:2307.05222)](https://arxiv.org/abs/2307.05222)
- [Liu ve diğerleri — LWM (arXiv:2402.08268)](https://arxiv.org/abs/2402.08268)
- [Yu ve diğerleri — MAGVIT-v2 (arXiv:2310.05737)](https://arxiv.org/abs/2310.05737)
- [Tian ve diğerleri — VAR (arXiv:2404.02905)](https://arxiv.org/abs/2404.02905)
