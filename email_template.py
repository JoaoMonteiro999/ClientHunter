def get_email_template(empresa, language='pt'):
    """
    Returns email template for different languages
    """
    templates = {
        'pt': {
            'subject': "Transforme visitantes do seu website em clientes automaticamente",
            'html': f"""
<html>
<body>
<p>Caro Responsável da {empresa},</p>

<p>Sei que está muito ocupado e recebe muitas mensagens, por isso vou ser breve - 60 segundos.</p>

<p>Ajudo empresas como a sua a converter mais visitantes do website em clientes—automaticamente. Os nossos agentes de IA trabalham 24/7 para responder a perguntas, gerar leads e até fechar vendas, reduzindo os custos de suporte até 80% e aumentando as conversões em 23% em média.</p>

<p>Já se perguntou quantos potenciais clientes saem do seu site sem tomar qualquer ação? Com o VYQO, pode capturar essas oportunidades, fornecer suporte instantâneo e aumentar a receita—sem trabalho extra para a sua equipa.</p>

                <p>Se tem curiosidade, adoraria mostrar-lhe uma demo rápida (aqui está um vídeo de 1 minuto: <a href="https://www.youtube.com/watch?v=AXMbsF2nPNU">https://www.youtube.com/watch?v=AXMbsF2nPNU</a>) ou podemos conversar 15 minutos quando for conveniente. Responda com um horário que funcione, ou marque diretamente aqui: <a href="https://calendly.com/vyqo/demo-vyqo-chatbot">https://calendly.com/vyqo/demo-vyqo-chatbot</a></p><p>Também pode saber mais e ver resultados reais de clientes no nosso website: <a href="https://www.vyqo.eu">https://www.vyqo.eu</a></p>

<p>Se está muito ocupado para responder, sem problema—uma resposta de uma linha já me faria o dia.</p>

<p>Com os melhores cumprimentos,<br>
<b>João Monteiro</b><br>
<b>VYQO AI Solutions</b><br>
✉️ VYQO.EU@gmail.com</p>

<p><b>P.S.</b> A integração é rápida e gratuita—além disso, pode experimentar o nosso agente de IA com os seus clientes reais durante 2 semanas, completamente sem risco.</p>
</body>
</html>
            """,
            'text': f"""
Caro Responsável da {empresa},

Sei que está muito ocupado e recebe muitas mensagens, por isso vou ser breve - 60 segundos.

Ajudo empresas como a sua a converter mais visitantes do website em clientes—automaticamente. Os nossos agentes de IA trabalham 24/7 para responder a perguntas, gerar leads e até fechar vendas, reduzindo os custos de suporte até 80% e aumentando as conversões em 23% em média.

Já se perguntou quantos potenciais clientes saem do seu site sem tomar qualquer ação? Com o VYQO, pode capturar essas oportunidades, fornecer suporte instantâneo e aumentar a receita—sem trabalho extra para a sua equipa.

Se tem curiosidade, adoraria mostrar-lhe uma demo rápida (aqui está um vídeo de 1 minuto: https://www.youtube.com/watch?v=AXMbsF2nPNU) ou podemos conversar 15 minutos quando for conveniente. Responda com um horário que funcione, ou marque diretamente aqui: https://calendly.com/vyqo/demo-vyqo-chatbot

Também pode saber mais e ver resultados reais de clientes no nosso website: https://www.vyqo.eu

Se está muito ocupado para responder, sem problema—uma resposta de uma linha já me faria o dia.

Com os melhores cumprimentos,
João Monteiro
VYQO AI Solutions
✉️ VYQO.EU@gmail.com

P.S. A integração é rápida e gratuita—além disso, pode experimentar o nosso agente de IA com os seus clientes reais durante 2 semanas, completamente sem risco.
            """
        },
        'en': {
            'subject': "Turn your website visitors into customers automatically",
            'html': f"""
<html>
<body>
<p>Dear {empresa} Manager,</p>

<p>I know you're incredibly busy and get a lot of messages, so I'll keep this to 60 seconds.</p>

<p>I help businesses like yours turn more website visitors into customers—automatically. Our AI agents work 24/7 to answer questions, generate leads, and even close sales, all while cutting support costs by up to 80% and boosting conversions by 23% on average.</p>

<p>Have you ever wondered how many potential customers leave your site without taking action? With VYQO, you can capture those opportunities, provide instant support, and grow your revenue—no extra work for your team.</p>

<p>If you're curious, I'd love to show you a quick demo (here's a 1-minute video: <a href="https://www.youtube.com/watch?v=AXMbsF2nPNU">https://www.youtube.com/watch?v=AXMbsF2nPNU</a>) or we can chat for 15 minutes at your convenience. Just reply with a time that works, or book directly here: <a href="https://calendly.com/vyqo/demo-vyqo-chatbot">https://calendly.com/vyqo/demo-vyqo-chatbot</a></p>

<p>You can also learn more and see real client results at our website: <a href="https://www.vyqo.eu">https://www.vyqo.eu</a></p>

<p>If you're too busy to reply, no worries at all—a one-line response would make my day.</p>

<p>All the best,<br>
<b>João Monteiro</b><br>
<b>VYQO AI Solutions</b><br>
✉️ VYQO.EU@gmail.com</p>

<p><b>P.S.</b> Integration is quick and free—plus, you can try our AI agent with your real customers for 2 weeks, completely risk-free.</p>
</body>
</html>
            """,
            'text': f"""
Dear {empresa} Manager,

I know you're incredibly busy and get a lot of messages, so I'll keep this to 60 seconds.

I help businesses like yours turn more website visitors into customers—automatically. Our AI agents work 24/7 to answer questions, generate leads, and even close sales, all while cutting support costs by up to 80% and boosting conversions by 23% on average.

Have you ever wondered how many potential customers leave your site without taking action? With VYQO, you can capture those opportunities, provide instant support, and grow your revenue—no extra work for your team.

If you're curious, I'd love to show you a quick demo (here's a 1-minute video: https://www.youtube.com/watch?v=AXMbsF2nPNU) or we can chat for 15 minutes at your convenience. Just reply with a time that works, or book directly here: https://calendly.com/vyqo/demo-vyqo-chatbot

You can also learn more and see real client results at our website: https://www.vyqo.eu

If you're too busy to reply, no worries at all—a one-line response would make my day.

All the best,
João Monteiro
VYQO AI Solutions
✉️ VYQO.EU@gmail.com

P.S. Integration is quick and free—plus, you can try our AI agent with your real customers for 2 weeks, completely risk-free.
            """
        },
        'de': {
            'subject': "Verwandeln Sie Ihre Website-Besucher automatisch in Kunden",
            'html': f"""
<html>
<body>
<p>Sehr geehrte Damen und Herren von {empresa},</p>

<p>Ich weiß, dass Sie sehr beschäftigt sind und viele Nachrichten erhalten, deshalb halte ich mich kurz - 60 Sekunden.</p>

<p>Ich helfe Unternehmen wie Ihrem dabei, mehr Website-Besucher automatisch in Kunden zu verwandeln. Unsere KI-Agenten arbeiten 24/7, um Fragen zu beantworten, Leads zu generieren und sogar Verkäufe abzuschließen, während sie gleichzeitig die Support-Kosten um bis zu 80% senken und die Conversions um durchschnittlich 23% steigern.</p>

<p>Haben Sie sich jemals gefragt, wie viele potenzielle Kunden Ihre Website verlassen, ohne eine Aktion durchzuführen? Mit VYQO können Sie diese Gelegenheiten erfassen, sofortigen Support bieten und Ihren Umsatz steigern—ohne zusätzliche Arbeit für Ihr Team.</p>

<p>Falls Sie neugierig sind, würde ich Ihnen gerne eine schnelle Demo zeigen (hier ist ein 1-minütiges Video: <a href="https://www.youtube.com/watch?v=AXMbsF2nPNU">https://www.youtube.com/watch?v=AXMbsF2nPNU</a>) oder wir können uns 15 Minuten zu Ihrer Bequemlichkeit unterhalten. Antworten Sie einfach mit einer passenden Zeit oder buchen Sie direkt hier: <a href="https://calendly.com/vyqo/demo-vyqo-chatbot">https://calendly.com/vyqo/demo-vyqo-chatbot</a></p>

<p>Sie können auch mehr erfahren und echte Kundenergebnisse auf unserer Website sehen: <a href="https://www.vyqo.eu">https://www.vyqo.eu</a></p>

<p>Falls Sie zu beschäftigt sind zu antworten, kein Problem—eine einzeilige Antwort würde meinen Tag machen.</p>

<p>Mit freundlichen Grüßen,<br>
<b>João Monteiro</b><br>
<b>VYQO AI Solutions</b><br>
✉️ VYQO.EU@gmail.com</p>

<p><b>P.S.</b> Die Integration ist schnell und kostenlos—außerdem können Sie unseren KI-Agenten 2 Wochen lang mit Ihren echten Kunden testen, völlig risikofrei.</p>
</body>
</html>
            """,
            'text': f"""
Sehr geehrte Damen und Herren von {empresa},

Ich weiß, dass Sie sehr beschäftigt sind und viele Nachrichten erhalten, deshalb halte ich mich kurz - 60 Sekunden.

Ich helfe Unternehmen wie Ihrem dabei, mehr Website-Besucher automatisch in Kunden zu verwandeln. Unsere KI-Agenten arbeiten 24/7, um Fragen zu beantworten, Leads zu generieren und sogar Verkäufe abzuschließen, während sie gleichzeitig die Support-Kosten um bis zu 80% senken und die Conversions um durchschnittlich 23% steigern.

Haben Sie sich jemals gefragt, wie viele potenzielle Kunden Ihre Website verlassen, ohne eine Aktion durchzuführen? Mit VYQO können Sie diese Gelegenheiten erfassen, sofortigen Support bieten und Ihren Umsatz steigern—ohne zusätzliche Arbeit für Ihr Team.

Falls Sie neugierig sind, würde ich Ihnen gerne eine schnelle Demo zeigen (hier ist ein 1-minütiges Video: https://www.youtube.com/watch?v=AXMbsF2nPNU) oder wir können uns 15 Minuten zu Ihrer Bequemlichkeit unterhalten. Antworten Sie einfach mit einer passenden Zeit oder buchen Sie direkt hier: https://calendly.com/vyqo/demo-vyqo-chatbot

Sie können auch mehr erfahren und echte Kundenergebnisse auf unserer Website sehen: https://www.vyqo.eu

Falls Sie zu beschäftigt sind zu antworten, kein Problem—eine einzeilige Antwort würde meinen Tag machen.

Mit freundlichen Grüßen,
João Monteiro
VYQO AI Solutions
✉️ VYQO.EU@gmail.com

P.S. Die Integration ist schnell und kostenlos—außerdem können Sie unseren KI-Agenten 2 Wochen lang mit Ihren echten Kunden testen, völlig risikofrei.
            """
        }
    }
    
    template = templates.get(language, templates['pt'])
    return template['subject'], template['html'], template['text']
