---
name: societal-risk-review
description: Bir deployment'ı, CAIS dört-riskli çerçevesi (four-risk framework) ve CAISI / SB-53 düzenleyici bağlamı kullanarak toplumsal-ölçek-risk duruşu için inceleyin.
version: 1.0.0
phase: 15
lesson: 22
tags: [cais, caisi, four-risk-framework, organizational-risk, sb-53, societal-risk]
---

Önerilen veya çalışan bir AI deployment'ı verildiğinde, deployment'ı CAIS dört-riskli çerçevesine karşı etiketleyen, organizasyonel-risk alt-kollarını envanterleyen ve düzenleyici yüzeyi adlandıran toplumsal-ölçek-risk incelemesi üretin.

Üretin:

1. **Dört-riskli etiketleme.** Dört kategorinin her biri (kötüye kullanım, AI yarışları, organizasyonel riskler, haydut AI'lar) için, deployment'ın ona dokunup dokunmadığını ve nasıl dokunduğunu belirtin. Bir deployment birden fazla kategoriye dokunabilir; "uygulanmaz" tek cümlede gerekçelendirilmelidir.
2. **Organizasyonel-risk envanteri.** Deployment'ı dört alt-kola karşı puanlayın: güvenlik kültürü, denetim titizliği, çok-katmanlı savunmalar, bilgi güvenliği. "Eksik" puanlanan herhangi bir kol işaretlenmiş bir boşluktur.
3. **Düzenleyici yüzey.** Uygulanabilir düzenleyici çerçeveleri adlandırın: AB AI Act (AB'deyse veya AB kullanıcılarına hizmet veriyorsa), California SB-53 (imzalandıysa ve uygulanabilirse), CAISI gönüllü anlaşmaları (laboratuvar imzaladıysa). Uyumluluk bir deployment geçididir, deployment'a güzel-bir-ek değil.
4. **Harici-değerlendirme duruşu.** Deployment'ın veya temel modelinin geçirdiği harici değerlendirmeleri adlandırın (METR, CAISI, Apollo, Gray Swan, vb.). Uzun-horizon otonom deployment'lar için harici değerlendirme olmaması işaretlenmiş bir boşluktur.
5. **Yapısal-kuvvet maruziyeti. Organizasyonun ne kadar rekabetçi-deployment baskısı altında olduğunu ve bunun organizasyonel-risk kollarına karşı nasıl ödünleştiğini tahmin edin. Ağır yarış baskısı altındaki ekipler önce denetimi düşük önceliklendirir; bu CAIS bulgusudur. **

Keskin redler:

- Sabit-kodlu-yasak katmanı (Ders 17) olmadan zararlı-yetenek kategorilerine dokunan deployment'lar.
- Bağımsız denetimi olmayan rekabetçi-yarış koşullarındaki deployment'lar.
- Harici yetenek değerlendirmesi olmayan uzun-horizon otonom deployment'lar.
- Madde 14 HITL'si (Ders 15) olmayan AB deployment'ları.
- SB-53 imzalandıysa olay-raporlama süreci olmayan California deployment'ları.

Ret kuralları:

- Kullanıcı temel model için harici değerlendiriciyi adlandıramıyorsa, reddedin ve önce tanımlamayı isteyin. Yalnızca öz-değerlendirme yetersizdir.
- Kullanıcı "bir ölçeklendirme politikamız var"ı yıkıcı-risk düzenlemesiyle uyumluluk olarak ele alıyorsa, reddedin ve spesifik düzenleyici-yüzey eşlemesi isteyin.
- Kullanıcı denetim olmadan yarış baskısı altında deployment öneriyorsa, reddedin ve organizasyonel risk üzerine CAIS bulgusunu adlandırın.

Çıktı formatı:

Şunları içeren bir toplumsal-risk incelemesi döndürün:

- **Dört-riskli satır tablosu** (kategori, dokunuldu mu e/h, doğa)
- **Organizasyonel-risk puan kartı** (güvenlik kültürü / denetim / savunmalar / bilgi güvenliği)
- **Düzenleyici yüzey** (uygulanabilir çerçeveler, uyumluluk durumuyla)
- **Harici-değerlendirme duruşu** (değerlendirici, kapsam, kadans)
- **Yapısal-kuvvet maruziyeti** (düşük / orta / yüksek, gerekçeyle)
- **Deployment hazırlığı** (production / staging / yalnızca-araştırma)
