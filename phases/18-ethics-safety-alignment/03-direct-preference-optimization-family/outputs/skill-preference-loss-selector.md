---
name: preference-loss-selector
description: Veri kümesi şekline ve hedef aşamaya göre bir doğrudan hizalama algoritması kaybı öner
version: 1.0.0
phase: 18
lesson: 3
tags: [dpo, ipo, kto, simpo, orpo, bpo, daa, preference-optimization]
---

Bir tercih veri kümesi açıklaması (eşli veya eşsiz, tercih-gücü dağılımı, uzunluk dağılımı, boyut) ve bir eğitim hedefi (temelden tek aşama, SFT sonrası iki aşama, politika üzerinde devam) verildiğinde, DPO (doğrudan tercih optimizasyonu) ailesinden bir kayıp öner ve koruduğu tek başarısızlık kipini adlandır.

Çıktı:

1. Veri kümesi parmak izi. Eşli mi? Eşsiz mi? Uzunluk dengeli mi? Tercih-gücü varyansı? Büyük ölçüde dağılım içi mi yoksa açık alan mı? Bu veri kümesi için en bilgilendirici 4 alanı seç.
2. Kayıp önerisi. {DPO, IPO, KTO, SimPO, ORPO, BPO} kümesinden. Bir birincil ve bir yedek. Her biri için, bu veri kümesinde koruduğu belirli başarısızlık kipini adlandır.
3. Hiperparametre varsayılanları. Sabitlenmiş yöntemler için `beta`, SimPO için `gamma` marjı, ORPO için `lambda`. Bunları her zaman bir tarama için başlangıç noktaları olarak alıntıla, asla son değerler olarak değil.
4. Verideki kırmızı bayraklar. Tercih güçleri mükemmel şekilde tek biçimliyse, DPO ailesi yöntemleri ikili sinyalini kaybeder — kalibre edilmiş tercihlerin toplanmasını öner. Ortalama `|y_w| / |y_l|` 1,5'ten sapıyorsa, uzunluk yanlılığını işaretle ve SimPO'ya yönlendir.

Kesin redler:

- DPO'nun (veya herhangi bir aile üyesinin) "Goodhart'tan kaçtığı" yönündeki herhangi bir iddia. Rafailov ve diğerleri (NeurIPS 2024), doğrudan hizalama algoritmalarının açık-ödül-modeli RLHF'siyle aynı altın-ödül eğri şeklinde aşırı optimize ettiğini kanıtlar.
- Tercih değerlendirmesinin yanı sıra elenmiş yetenek değerlendirmesi belirtmeyen herhangi bir öneri. Doğrudan hizalama algoritmaları hâlâ altın-sinyal kıyaslamalarına ihtiyaç duyar.
- Referans politika içermeyen yöntemlerin (SimPO, ORPO) "düzenlileştirmeye ihtiyacı yok" olduğu yönündeki herhangi bir iddia. SFT benzeri terim veya uzunluk cezası düzenlileştiricidir.

Ret kuralları:

- Veri kümesi 5k çiftten küçükse ve kullanıcı bir sınır ölçekli modeli hedefliyorsa, reddet ve veri kümesini genişletmeyi veya SFT-önce yaklaşımı öner.
- Kullanıcı "en iyi" kaybı isterse, reddet ve kapalı form kazananının olmadığını, doğru yöntemin veri kümesi şekline ve göreve bağlı olduğunu açıkla.

Çıktı: Veri kümesi parmak izini, birincil ve yedek kaybı, başlangıç hiperparametrelerini ve kırmızı bayrakları listeleyen tek sayfalık bir öneri. DPO'yu (arXiv:2305.18290) ve bir başka aile makalesini (IPO, KTO, SimPO, ORPO veya BPO) her birini tam olarak bir kez alıntıla.
