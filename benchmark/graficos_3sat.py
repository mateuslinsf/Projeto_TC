"""Gera os gráficos do 3-SAT (DPLL em C) a partir de resultados/3sat_tempos.csv.

Uso: python benchmark/graficos_3sat.py   (requer matplotlib)
Saída: resultados/graficos/3sat_*.png
"""

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator

RAIZ = Path(__file__).resolve().parents[1]
PASTA_RESULTADOS = RAIZ / "resultados"
PASTA_GRAFICOS = PASTA_RESULTADOS / "graficos"
LIMITE_MS = 60_000

# Cada caso tem sempre a mesma cor em todos os gráficos.
COR = {"melhor": "#2a78d6", "aleatorio": "#eb6834", "pior": "#1baf7a", "2sat": "#eda100"}
MARCADOR = {"melhor": "o", "aleatorio": "s", "pior": "^", "2sat": "D"}
ROTULO = {"melhor": "Melhor caso", "aleatorio": "Aleatório (m = 4,26·n)",
          "pior": "Pior caso", "2sat": "2-SAT (Kosaraju, C)"}
TINTA, TINTA_2, MUDO, GRADE, EIXO = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": ["Segoe UI", "DejaVu Sans"],
    "font.size": 10,
    "text.color": TINTA,
    "axes.labelcolor": TINTA_2,
    "axes.edgecolor": EIXO,
    "axes.linewidth": 0.8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "grid.color": GRADE,
    "grid.linewidth": 0.6,
    "xtick.color": MUDO,
    "ytick.color": MUDO,
    "xtick.labelcolor": TINTA_2,
    "ytick.labelcolor": TINTA_2,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def br(v, _=None):
    """Número no formato brasileiro: 1.000 / 0,5."""
    if v >= 1:
        return f"{v:,.0f}".replace(",", ".")
    return f"{v:g}".replace(".", ",")


def carregar():
    with open(PASTA_RESULTADOS / "3sat_tempos.csv", encoding="utf-8-sig") as f:
        linhas = list(csv.DictReader(f))
    por = defaultdict(lambda: defaultdict(list))
    for d in linhas:
        por[d["caso"]][int(d["n"])].append(d)
    return por


def resumo(por, caso):
    """Lista de (n, m, media_ms, [medias por instancia], memoria_bytes) em ordem de n."""
    saida = []
    for n in sorted(por[caso]):
        rs = por[caso][n]
        medias = [float(r["media_ms"]) for r in rs]
        saida.append((n, int(rs[0]["m"]), statistics.mean(medias), medias, int(rs[0]["memoria_bytes"])))
    return saida


def viaveis(por):
    with open(PASTA_RESULTADOS / "3sat_maior_n_viavel.csv", encoding="utf-8-sig") as f:
        return {d["caso"]: int(d["maior_n_viavel"]) for d in csv.DictReader(f)}


def ajustar_escala(medido, teorico):
    """Constante c que melhor encaixa c·teorico nos pontos medidos (média geométrica das razões)."""
    return math.exp(statistics.mean(math.log(m / t) for m, t in zip(medido, teorico)))


def linha(ax, x, y, caso, rotulo=None):
    ax.plot(x, y, color=COR[caso], marker=MARCADOR[caso], linewidth=2, markersize=6,
            markeredgecolor="white", markeredgewidth=1.2, label=rotulo or ROTULO[caso], zorder=3)


def teorica(ax, x, y, rotulo, zorder=2):
    ax.plot(x, y, color=TINTA_2, linestyle="--", linewidth=1.4, label=rotulo, zorder=zorder)


def rotulo_final(ax, x, y, texto, dx=6, dy=0):
    ax.annotate(texto, (x, y), xytext=(dx, dy), textcoords="offset points",
                color=TINTA_2, fontsize=9, va="center")


def eixo_log(ax, eixo="y"):
    alvo = ax.yaxis if eixo == "y" else ax.xaxis
    alvo.set_major_locator(LogLocator(base=10, numticks=12))
    alvo.set_major_formatter(FuncFormatter(br))


