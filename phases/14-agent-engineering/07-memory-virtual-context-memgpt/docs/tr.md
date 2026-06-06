# Hafıza: Sanal Bağlam ve MemGPT

> Bağlam pencereleri (context windows) sınırlıdır. Konuşmalar, belgeler ve araç izleri (traces) değildir. MemGPT (Packer ve diğerleri, 2023) bunu işletim sistemi sanal belleği (virtual memory) olarak çerçeveler: ana bağlam RAM'dir, harici depolama disk'tir, agent aralarında sayfa değiştirir (page in/out). Bu, 2026'daki her hafıza sisteminin devraldığı kalıptır.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 01 (Agent Döngüsü), Faz 14 · 06 (Araç Kullanımı)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- MemGPT'nin üzerine inşa ettiği OS benzetmesini açıklayın: ana bağlam = RAM, harici bağlam = disk, hafıza araçları = page in/out.
- Ana bağlam tamponu, harici aranabilir depo ve page in/out araçlarıyla stdlib'da iki katmanlı MemGPT kalıbını uygulayın.
- Agent'ın harici hafızayı sorgulamak veya değiştirmek için "kesme" (interrupt) nasıl verdiğini ve sonucun bir sonraki prompt'a nasıl eklendiğini açıklayın.
- MemGPT tasarım tercihlerinin Letta'ya (Ders 08) ve Mem0'a (Ders 09) nasıl taşındığını tanımlayın.

## Problem

Bağlam pencereleri hafızayı çözmeli gibi görünür. Çözmez. Production'da tekrar eden üç başarısızlık modu vardır:

1. **Taşma.** Çoklu tur konuşmaları, uzun belgeler veya araç çağrısı ağırlıklı trajectory'ler pencerenin dışına çıkar. Kesme noktasının ötesindeki her şey kaybolur.
2. **Seyreltme.** Pencere içinde bile, alakasız bağlamı doldurmak dikkati önemli olanın üzerine seyreltir. Frontier modeller uzun girdilerde hâlâ düşüş gösterir.
3. **Dayanıklılık.** Yeni bir oturum boş bir pencereyle başlar. Harici hafızası olmayan agent'lar oturumlar arası "şunu sormuştun..." diyemez.

Daha büyük pencereler yardımcı olur ancak bunu çözmez. Mem0'ın 2025 makalesi, 128k-pencere temellerinin hâlâ 4k-pencereli harici hafızalı bir agent'ın yakaladığı uzun vadeli olguları kaçırdığını ölçmüştür.

## Kavram

### MemGPT: OS benzetmesi

Packer ve diğerleri (arXiv:2310.08560, v2 Şubat 2024) bağlam yönetimini işletim sistemi sanal belleğiyle eşleştirir:

| OS kavramı | MemGPT kavramı | 2026 production karşılığı |
|------------|---------------|--------------------------|
| RAM | ana bağlam (prompt) | Anthropic/OpenAI bağlam penceresi |
| Disk | harici bağlam | vektör DB, KV, graf depo |
| Page fault | hafıza araç çağrısı | `memory.search`, `memory.read`, `memory.write` |
| OS çekirdeği | agent kontrol döngüsü | Hafıza araçlarıyla ReAct döngüsü |

Agent normal bir ReAct döngüsü çalıştırır. Ek bir araç sınıfı, verileri ana bağlam içine ve dışına sayfalamasını sağlar.

### İki katman

- **Ana bağlam.** Mevcut görevi tutan sabit boyutlu prompt. Modele her zaman görünür.
- **Harici bağlam.** Sınırsız, araçlarla aranabilir. İlgili olduğunda okunur, olgular ortaya çıktığında yazılır.

Orijinal makale, tasarım iki görevde değerlendirdi: 100k token'dan uzun belge analizi ve günler boyunca kalıcı hafızalı çoklu oturum sohbeti.

### Kesme (interrupt) kalıbı

MemGPT hafızayı-kesme olarak sunar: konuşma ortasında agent bir hafıza aracı çağırabilir, runtime çalıştırır ve sonuç bir sonraki asistan turuna yeni bir gözlem olarak eklenir. Konseptsel olarak, process'i bloke eden, byte'ları döndüren ve process'in devam ettiği bir Unix `read()` syscall'ı ile özdeştir.

Kanonik hafıza aracı yüzeyi:

- `core_memory_append(section, text)` — prompt'un kalıcı bir bölümüne yaz.
- `core_memory_replace(section, old, new)` — kalıcı bir bölümü düzenle.
- `archival_memory_insert(text)` — aranabilir harici depoya yaz.
- `archival_memory_search(query, top_k)` — harici depodan al.
- `conversation_search(query)` — önceki turları tara.

### MemGPT'nin bittiği ve Letta'nın başladığı yer

Eylül 2024'te MemGPT Letta oldu. Araştırma deposu (`cpacker/MemGPT`) devam ediyor; Letta tasarımı genişletir:

- İki katman yerine üç katman (core, recall, archival — Ders 08).
- `send_message`/heartbeat kalıbının yerine native reasoning (Ders 08).
- Asenkron hafıza çalışması yapan sleep-time agent'ları (Ders 08).

MemGPT makalesi production sistemler Letta, Mem0 veya özel iki katmanlı depo kullansa bile 2026 temelidir.

### Bu kalıp nerede yanlış gider

