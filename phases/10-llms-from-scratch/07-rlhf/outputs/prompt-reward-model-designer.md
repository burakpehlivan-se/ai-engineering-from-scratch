---
name: prompt-reward-model-designer
description: RLHF hizalama (alignment) için ödül modeli eğitim pipeline'ları tasarlayın
version: 1.0.0
phase: 10
lesson: 7
tags: [rlhf, reward-model, ppo, alignment, human-feedback, preference-learning]
---

# Ödül Modeli Tasarımcısı

Bir dil modelini hedef davranışa (yardımseverlik, kodlama yeteneği, güvenlik, dürüstlük) hizalamak için RLHF (İnsan Geri Bildirimiyle Pekiştirmeli Öğrenme) pipeline'ı oluştururken, veri toplama protokolünü tasarlamak, ödül modelini eğitmek ve PPO'yu yapılandırmak için bu çerçeveyi kullanın.

## Girdi Gereksinimleri

Şunları sağlayın:
- **Hedef davranış** (örneğin, "yardımcı ve zararsız asistan", "uzman Python kodlayıcısı", "güvenlikli tıbbi soru-cevap")
- **Temel model** (örneğin, SFT sonrası Llama 3 8B, Mistral 7B Chat)
- **Ödül modeli boyutu** (genellikle politika modeliyle aynı boyut veya daha büyük)
- **Etiketleme bütçesi** (insan saatleri veya mevcut karşılaştırma çiftleri)
- **Hesaplama bütçesi** (ödül modeli eğitimi + PPO için GPU saatleri)

## Adım 1: Tercih Verisi Toplama

### Etiketleme Protokolü

1. **Prompt seçimi**: SFT eğitim dağılımından ve dağılım dışı (OOD) promptlardan örnekleyin (%10-20 yeni)
2. **Yanıt üretimi**: SFT modelini farklı sıcaklıklarla (0.3, 0.7, 1.0) kullanarak her prompt için 2-4 yanıt üretin
3. **Karşılaştırma formatı**: Etiketleyicilere tam olarak 2 yanıt gösterin ve "Hangi yanıt daha iyi?" diye sorun
4. **Kriter puanlama cetveli**: Kullanım senaryonuz için "daha iyi"nin ne anlama geldiğini tanımlayın

### Puanlama Cetveli Şablonu

| Kriter | Ağırlık | Açıklama |
|-----------|--------|-------------|
| Yardımseverlik | %40 | Soruyu tam ve doğru cevaplıyor mu? |
| Zararsızlık | %25 | Zararlı, önyargılı veya yanıltıcı içerikten kaçınıyor mu? |
| Dürüstlük | %20 | Halüsinasyon (uydurma) yerine belirsizliği kabul ediyor mu? |
| Kısalık | %15 | Yanıt, soru için uygun uzunlukta mı? |

Kullanım senaryonuz için ağırlıkları ayarlayın. Bir kodlama asistanı, doğruluğu %60 ve kısalığı %20 olarak ağırlıklandırabilir.

### Veri Boyutu Kılavuzları

| Ölçek | Karşılaştırma Çiftleri | Etiketleyici Saatleri | Beklenen RM Doğruluğu |
|-------|-----------------|-----------------|---------------------|
| Asgari uygulanabilir | 5,000-10,000 | 400-800 | %60-65 |
| Üretim v1 | 20,000-50,000 | 1,600-4,000 | %65-72 |
| Üretim v2 | 100,000-500,000 | 8,000-40,000 | %72-78 |

InstructGPT, 40 yükleniciden 33,000 karşılaştırma kullandı. Anthropic'in ilk makalesi 20 etiketleyiciden 22,000 kullandı. Etiketleyiciler arası uyum genellikle %70-75'tir -- ödül modeli insan uyum düzeylerini aşamaz.

### Kalite Kontrolü

- **Uyum filtreleme**: Etiketleyicilerin %70'inden azının hemfikir olduğu çiftleri atın
- **Etiketleyici kalibrasyonu**: Gerçek etiketlemeden önce bilinen iyi çiftlerle kalibrasyon turları çalıştırın
- **Önyargı tespiti**: Etiketleyicilerin tutarlı olarak daha uzun yanıtları, resmi dili veya belirli kalıpları tercih edip etmediğini izleyin
- **Düşmanca örnekler**: Dikkatli okumayan etiketleyicileri yakalamak için tasarlanmış %5-10 örnek ekleyin

## Adım 2: Ödül Modeli Mimarisi

### Mimari Kararları

| Karar | Öneri | Gerekçe |
|----------|---------------|--------|
| Temel mimari | Politika ile aynı transformer | SFT kontrol noktasından ağırlık başlatma güçlü başlangıç özellikleri verir |
| Çıktı kafası | Son gizli durumdan tek doğrusal projeksiyon | En eksiksiz konum gösteriminden skaler ödül |
| Model boyutu | >= politika modeli boyutu | Daha küçük RM, PPO'yu destabilize eden güvenilmez sinyaller üretir |
| Başlatma | Yeni çıktı kafasıyla SFT kontrol noktası | Önceden eğitilmiş özellikler dil kalitesini zaten yakalar |

### Eğitim Yapılandırması

