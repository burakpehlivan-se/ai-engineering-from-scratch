# Otonom Kodlama Agentı Peyzajı (2026)

> SWE-bench Verified üç yıldan kısa sürede %4'den %80,9'ye çıktı. Aynı Claude Sonnet 4.5, SWE-agent v1'de %43,2 ve Cline otonom modunda %59,8 puan aldı — modelin etrafındaki iskelet (scaffolding) artık modelin kendisi kadar önemli. OpenHands (eski adıyla OpenDevin), en aktif MIT-licensed platformdur ve CodeAct döngüsü JSON araç çağrıları (tool calls) yerine sandbox'ta doğrudan Python eylemleri çalıştırır. Başlık sayıları bir metodolojik sorunu gizler: SWE-bench Verified'ın 500 görevinden 161'i yalnızca 1-2 satırlık bir değişiklik gerektirir ve SWE-bench Pro (10+ satır görevleri) aynı sınır modelleri için %23-59 arasında oturur.

**Tür:** Öğrenme
**Diller:** Python (stdlib, CodeAct vs JSON araç çağrısı karşılaştırması)
**Önkoşullar:** Faz 14 · 07 (Araç kullanımı), Faz 15 · 01 (Uzun vadeli agentlar)
**Süre:** ~45 dakika

## Sorun

"En iyi kodlama agentı hangisi" yanlış sorudur. Doğru soru: benim işime uyan bir görev dağıtımında, üretimde çalıştıracağım iskelet ile, ne kadar uçtan uca güvenilirlik elde ederim?

2022 ile 2026 arasında alan, iskeletin — getirme katmanı (retrieval), planlayıcı, sandbox, düzenle-doğrula döngüsü, geri bildirim biçiminin — taşıyıcı (load-bearing) olduğunu öğrendi. Claude Sonnet 4.5, SWE-agent v1'de SWE-bench Verified'da %43,2 puan aldı; aynı model Cline'ın otonom iskeletinde %59,8 puan aldı. 16,6 puanlık mutlak fark, aynı ağırlıklarla. Temel model bir bileşendir; döngü üründür.

Eşlik eden sorun, doygunluk (saturation) olan benchmark'ların gerilemeleri (regressions) gizlemesidir. SWE-bench Verified doygunluğa yakındır ve kolay görev kuyruğu (161/500 görev ≤2 satır) üst puanları yukarı çeker. Gerçek dünya kalitesi, SWE-bench Pro (10+ satır değişiklikler) gibi dağıtımlarda daha iyi ölçülür; aynı liderler hâlâ %23-59 arasında oturur.

## Kavram

### SWE-bench, bir paragrafta

SWE-bench (Jimenez ve ark.), ground-truth yamalara sahip gerçek GitHub sorunlarını alır ve bir agent'tan test paketini geçiren bir yama üretmesini ister. SWE-bench Verified (OpenAI, 2024), belirsiz ve bozuk görevlerin kaldırılmış, insan tarafından düzenlenmiş 500 görevlik bir alt kümedir. SWE-bench Pro, daha zor olan halefidir — 10+ satırlık değişiklik gerektiren görevler; mevcut sınır agentları %23-59 arasında oturur.

### 2022 → 2026 eğrisi aslında ne gösteriyor

- **2022**: araştırma modelleri ham SWE-bench'de ~%4.
- **2024**: GPT-4 + Devin tarzı iskelet ~%14; SWE-agent ~%12.
- **2025**: Claude 3.5/3.7 Sonnet, Aider ve SWE-agent içinde %40-55 aralığına giriyor.
- **2026**: Claude Sonnet 4.5 ve sınır rakipleri SWE-bench Verified'da %70-80+'a ulaşıyor. Epoch AI'nin liderlik tablosu bunu canlı takip ediyor.

Eğim, üç birikimli kaynaktan geliyor: daha iyi temel modeller, daha iyi iskelet (CodeAct, reflection, verifier loops) ve daha iyi benchmark'lar (Verified'ın gürültüyü temizlemesi).

### CodeAct ve JSON araç çağrıları

