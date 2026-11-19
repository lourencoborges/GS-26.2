"""Citizen Assist AI — catálogo de serviços e orientações ao cidadão.

Estruturas e algoritmos didáticos: lista simplesmente encadeada, busca linear
e ordenação por insertion sort. Execute com: python main.py
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Servico:
    identificador: int
    titulo: str
    categoria: str
    descricao: str
    requisitos: str
    local: str


class No:
    def __init__(self, servico: Servico):
        self.servico = servico
        self.proximo: Optional["No"] = None


class ListaServicos:
    """Lista simplesmente encadeada; não usa listas nativas para armazenar nós."""

    def __init__(self):
        self.inicio: Optional[No] = None
        self.tamanho = 0

    def buscar_id(self, identificador: int) -> Optional[Servico]:
        atual = self.inicio
        while atual:
            if atual.servico.identificador == identificador:
                return atual.servico
            atual = atual.proximo
        return None

    def inserir(self, servico: Servico) -> bool:
        if self.buscar_id(servico.identificador):
            return False
        novo = No(servico)
        if self.inicio is None:
            self.inicio = novo
        else:
            atual = self.inicio
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo
        self.tamanho += 1
        return True

    def remover(self, identificador: int) -> bool:
        anterior = None
        atual = self.inicio
        while atual:
            if atual.servico.identificador == identificador:
                if anterior is None:
                    self.inicio = atual.proximo
                else:
                    anterior.proximo = atual.proximo
                self.tamanho -= 1
                return True
            anterior, atual = atual, atual.proximo
        return False

    def percurso(self):
        atual = self.inicio
        while atual:
            yield atual.servico
            atual = atual.proximo

    def pesquisar(self, termo: str):
        termo = termo.casefold().strip()
        atual = self.inicio
        while atual:
            s = atual.servico
            if termo in s.titulo.casefold() or termo in s.categoria.casefold():
                yield s
            atual = atual.proximo

    def atualizar(self, identificador: int, dados: Servico) -> bool:
        existente = self.buscar_id(identificador)
        if existente is None:
            return False
        existente.titulo = dados.titulo
        existente.categoria = dados.categoria
        existente.descricao = dados.descricao
        existente.requisitos = dados.requisitos
        existente.local = dados.local
        return True

    def ordenar_por_titulo(self):
        """Insertion sort in-place por religações de nós; estável, O(n²)."""
        ordenada: Optional[No] = None
        atual = self.inicio
        while atual:
            proximo = atual.proximo
            if ordenada is None or atual.servico.titulo.casefold() < ordenada.servico.titulo.casefold():
                atual.proximo = ordenada
                ordenada = atual
            else:
                cursor = ordenada
                while (cursor.proximo and
                       cursor.proximo.servico.titulo.casefold() <= atual.servico.titulo.casefold()):
                    cursor = cursor.proximo
                atual.proximo = cursor.proximo
                cursor.proximo = atual
            atual = proximo
        self.inicio = ordenada

    def resumo_categorias(self):
        contagens = {}
        for servico in self.percurso():
            chave = servico.categoria.strip().casefold()
            if chave not in contagens:
                contagens[chave] = [servico.categoria.strip(), 0]
            contagens[chave][1] += 1
        return sorted(contagens.values(), key=lambda item: item[0].casefold())


def ler_inteiro(mensagem: str) -> int:
    while True:
        entrada = input(mensagem).strip()
        try:
            return int(entrada)
        except ValueError:
            print("Entrada inválida: informe um número inteiro.")


def ler_texto(mensagem: str, atual: Optional[str] = None) -> str:
    while True:
        sufixo = f" [{atual}]" if atual is not None else ""
        valor = input(f"{mensagem}{sufixo}: ").strip()
        if atual is not None and not valor:
            return atual
        if valor:
            return valor
        print("Este campo não pode ficar vazio.")


def ler_servico(identificador: int, existente: Optional[Servico] = None) -> Servico:
    print("Preencha os dados" + (" (Enter mantém o valor atual)" if existente else ":"))
    return Servico(
        identificador,
        ler_texto("Título", existente.titulo if existente else None),
        ler_texto("Categoria", existente.categoria if existente else None),
        ler_texto("Descrição", existente.descricao if existente else None),
        ler_texto("Requisitos", existente.requisitos if existente else None),
        ler_texto("Local de atendimento", existente.local if existente else None),
    )


def exibir(servico: Servico):
    print(f"\nID: {servico.identificador} | {servico.titulo} [{servico.categoria}]")
    print(f"Descrição: {servico.descricao}")
    print(f"Requisitos: {servico.requisitos}")
    print(f"Local: {servico.local}")


def exibir_varios(servicos):
    encontrou = False
    for servico in servicos:
        exibir(servico)
        encontrou = True
    if not encontrou:
        print("Nenhum serviço encontrado.")


def menu():
    catalogo = ListaServicos()
    while True:
        print("""
=== CITIZEN ASSIST AI ===
1. Cadastrar serviço/orientação
2. Consultar por identificador
3. Atualizar registro
4. Excluir registro
5. Pesquisar por título ou categoria
6. Listar todos
7. Ordenar por título
8. Análise do catálogo
0. Encerrar
""")
        opcao = input("Escolha uma opção: ").strip()
        if opcao == "1":
            identificador = ler_inteiro("Identificador: ")
            if catalogo.buscar_id(identificador):
                print("Já existe um registro com esse identificador.")
                continue
            catalogo.inserir(ler_servico(identificador))
            print("Registro cadastrado.")
        elif opcao == "2":
            servico = catalogo.buscar_id(ler_inteiro("Identificador: "))
            if servico:
                exibir(servico)
            else:
                print("Nenhum registro encontrado com esse identificador.")
        elif opcao == "3":
            identificador = ler_inteiro("Identificador a atualizar: ")
            servico = catalogo.buscar_id(identificador)
            if not servico:
                print("Nenhum registro encontrado.")
            else:
                catalogo.atualizar(identificador, ler_servico(identificador, servico))
                print("Registro atualizado.")
        elif opcao == "4":
            if catalogo.remover(ler_inteiro("Identificador a excluir: ")):
                print("Registro excluído.")
            else:
                print("Nenhum registro encontrado.")
        elif opcao == "5":
            termo = input("Termo para título ou categoria: ").strip()
            if not termo:
                print("Informe um termo para pesquisa.")
            else:
                exibir_varios(catalogo.pesquisar(termo))
        elif opcao == "6":
            if catalogo.tamanho == 0:
                print("Catálogo vazio.")
            else:
                exibir_varios(catalogo.percurso())
        elif opcao == "7":
            catalogo.ordenar_por_titulo()
            print("Registros ordenados por título.")
            exibir_varios(catalogo.percurso())
        elif opcao == "8":
            print(f"Total de registros: {catalogo.tamanho}")
            categorias = catalogo.resumo_categorias()
            if not categorias:
                print("Ainda não há categorias cadastradas.")
            else:
                print("Quantidade por categoria:")
                for nome, quantidade in categorias:
                    print(f"- {nome}: {quantidade}")
        elif opcao == "0":
            print("Até logo!")
            break
        else:
            print("Opção inválida. Escolha uma opção do menu.")


if __name__ == "__main__":
    menu()
