import csv
from pathlib import Path
import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parents[1]

PASTA_RESULTADOS = RAIZ / "resultados"
PASTA_GRAFICOS = PASTA_RESULTADOS / "graficos"

PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)


def carregar_csv(caminho):
    with open(caminho, "r", encoding="utf-8-sig") as arquivo:
        return list(csv.DictReader(arquivo))


def ordenar(dados):
    return sorted(dados, key=lambda x: int(x["variaveis"]))


aleatorios = ordenar(
    carregar_csv(PASTA_RESULTADOS / "2sat_python_resumo.csv")
)

controlados = ordenar(
    carregar_csv(
        PASTA_RESULTADOS / "2sat_python_controlados_resumo.csv"
    )
)

n = [int(d["variaveis"]) for d in aleatorios]
medias = [float(d["media_ms"]) for d in aleatorios]
desvios = [float(d["desvio_padrao_ms"]) for d in aleatorios]

plt.figure(figsize=(9, 5))
plt.errorbar(n, medias, yerr=desvios, marker="o", capsize=4)

plt.xlabel("Quantidade de variáveis")
plt.ylabel("Tempo médio (ms)")
plt.title("Desempenho do 2-SAT em Python - Entradas aleatórias")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "2sat_aleatorio.png",
    dpi=300
)
plt.close()

plt.figure(figsize=(9, 5))

for tipo in ["SAT", "UNSAT"]:
    dados = ordenar([
        d for d in controlados
        if d["tipo"] == tipo
    ])

    x = [int(d["variaveis"]) for d in dados]
    y = [float(d["media_ms"]) for d in dados]
    erro = [float(d["desvio_padrao_ms"]) for d in dados]

    plt.errorbar(
        x,
        y,
        yerr=erro,
        marker="o",
        capsize=4,
        label=tipo
    )

plt.xlabel("Quantidade de variáveis")
plt.ylabel("Tempo médio (ms)")
plt.title("Comparação entre fórmulas SAT e UNSAT")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "2sat_sat_vs_unsat.png",
    dpi=300
)
plt.close()

razao = [
    media / (variaveis + clausulas)
    for media, variaveis, clausulas in zip(
        medias,
        n,
        [int(d["clausulas"]) for d in aleatorios]
    )
]

plt.figure(figsize=(9, 5))
plt.plot(n, razao, marker="o")

plt.xlabel("Quantidade de variáveis")
plt.ylabel("Tempo médio / (n + m) (ms)")
plt.title("Verificação do crescimento linear do 2-SAT")
plt.grid(True)
plt.tight_layout()

plt.savefig(
    PASTA_GRAFICOS / "2sat_razao_linear.png",
    dpi=300
)
plt.close()

print(f"Localização: {PASTA_GRAFICOS}")