OpenHands (All-Hands-AI, arXiv:2407.16741, eski adıyla OpenDevin), belirli bir mimari bahse girdi: modelin JSON araç çağrıları üretmesi ve bunu bir ana bilgisayarın (host) çözümleyip çalıştırması yerine, model Python kodu üretir ve Jupyter tarzı bir çekirdek (kernel) bunu sandbox'ta çalıştırır. Agent dosyalar üzerinde döngü yapabilir, araçları zincirleyebilir ve bir eylem içinde kendi istisnalarını (exceptions) yakalayabilir.

Takas:

- **JSON araç çağrıları**: her eylem bir tur; denetlenmesi kolay; sınırlı bileşimsellik (compositionality); her çağrı açık bir doğrulayıcıdan (validator) geçtiği için varsayılan olarak güvenli.
- **CodeAct**: bir eylem bütün bir program olabilir; bileşimsel; sertleştirilmiş bir sandbox gerektirir (OpenHands Docker izolasyonu kullanır); hata modları sandbox runtime'ın izin verdiği her şeyi kapsar.

Her iki mimari de production'da. CodeAct, açık platformlarda (OpenHands, smolagents) hakimdir. JSON araç çağrıları, sağlayıcının (provider) çalıştırıcıyı (executor) kontrol ettiği yönetilen hizmetlerde (Anthropic Managed Agents, OpenAI Assistants) hakim kalmaya devam ediyor.

### 2026 peyzajında iskeletler

| İskelet | Lisans | Çalıştırma modeli | Dikkat çekici özellik |
|---|---|---|---|
| OpenHands (OpenDevin) | MIT | Docker'da CodeAct | En aktif açık platform; olay akışı (event-stream) yeniden oynatılabilir |
| SWE-agent | MIT | Agent-Bilgisayar Arayüzü (ACI) | İlk uçtan uca SWE-bench iskeleti |
| Aider | Apache-2 | Yerel depoda diff ile düzenleme | Minimal iskelet, güçlü gerileme kararlılığı |
| Cline | Apache-2 | Araç politikasıyla VS Code agentı | Sonnet 4.5'te en yüksek puanlı açık iskelet |
| Devin (Cognition) | Tescilli | Yönetilen VM + planlayıcı | İlk "AI yazılım mühendisi" ürün kategorisi |
| Claude Code | Tescilli | İzin modları + rutinler | Ders 10 agent döngüsünü ayrıntılı olarak ele alır |

### Neden iskelet hakim

Bir kodlama çalışması, uzun vadeli bir yörüngedir (trajectory — Ders 1). Güvenilirlik adımlar boyunca birikir. İskeletin puan kazandığı üç yer:

1. **Getirme**: doğru dosyaları bulmak sessiz bir darboğazdır (bottleneck). SWE-agent'ın ACI'si, OpenHands'in dosya indeksi ve Aider'ın repo haritası bunu hedefler.
2. **Doğrulayıcı döngüsü (verifier loop)**: testleri çalıştırmak, yığın izlerini (stack traces) okumak ve yeniden denemek, SWE-bench'de 10+ puanlık bir farktır.
3. **Hata izolasyonu (failure containment)**: hatada geri alma yapan bir sandbox, birikimli hasarı önler. Aynı modelin doğrulayıcı döngüsüyle ve onsuz görünümü iki farklı ürün gibidir.

### Benchmark doygunluğu ve gerçek dağıtım

OpenHands yazarları ve Epoch AI ikisi de SWE-bench Verified'ın kolay bir kuyruğa sahip olduğunu belirtiyor: 500 görevden 161'i yalnızca 1-2 satırlık değişiklik gerektirir. Yüksek puanlar bu kuyruk tarafından kısmen sürdürülür. SWE-bench Pro, 10+ satırlık değişiklikleri kısıtlar ve sınır sistemler için bile %23-59 aralığında puanlar döndürür. Üretim dağıtımınız neredeyse kesinlikle Verified'dan daha çok Pro'ya yakındır.

Agent seçimindeki ima: kendi hata birikiminizden Pro benzeri bir alt küme çalıştırın. Önemli puan, gönderdiklerinizi temsil eden görevlerdeki puandır.

## Kullan

`code/main.py`, sabit bir mini görev dağıtımı üzerinde iki oyuncak agent iskeletini karşılaştırır:

1. Her turda bir eylem alan bir **JSON araç çağrısı** iskeleti.
2. Her eylemde küçük bir Python parçası üretebilen bir **CodeAct** iskeleti.

