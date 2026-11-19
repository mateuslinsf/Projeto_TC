#include <stdlib.h>
#include <string.h>
#include "dpll.h"

typedef struct {
    const Formula *f;
    signed char *valor;
    int *occ_inicio;
    int *occ;
    int *n_verd;
    int *n_falso;
    int *trilha;
    int tam_trilha;
    int qhead;
    int *dec_pos;
    int *dec_var;
    char *dec_invertida;
    int n_dec;
    int n_satisfeitas;
    Estatisticas *est;
} Solver;

#define IDX(l) (2 * (abs(l) - 1) + ((l) < 0))
#define ALINHAR(x) (((x) + 7) & ~(size_t)7)

static int valor_lit(const Solver *s, int l) {
    int v = s->valor[abs(l)];
    return l > 0 ? v : -v;
}

static void atribuir(Solver *s, int l) {
    s->valor[abs(l)] = l > 0 ? 1 : -1;
    s->trilha[s->tam_trilha++] = l;
}

/* uma unica alocacao para todas as estruturas do solver */
static void *alocar_arena(Solver *s, const Formula *f) {
    int n = f->n_vars, m = f->n_clausulas, L = f->n_literais;
    size_t t_valor = ALINHAR((size_t)(n + 1));
    size_t t_occi = ALINHAR((size_t)(2 * n + 1) * sizeof(int));
    size_t t_occ = ALINHAR((size_t)L * sizeof(int));
    size_t t_cont = ALINHAR((size_t)m * sizeof(int));
    size_t t_n = ALINHAR((size_t)n * sizeof(int));
    size_t t_inv = ALINHAR((size_t)n);
    size_t total = t_valor + t_occi + t_occ + 2 * t_cont + 3 * t_n + t_inv + 8;

    char *p = calloc(total, 1);
    if (!p) return NULL;
    char *q = p;
    s->valor = (signed char *)q; q += t_valor;
    s->occ_inicio = (int *)q;    q += t_occi;
    s->occ = (int *)q;           q += t_occ;
    s->n_verd = (int *)q;        q += t_cont;
    s->n_falso = (int *)q;       q += t_cont;
    s->trilha = (int *)q;        q += t_n;
    s->dec_pos = (int *)q;       q += t_n;
    s->dec_var = (int *)q;       q += t_n;
    s->dec_invertida = q;
    s->est->memoria_bytes = (unsigned long)total;
    return p;
}

static void montar_ocorrencias(Solver *s) {
    const Formula *f = s->f;
    int nl = 2 * f->n_vars;
    for (int i = 0; i < f->n_literais; i++)
        s->occ_inicio[IDX(f->literais[i]) + 1]++;
    for (int i = 0; i < nl; i++)
        s->occ_inicio[i + 1] += s->occ_inicio[i];

    /* preenche de tras para frente para manter as listas em ordem crescente de clausula */
    for (int c = f->n_clausulas - 1; c >= 0; c--)
        for (int k = f->inicio[c]; k < f->inicio[c + 1]; k++)
            s->occ[--s->occ_inicio[IDX(f->literais[k]) + 1]] = c;

    memmove(s->occ_inicio, s->occ_inicio + 1, (size_t)nl * sizeof(int));
    s->occ_inicio[nl] = f->n_literais;
}

static int propagar(Solver *s) {
    const Formula *f = s->f;
    while (s->qhead < s->tam_trilha) {
        int l = s->trilha[s->qhead++];
        int li = IDX(l);
        int conflito = 0;

        for (int k = s->occ_inicio[li]; k < s->occ_inicio[li + 1]; k++)
            if (s->n_verd[s->occ[k]]++ == 0) s->n_satisfeitas++;

        int ln = li ^ 1;
        for (int k = s->occ_inicio[ln]; k < s->occ_inicio[ln + 1]; k++) {
            int c = s->occ[k];
            s->n_falso[c]++;
            if (conflito || s->n_verd[c] > 0) continue;
            int tam = f->inicio[c + 1] - f->inicio[c];
            if (s->n_falso[c] == tam) {
                conflito = 1;
            } else if (s->n_falso[c] == tam - 1) {
                for (int j = f->inicio[c]; j < f->inicio[c + 1]; j++) {
                    int u = f->literais[j];
                    if (s->valor[abs(u)] == 0) {
                        atribuir(s, u);
                        s->est->propagacoes++;
                        break;
                    }
                }
            }
        }
        if (conflito) return 1;
    }
    return 0;
}

static void desfazer_ate(Solver *s, int pos) {
    while (s->tam_trilha > pos) {
        int i = --s->tam_trilha;
        int l = s->trilha[i];
        if (i < s->qhead) {
            int li = IDX(l), ln = li ^ 1;
            for (int k = s->occ_inicio[li]; k < s->occ_inicio[li + 1]; k++)
                if (--s->n_verd[s->occ[k]] == 0) s->n_satisfeitas--;
            for (int k = s->occ_inicio[ln]; k < s->occ_inicio[ln + 1]; k++)
                s->n_falso[s->occ[k]]--;
        }
        s->valor[abs(l)] = 0;
    }
    if (s->qhead > pos) s->qhead = pos;
}

static int buscar(Solver *s) {
    const Formula *f = s->f;

    for (int c = 0; c < f->n_clausulas; c++) {
        int tam = f->inicio[c + 1] - f->inicio[c];
        if (tam == 0) return DPLL_UNSAT;
        if (tam == 1) {
            int l = f->literais[f->inicio[c]];
            int v = valor_lit(s, l);
            if (v == 0) atribuir(s, l);
            else if (v < 0) return DPLL_UNSAT;
        }
    }

    for (;;) {
        if (propagar(s)) {
            s->est->conflitos++;
            for (;;) {
                if (s->n_dec == 0) return DPLL_UNSAT;
                int d = s->n_dec - 1;
                desfazer_ate(s, s->dec_pos[d]);
                if (!s->dec_invertida[d]) {
                    s->dec_invertida[d] = 1;
                    atribuir(s, -s->dec_var[d]);
                    break;
                }
                s->n_dec--;
            }
            continue;
        }

        if (s->n_satisfeitas == f->n_clausulas) return DPLL_SAT;

        int v = s->n_dec > 0 ? s->dec_var[s->n_dec - 1] + 1 : 1;
        while (v <= f->n_vars && s->valor[v] != 0) v++;
        if (v > f->n_vars) return DPLL_SAT;

        s->est->decisoes++;
        s->dec_pos[s->n_dec] = s->tam_trilha;
        s->dec_var[s->n_dec] = v;
        s->dec_invertida[s->n_dec] = 0;
        s->n_dec++;
        atribuir(s, v);
    }
}

int dpll_resolver(const Formula *f, signed char *modelo, Estatisticas *est) {
    Solver s;
    memset(&s, 0, sizeof s);
    memset(est, 0, sizeof *est);
    s.f = f;
    s.est = est;

    void *arena = alocar_arena(&s, f);
    if (!arena) return DPLL_ERRO_MEMORIA;
    montar_ocorrencias(&s);

    int r = buscar(&s);
    if (modelo) {
        modelo[0] = 0;
        for (int v = 1; v <= f->n_vars; v++)
            modelo[v] = s.valor[v] != 0 ? s.valor[v] : -1;
    }
    free(arena);
    return r;
}
