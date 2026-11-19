"""Gera as entradas de 3-SAT (formato DIMACS) com semente fixa, usadas por C e Python.

Casos:
  aleatorio  m = 4.26·n (limiar de satisfatibilidade) -> caso médio
  melhor     toda cláusula tem ao menos um literal positivo -> DPLL sem conflitos, Θ(n + m)
  pior       UNSAT com conflito só nas 3 últimas variáveis -> DPLL percorre 2^(n-3) ramos

Uso: python gerador/gerar_3sat.py [--semente 42] [--saida entradas/3sat]
"""

import argparse
import random
from pathlib import Path

RAZAO = 4.26
TAMANHOS = {
    "aleatorio": [10, 14, 20, 28, 40, 57, 80, 113, 160, 226],
    "melhor": [1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000],
    "pior": [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36],
}
INSTANCIAS = {"aleatorio": 15, "melhor": 3, "pior": 1}


def clausula_aleatoria(rng, n):
    variaveis = rng.sample(range(1, n + 1), 3)
    return [v if rng.random() < 0.5 else -v for v in variaveis]


def gerar_aleatorio(rng, n):
    return [clausula_aleatoria(rng, n) for _ in range(round(RAZAO * n))]


def gerar_melhor(rng, n):
    clausulas = []
    for _ in range(round(RAZAO * n)):
        c = clausula_aleatoria(rng, n)
        if all(l < 0 for l in c):
            k = rng.randrange(3)
            c[k] = -c[k]
        clausulas.append(c)
    return clausulas


def gerar_pior(rng, n):
    a, b, c = n - 2, n - 1, n
    nucleo = [[s1 * a, s2 * b, s3 * c] for s1 in (1, -1) for s2 in (1, -1) for s3 in (1, -1)]
    preenchimento = []
    for v in range(1, n - 2):
        x, y = rng.sample([a, b, c], 2)
        preenchimento.append([v, x * rng.choice((1, -1)), y * rng.choice((1, -1))])
    return preenchimento + nucleo


GERADORES = {"aleatorio": gerar_aleatorio, "melhor": gerar_melhor, "pior": gerar_pior}


def escrever_dimacs(caminho, n, clausulas, comentario):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w") as f:
        f.write(f"c {comentario}\n")
        f.write(f"p cnf {n} {len(clausulas)}\n")
        for c in clausulas:
            f.write(" ".join(map(str, c)) + " 0\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--semente", type=int, default=42)
    parser.add_argument("--saida", default="entradas/3sat")
    args = parser.parse_args()

    base = Path(args.saida)
    for caso, tamanhos in TAMANHOS.items():
        for n in tamanhos:
            for i in range(INSTANCIAS[caso]):
                rng = random.Random(f"{args.semente}-{caso}-{n}-{i}")
                clausulas = GERADORES[caso](rng, n)
                arquivo = base / caso / f"n{n:06d}_i{i:02d}.cnf"
                escrever_dimacs(arquivo, n, clausulas, f"caso={caso} n={n} instancia={i} semente={args.semente}")
        print(f"{caso}: {len(tamanhos)} tamanhos x {INSTANCIAS[caso]} instancias")


if __name__ == "__main__":
    main()
