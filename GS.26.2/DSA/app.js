class No {
  constructor(servico) {
    this.servico = servico;
    this.proximo = null;
  }
}

class ListaServicos {
  constructor() {
    this.inicio = null;
    this.tamanho = 0;
  }

  buscarId(identificador) {
    let atual = this.inicio;
    while (atual) {
      if (atual.servico.identificador === identificador) return atual.servico;
      atual = atual.proximo;
    }
    return null;
  }

  inserir(servico) {
    if (this.buscarId(servico.identificador)) return false;
    const novo = new No(servico);
    if (!this.inicio) {
      this.inicio = novo;
    } else {
      let atual = this.inicio;
      while (atual.proximo) atual = atual.proximo;
      atual.proximo = novo;
    }
    this.tamanho += 1;
    return true;
  }

  remover(identificador) {
    let anterior = null;
    let atual = this.inicio;
    while (atual) {
      if (atual.servico.identificador === identificador) {
        if (anterior) anterior.proximo = atual.proximo;
        else this.inicio = atual.proximo;
        this.tamanho -= 1;
        return true;
      }
      anterior = atual;
      atual = atual.proximo;
    }
    return false;
  }

  *percurso() {
    let atual = this.inicio;
    while (atual) {
      yield atual.servico;
      atual = atual.proximo;
    }
  }

  *pesquisar(termo) {
    const consulta = termo.trim().toLocaleLowerCase('pt-BR');
    let atual = this.inicio;
    while (atual) {
      const servico = atual.servico;
      if (servico.titulo.toLocaleLowerCase('pt-BR').includes(consulta) ||
          servico.categoria.toLocaleLowerCase('pt-BR').includes(consulta)) {
        yield servico;
      }
      atual = atual.proximo;
    }
  }

  atualizar(identificador, dados) {
    const existente = this.buscarId(identificador);
    if (!existente) return false;
    Object.assign(existente, dados, { identificador });
    return true;
  }

  ordenarPorTitulo() {
    let ordenada = null;
    let atual = this.inicio;
    while (atual) {
      const proximo = atual.proximo;
      const titulo = atual.servico.titulo.toLocaleLowerCase('pt-BR');
      if (!ordenada || titulo < ordenada.servico.titulo.toLocaleLowerCase('pt-BR')) {
        atual.proximo = ordenada;
        ordenada = atual;
      } else {
        let cursor = ordenada;
        while (cursor.proximo &&
               cursor.proximo.servico.titulo.toLocaleLowerCase('pt-BR') <= titulo) {
          cursor = cursor.proximo;
        }
        atual.proximo = cursor.proximo;
        cursor.proximo = atual;
      }
      atual = proximo;
    }
    this.inicio = ordenada;
  }
}

const catalogo = new ListaServicos();
const exemplos = [
  { identificador: 101, titulo: 'Cartão SUS', categoria: 'Saúde', descricao: 'Emita ou atualize seu Cartão Nacional de Saúde para acessar os serviços do SUS.', requisitos: 'Documento com foto e CPF', local: 'Unidade Básica de Saúde' },
  { identificador: 102, titulo: 'Agendamento de consulta', categoria: 'Saúde', descricao: 'Marque consultas médicas e acompanhe os encaminhamentos da rede pública.', requisitos: 'Cartão SUS e documento com foto', local: 'UBS do seu bairro' },
  { identificador: 103, titulo: 'Passe livre estudantil', categoria: 'Mobilidade', descricao: 'Solicite o benefício de transporte público para estudantes da rede de ensino.', requisitos: 'Comprovante de matrícula e documento com foto', local: 'Central de atendimento ao estudante' },
  { identificador: 104, titulo: 'Coleta de recicláveis', categoria: 'Meio ambiente', descricao: 'Consulte dias e pontos de coleta seletiva perto da sua residência.', requisitos: 'Consulte o calendário do seu bairro', local: 'Pontos de coleta municipais' },
  { identificador: 105, titulo: 'Matrícula na rede municipal', categoria: 'Educação', descricao: 'Conheça o processo de matrícula e encontre vagas na rede municipal de ensino.', requisitos: 'Certidão de nascimento e comprovante de residência', local: 'Secretaria Municipal de Educação' },
  { identificador: 106, titulo: 'Vacinação', categoria: 'Saúde', descricao: 'Consulte as vacinas disponíveis e atualize sua caderneta de vacinação.', requisitos: 'Caderneta de vacinação e documento com foto', local: 'Unidade Básica de Saúde' },
];
exemplos.forEach((servico) => catalogo.inserir(servico));

