import random
from pathlib import Path


TAMANHOS = [1000, 2000, 4000, 8000, 16000, 32000]
FATOR_CLAUSULAS = 2
SEMENTE = 42

PASTA_BASE = Path(__file__).resolve().parent / "entradas"


def escolher_variaveis_distintas(n, rng):
    v1 = rng.randint(1, n)

    v2 = rng.randint(1, n - 1)

    if v2 >= v1:
        v2 += 1

    return v1, v2


def gerar_sat(n, m, rng):

    atribuicao = {
        i: rng.choice([True, False])
        for i in range(1, n + 1)
    }

    clausulas = []

    for _ in range(m):

        v1, v2 = escolher_variaveis_distintas(n, rng)

        if atribuicao[v1]:
            literal1 = v1
        else:
            literal1 = -v1

        literal2 = v2 * rng.choice([-1, 1])

        clausulas.append((literal1, literal2))

    return clausulas


def gerar_unsat(n, m, rng):
    clausulas = [
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2)
    ]

    while len(clausulas) < m:

        v1, v2 = escolher_variaveis_distintas(n, rng)

        literal1 = v1 * rng.choice([-1, 1])
        literal2 = v2 * rng.choice([-1, 1])

        clausulas.append((literal1, literal2))

    return clausulas


def salvar_formula(n, m, clausulas, tipo):

    pasta = PASTA_BASE / tipo
    pasta.mkdir(parents=True, exist_ok=True)

    arquivo = pasta / f"2sat_n{n}.txt"

    with open(arquivo, "w", encoding="utf-8") as f:

        f.write(f"{n} {m}\n")

        for a, b in clausulas:
            f.write(f"{a} {b}\n")

    print(f"[{tipo.upper()}] Gerado: {arquivo.name}")


def main():

    gerador_sat = random.Random(SEMENTE)
    gerador_unsat = random.Random(SEMENTE + 1)

    for n in TAMANHOS:

        m = n * FATOR_CLAUSULAS

        clausulas_sat = gerar_sat(n, m, gerador_sat)
        clausulas_unsat = gerar_unsat(n, m, gerador_unsat)

        salvar_formula(n, m, clausulas_sat, "sat")
        salvar_formula(n, m, clausulas_unsat, "unsat")

    print("\nTodas as entradas controladas foram geradas!")


if __name__ == "__main__":
    main()