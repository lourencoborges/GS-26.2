# Análise energética — iluminação residencial

**Integrantes:** Lourenco Borges (RM 569515); Davi Teodoro (RM 571022); Matheus Jorge (RM 574166).

## Pergunta e público

Como uma família pode reduzir o consumo da iluminação sem perder o serviço de luz, e como comparar a eficiência de lâmpadas LED com o fornecimento renovável por solar fotovoltaica?

O exemplo é deliberadamente simples: cinco pontos de luz usados cinco horas por dia. Nenhum dado foi coletado de uma família real. É uma simulação educacional, com parâmetros que devem ser substituídos por dados da residência.

## Dados, unidades e período

| Parâmetro | Valor padrão | Unidade | Natureza |
|---|---:|---|---|
| Lâmpadas | 5 | unidades | Estimativa editável |
| Uso diário | 5 | h/dia | Estimativa editável |
| Potência atual | 60 | W por lâmpada | Exemplo estimado |
| LED comparável | 9 | W por lâmpada | Exemplo; confirmar lúmens e produto |
| Preço da energia | R$ 0,90 | R$/kWh | Hipótese editável, não tarifa oficial |
| Produção FV específica | 90 | kWh/kWp/mês | Hipótese de cenário, não previsão local |
| Custo solar instalado | R$ 3.000 | R$/kWp | Referência didática, sem cotação |
| Período | 30 dias / 12 meses | dia / mês | Convenção simplificadora |

O CSV `dados/cenario_iluminacao.csv` mantém os valores e sua classificação. As referências institucionais sustentam as orientações de eficiência, tarifas, regras e contexto da matriz elétrica; não são fonte dos custos hipotéticos deste cenário.

## Método

Consumo mensal estimado:

`E = potência (W) × quantidade × horas/dia × 30 ÷ 1.000`

Custo variável estimado:

`C = E (kWh) × preço efetivo (R$/kWh)`

Para comparar com geração fotovoltaica, o sistema ilustrativo é dimensionado para compensar o consumo de iluminação atual:

`potência FV (kWp) = consumo mensal atual ÷ produção específica (kWh/kWp/mês)`

`investimento FV ilustrativo = potência FV × custo de referência (R$/kWp)`

O simulador recalcula a comparação quando qualquer entrada muda. Estima o custo da energia consumida; não reproduz integralmente a fatura.

## Resultado padrão

- Atual: `5 × 60 W × 5 h/dia × 30 ÷ 1.000 = 45 kWh/mês`, ou 540 kWh/ano. Ao preço assumido, R$ 40,50/mês e R$ 486,00/ano de custo variável.
- LEDs: `5 × 9 W × 5 h/dia × 30 ÷ 1.000 = 6,75 kWh/mês`, ou 81 kWh/ano. Economia estimada de 38,25 kWh/mês (85%) e R$ 34,43/mês ou R$ 413,10/ano ao preço assumido.
- Solar FV: para 45 kWh/mês e produtividade suposta de 90 kWh/kWp/mês, potência calculada de 0,50 kWp. Ao custo didático suposto de R$ 3.000/kWp, investimento indicativo de R$ 1.500. Isso não é dimensionamento de engenharia, proposta comercial ou garantia de geração.

## Comparação e recomendação

| Alternativa | Energia anual do cenário | Custo/viabilidade | Impacto e limites |
|---|---:|---|---|
| Manter lâmpadas atuais | 540 kWh | Sem investimento novo; maior custo variável estimado | Sem redução de potência; representa linha de base |
| Trocar por LED | 81 kWh | Aquisição simples por lâmpada; custo local depende de marca, potência, fluxo luminoso e vida útil | Redução teórica de 85% no consumo de iluminação, mantendo horas de uso; descartar lâmpadas corretamente |
| Solar fotovoltaica | Geração dimensionada em 540 kWh/ano (estimativa) | Investimento inicial, instalação e adequação; custo usado aqui é apenas hipótese | Fonte renovável; geração depende de telhado, localização, orientação, sombra, perdas e regras de compensação |

**Orientação para este caso:** avaliar primeiro a substituição por LED eficiente e compatível, pois reduz a demanda com investimento por ponto de luz e sem depender de telhado. Solar é uma alternativa renovável que merece orçamento quando a família deseja cobrir outros usos e dispõe de local e condições adequadas. Não se conclui qual tem menor custo total sem preços locais, vida útil, manutenção, financiamento e conta real. A geração solar não garante conta zero: custos mínimos, tributos e componentes não compensados podem permanecer.

A matriz elétrica brasileira teve 88,2% de renovabilidade em 2024, segundo a EPE. Esse dado dá contexto nacional; não significa que a eletricidade consumida em cada hora ou local tenha essa composição, nem substitui a análise de impacto de ciclo de vida dos equipamentos.

## Integração ao Citizen Assist AI

A demonstração inclui perguntas rápidas e campo livre. O protótipo identifica temas por palavras-chave e responde com os cálculos e ressalvas desta análise. Ele não usa IA generativa nem envia dados para um servidor. A integração ao assistente principal deve manter: (1) a definição da necessidade, (2) estimativas calculadas com premissas visíveis, (3) recomendação proporcional às evidências, (4) links de fonte e (5) aviso de que não é orçamento nem garantia.

## Limitações e validação necessária

Consumo real varia com potência e quantidade medidas, tempo de uso, tensão, qualidade do LED e tarifas. O cálculo usa mês de 30 dias e não considera variação diária/sazonal, consumo em standby, substituição e descarte, custos fixos, taxa mínima, tributos específicos, bandeiras, iluminação pública, compensação de créditos, custo financeiro, operação, manutenção ou degradação de painel. A tarifa efetiva deve ser lida da fatura e pode variar; a ANEEL informa que suas tarifas homologadas não contemplam todos esses elementos. A produtividade solar e custo instalado são hipóteses editáveis a substituir por estimativa técnica e cotações locais. Não calcular payback com estes dados.

Fontes públicas e acessos em 17 nov. 2026:

1. EPE, [Balanço Energético Nacional 2025](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/balanco-energetico-nacional-2025), ano-base 2024. A matriz elétrica foi 88,2% renovável.
2. ANEEL, [Tarifas e Informações Econômico-Financeiras](https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras). Tarifas homologadas por distribuidora, sem todos os tributos e adicionais da conta.
3. Inmetro, [Tabela de eficiência energética — lâmpadas](https://www.gov.br/inmetro/pt-br/assuntos/regulamentacao/avaliacao-da-conformidade/programa-brasileiro-de-etiquetagem/tabelas-de-eficiencia-energetica/lampadas). Consulta de produtos e desempenho.
4. ANEEL, [Geração distribuída](https://www.gov.br/aneel/pt-br/assuntos/geracao-distribuida). Orientações regulatórias para geração junto à unidade consumidora.
