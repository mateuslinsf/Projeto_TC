#ifndef FORMULA_H
#define FORMULA_H

typedef struct {
    int n_vars;
    int n_clausulas;
    int n_literais;
    int *inicio;
    int *literais;
} Formula;

int formula_ler_dimacs(const char *caminho, Formula *f);
void formula_liberar(Formula *f);
unsigned long formula_bytes(const Formula *f);

#endif
