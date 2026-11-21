
# 2-SAT × 3-SAT: Análise de Complexidade (P vs NP)

Projeto da disciplina **Teoria da Computação** (Prof. Daniel Bezerra): Teoria da Complexidade e Análise de Tempo de Algoritmos.

---

## 👥 Equipe

| Integrante | Github |
|---|---|
| Eros Amancio |@erosamancio|
| Luiz Felipe |@LuizGoncalves10| 
| Lucas Bayma | @Lucascbayma | 
| Mateus Lins | @mateuslinsf |
| Pedro Moreira| @PedroMoreira18| 

## 📅 Prazos

- **Entrega 2 (relatório + código):** 24/11, até 23:59h (atraso: −0,5 ponto/hora)
- **Apresentações:** 25/11 e 30/11 (até 7 minutos, todos apresentam)

## ✅ Checklist de entrega

- [x] Algoritmo A (2-SAT/SCC) na linguagem 1 (Python)
- [x] Algoritmo A (2-SAT/SCC) na linguagem 2 (C)
- [x] Algoritmo B (3-SAT/DPLL) na linguagem 1 (C)
- [ ] Algoritmo B (3-SAT/DPLL) na linguagem 2 (Python)
- [ ] Gerador de entradas com semente fixa (3-SAT pronto; falta 2-SAT)
- [ ] Script de medição (repetições, média, desvio-padrão) (3-SAT pronto; falta 2-SAT)
- [ ] Testes de corretude das 4 implementações (3-SAT em C pronto)
- [ ] Gráficos: teórico × medido, A × B, linguagem × linguagem
- [ ] Gráfico mostrando onde o 3-SAT deixa de ser viável
- [ ] (Bônus) Medição de memória × complexidade de espaço
- [ ] Relatório em PDF (itens 1–7, ambiente, contribuições, declaração de uso de IA)
- [ ] Slides da apresentação (≤ 7 min)

## 🧩 3-SAT (DPLL em C)

Requisitos: `gcc` e Python 3.

```bash
gcc -O2 -std=c99 -o c/dpll3 c/main.c c/dpll.c c/formula.c -lm   # compilar
python gerador/gerar_3sat.py                                    # gerar entradas (semente 42)
python testes/teste3-sat.py                                     # testes de corretude
python benchmark/medir_3sat.py                                  # medição -> resultados/
python benchmark/graficos_3sat.py                               # gráficos -> resultados/graficos/ (requer matplotlib)
```

Uso: `c/dpll3 arquivo.cnf [-r repeticoes] [-l limite_s] [-m]` (entrada em formato DIMACS).

## 🧩 2-SAT (Kosaraju em C)

Requisitos: `gcc` e Python 3.

```bash
gcc -O2 -std=c99 -o c/sat2c c/main_2sat.c c/sat2.c -lm   # compilar
python gerador/gerar_2sat.py                              # gerar entradas aleatorias (semente 42)
python gerador/gerar_2sat_controlado.py                   # gerar entradas SAT e UNSAT
python testes/teste2-sat-c.py                             # testes C x Python x forca bruta
python benchmark/comparar_2sat_c_python.py                # medicao C x Python -> resultados/
python benchmark/memoria_2sat_c.py                        # medicao de memoria do C -> resultados/
python benchmark/graficos_2sat_c.py                       # graficos do 2-SAT em C (requer matplotlib)
```

Uso: `c/sat2c arquivo.txt [-r repeticoes] [-m]` (primeira linha `n m`, depois uma clausula `a b` por linha).

## 🤖 Uso de IA

Conforme as regras da disciplina, todo uso de ferramentas de IA será declarado no relatório (ferramenta e finalidade).
