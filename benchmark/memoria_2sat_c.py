import csv
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BINARIO = RAIZ / "c" / ("sat2c.exe" if os.name == "nt" else "sat2c")
PASTA_ENTRADAS = RAIZ / "gerador" / "entradas"
SAIDA = RAIZ / "resultados" / "2sat_c_memoria.csv"

CAMPOS = ["caso", "n", "m", "resultado", "memoria_bytes", "pico_rss_bytes"]


def compilar():
    fontes = [str(RAIZ / "c" / f) for f in ("main_2sat.c", "sat2.c")]
    subprocess.run(
        ["gcc", "-O2", "-std=c99", "-o", str(BINARIO), *fontes, "-lm"],
        check=True
    )


def nome_do_caso(caminho):
    pasta = caminho.parent.name
    return "aleatorio" if pasta == "entradas" else pasta


def executar(caminho):
    if os.name == "nt":
        saida = subprocess.run(
            [str(BINARIO), str(caminho)],
            capture_output=True, text=True, check=True
        ).stdout
        return saida, ""

    processo = subprocess.Popen(
        [str(BINARIO), str(caminho)],
        stdout=subprocess.PIPE, text=True
    )
    saida = processo.stdout.read()
    _, status, uso = os.wait4(processo.pid, 0)
    processo.returncode = 0 if status == 0 else 1
    if processo.returncode != 0:
        raise RuntimeError(f"Falha ao executar {caminho.name}")

    pico = uso.ru_maxrss if sys.platform == "darwin" else uso.ru_maxrss * 1024
    return saida, pico


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
            saida, pico = executar(caminho)
            info = dict(linha.partition(" ")[::2] for linha in saida.splitlines())

            escritor.writerow({
                "caso": nome_do_caso(caminho),
                "n": info["n"],
                "m": info["m"],
                "resultado": info["resultado"],
                "memoria_bytes": info["memoria_bytes"],
                "pico_rss_bytes": pico,
            })

            print(
                f"{nome_do_caso(caminho):9s} n={info['n']:>6s}  "
                f"estruturas {int(info['memoria_bytes']) / 1e6:8.2f} MB  "
                f"pico RSS {pico / 1e6 if pico != '' else float('nan'):8.2f} MB"
            )

    print(f"\nResultados salvos em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
