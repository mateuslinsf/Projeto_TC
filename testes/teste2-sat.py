import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "python"))

from sat2 import satisfaz_2sat


def testar():
    assert satisfaz_2sat(2, [
        (1, 2),
        (-1, 2),
        (1, -2)
    ]) == True

    assert satisfaz_2sat(2, [
        (1, 2),
        (-1, 2),
        (1, -2),
        (-1, -2)
    ]) == False

    assert satisfaz_2sat(1, [(1, 1)]) == True

    assert satisfaz_2sat(1, [(-1, -1)]) == True

    assert satisfaz_2sat(1, [
        (1, 1),
        (-1, -1)
    ]) == False

    assert satisfaz_2sat(2, []) == True

    print("Todos os testes passaram!")


testar()

import random


def forca_bruta(n, clausulas):
    for combinacao in range(2 ** n):

        satisfaz_todas = True

        for clausula in clausulas:
            satisfaz_clausula = False

            for literal in clausula:
                variavel = abs(literal) - 1

                valor = bool((combinacao >> variavel) & 1)

                if literal < 0:
                    valor = not valor

                if valor:
                    satisfaz_clausula = True
                    break

            if not satisfaz_clausula:
                satisfaz_todas = False
                break

        if satisfaz_todas:
            return True

    return False


random.seed(42)

for i in range(200):

    n = random.randint(1, 6)
    quantidade_clausulas = random.randint(0, 12)

    clausulas = []

    for j in range(quantidade_clausulas):

        tamanho = random.randint(1, 2)

        clausula = []

        for k in range(tamanho):
            variavel = random.randint(1, n)
            sinal = random.choice([-1, 1])

            clausula.append(variavel * sinal)

        clausulas.append(tuple(clausula))

    resultado_kosaraju = satisfaz_2sat(n, clausulas)
    resultado_forca_bruta = forca_bruta(n, clausulas)

    assert resultado_kosaraju == resultado_forca_bruta, (
        f"Erro no teste {i + 1}: "
        f"n={n}, clausulas={clausulas}, "
        f"Kosaraju={resultado_kosaraju}, "
        f"Força bruta={resultado_forca_bruta}"
    )

print("Os 200 testes aleatórios passaram!")