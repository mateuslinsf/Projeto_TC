import contextlib
import io
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BINARIO = RAIZ / "c" / ("sat2c.exe" if os.name == "nt" else "sat2c")
PASTA_ENTRADAS = RAIZ / "gerador" / "entradas"

sys.path.insert(0, str(RAIZ / "python"))

with contextlib.redirect_stdout(io.StringIO()):
    from sat2 import satisfaz_2sat


def compilar():
    fontes = [str(RAIZ / "c" / f) for f in ("main_2sat.c", "sat2.c")]
    subprocess.run(
        ["gcc", "-O2", "-std=c99", "-o", str(BINARIO), *fontes, "-lm"],
        check=True
    )


def forca_bruta(n, clausulas):
    for combinacao in range(2 ** n):
        if all(
            any(
                bool((combinacao >> (abs(l) - 1)) & 1) == (l > 0)
                for l in clausula
            )
            for clausula in clausulas
        ):
            return True
    return False


def escrever_formula(caminho, n, clausulas):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(f"{n} {len(clausulas)}\n")
        for clausula in clausulas:
            a, b = (clausula[0], clausula[0]) if len(clausula) == 1 else clausula
            f.write(f"{a} {b}\n")


def executar_c(caminho):
    saida = subprocess.run(
        [str(BINARIO), str(caminho), "-m"],
        capture_output=True, text=True, check=True
    ).stdout
    info = dict(linha.partition(" ")[::2] for linha in saida.splitlines())
    modelo = None
    if info["resultado"] == "SAT":
        modelo = [int(x) for x in info["modelo"].split()[:-1]]
    return info["resultado"] == "SAT", modelo


def modelo_satisfaz(modelo, clausulas):
    verdadeiros = set(modelo)
    return all(any(l in verdadeiros for l in clausula) for clausula in clausulas)


def verificar(caminho, n, clausulas, esperado=None, nome=""):
    resultado_c, modelo = executar_c(caminho)
    resultado_python = satisfaz_2sat(n, clausulas)

    assert resultado_c == resultado_python, (
        f"{nome}: C={resultado_c}, Python={resultado_python}, "
        f"n={n}, clausulas={clausulas}"
    )

    if esperado is not None:
        assert resultado_c == esperado, (
            f"{nome}: esperado {esperado}, obtido {resultado_c}"
        )

    if resultado_c:
        assert modelo_satisfaz(modelo, clausulas), (
            f"{nome}: modelo do C nao satisfaz a formula"
        )

    return resultado_c


def testar_casos_fixos(pasta):
    casos = [
        (2, [(1, 2), (-1, 2), (1, -2)], True),
        (2, [(1, 2), (-1, 2), (1, -2), (-1, -2)], False),
        (1, [(1, 1)], True),
        (1, [(-1, -1)], True),
        (1, [(1, 1), (-1, -1)], False),
        (2, [], True),
        (3, [(1, 1), (-1, 2), (-2, 3), (-3, -3)], False),
        (3, [(1, 1), (-1, 2), (-2, 3)], True),
    ]

    for i, (n, clausulas, esperado) in enumerate(casos, start=1):
        caminho = pasta / f"fixo_{i}.txt"
        escrever_formula(caminho, n, clausulas)
        verificar(caminho, n, clausulas, esperado, f"caso fixo {i}")

    print(f"{len(casos)} casos fixos passaram!")


def testar_aleatorios(pasta, quantidade=500):
    random.seed(42)
    sat = 0

    for i in range(quantidade):
        n = random.randint(1, 8)
        m = random.randint(0, 3 * n)

        clausulas = []
        for _ in range(m):
            tamanho = random.randint(1, 2)
            clausulas.append(tuple(
                random.randint(1, n) * random.choice([-1, 1])
                for _ in range(tamanho)
            ))

        caminho = pasta / "aleatorio.txt"
        escrever_formula(caminho, n, clausulas)

        esperado = forca_bruta(n, clausulas)
        sat += verificar(caminho, n, clausulas, esperado, f"aleatorio {i + 1}")

    print(f"{quantidade} testes aleatorios passaram! ({sat} SAT, {quantidade - sat} UNSAT)")


def carregar_formula(caminho):
    with open(caminho, "r", encoding="utf-8") as f:
        n, m = map(int, f.readline().split())
        clausulas = [tuple(map(int, linha.split())) for linha in f if linha.strip()]
    assert len(clausulas) == m
    return n, clausulas


def testar_entradas_geradas():
    arquivos = sorted(PASTA_ENTRADAS.rglob("2sat_n*.txt"))

    if not arquivos:
        print("Nenhuma entrada gerada encontrada; rode gerador/gerar_2sat.py e gerador/gerar_2sat_controlado.py")
        return

    for caminho in arquivos:
        n, clausulas = carregar_formula(caminho)
        esperado = None
        if caminho.parent.name == "sat":
            esperado = True
        elif caminho.parent.name == "unsat":
            esperado = False
        verificar(caminho, n, clausulas, esperado, str(caminho.relative_to(PASTA_ENTRADAS)))

    print(f"{len(arquivos)} entradas geradas concordam entre C e Python!")


def main():
    compilar()

    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        testar_casos_fixos(pasta)
        testar_aleatorios(pasta)

    testar_entradas_geradas()

    print("Todos os testes passaram!")


main()
