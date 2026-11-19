def satisfaz_2sat(n, clausulas):
    
    grafo = [[] for _ in range(2 * n)]
    transposto = [[] for _ in range(2 * n)]

    def indice(literal):
        if literal == 0 or abs(literal) > n:
            raise ValueError("Literal inválido")

        base = 2 * (abs(literal) - 1)

        if literal > 0:
            return base
        return base + 1

    def adicionar_aresta(origem, destino):
        grafo[origem].append(destino)
        transposto[destino].append(origem)

    for clausula in clausulas:
        if len(clausula) == 1:
            a = clausula[0]
            b = a
        elif len(clausula) == 2:
            a, b = clausula
        else:
            raise ValueError("Cada cláusula deve ter 1 ou 2 literais")

        adicionar_aresta(indice(-a), indice(b))
        adicionar_aresta(indice(-b), indice(a))

    total_vertices = 2 * n

    visitado = [False] * total_vertices
    ordem = []

    for inicio in range(total_vertices):
        if not visitado[inicio]:
            visitado[inicio] = True
            pilha = [(inicio, 0)]

            while pilha:
                atual, proximo = pilha[-1]

                if proximo < len(grafo[atual]):
                    vizinho = grafo[atual][proximo]
                    pilha[-1] = (atual, proximo + 1)

                    if not visitado[vizinho]:
                        visitado[vizinho] = True
                        pilha.append((vizinho, 0))
                else:
                    ordem.append(atual)
                    pilha.pop()

    componente = [-1] * total_vertices
    numero_componente = 0

    for inicio in reversed(ordem):
        if componente[inicio] == -1:
            pilha = [inicio]
            componente[inicio] = numero_componente

            while pilha:
                atual = pilha.pop()

                for vizinho in transposto[atual]:
                    if componente[vizinho] == -1:
                        componente[vizinho] = numero_componente
                        pilha.append(vizinho)

            numero_componente += 1

    for i in range(n):
        positivo = 2 * i
        negativo = 2 * i + 1

        if componente[positivo] == componente[negativo]:
            return False

    return True

n = 2
clausulas = [
    (1, 2),
    (-1, 2),
    (1, -2)
]

print(satisfaz_2sat(n, clausulas))

n = 2
clausulas = [
    (1, 2),
    (-1, 2),
    (1, -2),
    (-1, -2)
]

print(satisfaz_2sat(n, clausulas))