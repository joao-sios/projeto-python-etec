import queue
import threading
import tkinter as tk
from math import ceil
from time import monotonic
from tinkter import messagebox, ttk 

from .config import INTERVALO_ENTRE_TESTES
from .speed_test import executar_teste 

fila = queue.Queue()
proximo_teste = 0

def atualizar_progresso(porcentagem, mensagem):
    fila.put(("progresso", porcentagem, mensagem))

def realizar_teste():
    try:
        resultado = executar_teste(atualizar_progresso)
        fila.put(("resultado", resultado))
    except Exception as erro:
        fila.put(("erro", str(erro)))

def iniciar_teste():
    global proximo_teste

    segundos_restantes = ceil(proximo_teste - monotonic())
    if segundos_restantes > 0:
        messagebox.showinfo(
            "Aguarde",
            f"Um novo teste poderá ser iniciado em {segundos_restantes} segundos.",
        )
        return
    
    botao_iniciar.config(state = "disabled")
    barra_progresso["value"] = 0
    texto_status.config(text="Iniciando...")

    valor_latencia.config(text="-- ms")
    valor_jitter.config(text="-- ms")
    valor_download.config(text="--mbps")
    valor_upload.config(text="--mbps")

    threading.Thread(target=realizar_teste, daemon=True).start()

def iniciar_intervalo():
    global proximo_teste
    proximo_teste = monotonic() + INTERVALO_ENTRE_TESTES
    atualizar_intervalo()

def atualizar_intervalo():
    segundos_restantes = ceil(proximo_teste - monotonic())

    if segundos_restantes > 0:
        botao_iniciar.config(
            state="disabled",
            text=f"Aguarde {segundos_restantes}s",
        )
        janela.after(1000, atualizar_intervalo)
    else:
        botao_iniciar.config(state="normal", text="Iniciar teste")


def verificar_fila():
    while not fila.empty():
        mensagem = fila.get()

        if mensagem[0] == "progresso":
            barra_progresso["value"] = mensagem[1]
            texto_status.config(text=mensagem[2])

        elif mensagem[0] == "resultado":
            resultado = mensagem[1]
            valor_latencia.config(
                text=formatar_resultado(resultado["latencia"], "ms")
            )
            valor_jitter.config(text=formatar_resultado(resultado["jitter"], "ms"))
            valor_download.config(text=formatar_resultado(resultado["download"], "mbps"))
            valor_upload.config(text=formatar_resultado(resultado["upload"], "mbps"))
            iniciar_intervalo()

        elif mensagem[0] == "erro":
            texto_status.config(text="Não foi possível concluir o teste.")
            iniciar_intervalo()
            messgaebox.showerror("Erro", mensagem[1])

    janela.after(100, verificar_fila)

def formatar_resultado(valor, unidade):
    if abs(valor) >= 100_000:
        return f"{valor:.2e} {unidade}"
    return f"{valor:.2f} {unidade}"