def salvar(fig, nome):
    fig.tight_layout()
    fig.savefig(PASTA_GRAFICOS / nome, dpi=300)
    plt.close(fig)


# 1. Teórico x medido, um painel por caso
def grafico_tempo(por):
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.6))

    # Melhor caso: Θ(n + m)
    ax = axs[0]
    dados = resumo(por, "melhor")
    x = [d[0] for d in dados]
    y = [d[2] for d in dados]
    ref = [d[0] + d[1] for d in dados]
    c = ajustar_escala(y, ref)
    linha(ax, x, y, "melhor", "Medido")
    teorica(ax, x, [c * r for r in ref], "Teórico Θ(n + m)")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(FuncFormatter(br))
    eixo_log(ax)
    ax.set_title("Melhor caso: próximo do linear")
    ax.set_xlabel("Variáveis (n)")
    ax.set_ylabel("Tempo médio (ms)")
    ax.legend(loc="upper left")

    # Caso aleatório: instâncias + média + ajuste exponencial
    ax = axs[1]
    dados = resumo(por, "aleatorio")
    dados = [d for d in dados if len(d[3]) > 1]  # n=160 tem só 1 instância medida
    for n, _, _, medias, _ in dados:
        ax.scatter([n] * len(medias), medias, s=10, color=COR["aleatorio"], alpha=0.25,
                   linewidths=0, zorder=2)
    x = [d[0] for d in dados]
    y = [d[2] for d in dados]
    linha(ax, x, y, "aleatorio", "Média das 15 instâncias")
    cauda = [(n, t) for n, t in zip(x, y) if n >= 28]
    b, a = _regressao([n for n, _ in cauda], [math.log2(t) for _, t in cauda])
    xs = list(range(cauda[0][0], x[-1] + 1))
    teorica(ax, xs, [2 ** (a + b * n) for n in xs], f"Ajuste exponencial ≈ 2^(n/{1 / b:.1f})")
    ax.set_yscale("log")
    eixo_log(ax)
    ax.set_title("Caso aleatório: exponencial")
    ax.set_xlabel("Variáveis (n)")
    ax.set_ylabel("Tempo (ms)")
    ax.legend(loc="upper left")

    # Pior caso: Θ(2^n · (n + m))
    ax = axs[2]
    dados = resumo(por, "pior")
    x = [d[0] for d in dados]
    y = [d[2] for d in dados]
    ref = [2 ** d[0] * (d[0] + d[1]) for d in dados]
    c = ajustar_escala(y[3:], ref[3:])  # pontos muito pequenos têm custo fixo dominando
    linha(ax, x, y, "pior", "Medido")
    teorica(ax, x, [c * r for r in ref], "Teórico Θ(2ⁿ · (n + m))")
    ax.set_yscale("log")
    eixo_log(ax)
    ax.set_title("Pior caso: dobra a cada variável")
    ax.set_xlabel("Variáveis (n)")
    ax.set_ylabel("Tempo médio (ms)")
    ax.legend(loc="upper left")

    fig.suptitle("3-SAT (DPLL em C): tempo medido × complexidade teórica",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    salvar(fig, "3sat_c_tempo.png")
    return b


def _regressao(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return b, my - b * mx


# 2. Onde o 3-SAT deixa de ser viável
def grafico_viabilidade(por, maior):
    fig, ax = plt.subplots(figsize=(10, 5.2))

    ax.axhline(LIMITE_MS, color=TINTA_2, linestyle="--", linewidth=1.2, zorder=1)
    ax.annotate("Limite de 60 s", (2, LIMITE_MS), xytext=(0, 6), textcoords="offset points",
                color=TINTA_2, fontsize=9)

    for caso in ("aleatorio", "pior"):
        dados = resumo(por, caso)
        completos = [d for d in dados if d[0] <= maior[caso]]
        x = [d[0] for d in completos]
        y = [d[2] for d in completos]
        linha(ax, x, y, caso)
        rotulo_final(ax, x[-1], y[-1], f"maior n viável = {maior[caso]}", dx=8, dy=-10)

        # tamanho onde parou: só a 1ª instância foi medida antes de estourar o limite
        sobra = [d for d in dados if d[0] > maior[caso]]
        for n, _, _, medias, _ in sobra:
            ax.scatter([n], medias, s=40, facecolors="white", edgecolors=COR[caso],
                       linewidths=1.6, zorder=4)
            rotulo_final(ax, n, medias[0], "1ª instância\n(a 2ª passou de 60 s)", dx=-8, dy=-22)

    ax.set_yscale("log")
    eixo_log(ax)
    ax.set_xlim(0, 175)
    ax.set_ylim(top=LIMITE_MS * 6)
    ax.set_xlabel("Variáveis (n)")
    ax.set_ylabel("Tempo médio (ms)")
    ax.set_title("3-SAT em C: até onde é viável resolver em 60 s")
    ax.legend(loc="lower right")
    ax.text(0.01, -0.16, "O melhor caso continua viável até n = 128.000 (43,6 ms), fora desta escala.",
            transform=ax.transAxes, color=MUDO, fontsize=9)
    salvar(fig, "3sat_viabilidade.png")


# 3. 2-SAT x 3-SAT
def grafico_2sat_vs_3sat(por):
    caminho = PASTA_RESULTADOS / "2sat_c_vs_python.csv"
    if not caminho.exists():
        print("  (pulando 2-SAT × 3-SAT: falta resultados/2sat_c_vs_python.csv)")
        return
    with open(caminho, encoding="utf-8-sig") as f:
        dois = sorted((d for d in csv.DictReader(f) if d["linguagem"] == "C" and d["caso"] == "aleatorio"),
                      key=lambda d: int(d["n"]))

    fig, ax = plt.subplots(figsize=(10, 5.2))
    for caso in ("melhor", "aleatorio", "pior"):
        dados = [d for d in resumo(por, caso) if len(d[3]) > 1 or caso != "aleatorio"]
        x = [d[0] for d in dados]
        y = [d[2] for d in dados]
        linha(ax, x, y, caso, "3-SAT · " + ROTULO[caso])
        rotulo_final(ax, x[-1], y[-1], "3-SAT " + ROTULO[caso].split(" (")[0].lower())
    x = [int(d["n"]) for d in dois]
    y = [float(d["media_ms"]) for d in dois]
    linha(ax, x, y, "2sat")
    rotulo_final(ax, x[-1], y[-1], "2-SAT", dy=10)

    ax.set_xscale("log")
    ax.set_yscale("log")
    eixo_log(ax, "x")
    eixo_log(ax)
    ax.set_xlim(right=ax.get_xlim()[1] * 3)
    ax.set_xlabel("Variáveis (n)")
    ax.set_ylabel("Tempo médio (ms)")
    ax.set_title("2-SAT × 3-SAT em C: polinomial × exponencial")
    ax.legend(loc="lower right")
    salvar(fig, "3sat_vs_2sat.png")


# 4. Memória x Θ(n + m)
def grafico_memoria(por):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    dados = resumo(por, "melhor")
    x = [d[0] + d[1] for d in dados]
    y = [d[4] / 1e6 for d in dados]
    c = ajustar_escala(y, x)
    linha(ax, x, y, "melhor", "Medido (estruturas do DPLL)")
    teorica(ax, x, [c * v for v in x], "Teórico Θ(n + m)", zorder=4)
    rotulo_final(ax, x[-1], y[-1], f"{y[-1]:.2f} MB".replace(".", ","), dx=-60, dy=8)
    ax.xaxis.set_major_formatter(FuncFormatter(br))
    ax.set_xlabel("Tamanho da entrada (n + m)")
    ax.set_ylabel("Memória (MB)")
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0)
    ax.set_title("3-SAT em C: memória cresce linearmente com a entrada")
    ax.legend(loc="upper left")
    salvar(fig, "3sat_memoria.png")


def main():
    PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    por = carregar()
    maior = viaveis(por)
    b = grafico_tempo(por)
    grafico_viabilidade(por, maior)
    grafico_2sat_vs_3sat(por)
    grafico_memoria(por)
    print(f"caso aleatório: tempo dobra a cada ~{1 / b:.1f} variáveis")
    print(f"Gráficos salvos em {PASTA_GRAFICOS.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
