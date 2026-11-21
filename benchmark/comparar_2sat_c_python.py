import contextlib
import csv
import io
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BINARIO = RAIZ / "c" / ("sat2c.exe" if os.name == "nt" else "sat2c")
PASTA_ENTRADAS = RAIZ / "gerador" / "entradas"
SAIDA = RAIZ / "resultados" / "2sat_c_vs_python.csv"

REPETICOES = 20
CAMPOS = ["linguagem", "caso", "n", "m", "resultado", "reps",
          "media_ms", "desvio_ms", "minimo_ms", "maximo_ms", "memoria_bytes"]

sys.path.insert(0, str(RAIZ / "python"))

with contextlib.redirect_stdout(io.StringIO()):
    from sat2 import satisfaz_2sat


def compilar():
    fontes = [str(RAIZ / "c" / f) for f in ("main_2sat.c", "sat2.c")]
    subprocess.run(
        ["gcc", "-O2", "-std=c99", "-o", str(BINARIO), *fontes, "-lm"],
        check=True
    )


def carregar_formula(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        n, m = map(int, f.readline().split())
        clausulas = [tuple(map(int, linha.split())) for linha in f if linha.strip()]
    if len(clausulas) != m:
        raise ValueError(f"Quantidade incorreta de clausulas em {caminho.name}")
    return n, m, clausulas


def medir_c(caminho):
    saida = subprocess.run(
        [str(BINARIO), str(caminho), "-r", str(REPETICOES)],
        capture_output=True, text=True, check=True
    ).stdout
    info = dict(linha.partition(" ")[::2] for linha in saida.splitlines())
    tempos = [float(t) for t in info["tempos_ms"].split()]
    return {
        "resultado": info["resultado"],
        "media_ms": statistics.mean(tempos),
        "desvio_ms": statistics.stdev(tempos),
        "minimo_ms": min(tempos),
        "maximo_ms": max(tempos),
        "memoria_bytes": info["memoria_bytes"],
    }


def medir_python(n, clausulas):
    tempos = []
    resultado = None

    for _ in range(REPETICOES):
        inicio = time.perf_counter()
        r = satisfaz_2sat(n, clausulas)
        fim = time.perf_counter()
        tempos.append((fim - inicio) * 1000)
        if resultado is None:
            resultado = r
        elif r != resultado:
            raise RuntimeError("Resultados inconsistentes no Python")

    return {
        "resultado": "SAT" if resultado else "UNSAT",
        "media_ms": statistics.mean(tempos),
        "desvio_ms": statistics.stdev(tempos),
        "minimo_ms": min(tempos),
        "maximo_ms": max(tempos),
        "memoria_bytes": "",
    }


def nome_do_caso(caminho):
    pasta = caminho.parent.name
    return "aleatorio" if pasta == "entradas" else pasta


def main():
    compilar()

    arquivos = sorted(
        PASTA_ENTRADAS.rglob("2sat_n*.txt"),
        key=lambda c: (nome_do_caso(c), int(c.stem.replace("2sat_n", "")))
    )

    if not arquivos:
        raise FileNotFoundError("Nenhuma entrada encontrada! Rode os geradores antes.")

    SAIDA.parent.mkdir(parents=True, exist_ok=True)

    with open(SAIDA, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS)
        escritor.writeheader()

        for caminho in arquivos:
            n, m, clausulas = carregar_formula(caminho)
            caso = nome_do_caso(caminho)

            resultado_c = medir_c(caminho)
            resultado_py = medir_python(n, clausulas)

            if resultado_c["resultado"] != resultado_py["resultado"]:
                raise RuntimeError(f"C e Python divergem em {caminho.name} ({caso})")

            for linguagem, dados in (("C", resultado_c), ("Python", resultado_py)):
                escritor.writerow({
                    "linguagem": linguagem, "caso": caso, "n": n, "m": m,
                    "reps": REPETICOES, **dados
                })

            print(
                f"{caso:9s} n={n:6d}  "
                f"C {resultado_c['media_ms']:9.4f} ms  "
                f"Python {resultado_py['media_ms']:9.4f} ms  "
                f"({resultado_c['resultado']})"
            )

    print(f"\nResultados salvos em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
