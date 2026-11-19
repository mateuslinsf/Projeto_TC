"""Testes de corretude do 3-SAT (DPLL em C).

Uso:
    python testes/teste3-sat.py
    python testes/teste3-sat.py --outro "python python/arquivo_do_colega.py"

Com --outro, cada instância também roda na outra implementação (mesma saída do
c/dpll3.exe) e as respostas precisam ser iguais.
"""

import argparse
import contextlib
import io
import os
import random
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
BINARIO = RAIZ / "c" / ("dpll3.exe" if os.name == "nt" else "dpll3")


def compilar():
    if not BINARIO.exists():
        fontes = [str(RAIZ / "c" / f) for f in ("main.c", "dpll.c", "formula.c")]
        subprocess.run(["gcc", "-O2", "-std=c99", "-o", str(BINARIO), *fontes, "-lm"], check=True)


def forca_bruta(n, clausulas):
    for comb in range(2 ** n):
        if all(any((((comb >> (abs(l) - 1)) & 1) == 1) == (l > 0) for l in c) for c in clausulas):
            return True
    return False


def satisfaz(modelo, clausulas):
    return all(any((modelo[abs(l)] > 0) == (l > 0) for l in c) for c in clausulas)


def escrever(caminho, n, clausulas):
    with open(caminho, "w") as f:
        f.write(f"p cnf {n} {len(clausulas)}\n")
        for c in clausulas:
            f.write(" ".join(map(str, c)) + " 0\n")


def ler_dimacs(caminho):
    n, clausulas, atual = 0, [], []
    with open(caminho) as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha[0] == "c":
                continue
            if linha[0] == "p":
                n = int(linha.split()[2])
                continue
            for t in map(int, linha.split()):
                if t == 0:
                    clausulas.append(atual)
                    atual = []
                else:
                    atual.append(t)
    return n, clausulas


def executar(comando, caminho):
    saida = subprocess.run(comando + [str(caminho), "-m"], capture_output=True, text=True, check=True).stdout
    info = dict(linha.partition(" ")[::2] for linha in saida.splitlines())
    modelo = None
    if "modelo" in info:
        lits = list(map(int, info["modelo"].split()))[:-1]
        modelo = [0] + [1 if l > 0 else -1 for l in lits]
    return info["resultado"] == "SAT", modelo


class Testador:
    def __init__(self, outro):
        self.comandos = {"C": [str(BINARIO)]}
        if outro:
            self.comandos["outro"] = shlex.split(outro, posix=os.name != "nt")

    def conferir(self, caminho, n, clausulas, esperado):
        for nome, comando in self.comandos.items():
            sat, modelo = executar(comando, caminho)
            msg = f"[{nome}] {caminho.name}: n={n} clausulas={clausulas}"
            assert sat == esperado, f"esperado {esperado}, obtido {sat} | {msg}"
            if sat and modelo is not None:
                assert satisfaz(modelo, clausulas), f"modelo nao satisfaz a formula | {msg}"


def testes_fixos(t, pasta):
    todas_8 = [[a, b, c] for a in (1, -1) for b in (2, -2) for c in (3, -3)]
    casos = [
        (3, [], True),
        (1, [[1], [-1]], False),
        (2, [[1, 2], [-1, 2], [1, -2]], True),
        (2, [[1, 2], [-1, 2], [1, -2], [-1, -2]], False),
        (3, todas_8, False),
        (3, todas_8[:-1], True),
        (2, [[1, -1, 2]], True),
        (2, [[1, 1, 1], [-1, -1]], False),
    ]
    for i, (n, clausulas, esperado) in enumerate(casos):
        caminho = pasta / f"fixo{i}.cnf"
        escrever(caminho, n, clausulas)
        t.conferir(caminho, n, clausulas, esperado)
    print(f"{len(casos)} testes fixos passaram")


def testes_aleatorios(t, pasta, quantidade=300):
    rng = random.Random(42)
    for i in range(quantidade):
        n = rng.randint(1, 12)
        clausulas = []
        for _ in range(rng.randint(0, 6 * n)):
            k = rng.choice((1, 2, 3, 3, 3))
            clausulas.append([rng.randint(1, n) * rng.choice((1, -1)) for _ in range(k)])
        caminho = pasta / f"aleat{i}.cnf"
        escrever(caminho, n, clausulas)
        t.conferir(caminho, n, clausulas, forca_bruta(n, clausulas))
    print(f"{quantidade} testes aleatorios passaram (iguais a forca bruta)")


def teste_contra_2sat(t, pasta, quantidade=100):
    sys.path.append(str(RAIZ / "python"))
    with contextlib.redirect_stdout(io.StringIO()):
        from sat2 import satisfaz_2sat
    rng = random.Random(7)
    for i in range(quantidade):
        n = rng.randint(2, 30)
        clausulas = [[rng.randint(1, n) * rng.choice((1, -1)) for _ in range(2)]
                     for _ in range(rng.randint(1, 3 * n))]
        caminho = pasta / f"dois{i}.cnf"
        escrever(caminho, n, clausulas)
        t.conferir(caminho, n, clausulas, satisfaz_2sat(n, [tuple(c) for c in clausulas]))
    print(f"{quantidade} instancias 2-CNF passaram (iguais ao 2-SAT por SCC)")


def teste_entradas_geradas(t, n_max_pior=24, n_max_aleatorio=80):
    pasta = RAIZ / "entradas" / "3sat"
    if not pasta.exists():
        print("entradas/3sat nao existe; rode gerador/gerar_3sat.py para testar tambem essas entradas")
        return
    total = 0
    for caminho in sorted(pasta.rglob("*.cnf")):
        n, clausulas = ler_dimacs(caminho)
        caso = caminho.parent.name
        if caso == "pior":
            if n > n_max_pior:
                continue
            esperado = False
        elif caso == "melhor":
            esperado = True
        elif n > n_max_aleatorio:
            continue
        elif n <= 14:
            esperado = forca_bruta(n, clausulas)
        else:
            esperado = executar(t.comandos["C"], caminho)[0]
        t.conferir(caminho, n, clausulas, esperado)
        total += 1
    print(f"{total} entradas do gerador passaram")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outro", help="comando de outra implementacao com a mesma saida do C")
    args = parser.parse_args()

    compilar()
    t = Testador(args.outro)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        testes_fixos(t, tmp)
        testes_aleatorios(t, tmp)
        teste_contra_2sat(t, tmp)
    teste_entradas_geradas(t)
    print("Todos os testes do 3-SAT passaram!")


if __name__ == "__main__":
    main()
