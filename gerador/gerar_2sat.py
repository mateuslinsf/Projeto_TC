import random
from pathlib import Path

TAMANHOS = [1000, 2000, 4000, 8000, 16000, 32000]

FATOR_CLAUSULAS = 2
SEMENTE = 42
PASTA_SAIDA = Path(__file__).resolve().parent / "entradas"


def gerar_formula(n, m, gerador):
    clausulas = []

    for _ in range(m):
        v1 = gerador.randint(1, n)

        v2 = gerador.randint(1, n - 1)

        if v2 >= v1:
            v2 += 1
        literal1 = v1 * gerador.choice([-1, 1])
        literal2 = v2 * gerador.choice([-1, 1])

        clausulas.append((literal1, literal2))

    return clausulas


def salvar_formula(n, m, clausulas):
    arquivo = PASTA_SAIDA / f"2sat_n{n}.txt"

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(f"{n} {m}\n")

        for a, b in clausulas:
            f.write(f"{a} {b}\n")

    print(f"Arquivo gerado: {arquivo.name}")


def main():

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    gerador = random.Random(SEMENTE)

    for n in TAMANHOS:

        m = n * FATOR_CLAUSULAS

        clausulas = gerar_formula(n, m, gerador)

        salvar_formula(n, m, clausulas)

    print("\nTodas as entradas foram geradas!")
    print(f"Semente utilizada: {SEMENTE}")


if __name__ == "__main__":
    main()