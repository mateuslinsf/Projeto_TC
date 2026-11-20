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

        primeira_linha = arquivo.readline().split()

        n, m = map(int, primeira_linha)

        clausulas = []

        for linha in arquivo:
            valores = linha.split()

            if valores:
                a, b = map(int, valores)
                clausulas.append((a, b))

    if len(clausulas) != m:
        raise ValueError(
            f"Quantidade incorreta de cláusulas em {caminho.name}"
        )

    return n, m, clausulas


def medir_desempenho(n, clausulas, nome_arquivo):

    tempos = []

    resultado_referencia = None

    for repeticao in range(1, REPETICOES + 1):

        inicio = time.perf_counter()

        resultado = satisfaz_2sat(n, clausulas)

        fim = time.perf_counter()

        tempo = fim - inicio

        tempos.append(tempo)

        if resultado_referencia is None:
            resultado_referencia = resultado

        elif resultado != resultado_referencia:
            raise RuntimeError("Resultados inconsistentes!")

    media = statistics.mean(tempos)
    desvio = statistics.stdev(tempos)

    print(f"\nArquivo: {nome_arquivo}")
    print(f"Resultado: {'SAT' if resultado_referencia else 'UNSAT'}")
    print(f"Média: {media * 1000:.4f} ms")
    print(f"Desvio padrão: {desvio * 1000:.4f} ms")

    return {
        "arquivo": nome_arquivo,
        "variaveis": n,
        "clausulas": len(clausulas),
        "resultado": "SAT" if resultado_referencia else "UNSAT",
        "media_ms": media * 1000,
        "desvio_padrao_ms": desvio * 1000,
        "minimo_ms": min(tempos) * 1000,
        "maximo_ms": max(tempos) * 1000,
        "repeticoes": REPETICOES
    }, tempos


def main():

    PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(
        PASTA_ENTRADAS.glob("2sat_n*.txt"),
        key=lambda caminho: int(
            caminho.stem.replace("2sat_n", "")
        )
    )

    if not arquivos:
        raise FileNotFoundError("Nenhuma entrada encontrada!")

    resumos = []
    tempos_detalhados = []

    print("INICIANDO EXPERIMENTOS 2-SAT")
    print(f"Repetições por entrada: {REPETICOES}")

    for caminho in arquivos:

        n, m, clausulas = carregar_formula(caminho)

        resumo, tempos = medir_desempenho(
            n, clausulas, caminho.name
        )

        resumos.append(resumo)

        for i, tempo in enumerate(tempos, start=1):
            tempos_detalhados.append({
                "arquivo": caminho.name,
                "variaveis": n,
                "clausulas": m,
                "repeticao": i,
                "tempo_ms": tempo * 1000
            })

    with open(
        PASTA_RESULTADOS / "2sat_python_resumo.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=resumos[0].keys()
        )

        escritor.writeheader()
        escritor.writerows(resumos)

    with open(
        PASTA_RESULTADOS / "2sat_python_tempos.csv",
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=tempos_detalhados[0].keys()
        )

        escritor.writeheader()
        escritor.writerows(tempos_detalhados)

    print("\nEXPERIMENTOS CONCLUÍDOS!")
    print("Resultados salvos na pasta resultados/")


if __name__ == "__main__":
    main()