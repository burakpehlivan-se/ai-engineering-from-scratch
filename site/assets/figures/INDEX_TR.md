# Şekil İndeksi

`site/assets/figures/` altında yayınlanan her şekil aşağıda listelenmiştir. FIG numaraları globaldir, monoton olarak artar ve asla yeniden kullanılmaz.

Estetik, `blueprint-diagram` Claude Code becerisinde belgelenmiştir; bu beceri bu depodan ayrı olarak dağıtılır (projenin "depolar içinde satıcı/araç yapayı bulundurulmaz" kuralı gereği). Beceri kaynağı, kurulduktan sonra `~/.claude/skills/blueprint-diagram/` altında bulunur; kurulum yolu için bir bakımcıya sorun ya da beceriyi gerektirmeyen manuel bir iş akışı için aşağıdaki [Nasıl Eklenir](#nasıl-eklenir) bölümüne başvurun.

| FIG | slug | faz | ders | eklenme | notlar |
|---|---|---|---|---|---|
| 000 | (müfredat yığını — README banner'ına gömülü) | — | — | 2026-05-09 | hero, bu dizinde değil `assets/banner.svg` içinde yaşıyor |
| 001 | exploded-view-floppy | — | — | 2026-05-09 | beceri için referans örnek, `~/.claude/skills/blueprint-diagram/references/examples/` altında |
| 001.A | prompts | — | — | 2026-05-13 | README "her ders bir şey sunar" kartı — prompt yapayı ikonu |
| 001.B | skills | — | — | 2026-05-13 | README kartı — SKILL.md drop-in ikonu |
| 001.C | agents | — | — | 2026-05-13 | README kartı — ReAct tarzı ajan döngüsü ikonu |
| 001.D | mcp-servers | — | — | 2026-05-13 | README kartı — tools/resources/prompts içeren MCP sunucu rafı ikonu |
| 002 | kernel-surface-gaussian | — | — | 2026-05-09 | beceri için referans örnek |
| 003 | pixel-vector-bezier | — | — | 2026-05-09 | beceri için referans örnek |
| 004 | gaussian-kernel-blur | 1 | 8 | 2026-05-09 | "Optimizasyon: Gradyan İnişi Ailesi" dersi için gaussian bulanıklık görselleştirmesi |
| 005 | transformer-attention-heads | 7 | 1 | 2026-05-09 | çok başlıklı dikkat bloğunun patlatılmış görünümü |

## Numaralandırma

- `001`–`099`: erken müfredat şekilleri için ayrılmıştır (Faz 0–7).
- `100`+: yazarlık sırasına göre atanır.
- Alt şekiller harf soneki kullanır: `004.A`, `004.B`. Üst öğeyle aynı satırı paylaşırlar.

## Nasıl Eklenir

`blueprint-diagram` becerisi kuruluysa:

1. Kavramın açıklamasıyla beceriyi çalıştırın.
2. Beceri, SVG dosyasını `site/assets/figures/NNN-slug.svg` konumuna yazar, buraya sıradaki uygun numarayla bir satır ekler ve (istendiğinde) şekli ilgili ders markdown'ına `![FIG_NNN](path)` aracılığıyla bağlar.

Beceri kurulu değilse, manuel olarak yapın:

1. Krem + blueprint estetiğinde bir SVG tasarlayın (krem `#fafaf5` kağıt, `#3553ff` blueprint mavisi konturlar, JetBrains Mono büyük harf etiketler ve yön çizgileri, başka kromatik vurgu olmadan).
2. Yukarıdaki tablodaki sıradaki uygun FIG numarasını kullanarak `site/assets/figures/<NNN>-<slug>.svg` olarak kaydedin.
3. Buradaki tabloya FIG numarası, slug, hedef faz + ders, bugünün tarihi ve tek satırlık bir not içeren bir satır ekleyin.
4. Şekle ders markdown'ından `![FIG_NNN](../../site/assets/figures/<NNN>-<slug>.svg)` olarak referans verin.
5. 480 / 720 / 1200 px görüntü alanı genişliklerinde doğrulayın — etiketler geometriyle örtüşmemeli, yön çizgileri hedeflerine ulaşmalıdır.

## Lisans

Şekiller, deponun MIT lisansı altında yayınlanır. MIT lisansı, kaynak SVG'nin dağıtımlarında telif hakkı bildiriminin korunmasını zorunlu kılar; işlenmiş görüntünün görsel olarak yeniden kullanımı (örn. bir blog yazısına ya da slayt destesine gömme) ek atıf gerektirmez.
