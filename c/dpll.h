#ifndef DPLL_H
#define DPLL_H

#include "formula.h"

typedef struct {
    long long decisoes;
    long long conflitos;
    long long propagacoes;
    unsigned long memoria_bytes;
} Estatisticas;

#define DPLL_UNSAT 0
#define DPLL_SAT 1
#define DPLL_ERRO_MEMORIA -1

/* modelo (opcional) deve ter n_vars + 1 posicoes; modelo[v] = 1 ou -1 */
int dpll_resolver(const Formula *f, signed char *modelo, Estatisticas *est);

#endif
