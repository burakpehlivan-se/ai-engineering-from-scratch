# Yetenek Kütüphaneleri ve Ömür Boyu Öğrenme (Voyager)

> Voyager (Wang ve diğerleri, TMLR 2024) çalıştırılabilir kodu bir yetenek (skill) olarak ele alır. Yetenekler adlandırılabilir, alınabilir, birleştirilebilir ve ortam geri bildirimiyle iyileştirilebilir. Bu, Claude Agent SDK yetenekleri, skillkit ve 2026 yetenek-kütüphanesi kalıbının referans mimarisidir.

**Tür:** İnşa Et
**Diller:** Python (stdlib)
**Ön Koşullar:** Faz 14 · 07 (MemGPT), Faz 14 · 08 (Letta Blokları)
**Süre:** ~75 dakika

## Öğrenme Hedefleri

- Voyager'ın üç bileşenini — otomatik müfredat, yetenek kütüphanesi, yinelemeli promptlama — adlandırın ve her birinin rolünü açıklayın.
- Voyager'ın eylem alanını (action space) neden komutlar yerine kod yaptığını açıklayın.
- Kayıt, alma, birleştirme ve başarısızlık odaklı iyileştirme ile stdlib bir yetenek kütüphanesi uygulayın.
- Voyager kalıbını 2026 Claude Agent SDK yetenekleri ve skillkit ekosistemiyle eşleştirin.

## Problem

Her oturumda her yeteneği sıfırdan yeniden oluşturan agent'lar üç şeyi yanlış yapar:

1. **Token israfı.** Her görev aynı akıl yürütmeyi yeniden ister.
2. **İlerleme kaybı.** A oturumunda öğrenilen bir düzeltme B oturumuna aktarılmaz.
3. **Uzun vadeli bileşimde başarısızlık.** Karmaşık görevler yetenek hiyerarşileri gerektirir; tek seferlik promptlar bunları açıklayamaz.

Voyager'ın cevabı: her yeniden kullanılabilir yeteneği bir kütüphanede saklanmış, benzerlikle alınabilir, diğer yeteneklerle birleştirilebilir ve çalıştırma geri bildirimiyle iyileştirilebilir adlandırılmış bir kod parçası olarak ele almak.

## Kavram

### Üç bileşen

Voyager (arXiv:2305.16291) bir agent'ı etrafında yapılandırır:

1. **Otomatik müfredat.** Merak tarafından驱动 bir önerici, agent'ın mevcut yetenek kümesi ve ortam durumuna göre bir sonraki görevi seçer. Keşif aşağıdan yukarıya doğrudur.
2. **Yetenek kütüphanesi.** Her yetenek çalıştırılabilir koddur. Yeni yetenekler bir görev başarılı olduğunda eklenir. Yetenekler sorgudan-açıklamaya benzerlikle alınır.
3. **Yinelemeli promptlama mekanizması.** Başarısızlıkta, agent çalıştırma hataları, ortam geri bildirimi ve öz-doğrulama çıktısı alır, sonra yeteneği iyileştirir.

Minecraft değerlendirmesi (Wang ve diğerleri, 2024): temellere göre 3.3x daha fazla benzersiz eşya, 8.5x daha hızlı taş aletler, 6.4x daha hızlı demir aletler, 2.3x daha uzun harita geçişi. Sayılar Minecraft'a özgüdür ancak kalıp aktarılabilir.

### Eylem alanı = kod

Çoğu agent temel komutlar üretir. Voyager JavaScript fonksiyonları üretir. Bir yetenek şöyledir:

```text
async function craftIronPickaxe(bot) {
  await mineIron(bot, 3);
  await mineStick(bot, 2);
  await placeCraftingTable(bot);
  await craft(bot, 'iron_pickaxe');
}
```

Alt yeteneklerden birleştirilir. Açıklama ve embedding ile anahtarlanarak saklanır. Prompt olarak değil program olarak alınır.

Bu, 2026 Claude Agent SDK yeteneğidir: agent'ın talep üzerine yüklediği adlandırılmış, alınabilir bir kod parçası artı talimatlar.

### Yetenek arama

Yeni görev "bir elmas kazma yap". Agent:

1. Görev açıklamasını embed eder.
2. En benzer yetenekler için yetenek kütüphanesini sorgular.
3. `craftIronPickaxe`, `mineDiamond`, `placeCraftingTable` vb. alır.
4. Alınan temel unsurlardan + yeni mantıktan yeni yeteneği birleştirir.

Bu, MCP kaynaklarının (Faz 13) ve Agent SDK yeteneklerinin uyguladığı kalıptır: mevcut görevle sınırlı bilgi/kod yüzeyi üzerinde arama.

### Yinelemeli iyileştirme

Voyager'ın geri bildirim döngüsü:

1. Agent bir yetenek yazar.
2. Yetenek ortamda çalıştırılır.
3. Üç sinyalden biri döner: `success`, `error` (stack trace ile), `self-verification failure`.
4. Agent sinyali bağlam olarak kullanarak yeteneği yeniden yazar.
5. Başarıya veya maks tur kadar döngü.

Bu, çevresel temelli doğrulamayla kod üreticine uygulanmış Self-Refine'dır (Ders 05). CRITIC (Ders 05), harici araçların doğrulayıcı olarak kullanıldığı aynı kalıptır.

### Müfredat ve keşif

Voyager'ın müfredat modülü "gölün yakınında bir sığınak inşa et" gibi görevler önerir. Önerici, ortam durumu + yetenek envanterini kullanarak mevcut yeteneğin biraz üzerinde bir görev seçer — keşif tatlı noktası.

