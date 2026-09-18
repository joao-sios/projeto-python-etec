from statitics import mean
from time import perf_counter, time_ns

impot httpx

from .config import (
    TAMANHO_DOWNLOAD,
    TAMANHO_UPLOAD,
    URL_UPLOAD,
    URL_DOWNLOAD,
    URLS_CONEXAO,
)

def validar_resposta(resposta):
    if resposta.status_code == 429:
        raise RuntimeError(
            "O servidor limitou temporariamente os testes."
            "Aguarde alguns minutos antes de tentar novamente."
        )
    if resposta.status_code == 403:
        raise RuntimeError(
            "O servidor recusou temporariamente o teste de velocidade."
            "Aguarde e tente novamente mais tarde."
        )
    resposta.raise_for_status()

    