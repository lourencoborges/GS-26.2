# Citizen Assist — catálogo de serviços e demonstração DSA

Catálogo interativo de orientações úteis ao cidadão, com uma interface web para
demonstrar a lista simplesmente encadeada e seus algoritmos. Também inclui uma
versão de terminal em Python. Os dados ficam em memória e são reiniciados ao
recarregar a página ou encerrar o programa.

## Interface web

Abra `index.html` em um navegador. Não requer instalação nem servidor. A página
permite cadastrar, consultar, atualizar, excluir, pesquisar e ordenar registros;
a visualização da estrutura mostra os nós e permite animar um percurso.

## Versão de terminal

Requer Python 3.9 ou superior. No terminal, dentro desta pasta:

```bash
python main.py
```

## Modelo e estrutura de dados

Cada `Servico` contém identificador, título, categoria, descrição, requisitos e
local de atendimento. A classe `No` referencia um serviço e o próximo nó. A
classe `ListaServicos` mantém a referência ao primeiro nó e implementa inserção,
percurso, busca, atualização e remoção sem usar uma lista nativa para armazenar
os registros.

## Algoritmos e complexidade

- **Busca por ID:** percorre os nós sequencialmente até encontrar o ID. Busca
  por título/categoria também percorre todos os nós. Ambos têm tempo O(n) e
  espaço adicional O(1), desconsiderando os resultados exibidos.
- **Inserção no final:** primeiro percorre a lista para rejeitar ID duplicado e
  depois percorre até o último nó; tempo O(n), espaço O(1).
- **Remoção:** busca o nó e religa o anterior ao próximo; tempo O(n), espaço
  O(1).
- **Ordenação por título:** insertion sort implementado por religações de nós;
  tempo O(n²) no pior caso, O(n) no melhor caso, espaço O(1). A ordenação é
  estável e não usa `sorted()` nem `list.sort()`.
- **Resumo por categoria:** percorre os n registros e ordena as k categorias;
  O(n + k log k) no tempo, com O(k) de espaço.

## Roteiro de verificação manual

Use estes passos durante a demonstração e registre as saídas observadas:

1. Em lista vazia, escolha listar, ordenar e análise: o programa informa que o
   catálogo está vazio/sem categorias e não falha.
2. Cadastre ID `1`, título `Cartão SUS`, categoria `Saúde`, e preencha os demais
   campos. Consulte ID `1`: os dados cadastrados devem aparecer.
3. Tente cadastrar novamente ID `1`: deve ser recusado como duplicado.
4. Pesquise `saúde` (a pesquisa não diferencia maiúsculas/minúsculas): deve
   encontrar o registro. Pesquise `transporte`: deve informar nenhum resultado.
5. Atualize ID `1`, deixando um campo vazio para mantê-lo. Consulte de novo e
   confirme os novos dados.
6. Cadastre ID `2` com título `Agendamento de consulta`; ordene e liste: os
   títulos devem aparecer em ordem alfabética.
7. Analise o catálogo: total `2` e contagem `Saúde: 2` se ambos estiverem na
   categoria Saúde. Exclua ID `1` e consulte-o: deve informar que não existe.
8. Digite texto em um campo de ID/opção numérica ou uma opção inexistente: deve
   haver mensagem de validação, sem encerrar inesperadamente.

## Operações do menu

Cadastro, consulta por ID, atualização, exclusão, pesquisa por título/categoria,
listagem, ordenação por título e análise por categoria. Campos obrigatórios não
podem ficar vazios; no formulário de atualização, Enter preserva o valor atual.
