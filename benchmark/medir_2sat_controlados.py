import csv
import sys
import time
import statistics
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(RAIZ / "python"))

from sat2 import satisfaz_2sat

REPETICOES = 20

PASTA_ENTRADAS = RAIZ / "gerador" / "entradas"
PASTA_RESULTADOS = RAIZ / "resultados"


def carregar_formula(caminho):
    with open(caminho, "r", encoding="utf-8") as arquivo:
        n, m = map(int, arquivo.readline().split())

        clausulas = []

        for linha in arquivo:
            valores = linha.split()

            if valores:
                a, b = map(int, valores)
                clausulas.append((a, b))

    if len(clausulas) != m:
        raise ValueError(f"Quantidade incorreta de cláusulas: {caminho.name}")

    return n, m, clausulas


def medir_desempenho(n, clausulas, nome_arquivo, tipo):

    resultado_esperado = tipo == "sat"
    resultado = satisfaz_2sat(n, clausulas)

    if resultado != resultado_esperado:
        raise RuntimeError(
            f"Resultado incorreto em {nome_arquivo}: "
            f"esperado {resultado_esperado}, obtido {resultado}"
        )

    tempos = []

    for _ in range(REPETICOES):
        inicio = time.perf_counter()

        resultado = satisfaz_2sat(n, clausulas)

        fim = time.perf_counter()

        if resultado != resultado_esperado:
            raise RuntimeError(f"Resultado inconsistente: {nome_arquivo}")

        tempos.append(fim - inicio)

    media = statistics.mean(tempos)
    desvio = statistics.stdev(tempos)

    print(f"\nTipo: {tipo.upper()}")
    print(f"Arquivo: {nome_arquivo}")
    print(f"Resultado: {'SAT' if resultado else 'UNSAT'}")
    print(f"Média: {media * 1000:.4f} ms")
    print(f"Desvio padrão: {desvio * 1000:.4f} ms")

    resumo = {
        "tipo": tipo.upper(),
        "arquivo": nome_arquivo,
        "variaveis": n,
        "clausulas": len(clausulas),
        "resultado": "SAT" if resultado else "UNSAT",
        "media_ms": media * 1000,
        "desvio_padrao_ms": desvio * 1000,
        "minimo_ms": min(tempos) * 1000,
        "maximo_ms": max(tempos) * 1000,
        "repeticoes": REPETICOES
    }

    detalhados = []

    for i, tempo in enumerate(tempos, start=1):
        detalhados.append({
            "tipo": tipo.upper(),
            "arquivo": nome_arquivo,
            "variaveis": n,
            "clausulas": len(clausulas),
            "repeticao": i,
            "tempo_ms": tempo * 1000
        })

    return resumo, detalhados


def main():

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    resumos = []
    tempos_detalhados = []

    print("INICIANDO EXPERIMENTOS 2-SAT CONTROLADOS")
    print(f"Repetições por entrada: {REPETICOES}")

    for tipo in ["sat", "unsat"]:

        pasta = PASTA_ENTRADAS / tipo

        arquivos = sorted(
            pasta.glob("2sat_n*.txt"),
            key=lambda caminho: int(
                caminho.stem.replace("2sat_n", "")
            )
        )

        if len(arquivos) != 6:
            raise FileNotFoundError(
                f"Esperados 6 arquivos na pasta {pasta}"
            )

        for caminho in arquivos:

            n, m, clausulas = carregar_formula(caminho)

            resumo, detalhados = medir_desempenho(
                n, clausulas, caminho.name, tipo
            )

            resumos.append(resumo)
            tempos_detalhados.extend(detalhados)

    arquivo_resumo = PASTA_RESULTADOS / "2sat_python_controlados_resumo.csv"
    arquivo_tempos = PASTA_RESULTADOS / "2sat_python_controlados_tempos.csv"

    with open(arquivo_resumo, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=resumos[0].keys()
        )

        escritor.writeheader()
        escritor.writerows(resumos)

    with open(arquivo_tempos, "w", newline="", encoding="utf-8-sig") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=tempos_detalhados[0].keys()
        )

        escritor.writeheader()
        escritor.writerows(tempos_detalhados)

    print("\nEXPERIMENTOS CONCLUÍDOS!")
    print("12 entradas processadas.")
    print(f"{len(tempos_detalhados)} medições realizadas.")
    print("Resultados salvos na pasta resultados/")


if __name__ == "__main__":
    main()