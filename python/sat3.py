from __future__ import annotations

import argparse
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Estatisticas:
    decisoes: int = 0
    conflitos: int = 0
    propagacoes: int = 0
    memoria_bytes: int = 0


def ler_dimacs(caminho: str | Path) -> tuple[int, list[list[int]]]:
    n = 0
    clausulas: list[list[int]] = []
    atual: list[int] = []

    with open(caminho, encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if not linha or linha.startswith("c"):
                continue

            if linha.startswith("p"):
                partes = linha.split()

                if len(partes) < 4 or partes[1].lower() != "cnf":
                    raise ValueError("Cabecalho DIMACS invalido")

                n = int(partes[2])
                continue

            for token in linha.split():
                literal = int(token)

                if literal == 0:
                    clausulas.append(atual)
                    atual = []
                else:
                    atual.append(literal)

    if atual:
        raise ValueError("Clausula DIMACS sem terminador 0")

    if n < 0:
        raise ValueError("Quantidade de variaveis invalida")

    for clausula in clausulas:
        for literal in clausula:
            if literal == 0 or abs(literal) > n:
                raise ValueError(f"Literal fora do intervalo: {literal}")

    return n, clausulas


def indice_literal(literal: int) -> int:
    return 2 * (abs(literal) - 1) + (1 if literal < 0 else 0)


class DPLL:
    def __init__(self, n: int, clausulas: list[list[int]]):
        self.n = n
        self.clausulas = clausulas
        self.m = len(clausulas)

        self.valor = [0] * (n + 1)

        self.ocorrencias: list[list[int]] = [[] for _ in range(2 * n)]

        for c, clausula in enumerate(clausulas):
            for literal in clausula:
                self.ocorrencias[indice_literal(literal)].append(c)

        self.n_verd = [0] * self.m
        self.n_falso = [0] * self.m
        self.n_satisfeitas = 0

        self.trilha: list[int] = []
        self.qhead = 0

        self.dec_pos: list[int] = []
        self.dec_var: list[int] = []
        self.dec_invertida: list[bool] = []

        self.est = Estatisticas()

    def estimar_memoria(self) -> int:
        total = sys.getsizeof(self.valor)

        total += sys.getsizeof(self.ocorrencias)
        total += sum(
            sys.getsizeof(lista)
            for lista in self.ocorrencias
        )

        total += sys.getsizeof(self.n_verd)
        total += sys.getsizeof(self.n_falso)

        total += sys.getsizeof(self.trilha)
        total += sys.getsizeof(self.dec_pos)
        total += sys.getsizeof(self.dec_var)
        total += sys.getsizeof(self.dec_invertida)

        return total

    def valor_literal(self, literal: int) -> int:
        valor = self.valor[abs(literal)]

        if literal > 0:
            return valor

        return -valor

    def atribuir(self, literal: int) -> None:
        if literal > 0:
            self.valor[abs(literal)] = 1
        else:
            self.valor[abs(literal)] = -1

        self.trilha.append(literal)

    def propagar(self) -> bool:
        while self.qhead < len(self.trilha):
            literal = self.trilha[self.qhead]
            self.qhead += 1

            li = indice_literal(literal)
            conflito = False

            for c in self.ocorrencias[li]:
                if self.n_verd[c] == 0:
                    self.n_satisfeitas += 1

                self.n_verd[c] += 1

            for c in self.ocorrencias[li ^ 1]:
                self.n_falso[c] += 1

                if conflito or self.n_verd[c] > 0:
                    continue

                tamanho = len(self.clausulas[c])

                if self.n_falso[c] == tamanho:
                    conflito = True

                elif self.n_falso[c] == tamanho - 1:
                    for candidato in self.clausulas[c]:

                        if self.valor[abs(candidato)] == 0:
                            self.atribuir(candidato)
                            self.est.propagacoes += 1
                            break

            if conflito:
                return True

        return False

    def desfazer_ate(self, posicao: int) -> None:
        while len(self.trilha) > posicao:
            i = len(self.trilha) - 1

            literal = self.trilha.pop()

            if i < self.qhead:
                li = indice_literal(literal)

                for c in self.ocorrencias[li]:
                    self.n_verd[c] -= 1

                    if self.n_verd[c] == 0:
                        self.n_satisfeitas -= 1

                for c in self.ocorrencias[li ^ 1]:
                    self.n_falso[c] -= 1

            self.valor[abs(literal)] = 0

        if self.qhead > posicao:
            self.qhead = posicao

    def resolver(self) -> tuple[bool, list[int]]:
        for clausula in self.clausulas:

            if len(clausula) == 0:
                return False, self.modelo()

            if len(clausula) == 1:
                literal = clausula[0]

                valor = self.valor_literal(literal)

                if valor == 0:
                    self.atribuir(literal)

                elif valor < 0:
                    return False, self.modelo()

        while True:

            if self.propagar():
                self.est.conflitos += 1

                while True:

                    if not self.dec_var:
                        return False, self.modelo()

                    d = len(self.dec_var) - 1

                    self.desfazer_ate(
                        self.dec_pos[d]
                    )

                    if not self.dec_invertida[d]:
                        self.dec_invertida[d] = True

                        self.atribuir(
                            -self.dec_var[d]
                        )

                        break

                    self.dec_pos.pop()
                    self.dec_var.pop()
                    self.dec_invertida.pop()

                continue

            if self.n_satisfeitas == self.m:
                return True, self.modelo()

            if self.dec_var:
                variavel = self.dec_var[-1] + 1
            else:
                variavel = 1

            while (
                variavel <= self.n
                and self.valor[variavel] != 0
            ):
                variavel += 1

            if variavel > self.n:
                return True, self.modelo()

            self.est.decisoes += 1

            self.dec_pos.append(
                len(self.trilha)
            )

            self.dec_var.append(
                variavel
            )

            self.dec_invertida.append(
                False
            )

            self.atribuir(
                variavel
            )

    def modelo(self) -> list[int]:
        return [0] + [
            valor if valor != 0 else -1
            for valor in self.valor[1:]
        ]


def satisfaz_3sat(
    n: int,
    clausulas: list[list[int]],
) -> tuple[bool, list[int], Estatisticas]:

    solver = DPLL(
        n,
        clausulas,
    )

    sat, modelo = solver.resolver()

    return (
        sat,
        modelo,
        solver.est,
    )


def executar_repeticoes(
    n: int,
    clausulas: list[list[int]],
    repeticoes: int,
    aquecimento: int,
    limite_s: float,
):
    for _ in range(aquecimento):
        satisfaz_3sat(
            n,
            clausulas,
        )

    tempos_ms: list[float] = []

    sat = False

    modelo: list[int] = (
        [0]
        + [-1] * n
    )

    est = Estatisticas()

    excedeu = 0

    for _ in range(repeticoes):

        inicio = time.perf_counter()

        sat, modelo, est = satisfaz_3sat(
            n,
            clausulas,
        )

        fim = time.perf_counter()

        tempo_ms = (
            fim - inicio
        ) * 1000.0

        tempos_ms.append(
            tempo_ms
        )

        if (
            limite_s > 0
            and tempo_ms > limite_s * 1000.0
        ):
            excedeu = 1
            break

    media = statistics.mean(
        tempos_ms
    )

    if len(tempos_ms) > 1:
        desvio = statistics.stdev(
            tempos_ms
        )
    else:
        desvio = 0.0

    medidor_memoria = DPLL(
        n,
        clausulas,
    )

    est.memoria_bytes = (
        medidor_memoria.estimar_memoria()
    )

    return (
        sat,
        modelo,
        est,
        tempos_ms,
        media,
        desvio,
        excedeu,
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "arquivo",
        help="formula CNF no formato DIMACS",
    )

    parser.add_argument(
        "-r",
        type=int,
        default=1,
        dest="repeticoes",
    )

    parser.add_argument(
        "-w",
        type=int,
        default=0,
        dest="aquecimento",
    )

    parser.add_argument(
        "-l",
        type=float,
        default=0.0,
        dest="limite_s",
    )

    parser.add_argument(
        "-m",
        action="store_true",
        dest="mostrar_modelo",
    )

    args = parser.parse_args()

    if (
        args.repeticoes < 1
        or args.aquecimento < 0
        or args.limite_s < 0
    ):
        parser.error(
            "parametros numericos invalidos"
        )

    try:
        n, clausulas = ler_dimacs(
            args.arquivo
        )

        (
            sat,
            modelo,
            est,
            tempos,
            media,
            desvio,
            excedeu,
        ) = executar_repeticoes(
            n,
            clausulas,
            args.repeticoes,
            args.aquecimento,
            args.limite_s,
        )

    except (OSError, ValueError) as erro:
        print(
            f"erro ao ler {args.arquivo}: {erro}",
            file=sys.stderr,
        )

        raise SystemExit(1)

    print(
        "resultado",
        "SAT" if sat else "UNSAT",
    )

    print("n", n)

    print(
        "m",
        len(clausulas),
    )

    print(
        "tempos_ms",
        " ".join(
            f"{t:.6f}"
            for t in tempos
        ),
    )

    print(
        f"media_ms {media:.6f}"
    )

    print(
        f"desvio_ms {desvio:.6f}"
    )

    print(
        "decisoes",
        est.decisoes,
    )

    print(
        "conflitos",
        est.conflitos,
    )

    print(
        "propagacoes",
        est.propagacoes,
    )

    print(
        "memoria_bytes",
        est.memoria_bytes,
    )

    print(
        "excedeu",
        excedeu,
    )

    if args.mostrar_modelo and sat:

        literais = [
            str(
                v
                if modelo[v] > 0
                else -v
            )
            for v in range(
                1,
                n + 1,
            )
        ]

        print(
            "modelo",
            " ".join(literais),
            "0",
        )


if __name__ == "__main__":
    main()