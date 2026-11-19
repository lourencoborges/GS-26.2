# Citizen Assist AI · Energia em Casa

Contribuição acadêmica de **Soluções em Energias Renováveis e Sustentáveis** ao desafio Citizen Assist AI. O protótipo mostra como recomendações de energia podem ser fundamentadas em uma análise verificável e explicadas em linguagem acessível.

## Público e necessidade

Público escolhido: famílias que querem entender e reduzir o consumo de eletricidade residencial. Necessidade abordada: comparar o gasto de iluminação atual com lâmpadas LED e com geração solar fotovoltaica para atender o mesmo serviço (cinco pontos de luz usados cinco horas por dia, como cenário ilustrativo).

O cenário é estimado, não representa uma família entrevistada nem uma medição real. Quantidade de lâmpadas, horas, potências, tarifa e parâmetros solares podem ser alterados no simulador.

## Executar

Abra `index.html` diretamente em um navegador moderno. Não requer instalação, servidor, conta ou conexão com backend. A fonte, interface e assistente demonstrativo são servidos localmente; o Google Fonts pode usar rede para carregar a tipografia.

## O que demonstrar

- Simulador de consumo e custo mensal com parâmetros editáveis.
- Comparação de referência, substituição por LED e geração solar para o mesmo uso.
- Assistente demonstrativo com respostas sobre eficiência, energia solar e limitações.
- Referências e avisos de que as estimativas não são garantias nem cotações.

O chat é uma demonstração local baseada em regras e respostas escritas para este estudo; não chama um modelo generativo nem um serviço externo. Para integrar ao Citizen Assist AI existente, incorpore o módulo de respostas e seus textos ao fluxo de conversa do projeto principal.

## Dados, cálculos e premissas

O arquivo `dados/cenario_iluminacao.csv` documenta os parâmetros usados e indica se são estimativas. `ANALISE_ENERGETICA.md` contém fórmulas, comparação, justificativas e limitações. Valores padrão: cinco lâmpadas incandescentes de 60 W, cinco horas/dia; cinco LEDs de 9 W; R$ 0,90/kWh; produtividade solar de 90 kWh/kWp/mês; referência de R$ 3.000/kWp instalado. Os valores monetários e de produtividade são ilustrativos e editáveis, sem cotação ou validação local.

Fontes públicas: EPE/BEN, ANEEL e Inmetro, listadas também na interface. Verifique a tarifa efetiva na conta, regras de compensação e dados locais antes de tomar decisões.

## Entregáveis e pendências da equipe

- `index.html`, `styles.css`, `app.js`: interface e simulador.
- `ANALISE_ENERGETICA.md`: metodologia e análise comparativa.
- `dados/cenario_iluminacao.csv`: parâmetros e unidades.
- `VIDEO_ROTEIRO.md`: roteiro para vídeo de até três minutos.
- `TESTES_USUARIOS.md`: protocolo e espaço para registrar testes reais. Os testes ainda precisam ser realizados e documentados pela equipe.
- `ENTREGA.txt`: modelo do único arquivo texto final; preencher nomes completos, RMs, URL pública do GitHub e URL do vídeo não listado antes de enviar.

**Integrantes:** preencher nomes completos e RMs antes da entrega. Não publicar este projeto como repositório acessível sem adicionar os integrantes, revisar os links e realizar os testes com usuários.