const elementos = {
  lista: document.querySelector('#service-list'),
  nos: document.querySelector('#linked-list'),
  busca: document.querySelector('#search-input'),
  vazio: document.querySelector('#empty-state'),
  total: document.querySelector('#metric-total'),
  categorias: document.querySelector('#metric-categories'),
  contagem: document.querySelector('#result-count'),
  detalheId: document.querySelector('#detail-id'),
  detalheCategoria: document.querySelector('#detail-category'),
  detalheTitulo: document.querySelector('#detail-title'),
  detalheDescricao: document.querySelector('#detail-description'),
  detalheRequisitos: document.querySelector('#detail-requirements'),
  detalheLocal: document.querySelector('#detail-location'),
  editar: document.querySelector('#edit-service'),
  excluir: document.querySelector('#delete-service'),
  barras: document.querySelector('#category-bars'),
  status: document.querySelector('#catalog-foot-text'),
  toast: document.querySelector('#toast'),
  dialogo: document.querySelector('#service-dialog'),
  formulario: document.querySelector('#service-form'),
  erro: document.querySelector('#form-error'),
};

let selecionado = null;
let toastTimer;
let percursoAtivo = false;

function servicosVisiveis() {
  const termo = elementos.busca.value.trim();
  return termo ? [...catalogo.pesquisar(termo)] : [...catalogo.percurso()];
}

function criar(tag, className, texto) {
  const elemento = document.createElement(tag);
  if (className) elemento.className = className;
  if (texto !== undefined) elemento.textContent = texto;
  return elemento;
}

function renderizarCatalogo() {
  const servicos = servicosVisiveis();
  elementos.lista.replaceChildren();
  elementos.vazio.hidden = servicos.length > 0;
  elementos.contagem.textContent = `${servicos.length} ${servicos.length === 1 ? 'serviço' : 'serviços'}`;

  servicos.forEach((servico, indice) => {
    const linha = criar('button', `service-row${servico.identificador === selecionado ? ' is-selected' : ''}`);
    linha.type = 'button';
    linha.dataset.id = servico.identificador;
    linha.style.setProperty('--row-order', indice);
    const identificador = criar('span', 'service-id', `#${servico.identificador}`);
    const info = criar('span', 'service-info');
    info.append(criar('strong', 'service-title', servico.titulo), criar('small', 'service-category', servico.categoria));
    linha.append(identificador, info);
    elementos.lista.append(linha);
  });
}

function renderizarDetalhe() {
  const servico = selecionado === null ? null : catalogo.buscarId(selecionado);
  const habilitado = Boolean(servico);
  elementos.editar.disabled = !habilitado;
  elementos.excluir.disabled = !habilitado;
  elementos.detalheId.textContent = habilitado ? `ID ${servico.identificador}` : 'ID --';
  elementos.detalheCategoria.textContent = habilitado ? servico.categoria.toLocaleUpperCase('pt-BR') : 'SELECIONE UM SERVIÇO';
  elementos.detalheTitulo.textContent = habilitado ? servico.titulo : 'Cada nó\ntem seu lugar.';
  elementos.detalheDescricao.textContent = habilitado ? servico.descricao : 'Selecione um registro no catálogo para ver seus dados e acompanhar como ele se conecta à lista.';
  elementos.detalheRequisitos.textContent = habilitado ? servico.requisitos : '—';
  elementos.detalheLocal.textContent = habilitado ? servico.local : '—';
}

