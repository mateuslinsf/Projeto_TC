import csv
import os
import statistics
import subprocess
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]

BINARIO_C = (
    RAIZ
    / "c"
    / ("dpll3.exe" if os.name == "nt" else "dpll3")
)

PYTHON_3SAT = (
    RAIZ
    / "python"
    / "sat3.py"
)

PASTA_ENTRADAS = (
    RAIZ
    / "entradas"
    / "3sat"
)

SAIDA = (
    RAIZ
    / "resultados"
    / "3sat_c_vs_python.csv"
)


REPETICOES = 15
LIMITE_S = 60


TAMANHOS = {
    "melhor": [
        1000,
        2000,
        4000,
        8000,
        16000,
        32000,
    ],

    "aleatorio": [
        10,
        14,
        20,
        28,
        40,
        57,
    ],

    "pior": [
        8,
        10,
        12,
        14,
        16,
        18,
    ],
}


CAMPOS = [
    "linguagem",
    "caso",
    "n",
    "m",
    "resultado",
    "reps",
    "media_ms",
    "desvio_ms",
    "minimo_ms",
    "maximo_ms",
    "decisoes",
    "conflitos",
    "propagacoes",
    "memoria_bytes",
]


def compilar_c():
    fontes = [
        str(RAIZ / "c" / f)
        for f in (
            "main.c",
            "dpll.c",
            "formula.c",
        )
    ]

    subprocess.run(
        [
            "gcc",
            "-O2",
            "-std=c99",
            "-o",
            str(BINARIO_C),
            *fontes,
            "-lm",
        ],
        check=True,
    )


def interpretar_saida(texto):
    info = dict(
        linha.partition(" ")[::2]
        for linha in texto.splitlines()
    )

    tempos = [
        float(t)
        for t in info["tempos_ms"].split()
    ]

    return {
        "n": int(info["n"]),
        "m": int(info["m"]),

        "resultado":
            info["resultado"],

        "reps":
            len(tempos),

        "media_ms":
            statistics.mean(tempos),

        "desvio_ms":
            statistics.stdev(tempos)
            if len(tempos) > 1
            else 0.0,

        "minimo_ms":
            min(tempos),

        "maximo_ms":
            max(tempos),

        "decisoes":
            int(info["decisoes"]),

        "conflitos":
            int(info["conflitos"]),

        "propagacoes":
            int(info["propagacoes"]),

        "memoria_bytes":
            int(info["memoria_bytes"]),

        "excedeu":
            int(
                info.get(
                    "excedeu",
                    "0",
                )
            ),
    }


def executar(
    comando,
    caminho,
):
    processo = subprocess.run(
        comando
        + [
            str(caminho),
            "-r",
            str(REPETICOES),
            "-l",
            str(LIMITE_S),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=(
            LIMITE_S
            * (REPETICOES + 1)
            + 10
        ),
    )

    dados = interpretar_saida(
        processo.stdout
    )

    if dados["excedeu"]:
        raise RuntimeError(
            f"{caminho.name} ultrapassou "
            f"o limite de {LIMITE_S}s"
        )

    return dados


def caminho_entrada(
    caso,
    n,
):
    return (
        PASTA_ENTRADAS
        / caso
        / f"n{n:06d}_i00.cnf"
    )


def main():
    if not PASTA_ENTRADAS.exists():
        raise SystemExit(
            "Rode antes: "
            "python gerador/gerar_3sat.py"
        )

    if not PYTHON_3SAT.exists():
        raise SystemExit(
            "Arquivo ausente: "
            "python/sat3.py"
        )

    compilar_c()

    SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    comandos = {
        "C": [
            str(BINARIO_C)
        ],

        "Python": [
            sys.executable,
            str(PYTHON_3SAT),
        ],
    }

    with open(
        SAIDA,
        "w",
        newline="",
        encoding="utf-8",
    ) as arquivo:

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=CAMPOS,
        )

        escritor.writeheader()

        for caso, tamanhos in TAMANHOS.items():

            for n in tamanhos:

                entrada = caminho_entrada(
                    caso,
                    n,
                )

                if not entrada.exists():
                    raise FileNotFoundError(
                        f"Entrada nao encontrada: "
                        f"{entrada}"
                    )

                resultados = {}

                for linguagem, comando in comandos.items():

                    dados = executar(
                        comando,
                        entrada,
                    )

                    resultados[
                        linguagem
                    ] = dados

                    escritor.writerow({
                        "linguagem":
                            linguagem,

                        "caso":
                            caso,

                        **{
                            k: dados[k]
                            for k in CAMPOS
                            if k not in (
                                "linguagem",
                                "caso",
                            )
                        },
                    })

                    arquivo.flush()

                if (
                    resultados["C"]["resultado"]
                    != resultados["Python"]["resultado"]
                ):
                    raise RuntimeError(
                        "C e Python divergiram em "
                        f"{entrada.name}"
                    )

                c_ms = (
                    resultados["C"]["media_ms"]
                )

                py_ms = (
                    resultados["Python"]["media_ms"]
                )

                if c_ms > 0:
                    fator = py_ms / c_ms
                else:
                    fator = float("inf")

                print(
                    f"{caso:9s} "
                    f"n={n:6d} | "
                    f"C={c_ms:10.4f} ms | "
                    f"Python={py_ms:10.4f} ms | "
                    f"Python/C={fator:7.2f}x"
                )

    print(
        "\nResultados salvos em "
        f"{SAIDA.relative_to(RAIZ)}"
    )


if __name__ == "__main__":
    main()