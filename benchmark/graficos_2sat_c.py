import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "resultados"
PASTA_GRAFICOS = PASTA_RESULTADOS / "graficos"

CASOS = ["aleatorio", "sat", "unsat"]
ROTULOS = {"aleatorio": "Aleatório", "sat": "SAT forçado", "unsat": "UNSAT forçado"}


def carregar_csv(caminho):
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def filtrar(dados, linguagem=None, caso=None):
    linhas = [
        d for d in dados
        if (linguagem is None or d["linguagem"] == linguagem)
        and (caso is None or d["caso"] == caso)
    ]
    return sorted(linhas, key=lambda d: int(d["n"]))


def salvar(nome):
    plt.tight_layout()
    plt.savefig(PASTA_GRAFICOS / nome, dpi=300)
    plt.close()


def grafico_tempo_c(tempos):
    plt.figure(figsize=(9, 5))

    for caso in CASOS:
        dados = filtrar(tempos, "C", caso)
        x = [int(d["n"]) for d in dados]
        y = [float(d["media_ms"]) for d in dados]
        erro = [float(d["desvio_ms"]) for d in dados]
        plt.errorbar(x, y, yerr=erro, marker="o", capsize=4, label=ROTULOS[caso])

    dados = filtrar(tempos, "C", "aleatorio")
    x = [int(d["n"]) for d in dados]
    ref = [(int(d["n"]) + int(d["m"])) for d in dados]
    escala = float(dados[0]["media_ms"]) / ref[0]
    plt.plot(x, [escala * r for r in ref], "k--", label="Teórico O(n + m)")

    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("Quantidade de variáveis (n)")
    plt.ylabel("Tempo médio (ms)")
    plt.title("2-SAT em C: tempo medido × O(n + m)")
    plt.legend()
    plt.grid(True, which="both", alpha=0.4)
    salvar("2sat_c_tempo.png")


def grafico_razao_c(tempos):
    plt.figure(figsize=(9, 5))

    for caso in CASOS:
        dados = filtrar(tempos, "C", caso)
        x = [int(d["n"]) for d in dados]
        y = [
            float(d["media_ms"]) * 1e6 / (int(d["n"]) + int(d["m"]))
            for d in dados
        ]
        plt.plot(x, y, marker="o", label=ROTULOS[caso])

    plt.xscale("log", base=2)
    plt.ylim(bottom=0)
    plt.xlabel("Quantidade de variáveis (n)")
    plt.ylabel("T(n) / (n + m)  (ns por unidade)")
    plt.title("2-SAT em C: razão T(n) / (n + m)")
    plt.legend()
    plt.grid(True, which="both", alpha=0.4)
    salvar("2sat_c_razao.png")


def grafico_c_vs_python(tempos):
    plt.figure(figsize=(9, 5))

    for linguagem, estilo in (("C", "o-"), ("Python", "s--")):
        dados = filtrar(tempos, linguagem, "aleatorio")
        x = [int(d["n"]) for d in dados]
        y = [float(d["media_ms"]) for d in dados]
        erro = [float(d["desvio_ms"]) for d in dados]
        plt.errorbar(x, y, yerr=erro, fmt=estilo, capsize=4, label=linguagem)

    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("Quantidade de variáveis (n)")
    plt.ylabel("Tempo médio (ms)")
    plt.title("2-SAT: C × Python (entradas aleatórias)")
    plt.legend()
    plt.grid(True, which="both", alpha=0.4)
    salvar("2sat_c_vs_python.png")


def grafico_razao_c_vs_python(tempos):
    plt.figure(figsize=(9, 5))

    for linguagem in ("C", "Python"):
        dados = filtrar(tempos, linguagem, "aleatorio")
        x = [int(d["n"]) for d in dados]
        y = [
            float(d["media_ms"]) * 1e6 / (int(d["n"]) + int(d["m"]))
            for d in dados
        ]
        plt.plot(x, y, marker="o", label=linguagem)

    plt.xscale("log", base=2)
    plt.yscale("log")
    plt.xlabel("Quantidade de variáveis (n)")
    plt.ylabel("T(n) / (n + m)  (ns por unidade)")
    plt.title("2-SAT: razão T(n) / (n + m), C × Python")
    plt.legend()
    plt.grid(True, which="both", alpha=0.4)
    salvar("2sat_c_vs_python_razao.png")


def grafico_memoria(memoria):
    plt.figure(figsize=(9, 5))

    dados = sorted(
        [d for d in memoria if d["caso"] == "aleatorio"],
        key=lambda d: int(d["n"])
    )
    x = [int(d["n"]) + int(d["m"]) for d in dados]
    estruturas = [int(d["memoria_bytes"]) / 1e6 for d in dados]
    pico = [int(d["pico_rss_bytes"]) / 1e6 for d in dados if d["pico_rss_bytes"]]

    plt.plot(x, estruturas, marker="o", label="Estruturas do algoritmo")
    if pico:
        plt.plot(x[:len(pico)], pico, marker="s", label="Pico de memória do processo (RSS)")

    escala = estruturas[0] / x[0]
    plt.plot(x, [escala * v for v in x], "k--", label="Teórico O(n + m)")

    plt.xlabel("n + m")
    plt.ylabel("Memória (MB)")
    plt.title("2-SAT em C: memória × O(n + m)")
    plt.legend()
    plt.grid(True, alpha=0.4)
    salvar("2sat_c_memoria.png")


def main():
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    tempos = carregar_csv(PASTA_RESULTADOS / "2sat_c_vs_python.csv")
    memoria = carregar_csv(PASTA_RESULTADOS / "2sat_c_memoria.csv")

    grafico_tempo_c(tempos)
    grafico_razao_c(tempos)
    grafico_c_vs_python(tempos)
    grafico_razao_c_vs_python(tempos)
    grafico_memoria(memoria)

    print(f"Gráficos salvos em {PASTA_GRAFICOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
