#ifndef SAT2_H
#define SAT2_H

typedef struct {
    int n_vars;
    int n_clausulas;
    int *a;
    int *b;
} Formula2;

#define SAT2_UNSAT 0
#define SAT2_SAT 1
#define SAT2_ERRO_MEMORIA -1

int sat2_ler(const char *caminho, Formula2 *f);
void sat2_liberar(Formula2 *f);
int sat2_resolver(const Formula2 *f, signed char *modelo, unsigned long *memoria_bytes);

#endif