| Parametre | Aralık | Notlar |
|-----------|-------|-------|
| Öğrenme oranı | 1e-5 ile 5e-5 | SFT'den düşük, çünkü görev daha basit |
| Epoch sayısı | 1-3 | Sınırlı karşılaştırma verisiyle aşırı uyum (overfitting) büyük risktir |
| Parti boyutu | 64-256 | Her "örnek" bir çift olduğundan, etkin veri 2 katmanadır |
| Kayıp fonksiyonu | Bradley-Terry: -log(sigmoid(r_tercih_edilen - r_reddedilen)) | İkili karşılaştırmalar için standart |
| Doğrulama bölünmesi | %10-20 | Tutulan çiftler üzerinde doğruluğu izleyin |

### Değerlendirme Metrikleri

1. **İkili doğruluk**: Tutulan tercih çiftlerinin ne kadarını RM doğru sıralıyor? Hedef: > %65
2. **Marj dağılımı**: (r_tercih_edilen - r_reddedilen) dağılımını çizin. 0'ın üzerinde ortalanmalı, az sayıda negatif olmalı.
3. **Kalibrasyon**: sigmoid(r_tercih_edilen - r_reddedilen) gerçek insan tercih olasılığına yakın mı?
4. **Dağılım dışı genelleme**: Eğitimden farklı bir dağılımdan promptlarla test edin. Doğruluk < %10 düşmelidir.

## Adım 3: PPO Yapılandırması

### Hiperparametreler

| Parametre | Tipik Değer | Çok Yüksek Olursa Etkisi | Çok Düşük Olursa Etkisi |
|-----------|--------------|-------------------------|------------------------|
| KL katsayısı (beta) | 0.01-0.05 | Model neredeyse öğrenmiyor, SFT'ye çok yakın kalıyor | Ödül hackleme, dejenere çıktılar |
| Öğrenme oranı | 5e-6 ile 3e-5 | Eğitim instabilitesi, diverjans | Yavaş yakınsama, israf edilen hesaplama |
| Kırpma oranı (epsilon) | 0.1-0.3 | Büyük, potansiyel olarak destabilize edici güncellemeler | Çok muhafazakâr güncellemeler, yavaş öğrenme |
| Parti başına PPO epoch | 1-4 | Mevcut partiye aşırı uyum | Her partiyi yetersiz kullanma |
| Üretim parti boyutu | 128-512 | Bellek sorunları | Gürültülü gradyan tahminleri |
| Maksimum yanıt uzunluğu | 256-1024 | Yavaş üretim, bellek sorunları | Yararlı yanıtları keser |

### İzleme Paneli

PPO eğitimi sırasında bu metrikleri izleyin:

1. **Ortalama ödül**: Eğitim boyunca artmalı. Plato iyidir; düşüş instabilite demektir.
2. **KL diverjansı**: 10-20 nat'ın altında kalmalı. Sıçrama = ödül hackleme.
3. **Yanıt uzunluğu**: Stabil kalmalı. Monoton artış = uzunluk ödülü hackleme.
4. **Entropi**: Token dağılımı entropisi yavaşça azalmalı. Hızlı azalma = mod çöküşü.
5. **Ödül modeli uyumu**: PPO yanıtlarını ödül modeliyle puanlayın; uyum iyileşmeli.

### PPO Sırasında Kırmızı Bayraklar

| Belirti | Olası Neden | Çözüm |
|---------|-------------|-----|
| Ödül artıyor ama çıktılar bozuluyor | Ödül hackleme | KL katsayısını artırın, RM'yi düşmanca örneklerle yeniden eğitin |
| KL diverjansı patlıyor | Öğrenme oranı çok yüksek veya KL katsayısı çok düşük | Öğrenme oranını düşürün, beta'yı artırın |
| Yanıt uzunluğu monoton büyüyor | RM uzunluğu ödüllendiriyor | Ödüle uzunluk cezası ekleyin, RM'yi uzunluk kontrollü çiftlerle yeniden eğitin |
| Tüm yanıtlar aynı hale geliyor | Mod çöküşü | Üretim sıcaklığını artırın, PPO epoch'larını azaltın |
| Ödül çılgınca salınıyor | PPO instabilitesi | Öğrenme oranını düşürün, kırpme oranını artırın |

## Adım 4: Uçtan Uca Doğrulama

RLHF ile eğitilmiş bir modeli devreye almadan önce:

1. **SFT'ye karşı A/B testi**: SFT ve RLHF modellerini 200+ test promptunda çalıştırın. 3+ değerlendiricinin yanıtları karşılaştırmasını sağlayın. RLHF modeli zamanın > %60'ında kazanmalıdır.
2. **Güvenlik değerlendirmesi**: Bilinen düşmanca promptlarla (jailbreak'ler, zararlı istekler) test edin. RLHF modeli uygun şekilde reddetmelidir.
3. **Regresyon kontrolü**: RLHF modelinin temel yeteneklerini kaybetmediğini doğrulamak için standart kıyaslamaları (MMLU, HumanEval, MT-Bench) çalıştırın.
4. **Unutma kontrolü**: Genel bir metin derlemi üzerinde karmaşıklık (perplexity) ölçün. SFT modeline göre artış < %10 olmalıdır.
5. **Uzunluk analizi**: SFT ve RLHF modelleri arasında ortalama yanıt uzunluğunu karşılaştırın. RLHF > %50 daha uzunsa, ödül modeli muhtemelen bir uzunluk önyargısına sahiptir.
