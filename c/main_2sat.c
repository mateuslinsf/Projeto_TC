#define _POSIX_C_SOURCE 199309L
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sat2.h"

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
            "uso: %s arquivo.txt [-r repeticoes] [-m]\n"
            "  -m  imprime o modelo encontrado\n", prog);
}

int main(int argc, char **argv) {
    const char *caminho = NULL;
    int reps = 1, mostrar_modelo = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-r") && i + 1 < argc) reps = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-m")) mostrar_modelo = 1;
        else if (argv[i][0] != '-') caminho = argv[i];
        else { uso(argv[0]); return 2; }
    }
    if (!caminho || reps < 1) { uso(argv[0]); return 2; }

    Formula2 f;
    if (sat2_ler(caminho, &f) != 0) {
        fprintf(stderr, "erro ao ler %s\n", caminho);
        return 1;
    }

    signed char *modelo = calloc((size_t)f.n_vars + 1, 1);
    double *tempos = malloc((size_t)reps * sizeof(double));
    if (!modelo || !tempos) {
        fprintf(stderr, "sem memoria\n");
        return 1;
    }

    unsigned long memoria = 0;
    int r = 0;
    for (int i = 0; i < reps; i++) {
        double t0 = agora_ms();
        r = sat2_resolver(&f, modelo, &memoria);
        double t1 = agora_ms();
        tempos[i] = t1 - t0;
        if (r == SAT2_ERRO_MEMORIA) {
            fprintf(stderr, "sem memoria para o solver\n");
            return 1;
        }
    }

    double soma = 0, soma2 = 0;
    for (int i = 0; i < reps; i++) soma += tempos[i];
    double media = soma / reps;
    for (int i = 0; i < reps; i++) soma2 += (tempos[i] - media) * (tempos[i] - media);
    double desvio = reps > 1 ? sqrt(soma2 / (reps - 1)) : 0.0;

    printf("resultado %s\n", r == SAT2_SAT ? "SAT" : "UNSAT");
    printf("n %d\nm %d\n", f.n_vars, f.n_clausulas);
    printf("tempos_ms");
    for (int i = 0; i < reps; i++) printf(" %.6f", tempos[i]);
    printf("\nmedia_ms %.6f\ndesvio_ms %.6f\n", media, desvio);
    printf("memoria_bytes %lu\n", memoria + (unsigned long)(2 * f.n_clausulas) * sizeof(int));
    if (mostrar_modelo && r == SAT2_SAT) {
        printf("modelo");
        for (int v = 1; v <= f.n_vars; v++) printf(" %d", modelo[v] > 0 ? v : -v);
        printf(" 0\n");
    }

    free(tempos);
    free(modelo);
    sat2_liberar(&f);
    return 0;
}
