#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sat2.h"

#define IDX(l) (2 * (abs(l) - 1) + ((l) < 0))

int sat2_ler(const char *caminho, Formula2 *f) {
    FILE *arq = fopen(caminho, "r");
    if (!arq) return -1;

    int n, m;
    if (fscanf(arq, "%d %d", &n, &m) != 2 || n < 1 || m < 0) {
        fclose(arq);
        return -1;
    }

    int *a = malloc((size_t)(m > 0 ? m : 1) * sizeof(int));
    int *b = malloc((size_t)(m > 0 ? m : 1) * sizeof(int));
    if (!a || !b) {
        free(a);
        free(b);
        fclose(arq);
        return -1;
    }

    for (int i = 0; i < m; i++) {
        if (fscanf(arq, "%d %d", &a[i], &b[i]) != 2 ||
            a[i] == 0 || b[i] == 0 || abs(a[i]) > n || abs(b[i]) > n) {
            free(a);
            free(b);
            fclose(arq);
            return -1;
        }
    }
    fclose(arq);

    f->n_vars = n;
    f->n_clausulas = m;
    f->a = a;
    f->b = b;
    return 0;
}

void sat2_liberar(Formula2 *f) {
    free(f->a);
    free(f->b);
    f->a = f->b = NULL;
}

static void montar_csr(int V, int E, const int *origem, const int *destino,
                       int *inicio, int *adj, int *cursor) {
    for (int i = 0; i <= V; i++) inicio[i] = 0;
    for (int e = 0; e < E; e++) inicio[origem[e] + 1]++;
    for (int v = 0; v < V; v++) inicio[v + 1] += inicio[v];
    for (int v = 0; v < V; v++) cursor[v] = inicio[v];
    for (int e = 0; e < E; e++) adj[cursor[origem[e]]++] = destino[e];
}

int sat2_resolver(const Formula2 *f, signed char *modelo, unsigned long *memoria_bytes) {
    int n = f->n_vars, m = f->n_clausulas;
    int V = 2 * n, E = 2 * m;

    size_t n_ints = (size_t)(2 * E + 2 * (V + 1) + 2 * E + 4 * V);
    size_t total = n_ints * sizeof(int);
    int *mem = malloc(total);
    char *visitado = calloc((size_t)V, 1);
    if (!mem || !visitado) {
        free(mem);
        free(visitado);
        return SAT2_ERRO_MEMORIA;
    }

    int *origem = mem;
    int *destino = origem + E;
    int *ini_g = destino + E;
    int *adj_g = ini_g + (V + 1);
    int *ini_t = adj_g + E;
    int *adj_t = ini_t + (V + 1);
    int *ordem = adj_t + E;
    int *comp = ordem + V;
    int *pilha = comp + V;
    int *pos = pilha + V;

    for (int i = 0; i < m; i++) {
        int ia = IDX(f->a[i]), ib = IDX(f->b[i]);
        origem[2 * i] = ia ^ 1;
        destino[2 * i] = ib;
        origem[2 * i + 1] = ib ^ 1;
        destino[2 * i + 1] = ia;
    }

    montar_csr(V, E, origem, destino, ini_g, adj_g, pos);
    montar_csr(V, E, destino, origem, ini_t, adj_t, pos);

    int no = 0;
    for (int s = 0; s < V; s++) {
        if (visitado[s]) continue;
        int sp = 0;
        visitado[s] = 1;
        pos[s] = ini_g[s];
        pilha[sp++] = s;
        while (sp > 0) {
            int v = pilha[sp - 1];
            if (pos[v] < ini_g[v + 1]) {
                int w = adj_g[pos[v]++];
                if (!visitado[w]) {
                    visitado[w] = 1;
                    pos[w] = ini_g[w];
                    pilha[sp++] = w;
                }
            } else {
                ordem[no++] = v;
                sp--;
            }
        }
    }

    for (int v = 0; v < V; v++) comp[v] = -1;
    int n_comp = 0;
    for (int i = V - 1; i >= 0; i--) {
        int s = ordem[i];
        if (comp[s] != -1) continue;
        int sp = 0;
        comp[s] = n_comp;
        pilha[sp++] = s;
        while (sp > 0) {
            int v = pilha[--sp];
            for (int e = ini_t[v]; e < ini_t[v + 1]; e++) {
                int w = adj_t[e];
                if (comp[w] == -1) {
                    comp[w] = n_comp;
                    pilha[sp++] = w;
                }
            }
        }
        n_comp++;
    }

    int resultado = SAT2_SAT;
    for (int i = 0; i < n; i++) {
        if (comp[2 * i] == comp[2 * i + 1]) {
            resultado = SAT2_UNSAT;
            break;
        }
    }

    if (resultado == SAT2_SAT && modelo) {
        for (int i = 0; i < n; i++)
            modelo[i + 1] = comp[2 * i] > comp[2 * i + 1] ? 1 : -1;
    }

    if (memoria_bytes) *memoria_bytes = (unsigned long)(total + (size_t)V);

    free(mem);
    free(visitado);
    return resultado;
}