Her ikisi de "model" yerine bir stub (deterministik kurallar) kullanır, böylece karşılaştırma iskeleti model kalitesinden izole eder. Çıktı, CodeAct iskeletinin daha büyük bir eylem-başına patlama yarıçapı (blast radius) puanına karşılık aynı görev kümesinde daha az turda daha fazla görevi çözdüğünü gösterir.

## Üret

`outputs/skill-scaffold-audit.md`, benimsenmeden önce önerilen bir kodlama agentı iskeletini denetlemenize yardımcı olur: getirme kalitesi, doğrulayıcı varlığı, sandbox izolasyonu ve benchmark-dağıtım uyumu.

## Alıştırmalar

1. `code/main.py` dosyasını çalıştırın. Her iskelet aynı görev kümesinde kaç tur alıyor? Her birinin eylem-başına patlama yarıçapı nedir?

2. OpenHands makalesini okuyun (arXiv:2407.16741). Makale, CodeAct'in karmaşık görevlerde JSON araç çağrılarını geçtiğini savunuyor. Makalenin kabul ettiği bir hata modunu belirleyin ve bu modun üretimde ne zaman hakim olacağını bir cümleyle yazın.

3. Bug birikiminizden iki dosyada 10+ satırlık değişiklik gerektirecek bir görev seçin. Bir sınır modeli altında (a) JSON araç çağrılarıyla ve (b) CodeAct ile uçtan uca başarı olasılığını tahmin edin. Farkı gerekçelendirin.

4. SWE-bench Verified'da 161 tek dosyalık, 1-2 satır görev var. Bunları hariç tutan bir puan oluşturun. Liderlik tablosu nasıl değişir?

5. "SWE-bench Verified Tanıtımı"nı (OpenAI) okuyun. Belirsiz görevleri kaldırmak için kullanılan spesifik metodolojiyi açıklayın ve düzenlemenin kaçıracağı bir kategoriye ad verin.

## Anahtar Terimler

| Terim | Ne Söyleniyor | Aslında Ne Anlama Geliyor |
|---|---|---|
| SWE-bench | "Kodlama benchmark'ı" | Ground-truth yamalara ve test paketlerine sahip gerçek GitHub sorunları |
| SWE-bench Verified | "Temizlenmiş alt küme" | 500 insan tarafından düzenlenmiş görev, kolay kuyruk mevcut |
| SWE-bench Pro | "Daha zor alt küme" | 10+ satır değişiklik; sınır %23-59'da |
| CodeAct | "Kod-eylem olarak" | Agent Python üretir; Jupyter tarzı çekirdek sandbox'ta çalıştırır |
| JSON araç çağrısı (JSON tool call) | "Fonksiyon çağrısı" | Her eylem, çalıştırmadan önce doğrulanmış yapılandırılmış bir JSON yüküdür |
| İskelet (Scaffolding) | "Agent çerçevesi" | Temel modelin etrafındaki getirme + planlayıcı + çalıştırıcı + doğrulayıcı döngüsü |
| ACI (Agent-Bilgisayar Arayüzü) | "SWE-agent'ın biçimi" | İnsan kabukları (shells) için değil, LLM ergonomisi için tasarlanmış komut seti |
| Doğrulayıcı döngüsü (Verifier loop) | "Test-et ve yeniden-dene" | Testleri çalıştır, çıktıyı oku, yamayı revize et; model-dışı en büyük güvenilirlik kazancı |

## İleri Okuma

- [Jimenez ve ark. — SWE-bench](https://www.swebench.com/) — orijinal benchmark ve metodoloji.
- [OpenAI — SWE-bench Verified Tanıtımı](https://openai.com/index/introducing-swe-bench-verified/) — düzenlenmiş alt kümenin nasıl oluşturulduğu.
- [Wang ve ark. — OpenHands: An Open Platform for AI Software Developers](https://arxiv.org/abs/2407.16741) — CodeAct mimarisi ve olay akışı tasarımı.
- [Epoch AI — SWE-bench liderlik tablosu](https://epoch.ai/benchmarks) — canlı takip edilen puanlar.
- [Anthropic — Agent Otonomunu Ölçme](https://www.anthropic.com/research/measuring-agent-autonomy) — uzun vadeli kodlama agentı güvenilirliği çerçevesi.
