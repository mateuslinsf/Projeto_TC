#define _POSIX_C_SOURCE 199309L
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "dpll.h"
#include "formula.h"

#ifdef _WIN32
#include <windows.h>
static double agora_ms(void) {
    LARGE_INTEGER freq, cont;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&cont);
    return (double)cont.QuadPart * 1000.0 / (double)freq.QuadPart;
}
#else
#include <time.h>
static double agora_ms(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec * 1000.0 + t.tv_nsec / 1e6;
}
#endif

static void uso(const char *prog) {
    fprintf(stderr,
            "uso: %s arquivo.cnf [-r repeticoes] [-w aquecimento] [-l limite_s] [-m]\n"
            "  -m  imprime o modelo encontrado\n", prog);
}

int main(int argc, char **argv) {
    const char *caminho = NULL;
    int reps = 1, aquec = 0, mostrar_modelo = 0;
    double limite_ms = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-r") && i + 1 < argc) reps = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-w") && i + 1 < argc) aquec = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-l") && i + 1 < argc) limite_ms = atof(argv[++i]) * 1000.0;
        else if (!strcmp(argv[i], "-m")) mostrar_modelo = 1;
        else if (argv[i][0] != '-') caminho = argv[i];
        else { uso(argv[0]); return 2; }
    }
    if (!caminho || reps < 1) { uso(argv[0]); return 2; }

    Formula f;
    if (formula_ler_dimacs(caminho, &f) != 0) {
        fprintf(stderr, "erro ao ler %s\n", caminho);
        return 1;
    }

    signed char *modelo = malloc((size_t)f.n_vars + 1);
    double *tempos = malloc((size_t)reps * sizeof(double));
    if (!modelo || !tempos) {
        fprintf(stderr, "sem memoria\n");
        return 1;
    }

    Estatisticas est;
    int r = 0;
    for (int i = 0; i < aquec; i++) r = dpll_resolver(&f, NULL, &est);

    int feitas = 0, excedeu = 0;
    for (int i = 0; i < reps; i++) {
        double t0 = agora_ms();
        r = dpll_resolver(&f, modelo, &est);
        double t1 = agora_ms();
        tempos[feitas++] = t1 - t0;
        if (r == DPLL_ERRO_MEMORIA) break;
        if (limite_ms > 0 && t1 - t0 > limite_ms) { excedeu = 1; break; }
    }

    if (r == DPLL_ERRO_MEMORIA) {
        fprintf(stderr, "sem memoria para o solver\n");
        return 1;
    }

    double soma = 0, soma2 = 0;
    for (int i = 0; i < feitas; i++) soma += tempos[i];
    double media = soma / feitas;
    for (int i = 0; i < feitas; i++) soma2 += (tempos[i] - media) * (tempos[i] - media);
    double desvio = feitas > 1 ? sqrt(soma2 / (feitas - 1)) : 0.0;

    printf("resultado %s\n", r == DPLL_SAT ? "SAT" : "UNSAT");
    printf("n %d\nm %d\n", f.n_vars, f.n_clausulas);
    printf("tempos_ms");
    for (int i = 0; i < feitas; i++) printf(" %.6f", tempos[i]);
    printf("\nmedia_ms %.6f\ndesvio_ms %.6f\n", media, desvio);
    printf("decisoes %lld\nconflitos %lld\npropagacoes %lld\n",
           est.decisoes, est.conflitos, est.propagacoes);
    printf("memoria_bytes %lu\n", est.memoria_bytes + formula_bytes(&f));
    printf("excedeu %d\n", excedeu);
    if (mostrar_modelo && r == DPLL_SAT) {
        printf("modelo");
        for (int v = 1; v <= f.n_vars; v++) printf(" %d", modelo[v] > 0 ? v : -v);
        printf(" 0\n");
    }

    free(tempos);
    free(modelo);
    formula_liberar(&f);
    return 0;
}
