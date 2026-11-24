# 2-SAT × 3-SAT: Análise de Complexidade (P vs NP)

Projeto da disciplina **Teoria da Computação** (Prof. Daniel Bezerra): Teoria da Complexidade e Análise de Tempo de Algoritmos.

- **Relatório (Google Docs):** https://docs.google.com/document/d/1hkJdTO-MhE_gdmwABv3ue5Z5_GZDNh-r5oFc5VwbdTE/edit?usp=sharing

---

## 👥 Equipe

| Integrante | Github |
|---|---|
| Eros Amancio | @erosamancio |
| Luiz Felipe | @LuizGoncalves10 |
| Lucas Bayma | @Lucascbayma |
| Mateus Lins | @mateuslinsf |
| Pedro Moreira | @PedroMoreira18 |

## 📅 Prazos

- **Entrega 2 (relatório + código):** 24/11, até 23:59h (atraso: −0,5 ponto/hora)
- **Apresentações:** 25/11 e 30/11 (até 7 minutos, todos apresentam)

## ✅ Checklist de entrega

- [x] Algoritmo A (2-SAT/SCC) na linguagem 1 (Python)
- [x] Algoritmo A (2-SAT/SCC) na linguagem 2 (C)
- [x] Algoritmo B (3-SAT/DPLL) na linguagem 1 (C)
- [x] Algoritmo B (3-SAT/DPLL) na linguagem 2 (Python)
- [x] Gerador de entradas com semente fixa
- [x] Script de medição (repetições, média, desvio-padrão)
- [x] Testes de corretude das 4 implementações
- [x] Gráficos: teórico × medido, A × B, linguagem × linguagem
- [x] Gráfico mostrando onde o 3-SAT deixa de ser viável
- [x] (Bônus) Medição de memória × complexidade de espaço
- [x] Relatório em PDF (itens 1–7, ambiente, contribuições, declaração de uso de IA)
- [x] Slides da apresentação (≤ 7 min)

## 🧩 3-SAT (DPLL em C e Python)

Requisitos: `gcc` e Python 3.

```bash
gcc -O2 -std=c99 -o c/dpll3 c/main.c c/dpll.c c/formula.c -lm   # compilar
python gerador/gerar_3sat.py                                    # gerar entradas (semente 42)
python testes/teste3-sat.py                                     # testes de corretude (C e Python)
python benchmark/medir_3sat.py                                  # medição em C -> resultados/
python benchmark/comparar_3sat_c_python.py                      # comparação C x Python -> resultados/
python benchmark/graficos_3sat.py                               # gráficos do 3-SAT -> resultados/graficos/ (requer matplotlib)
python benchmark/graficos_3sat_c_python.py                      # gráficos C x Python -> resultados/graficos/ (requer matplotlib)
```

Uso:
- C: `c/dpll3 arquivo.cnf [-r repeticoes] [-l limite_s] [-m]` (entrada em formato DIMACS).
- Python: `python python/sat3.py arquivo.cnf` (entrada em formato DIMACS).

## 🧩 2-SAT (Kosaraju em C e Python)

Requisitos: `gcc` e Python 3.

```bash
gcc -O2 -std=c99 -o c/sat2c c/main_2sat.c c/sat2.c -lm   # compilar
python gerador/gerar_2sat.py                              # gerar entradas aleatorias (semente 42)
python gerador/gerar_2sat_controlado.py                   # gerar entradas SAT e UNSAT
python testes/teste2-sat.py                               # testes do 2-SAT em Python
python testes/teste2-sat-c.py                             # testes C x Python x forca bruta
python benchmark/medir_2sat.py                            # medicao em Python -> resultados/
python benchmark/medir_2sat_controlados.py                # medicao SAT x UNSAT em Python -> resultados/
python benchmark/comparar_2sat_c_python.py                # medicao C x Python -> resultados/
python benchmark/memoria_2sat_c.py                        # medicao de memoria do C -> resultados/
python benchmark/graficos_2sat.py                         # graficos do 2-SAT em Python (requer matplotlib)
python benchmark/graficos_2sat_c.py                       # graficos do 2-SAT em C (requer matplotlib)
```

Uso:
- C: `c/sat2c arquivo.txt [-r repeticoes] [-m]` (primeira linha `n m`, depois uma clausula `a b` por linha).
- Python: `python python/sat2.py arquivo.txt` (primeira linha `n m`, depois uma clausula `a b` por linha).

## 🤖 Uso de IA

1. Utilizamos o Chat GPT para ajudar na formulação e formatação do relatório;
2. Utilizamos o Chat GPT para auxiliar na criação do código e de geração dos gráficos;
3. Utilizamos o claude para nos ajudar em seções do relatório relacionadas ao 2-SAT em C;
4. Utilizamos o Claude para nos ajudar na geração dos códigos e scripts de medição de tempo do 2-SAT em C;
5. Utilizamos o Claude para resumir os dados dos CSVs nas tabelas do relatório e para sugerir a interpretação dos resultados;
6. Utilizamos o Claude para fazer a geração dos gráficos do 3-SAT (`benchmark/graficos_3sat.py`);
7. Utilizamos o Chat GPT para auxiliar na comparação de dados entre os algoritmos feitos em Python e C;
8. Utilizamos o Chat GPT para compreender a proposta principal do projeto e sanar dúvidas relacionadas ao 2-SAT x 3-SAT, assim como entender algumas limitações.