function renderizarNos() {
  elementos.nos.replaceChildren();
  let indice = 0;
  for (const servico of catalogo.percurso()) {
    if (indice > 0) {
      const seta = criar('span', 'node-arrow', '→');
      seta.setAttribute('aria-hidden', 'true');
      elementos.nos.append(seta);
    }
    const no = criar('button', `linked-node${servico.identificador === selecionado ? ' is-selected' : ''}`);
    no.type = 'button';
    no.dataset.nodeId = servico.identificador;
    no.title = `Selecionar ${servico.titulo}, ID ${servico.identificador}`;
    no.append(criar('span', 'node-id', `#${servico.identificador}`), criar('span', 'node-title', servico.titulo));
    elementos.nos.append(no);
    indice += 1;
  }
  if (indice) {
    const nulo = criar('span', 'node-null', '∅');
    nulo.title = 'Próximo nó: nulo';
    nulo.setAttribute('aria-label', 'Próximo: nulo');
    elementos.nos.append(nulo);
  } else {
    elementos.nos.append(criar('span', 'nodes-empty', 'A lista está vazia. Cadastre um serviço para criar o primeiro nó.'));
  }
}

function renderizarAnalise() {
  const contagens = new Map();
  for (const servico of catalogo.percurso()) {
    const chave = servico.categoria.trim().toLocaleLowerCase('pt-BR');
    const atual = contagens.get(chave) || { nome: servico.categoria.trim(), total: 0 };
    atual.total += 1;
    contagens.set(chave, atual);
  }
  const categorias = [...contagens.values()].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR')).slice(0, 4);
  const maior = Math.max(1, ...categorias.map((categoria) => categoria.total));
  elementos.barras.replaceChildren();
  categorias.forEach((categoria, indice) => {
    const linha = criar('div', `category-bar-row color-${indice}`);
    const nome = criar('span', 'bar-name', categoria.nome);
    const trilho = criar('span', 'bar-track');
    const barra = criar('span', 'bar-fill');
    barra.style.width = `${(categoria.total / maior) * 100}%`;
    trilho.append(barra);
    linha.append(nome, trilho, criar('strong', 'bar-count', String(categoria.total)));
    elementos.barras.append(linha);
  });
  if (!categorias.length) elementos.barras.append(criar('span', 'bars-empty', 'Cadastre serviços para ver as categorias.'));
}

function renderizar() {
  elementos.total.textContent = String(catalogo.tamanho).padStart(2, '0');
  const categorias = new Set([...catalogo.percurso()].map((servico) => servico.categoria.trim().toLocaleLowerCase('pt-BR')));
  elementos.categorias.textContent = String(categorias.size).padStart(2, '0');
  renderizarCatalogo();
  renderizarDetalhe();
  renderizarNos();
  renderizarAnalise();
}

