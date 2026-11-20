"""Mede o tempo do DPLL nas entradas de entradas/3sat e salva em resultados/.

Uso:
    python benchmark/medir_3sat.py
    python benchmark/medir_3sat.py --impl Python "python python/arquivo_do_colega.py"
    python benchmark/medir_3sat.py --casos pior --reps 15 --limite 60

Qualquer implementação com a mesma saída do c/dpll3.exe pode ser medida.
Para cada caso, os tamanhos crescem até uma instância passar de --limite segundos;
esse tamanho e os maiores são marcados como inviáveis.
"""

import argparse
import csv
import os
import shlex
import statistics
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BINARIO = RAIZ / "c" / ("dpll3.exe" if os.name == "nt" else "dpll3")
CAMPOS = ["linguagem", "caso", "n", "m", "instancia", "resultado", "reps", "media_ms", "desvio_ms",
          "decisoes", "conflitos", "propagacoes", "memoria_bytes"]


def executar(comando, caminho, reps, limite):
    args = comando + [str(caminho), "-r", str(reps), "-l", str(limite)]
    try:
        saida = subprocess.run(args, capture_output=True, text=True, check=True,
                               timeout=limite * (reps + 1) + 10).stdout
    except subprocess.TimeoutExpired:
        return None
    info = dict(linha.partition(" ")[::2] for linha in saida.splitlines())
    if info.get("excedeu") == "1":
        return None
    return info


def medir_caso(nome, comando, caso, reps, limite, escritor):
    arquivos = sorted((RAIZ / "entradas" / "3sat" / caso).glob("*.cnf"))
    por_n = {}
    for arq in arquivos:
        por_n.setdefault(int(arq.stem[1:7]), []).append(arq)

    maior_viavel = None
    for n in sorted(por_n):
        medias = []
        for arq in por_n[n]:
            info = executar(comando, arq, reps, limite)
            if info is None:
                print(f"  {nome} {caso} n={n}: passou de {limite} s -> inviavel")
                return maior_viavel
            escritor.writerow({
                "linguagem": nome, "caso": caso, "n": n, "m": info["m"],
                "instancia": int(arq.stem[-2:]), "resultado": info["resultado"], "reps": reps,
                "media_ms": info["media_ms"], "desvio_ms": info["desvio_ms"],
                "decisoes": info["decisoes"], "conflitos": info["conflitos"],
                "propagacoes": info["propagacoes"], "memoria_bytes": info.get("memoria_bytes", ""),
            })
            medias.append(float(info["media_ms"]))
        maior_viavel = n
        desvio = statistics.stdev(medias) if len(medias) > 1 else 0.0
        print(f"  {nome} {caso} n={n}: {statistics.mean(medias):.4f} ms (dp entre instancias {desvio:.4f})")
    return maior_viavel


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl", nargs=2, action="append", metavar=("NOME", "COMANDO"),
                        help="implementacao extra a medir (pode repetir)")
    parser.add_argument("--casos", nargs="+", default=["melhor", "aleatorio", "pior"])
    parser.add_argument("--reps", type=int, default=15)
    parser.add_argument("--limite", type=float, default=60.0)
    parser.add_argument("--saida", default=str(RAIZ / "resultados" / "3sat_tempos.csv"))
    args = parser.parse_args()

    if not (RAIZ / "entradas" / "3sat").exists():
        raise SystemExit("rode antes: python gerador/gerar_3sat.py")

    impls = [("C", [str(BINARIO)])]
    for nome, cmd in args.impl or []:
        impls.append((nome, shlex.split(cmd, posix=os.name != "nt")))

    saida = Path(args.saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    viaveis = []
    with open(saida, "w", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS)
        escritor.writeheader()
        for nome, comando in impls:
            for caso in args.casos:
                viaveis.append((nome, caso, medir_caso(nome, comando, caso, args.reps, args.limite, escritor)))
                f.flush()

    with open(saida.with_name("3sat_maior_n_viavel.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["linguagem", "caso", "maior_n_viavel", "limite_s"])
        for nome, caso, n in viaveis:
            w.writerow([nome, caso, n, args.limite])
            print(f"maior n viavel ({nome}, {caso}): {n}")
    print(f"resultados em {saida}")


if __name__ == "__main__":
    main()