Production agent'ları için bu "eksik olan ne" operatörüne dönüşür: mevcut yetenek kütüphanesi ve bir alan verildiğinde, henüz hangi yetenekleri kapsamıyoruz? Ekipler bunu genellikle müfredat incelemesi olarak manuel uygular.

### Bu kalıp nerede yanlış gider

- **Yetenek kütüphanesi çürümesi.** Aynı yetenek 10 kez biraz farklı açıklamalarla eklendi. Yazmada ayıklama ekleyin; arama yalnızca birini döndürür.
- **Birleştirilmiş yetenek kayması.** Üst yetenek iyileştirilmiş bir çocuğa bağımlıdır. Yetenekleri versiyonlayın; v1'e sabitlenmiş bir üst yetenek v3'ü sihirli olarak almaz.
- **Arama kalitesi.** Yetenek açıklamaları üzerinde vektör araması几百'den fazla büyümeye başladığında düşer. Etiket filtreleri ve katı kısıtlamalarla ("yalnızca `category=tooling` olan yetenekler") tamamlayın.

## İnşa Et

`code/main.py` stdlib bir yetenek kütüphanesi uygular:

- `Skill` — name, description, code (string olarak), version, tags, dependencies.
- `SkillLibrary` — kayıt, arama (token overlap), birleştirme (deps topolojik sıralaması) ve iyileştirme (güncellemeyle versiyon artırma).
- Üç temel yetenek kaydeden, dördünü birleştiren, bir başarısızlığa uğrayan ve iyileştiren betiklenmiş bir agent.

Çalıştırın:

```bash
python3 code/main.py
```

Trace kütüphane yazmalarını, aramayı, birleştirmeyi, başarısız bir çalıştırmayı ve v2 iyileştirmesini gösterir — Voyager'ın döngüsü uçtan uca.

## Kullan

- **Claude Agent SDK yetenekleri** (Anthropic) — 2026 referansı: her yetenek bir açıklama, kod ve talimatlar içerir; agent oturumu sırasında talep üzerine yüklenir.
- **skillkit** (npm: skillkit) — 32+ AI kodlama agent'ı için çapraz-agent yetenek yönetimi.
- **Özel yetenek kütüphaneleri** — alan-specific (veri agent'ları için SQL yetenekleri, infra agent'ları için Terraform yetenekleri). Voyager kalıbı aşağıya ölçeklenir.
- **OpenAI Agents SDK `tools`** — alt uçta; her araç hafif bir yetenektir.

## Teslim Et

`outputs/skill-skill-library.md`, herhangi bir hedef runtime için kayıt, arama, versiyonlama ve iyileştirme bağlı Voyager şeklinde bir yetenek kütüphanesi üretir.

## Alıştırmalar

1. `compose()`'a bir bağımlılık döngüsü dedektörü ekleyin. Yetenek A, B'ye bağımlıysa ve B de A'ya bağımlıysa ne olur? Hata mı uyarı mı?
2. Yetenek başına versiyon sabitleme uygulayın. Bir üst yetenek `crafting@1` birleştirdiğinde, `crafting@2`'ye yapılan bir iyileştirme üst yeteneği sessizce yükseltmemelidir.
3. Token-overlap aramasını sentence-transformers embedding'leriyle (veya bir BM25 stdlib uygulamasıyla) değiştirin. 50 yetenekli bir oyuncak kütüphanede retrieval@5 ölçün.
4. Bir "müfredat" agent'ı ekleyin: mevcut kütüphane ve bir alan açıklaması verildiğinde 5 eksik yetenek önerin. Haftada bir çalıştırın.
5. Anthropic'in Claude Agent SDK yetenek dokümanlarını okuyun. Oyuncak kütüphaneyi SDK'nın yetenek şemasına taşıyın. Bulunabilirlikte ne değişir?

## Anahtar Terimler

| Terim | İnsanlar ne diyor | Aslında ne anlama geliyor |
|-------|-------------------|--------------------------|
| Skill | "Yeniden kullanılabilir yetenek" | Benzerlikle alınabilir adlandırılmış kod parçası + açıklama |
| Skill library | "Nasıl yapılır hafızası" | Aranabilir ve birleştirilebilir yeteneklerin kalıcı deposu |
| Curriculum | "Görev önerici" | Mevcut yetenek açığı tarafından驱动 aşağıdan yukarıya hedef üretici |
| Composition | "Yetenek DAG'i" | Yeteneklerin yetenekleri çağırması; çalıştırmada topolojik sıralı |
| Iterative refinement | "Kendini düzelten döngü" | Ortam geri bildirimi + hatalar + öz-doğrulama bir sonraki sürüme katlanır |
| Action-space-as-code | "Programlı eylemler" | Zamansal olarak genişletilmiş davranış için komutlar yerine fonksiyonlar üretin |
| Dedup on write | "Yetenek çöküşü" | Benzer açıklamalar tek bir kanonik yeteneğe çöker |

## İleri Okuma

- [Wang ve diğerleri, Voyager (arXiv:2305.16291)](https://arxiv.org/abs/2305.16291) — orijinal yetenek-kütüphanesi makalesi
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview) — yeteneklerin 2026 ürünleştirilmesi
- [Anthropic, Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk) — pratikte yetenekler ve subagent'lar
- [Madaan ve diğerleri, Self-Refine (arXiv:2303.17651)](https://arxiv.org/abs/2303.17651) — Voyager'ın altındaki iyileştirme döngüsü
