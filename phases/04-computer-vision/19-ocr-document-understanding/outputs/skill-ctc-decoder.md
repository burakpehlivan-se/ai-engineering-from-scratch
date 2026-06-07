---
name: skill-ctc-decoder
description: Uzunluk normalleştirmesi dahil açgözlü ve ışın arama CTC çözücülerini sıfırdan yazın
version: 1.0.0
phase: 4
lesson: 19
tags: [ocr, ctc, çözme, dizi-modelleri]
---

# CTC Çözücü

CTC çıktıları için iki kod çözme rutini üretin: açgözlü (hızlı) ve ışın (gürültülü girdilerde daha iyi).

## Ne zaman kullanılır

- Özel CRNN çıktılarında OCR çıkarımı çalıştırırken.
- Önceden eğitilmiş bir OCR modelini farklı çözücülere karşı kıyaslarken.
- ctcdecode'u çekmeden basit bir ışın araması uygularken.

## Girdiler

- `log_probs`: (T, N, C) kelimelik üzerinde log-softmax (endeks 0 = geleneksel olarak boş).
- `vocab`: C karakter listesi.
- `beam_width` (yalnızca ışın): tipik olarak 5-10.

## Açgözlü çözücü

```python
def greedy_ctc_decode(log_probs, vocab, blank=0):
 preds = log_probs.argmax(dim=-1).transpose(0, 1).cpu().tolist()
 out = []
 for seq in preds:
 decoded = []
 prev = None
 for idx in seq:
 if idx != prev and idx != blank:
 decoded.append(vocab[idx])
 prev = idx
 out.append("".join(decoded))
 return out
```

## Işın arama çözücü

```python
import heapq
import math

def beam_ctc_decode(log_probs, vocab, beam_width=5, blank=0):
 T, N, C = log_probs.shape
 lp = log_probs.cpu()
 results = []
 for n in range(N):
 beams = {("",): (0.0, -math.inf)} # (prefix_tuple) -> (p_blank, p_nonblank)
 for t in range(T):
 logits_t = lp[t, n]
 new_beams = {}
 for prefix, (p_b, p_nb) in beams.items():
 for c in range(C):
 p = logits_t[c].item()
 if c == blank:
 nb = p_b + p
 nnb = p_nb + p
 upd = new_beams.get(prefix, (-math.inf, -math.inf))
 new_beams[prefix] = (
 _logsumexp(upd[0], _logsumexp(nb, nnb)),
 upd[1],
 )
 else:
 last = prefix[-1] if prefix else ""
 char = vocab[c]
 if char == last:
 # Durum 1: aynı önek üzerinde kal (p_nb'den çök)
 upd = new_beams.get(prefix, (-math.inf, -math.inf))
 new_beams[prefix] = (upd[0], _logsumexp(upd[1], p_nb + p))
 # Durum 2: boşlukla ayrılmış tekrar aracılığıyla öneki genişlet ("a_a" -> "aa")
 new_prefix = prefix + (char,)
 upd = new_beams.get(new_prefix, (-math.inf, -math.inf))
 new_beams[new_prefix] = (upd[0], _logsumexp(upd[1], p_b + p))
 else:
 new_prefix = prefix + (char,)
 upd = new_beams.get(new_prefix, (-math.inf, -math.inf))
 nb = _logsumexp(p_b, p_nb) + p
 new_beams[new_prefix] = (upd[0], _logsumexp(upd[1], nb))
 beams = dict(heapq.nlargest(
 beam_width,
 new_beams.items(),
 key=lambda kv: _logsumexp(kv[1][0], kv[1][1]),
 ))
 best = max(beams.items(), key=lambda kv: _logsumexp(kv[1][0], kv[1][1]))[0]
 results.append("".join(best))
 return results


def _logsumexp(a, b):
 if a == -math.inf: return b
 if b == -math.inf: return a
 m = max(a, b)
 return m + math.log(math.exp(a - m) + math.exp(b - m))
```

## Kurallar

- CTC'deki boş endeks, PyTorch'un `nn. CTCLoss`'unda geleneksel olarak 0'dır.
- Işın araması, düşük güvenli girdilerde doğruluğu artırır; temiz girdilerde iyileşme <%1 CER'dir.
- Işını asla 5'in altına budamayın; doğruluk-gecikme takası bunun altında düzleşir.
- Sıkı bir gecikme bütçesi içinde ışın araması çalıştırırken, açgözlüye geçin; kalite kaybı çoğu üretim OCR verisinde küçüktür.
- Büyük kelimelikler için (3000+ karakterli CJK), yukarıdaki saf Python sürümü yerine `ctcdecode` (C++)'a geçin; Python ışını hızla darboğaz haline gelir.
