---
name: stategraph-designer
description: Bir ajan görevini, adlandırılmış düğümler, tipli durum, indirgeyiciler (reducers), denetim noktası alıcısı (checkpointer) ve insan kesintileri olan bir LangGraph StateGraph'e dönüştürün.
version: 1.0.0
phase: 11
lesson: 16
tags: [langgraph, stategraph, checkpointer, interrupt, time-travel, react-agent, human-in-the-loop]
---

Ajan görevi (kullanıcıya dönük hedef, mevcut araçlar, beklenen tur sayısı, güvenlik patlama yarıçaplı yan etkiler, dayanıklılık gereksinimleri, hedef gecikme bütçesi) verildiğinde, çıktı:

1. Düğüm listesi. Her ayrı adımı adlandırın: LLM düşünürü, her araç çalıştırıcısı, her insan inceleme adımı, herhangi bir özetleyici veya eleştirmen, herhangi bir geri getirici. Herhangi bir düğüm birden fazla endişeye dokunuyorsa tasarımı reddedin; bölün.
2. Durum şeması. Her liste için bir indirgeyici (reducer) ile TypedDict (veya Pydantic) alanları. Her zaman mesaj günlüğü üzerinde `Annotated[list, add_messages]`. Göreve özgü herhangi bir listeyi mesajların dışına çıkarın (bir plan, bir bütçe sayacı, geri getirilen-dokümanlar listesi) böylece indirgeyiciler paralel güncellemeler altında doğru kalır.
3. Kenar haritası. Bir sonraki adımın deterministik olduğu yerde statik kenarlar. Modelin bir sonraki adımı seçtiği yerde yalnızca adlandırılmış yönlendirici fonksiyonu olan koşullu kenarlar. Yönlendirici fonksiyonu daha önce bir düğümde yapmadığınız taze bir LLM çağrısına bağlı olan herhangi bir grafiği reddedin.
4. Kesinti yerleşimi. Geri dönüşü olmayan bir yan etkisi olan her düğümde (yazma, silme, ödeme, maliyetli harici API çağrıları) `interrupt_before`. Çıktı doğrulaması ayrı bir işlemde çalıştığında model düğümünde `interrupt_after`. Yan etkisi olan herhangi bir düğümde `interrupt_after`'ı reddedin; o noktada yan etki çoktan gerçekleşmiştir.
5. Denetim noktası alıcısı (checkpointer). Testler için yalnızca MemorySaver. Yeniden başlatmayı atlatması gereken herhangi bir ortam için PostgresSaver, SQLiteSaver, RedisSaver'dan seçin. `thread_id` stratejisini (kullanıcı başına, oturum başına, konuşma başına) ve denetim noktası TTL'sini onaylayın.

Denetim noktası alıcısı olmayan bir LangGraph'ı göndermeyi reddedin. Denetim noktası yok demek, sürdürme yok, zaman yolculuğu yok, insandan insana tekrar oynatma yok. `add_messages` olmadan bir `messages` alanı olan bir grafiği reddedin; ikinci yazma, birincinin üzerine sessizce yazar ve konuşmanın yarısı kaybolur. Her geçişi koşullu kenar olan ve planlayıcı LLM tarafından yönlendirilen bir grafiği reddedin; bu, fazladan adımlı bir AutoGen'dir ve tur başına token yakar.

Örnek girdi: "Anthropic Claude üzerinde iade işleme ajanı, üç araçla (lookup_order, issue_refund, send_email), 100 doların üzerindeki herhangi bir iadeden önce bir insan için duraklamalı, sunucu yeniden başlatıldıktan sonra devam etmeli, p95 gecikme bütçesi 8 saniye."

Örnek çıktı:
- Düğümler: agent (LLM çağrısı), lookup_tool, refund_tool, email_tool, human_review.
- Durum: add_messages ile messages, order_context (üzerine yaz), refund_amount (üzerine yaz), reviewer_decision (üzerine yaz).
- Kenarlar: dallar lookup_tool, refund_tool, email_tool, human_review, END ile agent'tan should_continue yönlendiricisine. Araç düğümleri agent'a geri döner.
- Kesintiler: refund_amount > 100 olduğunda refund_tool üzerinde interrupt_before. lookup_tool veya email_tool üzerinde kesinti yok.
- Denetim noktası alıcısı: thread_id "user:{user_id}:case:{case_id}" ve 30 günlük TTL ile PostgresSaver.
