---
name: framework-picker
description: Bir ajan görevi için soyutlamayı probleme uydurarak LangGraph, CrewAI, AutoGen, Agno veya düz Python arasında seçim yapın.
version: 1.0.0
phase: 11
lesson: 17
tags: [langgraph, crewai, autogen, agno, agent-framework, orchestration, decision-matrix]
---

Görev açıklaması (problem şekli, çalıştırma başına toplam LLM çağrıları, dallanma kalıbı, dayanıklılık ve sürdürme ihtiyaçları, insandan insana kontrol noktaları, paralel fan-out, oturum belleği, beklenen günlük çalıştırma hacmi) verildiğinde, çıktı:

1. Şekil eşleşmesi. Uygun soyutlamayı adlandıran tek cümle: graf (tipli durum, adlandırılmış geçişler), organizasyon şeması (uzman rolleri, yönetici yönlendirmeli devir), sohbet (ajanlar bitene kadar konuşur), araçlı tek ajan. Bir tane seçemiyorsanız, görev henüz ajan şeklinde değildir; durun ve ayrıştırın.
2. Dallanma otoritesi. Bir sonraki adımı kim seçer: geliştirici (açık kenarlar), yönetici LLM (CrewAI hiyerarşik), konuşma ortaya çıkan (AutoGen GroupChat), araç-çağrısı kendi kendine yönlendirilen (Agno). LLM ile seçilen yönlendirme için tur başına token maliyetini belirtin.
3. Durum bütçesi. Yeniden başlatmadan sonra sürdürme, zaman yolculuğu veya insan kesintilerinin gerekli olup olmadığını onaylayın. Evet ise, LangGraph durum-öncelikli soyutlamalarda kazanır; Agno yalnızca oturum kapsamlı belleği kapsar.
4. Çerçeve seçimi. langgraph, crewai, autogen, agno, plain_python'dan birini çıktılayın. Şekil ve durum cevaplarını çerçevenin temel soyutlamasıyla eşleştiren tek cümlelik gerekçeyi dahil edin.
5. Kaçış kapısı. Günlük çalıştırma hacmi 10.000'in üzerindeyse veya görev durum olmadan iki veya daha az LLM çağrısıysa, bunun yerine sağlayıcı SDK'sı ile düz Python önerin. Görev küçük olduğunda çerçevesiz olan en hızlı çerçevedir.

Bilinen DAG'ye sahip deterministik iş akışları için AutoGen önermeyi reddedin; GroupChatManager, geliştiricinin statik olarak bağlayabileceği konuşmacıları seçmek için token harcar. CrewAI, `output_pydantic` / `output_json` aracılığıyla yapılandırılmış görev çıktılarını destekler ([docs.crewai.com/en/concepts/tasks](https://docs.crewai.com/en/concepts/tasks) adresine bakın), ancak `context` kanalı hâlâ bir sonraki görevin prompt dizesinden akar. İş akışı, bu çıktı şemalarından biri kablolanmadan yapılandırılmış durumu görevler arasında taşımak için ham `context`'e güveniyorsa, CrewAI'ye karşı çıkın. İki çağrılık bir özetleyici için LangGraph'a karşı çıkın; StateGraph ek yükü salt vergidir. 4'ten fazla paralel alt-işçiye ve indirgeyici semantiğine dağılan görevler için Agno'ya karşı çıkın; Agno, çıktıları adım adına göre anahtarlanan bir sözlüğe birleştiren bir `Parallel` bloğu ile gelir ([docs-v1.agno.com/workflows_2/overview](https://docs-v1.agno.com/workflows_2/overview) ve [docs.agno.com/workflows/access-previous-steps](https://docs.agno.com/workflows/access-previous-steps) adreslerine bakın), ancak LangGraph'ınkiyle karşılaştırılabilir bir Send tarzı fan-out-and-reduce API'sini açığa çıkarmaz.

Örnek girdi: "Uzun süren araştırma iş akışı: planla, üç geri getiriciye dağıt, sentezle, insan brifi onaylar, rapor yaz, kaynakları belirt. Çökmeden sonra devam etmeli. Günde 50 çalıştırmaya üretim bağlı."

Örnek çıktı:
- Şekil: graf. Tipli plan, üç paralel geri getirici, sentezle ve yazma arasında adlandırılmış geçişler.
- Dallanma: koşullu kenarlar aracılığıyla geliştirici kararlıdır. Tur başına yönetici LLM yok.
- Durum: sürdürme ve insan kesintisi gerektirir. LangGraph zorunludur.
- Çerçeve: langgraph. Durum, Send fan-out, interrupt_before ve PostgresSaver'ın tümü birinci sınıftır.
- Kaçış kapısı: uygulanamaz. Günde 50 çalıştırma, düz Python eşiğinin çok altında ve iş akışı çerçevesiz bırakılmak için çok durum bilgisi barındırıyor.
