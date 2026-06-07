---
name: swarm-optimizer
description: Belirli bir LLM veya agent optimizasyon problemi için PSO, ACO, genetik algoritmalar ve gradyan-tabanlı optimize ediciler arasında seçim yapın. Biyo-ilhamlı swarm algoritmaları gradyan-free (gradyansız) olup arama uzayının ayrık veya uygunluk fonksiyonunun kara-kutu olduğu LLM-dönemi iş yüklerine uygundur.
version: 1.0.0
phase: 16
lesson: 19
tags: [multi-agent, swarm-optimization, PSO, ACO, prompt-optimization, routing]
---

Bir LLM veya agent optimizasyon problemi verildiğinde, doğru optimize ediciyi seçin.

Üretin:

1. **Problem parmak izi.** Arama uzayı (sürekli sayısal, prompt dizesi, model ağırlıkları, yönlendirme grafı), uygunluk sinyali (otomatik test, LLM hakem, insan puanlayıcı, iş KPI'sı), değer-zamanı (dakika, saat, gün).
2. **Optimize edici seçimi.** PSO, ACO, genetik algoritma, DPO/RL, manuel ayar. Her birinin varsayılan bir kullanım durumu vardır:
 - sınırlı uzayda sürekli sayısal → PSO
 - yönlendirme veya yol seçimi → ACO
 - ayrık sembolik / programlar → genetik algoritmalar
 - türevlenebilir ödül → DPO/RL
 - düşük-boyutlu, hızlı değerlendirme → grid/rastgele arama
3. **Popülasyon boyutlandırması.** PSO/GA için 10-30, ACO için feromon matris boyutu. Bütçe hesaplaması: N × T × değerlendirme başına maliyet. Ürettikleri değerden fazla maliyeti olan swarm'ları çalıştırmayın.
4. **Uygunluk + kalite kapısı.** Adayı hangi fonksiyon puanlar? ACO yönlendirmesi için, feromon birikimini hangi kalite eşiği tetikler?
5. **Yakınsama izleme.** İterasyon başına g_best veya feromon stabilitesini loglayın. Iraksamada (felaket-düzeyinde sürüklenme) ve erken yakınsamada (yerel optimum) uyarın.
6. **Azalma / keşif ayarı.** PSO atalet ve bilişsel/sosyal ağırlıklar; ACO feromon azalma oranı ve birikim miktarı. Ödünleşim: düşük azalma → erken kazanan üzerinde sıkışma; yüksek azalma → bellek yok.
7. **Sıfırlama koşulları.** Değerlendirme dağılımı kaydığında veya deployment örüntüsü değiştiğinde, g_best'i sıfırlayın veya feromonları geçici olarak sıfırlayın. Eski bellekler bellek olmamasından daha kötüdür.

Keskin redler:

- Uygunluğun insan incelemesi gerektirdiği görevlerde swarm optimize ediciler. İterasyon başına maliyet bütçeyi aşıyor.
- Net bir bütçe gerekçesi olmadan 50'den büyük popülasyon boyutları. Azalan getiriler baskındır.
- Kalite kapısı olmadan feromon yönlendirmesi. Hızlı-ama-yanlış agent'lar kilitlenir.
- Doğal sürekli gömme (embedding) olmayan ayrık arama uzaylarında PSO. Bunun yerine GA veya tavlama simülasyonu kullanın.

Ret kuralları:

- Kullanıcı net bir uygunluk fonksiyonu olmayan bir şeyi optimize etmeye çalışıyorsa, önce uygunluğu tanımlamasını önerin. Swarm optimize ediciler değerlendirici olmadan yardımcı olamaz.
- Kullanıcının bütçesi 100$'ın altındaysa, swarm'lar yerine manuel ayar + önbellekleme önerin.
- Dağılım günlük kayıyorsa, swarm optimize ediciler değil çevrimiçi öğrenme veya haydutlar (bandits) önerin.

Çıktı: Tek sayfalık özet. Tek cümlelik bir öneriyle başlayın ("3-agent × 4-görev-tipi yönlendirme problemi üzerinde kalite-kapılı feromon birikimi ile ACO kullanın. Azalma 0.05, eşik 0.6, 200 ısınma görevi."), sonra yukarıdaki yedi bölüm. Bütçe tahmini ve 1 haftalık bir dağıtım planı ile bitirin.
