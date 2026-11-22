import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


RAIZ = Path(__file__).resolve().parents[1]

ENTRADA = (
    RAIZ
    / "resultados"
    / "3sat_c_vs_python.csv"
)

PASTA_GRAFICOS = (
    RAIZ
    / "resultados"
    / "graficos"
)


CASOS = [
    "melhor",
    "aleatorio",
    "pior",
]


ROTULOS = {
    "melhor":
        "Melhor caso",

    "aleatorio":
        "Caso aleatório",

    "pior":
        "Pior caso",
}


def carregar():
    with open(
        ENTRADA,
        encoding="utf-8-sig",
    ) as arquivo:

        return list(
            csv.DictReader(
                arquivo
            )
        )


def filtrar(
    dados,
    linguagem,
    caso,
):
    return sorted(
        [
            d
            for d in dados
            if (
                d["linguagem"] == linguagem
                and d["caso"] == caso
            )
        ],

        key=lambda d: int(
            d["n"]
        ),
    )


def main():
    if not ENTRADA.exists():
        raise SystemExit(
            "Rode antes: "
            "python benchmark/"
            "comparar_3sat_c_python.py"
        )

    dados = carregar()

    PASTA_GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    fig, eixos = plt.subplots(
        1,
        3,
        figsize=(14, 4.8),
    )

    for eixo, caso in zip(
        eixos,
        CASOS,
    ):

        for linguagem, marcador in (
            ("C", "o"),
            ("Python", "s"),
        ):

            linhas = filtrar(
                dados,
                linguagem,
                caso,
            )

            x = [
                int(d["n"])
                for d in linhas
            ]

            y = [
                float(d["media_ms"])
                for d in linhas
            ]

            erro = [
                float(d["desvio_ms"])
                for d in linhas
            ]

            eixo.errorbar(
                x,
                y,
                yerr=erro,
                marker=marcador,
                capsize=3,
                label=linguagem,
            )

        eixo.set_yscale(
            "log"
        )

        if caso == "melhor":
            eixo.set_xscale(
                "log",
                base=2,
            )

        eixo.set_title(
            ROTULOS[caso]
        )

        eixo.set_xlabel(
            "Quantidade de variáveis (n)"
        )

        eixo.grid(
            True,
            which="both",
            alpha=0.35,
        )

        eixo.legend()

    eixos[0].set_ylabel(
        "Tempo médio (ms) - escala log"
    )

    fig.suptitle(
        "3-SAT (DPLL): "
        "comparação de tempo entre C e Python"
    )

    fig.tight_layout()

    saida = (
        PASTA_GRAFICOS
        / "3sat_c_vs_python.png"
    )

    fig.savefig(
        saida,
        dpi=300,
    )

    plt.close(fig)

    print(
        "Gráfico salvo em "
        f"{saida.relative_to(RAIZ)}"
    )


if __name__ == "__main__":
    main()