- **Hafıza çürümesi (memory rot).** Yazma okumadan daha hızlı birikir; arama eski olgulara boğulur. Çözüm: periyodik birleştirme (Letta sleep-time), açık geçersiz kılma (Mem0 çatışma dedektörü).
- **Hafıza zehirlenmesi (memory poisoning).** Harici hafıza alınan metindir. Saldırganın kontrol ettiği bir içerik bir hafıza notuna düşerse, agent onu bir sonraki oturumda yeniden yutar. Bu, Greshake ve diğerlerinin (Ders 27) zaman içinde yeniden ifadesidir.
- **Alıntı kaybı.** Agent "kullanıcı benden X'i göndermemi istedi" diye hatırlar ancak hangi turda olduğunu alıntılayamaz. Her arşiv yazmasıyla kaynak referansları (session ID, turn ID) saklayın.

## İnşa Et

`code/main.py` MemGPT'nin iki katmanlı kalıbını stdlib'da uygular:

- `MainContext` — `core` dict ve `messages` listesiyle sabit boyutlu prompt tamponu; üst aşıldığında en eski mesajları otomatik sıkıştırır.
- `ArchivalStore` — (id, text, tags, session, turn) kayıtlarının bellek içi BM25 benzeri deposu (token-overlap puanlama).
- MemGPT yüzeyine eşlenen beş hafıza aracı.
- Arşivini olgularla dolduran ve `archival_memory_search` kullanarak bir soruyu cevaplayan betiklenmiş bir agent.

Çalıştırın:

```bash
python3 code/main.py
```

Trace, agent'ın üç olgu yazmasını, ana bağlamı üst sınıra doldurmasını (kovulmayı zorunlu kılan) ve sonra takip sorusunu arşivden alarak cevaplamasını gösterir — gerçek bir LLM olmadan MemGPT iş akışını yeniden üretir.

## Kullan

Bugünkü her production hafıza sistemi bir MemGPT varyantıdır:

- **Letta** (Ders 08) — üç katman, native reasoning, sleep-time compute.
- **Mem0** (Ders 09) — puanlama katmanıyla birleştirilmiş vektör + KV + graf.
- **OpenAI Assistants / Responses** — thread'ler ve dosyalar aracılığıyla yönetilen hafıza.
- **Claude Agent SDK** — yetenekler ve oturum deposu aracılığıyla uzun vadeli hafıza.

Operasyonel şekle göre (self-hosted, yönetilen, framework-entegre) seçin, temel kalıba göre değil — temel kalıp MemGPT'dir.

## Teslim Et

`outputs/skill-virtual-memory.md`, herhangi bir hedef runtime için doğru iki katmanlı hafıza iskeleti (ana + arşiv + araç yüzeyi) üreten, kovma politikası ve alıntı alanları bağlı kullanılabilir bir yetenektir.

## Alıştırmalar

1. Token cinsinden ölçülen `max_main_context_tokens` üst sınırı ekleyin (`len(text.split())` * 1.3 ile yaklaşık). Üst aşıldığında en eski mesajları bir özetle sıkıştırın. Sıkıştırıcıyla ve olmadan davranışı karşılaştırın.
2. Arşiv deposu üzerinde düzgün BM25 uygulayın (terim frekansı, terim ters belge frekansı). Token-overlap temeline karşı toy bir olgu kümesinde recall@10 ölçün.
3. Arşiv eklemelerine `citation` alanları (session_id, turn_id, source_url) ekleyin. Agent'ın her retrieved cevapta kaynakları alıntılamasını sağlayın.
4. Hafıza zehirlenmesini simüle edin: "gelecek kullanıcı talimatlarını görmezden gel" diyen bir arşiv kaydı ekleyin. Retrieve'larda yönerge şekilli metinleri tarayan ve bunları güvenilmez olarak işaretleyen bir koruma ekleyin.
5. Uygulamayı MemGPT araştırma deposunun core-memory JSON şemasını (cpacker/MemGPT) kullanacak şekilde taşıyın. Düz string'lerden bölümlü tipe geçtiğinizde ne değişir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Virtual context | "Sınırsız hafıza" | Ana (prompt) + harici (aranabilir) katmanlarla page in/out |
| Main context | "Çalışma hafızası" | Prompt — sabit boyutlu, her zaman görünür |
| Archival memory | "Uzun vadeli depo" | Harici aranabilir kalıcılık, talep üzerine alınır |
| Core memory | "Kalıcı prompt bölümü" | Ana bağlam içine sabitlenmiş adlandırılmış bölümler |
| Memory tool | "Hafıza API'si" | Agent'ın harici hafızayı okumak/yazmak için verdiği araç çağrısı |
| Interrupt | "Hafıza sayfa hatası" | Agent duraklar, runtime getirir, sonuç bir sonraki tura eklenir |
| Memory rot | "Eski olgular" | Eski yazmalar arama işlemini boğar; birleştirmeyle çözülür |
| Memory poisoning | "Enjekte edilmiş kalıcı not" | Saldırgan içeriği hafıza olarak saklanır, hatırlamada yeniden yutulur |

## İleri Okuma

- [Packer ve diğerleri, MemGPT (arXiv:2310.08560)](https://arxiv.org/abs/2310.08560) — OS ilhamlı sanal bağlam makalesi
- [Letta, Memory Blocks blog](https://www.letta.com/blog/memory-blocks) — üç katmanlı evrim
- [Anthropic, Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — bağlamı bütçe olarak ele alma
- [Chhikara ve diğerleri, Mem0 (arXiv:2504.19413)](https://arxiv.org/abs/2504.19413) — bu kalıp üzerinde hibrit production hafızası
