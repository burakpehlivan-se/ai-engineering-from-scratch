# Durdurma Anahtarları, Devre Kesiciler ve Kanarya Token'ları

> Bir durdurma anahtarı (kill switch), agent'ın düzenleme yüzeyinin dışında tutulan bir boole değerdir — bir Redis anahtarı, bir özellik bayrağı (feature flag), imzalı bir yapılandırma — agent'ı tamamen devre dışı bırakır. Bir devre kesici (circuit breaker) daha ince tanelidir: belirli bir kalıbı tetikler (beş özdeş araç çağrısı art arda), sorunlu yolu duraklatır ve bir insana yükseltir. Bir kanarya token'ı (canary token) klasik aldatmacadan (deception) türetilmiştir: bir agent'ın meşru olarak dokunmaması gereken sahte bir kimlik bilgisi veya honeypot kaydı; erişim tetiklenir tetiklenmez bir uyarı verir. eBPF tabanlı veri yolları (ör. Cilium), karantinaya alınmış bir pod'un çıkış trafiğini (egress) çekirdek katmanında adli bir honeypota yeniden yönlendirebilir; yayınlanmış Cilium karşılaştırmaları, yük altında milisaniyenin altında P99 veri yolu gecikmesi raporlar (yayılma bütçeniz, bir politika güncellemesinin düğüme nasıl ulaştığına bağlıdır, veri yolunun kendisine değil). Hareketli bir temele (baseline) uyum sağlayan istatistiksel algılayıcılar (EWMA, CUSUM) sapmayı sessizce kabul eder — bunları bükülmeyen anayasal sınırlarla katmanlandırın.

**Tür:** Öğrenme
**Diller:** Python (stdlib, üç algılayıcı simülatörü: durdurma anahtarı, devre kesici, kanarya)
**Önkoşullar:** Faz 15 · 13 (Maliyet denetçileri), Faz 15 · 10 (İzin modları)
**Süre:** ~60 dakika

## Sorun

Maliyet denetçileri (Ders 13), agent'ın ne kadar harcayabileceğini sınırlar. Bütçe içinde ne yapabileceğini sınırlamazlar. 50$ hız sınırına sahip bir agent hala bir sırrı dışarı sızdırmamalı (exfiltrate), yanlış bir gönderiyi yayımlamamalı veya bir kaynağı silmemeli — pahalı eylem genellikle token açısından ucuz olandır.

Bu ders, maliyet katmanının yanında yer alan üç algılayıcıyı kapsar:

1. **Durdurma anahtarı:** agent'ın erişiminin dışında tutulan boole düğme.
2. **Devre kesici:** belirli bir kalıp algılayan eylem deseni dedektörü; belirli bir yolu duraklatır.
3. **Kanarya token'ı:** meşru olarak dokunmaması gereken bir agent'ın kendini ele vermesine neden olan yem.

Üçü de LLM öncesi mühendisliktir. Klasik aldatmaca, hız sınırı devreleri ve özellik bayrağı öldürmeleri otonom agent'lardan önce gelir. Yeni olan saldırı yüzeyidir: agent'lar güvenilmeyen içerik okur (Ders 11), kendi belleklerini düzenler ve birçok güvenli görünen eylemi güvensiz bir bileşime sokabilirler. Burada adlandırılan algılayıcılar çalışır çünkü agent'ın kendi beyanına güvenmezler.

## Kavram

### Durdurma anahtarları

Bir durdurma anahtarı, agent'ın okuyabildiği ancak yazamadığı bir booledir. Uygulama seçenekleri:

- **Yönetilen serviste özellik bayrağı.** LaunchDarkly, Statsig, Unleash. Güncellemeler saniyeler içinde yayılır.
- **Agent'ın sorguladığı Redis anahtarı.** Basit; agent sürecinin her turda kontrol etmesini gerektirir.
- **Nesne deposunda imzalı yapılandırma.** Agent önyüklemede bir imza doğrular; imzasız durumları reddeder.
- **İşletim sistemi düzeyinde sinyal veya konteyner yaşam döngüsü öldürme.** Docker `kill`, Kubernetes `kubectl delete pod`, systemd stop.

Doğru bir durdurma anahtarının sahip olduğu özellikler:

- Agent onu `off` olarak ayarlayamaz. (Agent'ın kimlik bilgilerinin yazamadığı bir sistemde yaşar.)
- Her sonuç eyleminde kontrol edilir, sadece başlangıçta değil.
- Kapalıyken agent,agentın erişebileceği sistemlere loglama da dahil olmak üzere dışarıdan gözlemlenebilir hiçbir şey yapmaz.
- Yeniden etkinleştirme otomatik bir zaman aşımı değil, açıkça insan eylemidir.

### Devre kesiciler

Bir devre kesici tüm agent'ı değil, belirli bir kalıbı duraklatır. Klasik biçim (2007 Nygard kitabından, hala güncel):

- **Kapalı (Closed):** eyleme izin var.
- **Açık (Open):** eylem engelleniyor.
- **Yarı açık (Half-open):** soğuma süresinden sonra 1–3 deneme girişimine izin verilir (varsayılan 1); başarılı olursa devre kapanır, kalan herhangi bir başarısızlık tekrar açar.

Agent ilgili tetikleyiciler:

- Beş özdeş araç çağrısı art arda (tekrarlayan döngü).
- Aynı araçta farklı girdilerle beş ardışık başarısızlık (sistemik hata).
- Araç çağrısı oranının eşik üzerinde olması (Ders 13 hızı).
- Güven dışı bir içerik okumasından sonra belirli bir aracın çağrılması (ör. `file.delete`) (Ders 11).

### Kanarya token'ları

Kanarya token'ları (honeytoken olarak da adlandırılır), agent'ın asla dokunmaması gereken girdilerdir. Eryiş alarmdır.

Agent'lar için örnekler:

- Ortamda gerçek ayrıcalığı olmayan sahte bir `AWS_SECRET_ACCESS_KEY`. Dışarı sızdırma denemeleri anında tanımlanabilir.
- Bilinen bir sentinel değeri ile işaretlenmiş sahte bir veritabanı kaydı. Bu kaydın her okuması veya güncellenmesi bir uyarı tetikler.
- Çalışma alanında sahte bir dosya. Bu dosyanın okunması veya düzenlenmesi şüphelidir.
- Oturum başında enjekte edilen sahte bir bellek girdisi. Sonraki bir çıktıda ortaya çıkarsa, bellek sızdırılmıştır.

Kanarya tasarımı iş akışına özgüdür. Agent'ın meşru olarak dokunma nedeni olan bir kanarya gürültüdür.

### Neden istatistiksel ve sert sınırları katmanlandırırsınız

İstatistiksel algılayıcılar (EWMA, CUSUM, araç çağrısı oranlarında z-puanı), hareketli bir temele uyum sağlar. Bu meşru sapma için bir özellik, düşmanca (adversarial) sapma için bir hatadır. Sabırlı bir saldırgan temeli öylesine yavaş kaydırabilir ki hiçbir uyarı tetiklenmez.

Sert anayasal sınırlar (Ders 17) bükülmez. "Asla `secrets@` e-posta gönderme" gibi bir anayasal kural, daha basit, denetlenebilir ve yavaş sapmayla kandırılamazdır. Katmanlı kalıp: istatistiksel algılayıcılar çoğu gürültüyü yakalar, sert sınırlar algılayıcıdan geçip gelen saldırıyı yakalar.

### eBPF veri yolu yönlendirmesiyle karantina

Cilium'un eBPF tabanlı ağ politikası, karantinaya alınmış bir pod'un çıkış trafiğini çekirdek katmanında adli bir honeypota yeniden yönlendirebilir. Cilium'un herkese açık karşılaştırmaları TCP_RR'de milisaniyenin altında P99 veri yolu gecikmesi raporlar; *tetikleme* bütçeniz bir politika güncellemesinin kontrol düzleminizden düğüme nasıl yayıldığına bağlıdır (Kubernetes'ta operatör önceden yüklüyse birkaç yüz milisaniye gerçekçidir; kuyruk gecikmesi küp boyutu ve uzlaşma ritmine bağlıdır). Bu size iki şey sağlar: agent gerçek hiçbir şeyi sızdırmaz ve honeypot içindeki davranışı tamamen gözlemlenir. Kanarya token'ıyla aynı kalıp, farklı katman: agent, konteyner içindeyken ne yapmaya çalıştığını niyetini açığa vurur.

### Hiçbir algılayıcının yakalayamadığı şeyler

- **İzin verilen ilkel elementlerden oluşan anlamsal saldırılar.** Her bireysel eylem her algılayıcıdan geçer; sorun bileşimedir. Bu, Ders 10'daki Otomatik Mod bileşik başarısızlığıdır.
- **Algılayıcıyı yükün bir parçası olarak içeren saldırılar.** Bir agent "harekete geçmeden önce kanaryayı devre dışı bırak" diyen bir sayfa okursa ve yeteneği varsa, algılayıcı tehlikeye girer. Kanarya token'ları agent'ın değiştiremeyeceği sistemlerde olmalıdır.

## Kullan

`code/main.py`, üç algılayıcıdan kısa bir agent yörüngesini simüle eder. Harici bir sözlükte tutulan bir durdurma anahtarı; beş özdeş araç çağrısında tetiklenen bir devre kesici; okuması bir uyarı tetikleyen sahte dosya kanaryası. Sentetik bir yörünge besler: meşru eylemler, tekrarlayan döngü, kanarya sondağı ve agent'ın eylemlerinin durdurulduğu bir durdurma anahtarı tetikleme senaryosu.

## Üret

`outputs/skill-tripwire-design.md`, önerilen bir agent dağıtıımı için algılayıcı yığınını inceler ve boşlukları işaretler (eksik durdurma anahtarı, eksik kanarya, devre kesici eşiği çok gevşek).

## Alıştırmalar

1. `code/main.py` çalıştırın. Devre kesicinin 5. turda (beşinci özdeş çağrı) ve kanaryanın 9. turda (sahte anahtar okuması) tetiklendiğini doğrulayın.

2. İstatistiksel bir algılayıcı ekleyin: araç çağrısı oranında EWMA z-puanı. Yavaşça sapma gösteren bir yörünge besleyin ve algılayıcının asla tetiklenmediğini gösterin. Şimdi bir sert sınır ekleyin (10 dakikada en fazla 50 araç çağrısı) ve aynı yörüngede sert sınırın tetiklendiğini gösterin.

3. Bir tarayıcı agent'ı (Ders 11) için kanarya token kümesi tasarlayın. En az üç kanarya ve her birinin neyi tespit edeceğini listeleyin.

4. Cilium ağ politikası belgelerini okuyun. Bir çıkış yönlendirmeli karantina akışını somut olarak açıklayın: hangi politika seçicisi, hangi pod, hangi çıkış yeniden yazma, hangi uyarı. "Karantinaya almaya karar vermekten" "ilk yeniden yönlendirilmiş pakete" kadar duvar saati gecikmesini ne yönetir?

5. Durdurma anahtarlı bir agent için yeniden etkinleştirme prosedürü tanımlayın. Kim yeniden etkinleştirebilir? Ne belgelenmelidir? Yeniden etkinleştirmeden önce agent'ın neyi değişmelidir?

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| Kill switch (Durdurma anahtarı) | "Kapatma düğmesi" | Agent'ın düzenleme yüzeyinin dışında boole; her sonuç eyleminde kontrol edilir |
| Circuit breaker (Devre kesici) | "Kalıp duraklatma" | Tekrar, başarısızlık oranı veya hız sınırı üzerinde eyleme özgü tetikleme |
| Canary token (Kanarya token'ı) | "Honeytoken" | Agent'ın meşru olarak dokunmaması gereken yem; erişim uyarı tetikler |
| Honeypot | "Adli sandbox" | Yeniden yönlendirilmiş trafik/çalışma alanı; karantinaya alınmış agent burada gözlemlenir |
| EWMA | "Hareketli ortalama" | Üstel ağırlıklı; sapmaya uyum sağlar (özellik + hata) |
| CUSUM | "Kümülatif toplam" | Temelden sürekli kaymayı algılar |
| Hard limit (Sert sınır) | "Anayasal kural" | Uyum sağlamaz; geçmişten bağımsız sabit |
| Constitutional limit (Anayasal sınır) | "Her zaman doğru kural" | Ders 17'nin anayasasına bağlı; agent tarafından düzenlenemez |

## İleri Okuma

- [Anthropic — Pratikte agent otonomunu ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — otonom agent'lar için durdurma anahtarı ve devre kesici çerçevesi.
- [Microsoft Agent Framework — HITL ve gözetim](https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop) — üretim yönetimi kalıpları.
- [OWASP LLM / Agentic Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — tespit ve yanıt gereksinimleri.
- [Cilium — Ağ politikası ve eBPF](https://docs.cilium.io/en/stable/security/network/) — düzeyinde çıkış yönlendirme ve adli honeypot kalıpları.
- [Anthropic — Claude'un Anayasası (Ocak 2026)](https://www.anthropic.com/news/claudes-constitution) — "anayasal sınırlar" olarak kodlanmış yasaklar.
