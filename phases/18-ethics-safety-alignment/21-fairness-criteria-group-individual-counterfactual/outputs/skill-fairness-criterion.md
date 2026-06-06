---
name: fairness-criterion
description: Bir adillik iddiasının hangi adillik kriterini çağırdığını belirle ve ilişkili varsayımları denetle
version: 1.0.0
phase: 18
lesson: 21
tags: [fairness, demographic-parity, equalized-odds, counterfactual-fairness, impossibility]
---

Bir adillik iddiası veya politikası verildiğinde, hangi kriterin çağrıldığını, iddianın hangi varsayımlara bağlı olduğunu ve imkansızlık teoremlerinin kalan kriterler için ne anlama geldiğini belirle.

Çıktı:

1. Kriter belirleme. İddiayı şu hedeflerden biri olarak etiketle: demografik eşitlik, eşitlenmiş odds, koşullu kullanım doğruluğu eşitliği, bireysel adillik, karşı-olgusal adillik. Belirsiz iddialar devam etmeden önce çözülmelidir.
2. Taban-oran denetimi. Dağıtımdaki grup başına taban oranları nedir? Eşit olmayan taban oranları altında, Chouldechova / KMR 2017 imkansızlığı geçerlidir: hiçbir model üç grup kriterini birden karşılamaz.
3. Nedensel-DAG bağımlılığı. İddia karşı-olgusal adillikse, nedensel DAG nedir? Karşı-olgusal adillik, ancak DAG kadar gerekçelendirilmiştir. DAG eksikliği iddiayı geçersiz kılar.
4. Benzerlik metriği. İddia bireysel adillikse, benzerlik metriği d nedir? Seçim göreve özgüdür ve istatistiksel değil, politik bir karardır.
5. Müdahale yasallığı. İddia karşı-olgusal muhakeme kullanıyorsa, korunan özellikler üzerinde müdahaleler var mı? Varsa, yasal sorunları atlatmak için geri-izleme karşı-olgusal durumlarını (arXiv:2401.13935) düşün.

Kesin redler:

- Kriter belirlemesi olmadan herhangi bir "adil" iddiası.
- Eşit olmayan taban oranları altında Chouldechova / KMR 2017'yi kabul etmeden "tüm adillik kriterleri karşılandı" iddiası.
- Yayınlanmış nedensel DAG olmadan herhangi bir karşı-olgusal adillik iddiası.

Ret kuralları:

- Kullanıcı hangi adillik kriterinin "doğru" olduğunu sorarsa, sıralamayı reddet ve bunun bir politika seçimi olduğunu açıkla.
- Kullanıcı modelin "adil" olup olmadığını sorarsa, ikili iddiayı reddet; adillik kritere göredir.

Çıktı: Yukarıdaki beş bölümü dolduran, uygulanabilirse imkansızlığı işaretleyen ve iddiadaki örtük politika seçimini adlandıran tek sayfalık bir denetim. Dwork ve diğerleri 2012, Kusner ve diğerleri 2017, Chouldechova 2017'yi uygun şekilde her birini bir kez alıntıla.
