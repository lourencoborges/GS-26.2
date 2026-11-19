# Citizen Assist AI · Energia em Casa

Contribuição acadêmica de **Soluções em Energias Renováveis e Sustentáveis** ao desafio Citizen Assist AI. O protótipo demonstra como recomendações de energia podem ser fundamentadas em uma análise verificável e explicadas em linguagem acessível.

## Integrantes

- Lourenco Borges — RM 569515
- Davi Teodoro — RM 571022
- Matheus Jorge — RM 574166

## Público e necessidade

Público escolhido: famílias que querem entender e reduzir o consumo de eletricidade residencial. Necessidade abordada: comparar o gasto de iluminação atual com lâmpadas LED e com geração solar fotovoltaica para atender ao mesmo serviço (cinco pontos de luz usados cinco horas por dia, como cenário ilustrativo).

O cenário é estimado, não representa uma família entrevistada nem uma medição real. Quantidade de lâmpadas, horas, potências, tarifa, produtividade solar e custo solar podem ser alterados no simulador.

## Executar

Abra `index.html` diretamente em um navegador moderno. Não requer instalação, servidor, conta ou conexão com backend. O chat demonstrativo funciona localmente. O Google Fonts pode usar a rede para carregar tipografia; a página permanece utilizável sem essa conexão.

## Funcionalidades

- Simulador de consumo e custo mensal com parâmetros editáveis.
- Comparação de referência, substituição por LED e geração solar para o mesmo uso.
- Assistente demonstrativo com respostas sobre eficiência, energia solar e limites das estimativas.
- Referências e avisos de que as estimativas não são garantias nem cotações.

O chat é uma demonstração local baseada em regras e respostas escritas para este estudo; não chama um modelo generativo nem um serviço externo. Para integração ao Citizen Assist AI existente, incorpore os textos e cálculos ao fluxo de conversa do projeto principal.

## Análise e fontes

`dados/cenario_iluminacao.csv` documenta os parâmetros e unidades. `ANALISE_ENERGETICA.md` contém fórmulas, comparação, justificativas, fontes e limitações. Valores padrão: cinco lâmpadas de 60 W, cinco horas/dia; LEDs de 9 W; R$ 0,90/kWh; produtividade solar de 90 kWh/kWp/mês; referência de R$ 3.000/kWp instalado. Preço e produtividade são ilustrativos, editáveis e sem cotação ou validação local.

Fontes públicas: EPE/BEN, ANEEL e Inmetro, citadas na análise e na interface. Use o custo efetivo da conta e dados de instalação locais antes de decidir.


Antes da entrega, realizar e documentar testes, publicar o repositório, gravar o vídeo e completar `ENTREGA.txt` com links acessíveis.
