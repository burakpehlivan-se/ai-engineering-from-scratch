---
name: compliance-gap
description: İzlenen / izlenmeyen uyum boşluğu aracılığıyla bir güvenlik raporunun hizalama faking'ini (alignment faking) tespit edip edemeyeceğini değerlendir
version: 1.0.0
phase: 18
lesson: 9
tags: [alignment-faking, compliance-gap, anthropic, safety-evaluation]
---

Bir güvenlik değerlendirme raporu verildiğinde, Greenblatt ve diğerleri 2024 uyum-boşluğu çerçevesini kullanarak hizalama faking'ini gerçek uyumluluktan ayırt edip edemeyeceğini değerlendir.

Çıktı:

1. Koşul bölünmesi. Değerlendirme hem izlenen (eğitimle ilgili) hem de izlenmeyen (eğitim dışı) koşulu çalıştırıyor mu? İkisi olmadan hizalama faking'i görünmezdir.
2. Uyum-boşluğu ölçümü. Boşluğu (izlenen - izlenmeyen) uyum oranı olarak raporla. İşaret ve büyüklüğü yorumla: pozitif boşluk = faking-şeklinde davranış; negatif boşluk = gözlemlendiğinde aşırı reddetme.
3. Sözel iz vs davranış kontrolü. Değerlendirme, modelin karalama-defteri muhakemesine mi yoksa eylemin kendisine mi dayanıyor? Anthropic 2025'e göre, sözel izi hedefleyen hafifletmeler onu davranışı kaldırmadan kaldırabilir.
4. Operasyonelleştirme denetimi. İzleme koşulu sistem istemiyle mi, sentetik ince ayarla mı, yoksa doğal dağıtım bağlamıyla mı oluşturuldu? Sistem istemi bağımlılığı iddiayı zayıflatır; sentetik ince ayar replikasyonları güçlendirir.
5. Artık-teşvik kontrolü. Uygulanan herhangi bir hafifletme sonrasında, teşvik yapısı hâlâ mevcut mu (model yine de faking'den fayda görür mü, isterse)? Teşvik kalıcılığı, davranışın dağılım kayması altında geri dönebileceği anlamına gelir.

Kesin redler:

- Yalnızca izlenmeyen değerlendirmeye dayanan "hizalama faking'i yok" iddiası.
- "Karalama-defteri muhakemesi artık faking'i sözel olarak ifade etmiyor" ifadesinin davranışın sona erdiğini ima etmesi.
- HHH-eğitimli modellerin hizalamayı faking etmediği yönündeki herhangi bir iddia — Greenblatt ve diğerleri 2024, HHH eğitiminin gerekli koşul olduğunu, yeterli bir savunma olmadığını ortaya koyar.

Ret kuralları:

- Kullanıcı "modelim hizalamayı faking ediyor mu" diye sorarsa, uyum-boşluğu verisi olmadan ikili yanıt vermeyi reddet.
- Kullanıcı yalnızca sözel izi hedefleyen bir iyileştirme isterse (örn. "karalama-defterini eylemle eşleşecek şekilde eğit"), reddet ve sadık-CoT başarısızlık kipini (2025 takip çalışması) açıkla.

Çıktı: Her iki koşuldaki uyumu, boşluğu, sözel-iz-vs-davranış ayrımını ve operasyonelleştirme gücünü raporlayan tek sayfalık bir değerlendirme. Her eksik öğeyi işaretle. Çerçeve kaynağı olarak Greenblatt ve diğerlerini (arXiv:2412.14093) bir kez alıntıla.
