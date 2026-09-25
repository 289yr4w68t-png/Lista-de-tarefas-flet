import flet as ft
import json
import os
import uuid
from datetime import datetime


ARQUIVO = "tarefas.json"


def main(page: ft.Page):

    page.title = "Lista de Tarefas"
    page.padding = 20
    page.bgcolor = "#F5F7FA"

    tarefas = []

    def carregar_tarefas():
        nonlocal tarefas

        if os.path.exists(ARQUIVO):
            try:
                with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                    tarefas = json.load(arquivo)
            except:
                tarefas = []
        else:
            tarefas = []

    def salvar_tarefas():
        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            json.dump(
                tarefas,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    campo_tarefa = ft.TextField(
        label="Digite uma tarefa",
        hint_text="Ex: Fazer trabalho de Flet",
        expand=True
    )

    campo_busca = ft.TextField(
        label="Pesquisar",
        hint_text="Pesquisar tarefa...",
        prefix_icon=ft.Icons.SEARCH,
        expand=True
    )

    lista_tarefas = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    contador = ft.Text(
        "0 tarefas",
        size=14,
        color="#666666"
    )

    def atualizar_lista(e=None):

        lista_tarefas.controls.clear()

        pesquisa = campo_busca.value.lower().strip()

        tarefas_encontradas = []

        for tarefa in tarefas:
            if pesquisa in tarefa["titulo"].lower():
                tarefas_encontradas.append(tarefa)

        for tarefa in tarefas_encontradas:
            criar_item_tarefa(tarefa)

        total = len(tarefas)

        concluidas = 0

        for tarefa in tarefas:
            if tarefa["concluida"]:
                concluidas += 1

        pendentes = total - concluidas

        contador.value = (
            f"{total} tarefa(s) - "
            f"{pendentes} pendente(s) - "
            f"{concluidas} concluida(s)"
        )

        page.update()

    def criar_item_tarefa(tarefa):

        checkbox = ft.Checkbox(
            value=tarefa["concluida"],
            on_change=lambda e: concluir_tarefa(
                tarefa["id"],
                e.control.value
            )
        )

        texto = ft.Text(
            tarefa["titulo"],
            size=16,
            expand=True
        )

        if tarefa["concluida"]:
            texto.style = ft.TextStyle(
                decoration=ft.TextDecoration.LINE_THROUGH,
                color="#888888"
            )

        botao_editar = ft.IconButton(
            icon=ft.Icons.EDIT,
            tooltip="Editar",
            on_click=lambda e: abrir_edicao(
                tarefa["id"]
            )
        )

        botao_excluir = ft.IconButton(
            icon=ft.Icons.DELETE,
            tooltip="Excluir",
            on_click=lambda e: confirmar_exclusao(
                tarefa["id"]
            )
        )

        linha = ft.Container(
            content=ft.Row(
                controls=[
                    checkbox,
                    texto,
                    botao_editar,
                    botao_excluir
                ]
            ),
            padding=10,
            bgcolor="white",
            border_radius=10,
            border=ft.Border.all(
                1,
                "#DDDDDD"
            )
        )

        lista_tarefas.controls.append(linha)

    def adicionar_tarefa(e):

        titulo = campo_tarefa.value.strip()

        if titulo == "":
            mostrar_mensagem(
                "Digite uma tarefa antes de adicionar."
            )
            return

        nova_tarefa = {
            "id": str(uuid.uuid4()),
            "titulo": titulo,
            "concluida": False,
            "data": datetime.now().strftime(
                "%d/%m/%Y %H:%M"
            )
        }

        tarefas.append(nova_tarefa)

        salvar_tarefas()

        campo_tarefa.value = ""

        atualizar_lista()

    def concluir_tarefa(id_tarefa, concluida):

        for tarefa in tarefas:

            if tarefa["id"] == id_tarefa:
                tarefa["concluida"] = concluida
                break

        salvar_tarefas()

        atualizar_lista()

    def abrir_edicao(id_tarefa):

        tarefa_encontrada = None

        for tarefa in tarefas:

            if tarefa["id"] == id_tarefa:
                tarefa_encontrada = tarefa
                break

        if tarefa_encontrada is None:
            return

        campo_edicao = ft.TextField(
            label="Nova tarefa",
            value=tarefa_encontrada["titulo"]
        )

        def salvar_edicao(e):

            novo_titulo = campo_edicao.value.strip()

            if novo_titulo == "":
                return

            tarefa_encontrada["titulo"] = novo_titulo

            salvar_tarefas()

            page.pop_dialog()

            atualizar_lista()

        dialogo = ft.AlertDialog(
            title=ft.Text(
                "Editar tarefa"
            ),
            content=campo_edicao,
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),
                ft.Button(
                    "Salvar",
                    on_click=salvar_edicao
                )
            ]
        )

        page.show_dialog(dialogo)

    def confirmar_exclusao(id_tarefa):

        tarefa_encontrada = None

        for tarefa in tarefas:

            if tarefa["id"] == id_tarefa:
                tarefa_encontrada = tarefa
                break

        if tarefa_encontrada is None:
            return

        def excluir(e):

            nonlocal tarefas

            tarefas = [
                tarefa
                for tarefa in tarefas
                if tarefa["id"] != id_tarefa
            ]

            salvar_tarefas()

            page.pop_dialog()

            atualizar_lista()

        dialogo = ft.AlertDialog(
            title=ft.Text(
                "Excluir tarefa"
            ),
            content=ft.Text(
                f'Você deseja excluir '
                f'"{tarefa_encontrada["titulo"]}"?'
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=lambda e:
                    page.pop_dialog()
                ),
                ft.Button(
                    "Excluir",
                    on_click=excluir
                )
            ]
        )

        page.show_dialog(dialogo)

    def mostrar_mensagem(texto):

        dialogo = ft.AlertDialog(
            title=ft.Text(
                "Atenção"
            ),
            content=ft.Text(
                texto
            ),
            actions=[
                ft.TextButton(
                    "OK",
                    on_click=lambda e:
                    page.pop_dialog()
                )
            ]
        )

        page.show_dialog(dialogo)

    botao_adicionar = ft.Button(
        "Adicionar",
        icon=ft.Icons.ADD,
        on_click=adicionar_tarefa
    )

    titulo = ft.Text(
        "Minha Lista de Tarefas",
        size=30,
        weight=ft.FontWeight.BOLD,
        color="#222222"
    )

    subtitulo = ft.Text(
        "Organize suas tarefas de forma simples.",
        size=14,
        color="#666666"
    )

    campo_busca.on_change = atualizar_lista

    page.add(
        ft.Column(
            controls=[
                titulo,
                subtitulo,
                ft.Divider(),
                ft.Row(
                    controls=[
                        campo_tarefa,
                        botao_adicionar
                    ]
                ),
                ft.Row(
                    controls=[
                        campo_busca,
                        contador
                    ]
                ),
                ft.Divider(),
                lista_tarefas
            ],
            expand=True
        )
    )

    carregar_tarefas()

    atualizar_lista()


if __name__ == "__main__":
    ft.run(main)