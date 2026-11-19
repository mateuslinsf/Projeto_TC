#include <stdio.h>
#include <stdlib.h>
#include "formula.h"

typedef struct {
    int *dados;
    int tam;
    int cap;
} Vetor;

static int vetor_push(Vetor *v, int x) {
    if (v->tam == v->cap) {
        int nova = v->cap ? 2 * v->cap : 1024;
        int *p = realloc(v->dados, (size_t)nova * sizeof(int));
        if (!p) return -1;
        v->dados = p;
        v->cap = nova;
    }
    v->dados[v->tam++] = x;
    return 0;
}

/* remove literais repetidos; retorna 1 se a clausula for tautologia */
static int normalizar_clausula(Vetor *lits, int ini) {
    int fim = ini;
    for (int i = ini; i < lits->tam; i++) {
        int l = lits->dados[i];
        int repetido = 0;
        for (int j = ini; j < fim; j++) {
            if (lits->dados[j] == l) repetido = 1;
            if (lits->dados[j] == -l) return 1;
        }
        if (!repetido) lits->dados[fim++] = l;
    }
    lits->tam = fim;
    return 0;
}

static void pular_linha(FILE *arq) {
    int ch;
    while ((ch = getc(arq)) != EOF && ch != '\n') {}
}

int formula_ler_dimacs(const char *caminho, Formula *f) {
    FILE *arq = fopen(caminho, "r");
    if (!arq) return -1;

    Vetor lits = {0}, inicio = {0};
    int n_decl = 0, m_decl = 0, max_var = 0, ini_atual = 0, erro = 0;
    if (vetor_push(&inicio, 0)) erro = 1;

    while (!erro) {
        int ch = getc(arq);
        if (ch == EOF) break;
        if (ch == ' ' || ch == '\t' || ch == '\n' || ch == '\r') continue;
        if (ch == '%') break;
        if (ch == 'c') { pular_linha(arq); continue; }
        if (ch == 'p') {
            if (fscanf(arq, " cnf %d %d", &n_decl, &m_decl) != 2) erro = 1;
            continue;
        }
        ungetc(ch, arq);
        int l;
        if (fscanf(arq, "%d", &l) != 1) { erro = 1; break; }
        if (l != 0) {
            if (abs(l) > max_var) max_var = abs(l);
            if (vetor_push(&lits, l)) erro = 1;
        } else {
            if (normalizar_clausula(&lits, ini_atual)) lits.tam = ini_atual;
            else if (vetor_push(&inicio, lits.tam)) erro = 1;
            ini_atual = lits.tam;
        }
    }
    fclose(arq);

    if (!erro && lits.tam != ini_atual) erro = 1;
    if (erro) {
        free(lits.dados);
        free(inicio.dados);
        return -1;
    }

    f->n_vars = n_decl > max_var ? n_decl : max_var;
    f->n_clausulas = inicio.tam - 1;
    f->n_literais = lits.tam;
    f->inicio = inicio.dados;
    f->literais = lits.dados ? lits.dados : malloc(sizeof(int));
    return 0;
}

void formula_liberar(Formula *f) {
    free(f->inicio);
    free(f->literais);
    f->inicio = f->literais = NULL;
}

unsigned long formula_bytes(const Formula *f) {
    return (unsigned long)(f->n_clausulas + 1 + f->n_literais) * sizeof(int);
}
