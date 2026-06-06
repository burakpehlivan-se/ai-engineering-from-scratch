---
name: dp-solver
description: Küçük tablo MDP'yi politika yineleme veya değer yineleme ile tam olarak çöz. Yakınsama davranışını raporla
version: 1.0.0
phase: 9
lesson: 2
tags: [rl, dinamik-programlama, bellman]
---

Bilinen modeli olan bir MDP verildiğinde, aşağıdakileri üret:

1. Seçim. Politika yinelemesi veya değer yinelemesi. |S|, |A|, γ'ya bağlı gerekçe.
2. Başlatma. V_0, başlangıç politikası. Yakınsama hassasiyeti.
3. Durdurma. Sup-norm toleransı ε. Beklenen süpürme sayısı.
4. Doğrulama. V*(s_0) tam olarak hesaplandı. Açgözlü politika çıkarıldı.
5. Kullanım. Bu temel çizginin örnekleme tabanlı yöntemleri hata ayıklamak/değerlendirmek için nasıl kullanılacağı.

> 10⁷ durum uzayında DP çalıştırma. Sup-norm kontrolü olmadan yakınsama iddia etme. Sonsuz-ufuk görevinde γ ≥ 1 olan herhangi bir değeri garanti ihlali olarak işaretle.

Geri dönüş. Yakınsama yavaşsa veya salınıyorsa (γ → 1 veya büyük ödül aralığı), adım boyutunu sıkılaştırmayı veya başka bir DP formülasyonuna (Gauss-Seidel, sıralı geri yükleme) geçmeyi düşün.
