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

def calcular_mbps(bytes, tempo):
    retun(bytes*8)/(tempo*1_000_000)

def calcular_jitter(latencias):
    diferencas = []

    for indice in range(1, len(latencias)):
        diferenca = abs(latencias[indice] - latencias[indice - 1])
        diferencas.append(diferenca)
    
    return mean(diferencas) if diferencas else 0

def verificar_conexao(cliente, urls=URLS_CONEXAO):
    for url in urls:
        try:
            resposta = cliente.get(url)
            if resposta.status_code < 500:
                return True
        except httpx.HTTPError:
            continue
        
        return False

def medir_latencia(cliente, repeticoes=5):
    latencias = []

    for numero in range(repeticoes):
        inicio = perf_counter()
        resposta = cliente.get(
            URL_DOWNLOAD,
            params ={"bytes": 0, "tentativa": numero, "cache": time_ns()},
        )
        validar_resposta(resposta)
        fim = perf_counter()
        latencias.append((fim - inicio)*1000)

    return mean(latencias), calcular_jitter(latencias)

def medir_download(cliente, tamanho=TAMANHO_DOWNLOAD):
    bytes_recebidos = 0
    inicio = perf_counter()

    with cliente.stream(
        "GET",
        URL_DOWNLOAD,
        params={"bytes": tamanho, "cache" : time_ns()},   
    ) as respostas:
        validar_resposta(resposta)

        for bloco in resposta.iter_bytes():
            bytes_recebidos += len(bloco)

    tempo = perf_counter() - inicio
    return calcular_mbps(bytes_recebidos, tempo)

def medir_upload(cliente,tamanho=TAMANHO_UPLOAD):
   dados = bytes(tamanho) 
   inicio = perf_counter()
   resposta = cliente.post(URL_UPLOAD, content=dados)
   validar_resposta(resposta)

   tempo = perf_counter() - inicio
   return calcular_mbps(tamanho, tempo)

def executar_teste(atualizar_progresso):
    with httpx.Client(timeout = 20,follow_redirects=True) as cliente:
        atualizar_progresso(10, "Verificando a conexão...")
        if not verificar_conexao(cliente):
            raise ConnectionError("Não foi possível conectar a internet.")

        atualizar_progresso(30,"Medindo a latência...")
        latencia, jitter = medir_latencia(cliente)

        atualizar_progresso(55, "Medindo download...")
        download = medir_download(cliente)

        atualizar_progresso(80, "Medindo o upload...")
        upload = medir_upload(cliente)

        atualizar_progresso(100, "Teste concluído.")

        return {
            "latencia": round(latencia, 2),
            "jitter": round(jitter, 2),
            "download": round(download, 2),
            "upload": round(upload, 2),
        }