function notificar(mensagem) {
  elementos.toast.textContent = mensagem;
  elementos.toast.classList.add('is-visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => elementos.toast.classList.remove('is-visible'), 2600);
}

function abrirFormulario(modo, servico = null) {
  elementos.formulario.reset();
  elementos.erro.hidden = true;
  document.querySelector('#form-mode').value = modo;
  document.querySelector('#form-eyebrow').textContent = modo === 'edit' ? 'EDITAR REGISTRO' : 'NOVO REGISTRO';
  document.querySelector('#form-title').textContent = modo === 'edit' ? 'Atualizar serviço' : 'Adicionar serviço';
  document.querySelector('#submit-service').innerHTML = modo === 'edit' ? 'Salvar alterações <span aria-hidden="true">→</span>' : 'Adicionar à lista <span aria-hidden="true">→</span>';
  document.querySelector('#form-id').disabled = modo === 'edit';
  if (servico) {
    document.querySelector('#form-id').value = servico.identificador;
    document.querySelector('#form-title-input').value = servico.titulo;
    document.querySelector('#form-category').value = servico.categoria;
    document.querySelector('#form-description').value = servico.descricao;
    document.querySelector('#form-requirements').value = servico.requisitos;
    document.querySelector('#form-location').value = servico.local;
  }
  elementos.dialogo.showModal();
  document.querySelector(modo === 'edit' ? '#form-title-input' : '#form-id').focus();
}

document.querySelector('#add-service').addEventListener('click', () => abrirFormulario('create'));
document.querySelector('#edit-service').addEventListener('click', () => {
  const servico = catalogo.buscarId(selecionado);
  if (servico) abrirFormulario('edit', servico);
});
document.querySelector('#delete-service').addEventListener('click', () => {
  const servico = catalogo.buscarId(selecionado);
  if (!servico) return;
  if (!window.confirm(`Excluir "${servico.titulo}" do catálogo?`)) return;
  catalogo.remover(selecionado);
  selecionado = null;
  elementos.status.textContent = `Nó #${servico.identificador} removido; ponteiros religados`;
  renderizar();
  notificar('Serviço removido da lista.');
});
document.querySelector('#close-dialog').addEventListener('click', () => elementos.dialogo.close());
document.querySelector('#cancel-dialog').addEventListener('click', () => elementos.dialogo.close());
elementos.formulario.addEventListener('submit', (evento) => {
  evento.preventDefault();
  const modo = document.querySelector('#form-mode').value;
  const identificador = Number(document.querySelector('#form-id').value);
  const dados = {
    titulo: document.querySelector('#form-title-input').value.trim(),
    categoria: document.querySelector('#form-category').value.trim(),
    descricao: document.querySelector('#form-description').value.trim(),
    requisitos: document.querySelector('#form-requirements').value.trim(),
    local: document.querySelector('#form-location').value.trim(),
  };
  if (modo === 'create') {
    if (catalogo.buscarId(identificador)) {
      elementos.erro.textContent = `O ID ${identificador} já existe. Escolha outro identificador.`;
      elementos.erro.hidden = false;
      return;
    }
    catalogo.inserir({ identificador, ...dados });
    selecionado = identificador;
    elementos.status.textContent = `Novo nó #${identificador} conectado ao final da lista`;
    notificar('Serviço conectado ao final da lista.');
  } else {
    catalogo.atualizar(identificador, dados);
    selecionado = identificador;
    elementos.status.textContent = `Dados do nó #${identificador} atualizados`;
    notificar('Alterações salvas.');
  }
  elementos.busca.value = '';
  elementos.dialogo.close();
  renderizar();
});

elementos.busca.addEventListener('input', () => {
  renderizarCatalogo();
  if (elementos.busca.value.trim()) {
    const total = [...catalogo.pesquisar(elementos.busca.value)].length;
    elementos.status.textContent = `${total} resultado${total === 1 ? '' : 's'} após percorrer a lista`;
  } else {
    elementos.status.textContent = 'Pronto para percorrer a lista';
  }
});
elementos.lista.addEventListener('click', (evento) => {
  const linha = evento.target.closest('[data-id]');
  if (!linha) return;
  selecionado = Number(linha.dataset.id);
  renderizar();
});
elementos.nos.addEventListener('click', (evento) => {
  const no = evento.target.closest('[data-node-id]');
  if (!no) return;
  selecionado = Number(no.dataset.nodeId);
  renderizar();
});
document.querySelector('#sort-services').addEventListener('click', () => {
  catalogo.ordenarPorTitulo();
  elementos.busca.value = '';
  elementos.status.textContent = 'Lista reordenada por título (insertion sort)';
  renderizar();
  notificar('Lista ordenada por título.');
});

document.querySelector('#traverse-list').addEventListener('click', async (evento) => {
  if (percursoAtivo || !catalogo.tamanho) return;
  percursoAtivo = true;
  const botao = evento.currentTarget;
  botao.disabled = true;
  const nos = [...document.querySelectorAll('.linked-node')];
  for (let indice = 0; indice < nos.length; indice += 1) {
    const no = nos[indice];
    no.classList.add('is-visiting');
    elementos.status.textContent = `Percorrendo nó #${no.dataset.nodeId} (${indice + 1} de ${nos.length})`;
    await new Promise((resolve) => setTimeout(resolve, 420));
    no.classList.remove('is-visiting');
  }
  elementos.status.textContent = `Percurso concluído: ${nos.length} nós visitados`;
  percursoAtivo = false;
  botao.disabled = false;
});

document.addEventListener('keydown', (evento) => {
  if (evento.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) && !elementos.dialogo.open) {
    evento.preventDefault();
    elementos.busca.focus();
  }
  if (evento.key === 'Escape' && document.activeElement === elementos.busca && elementos.busca.value) {
    elementos.busca.value = '';
    elementos.busca.dispatchEvent(new Event('input'));
  }
});

renderizar();
