# Laberinto definido manualmente
# 0 = libre
# 1 = muro
# 2 = penalización
# 3 = premio
# 9 = meta

import heapq

laberinto = [
    [0, 0, 0, 0, 3, 1, 0, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 2, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 1, 3, 0, 0, 1, 0],
    [1, 1, 0, 1, 1, 1, 0, 1, 0],
    [0, 0, 2, 0, 0, 0, 0, 0, 9]
]

# Tamaño del laberinto
N = len(laberinto)


def costo_celda(valor):
    if valor == 0:
        return 1
    elif valor == 2:
        return 3
    elif valor == 3:
        return 0.25
    elif valor == 9:
        return 0
    else:
        return float("inf")


# Coins para recorrer el laberinto
def calcular_coins_camino(laberinto, camino):
    coins = 25  # Se empieza con 25 coins

    # Recorremos cada celda del camino, excepto la primera
    for celda in camino[1:]:
        fila, columna = celda
        costo = costo_celda(laberinto[fila][columna])
        coins = coins - costo
    return coins


# CONSTRUCCIÓN DEL GRAFO
def construccion_grafo(laberinto):
    grafo = {}

    for fila in range(N):
        for columna in range(N):

            # Los muros no son estados transitables
            if laberinto[fila][columna] == 1:
                continue

            vecinos = []

            # Arriba
            if fila > 0 and laberinto[fila - 1][columna] != 1:
                vecinos.append((fila - 1, columna))

            # Abajo
            if fila < N - 1 and laberinto[fila + 1][columna] != 1:
                vecinos.append((fila + 1, columna))

            # Izquierda
            if columna > 0 and laberinto[fila][columna - 1] != 1:
                vecinos.append((fila, columna - 1))

            # Derecha
            if columna < N - 1 and laberinto[fila][columna + 1] != 1:
                vecinos.append((fila, columna + 1))

            grafo[(fila, columna)] = vecinos

    return grafo


# BFS
def bfs_camino(grafo, inicio, objetivo):
    cola = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}

    while cola:
        nodo = cola.pop(0)

        if nodo == objetivo:
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]
            return list(reversed(camino))

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)

    return None



# DFS
def dfs_camino(grafo, inicio, objetivo):
    # Estructuras necesarias
    pila = [inicio]
    visitados = set()
    predecesores = {inicio: None}

    while pila:
        nodo = pila.pop()

        if nodo not in visitados:
            visitados.add(nodo)

            # Si llegamos al objetivo, reconstruimos el camino
            if nodo == objetivo:
                camino = []
                actual = nodo

                while actual is not None:
                    camino.append(actual)
                    actual = predecesores[actual]

                camino.reverse()
                return camino

            # Obtener los vecinos del nodo actual
            vecinos = grafo[nodo]

            # Invertir el orden para explorar con la pila
            for vecino in reversed(vecinos):
                if vecino not in predecesores:
                    predecesores[vecino] = nodo
                    pila.append(vecino)


    return None


# UCS
def ucs_camino(grafo, laberinto, inicio, objetivo):
    # La cola guarda pares: (costo_acumulado, nodo)
    cola = [(0, inicio)]
    visitados = set()
    predecesor = {inicio: None}
    costo_hasta = {inicio: 0}

    while cola:
        costo_actual, nodo = heapq.heappop(cola)

        if nodo == objetivo:
            camino = []
            while nodo is not None:
                camino.append(nodo)
                nodo = predecesor[nodo]
            return list(reversed(camino))

        if nodo in visitados:
            continue

        visitados.add(nodo)

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                fila, columna = vecino
                costo_vecino = costo_celda(laberinto[fila][columna])
                nuevo_costo = costo_actual + costo_vecino

                if vecino not in costo_hasta or nuevo_costo < costo_hasta[vecino]:
                    costo_hasta[vecino] = nuevo_costo
                    predecesor[vecino] = nodo
                    heapq.heappush(cola, (nuevo_costo, vecino))

    return None


# FUNCIONES AUXILIARES
def ejecutar_algoritmo(nombre, grafo, laberinto, inicio, objetivo):
    """Ejecuta un algoritmo y devuelve (nombre, camino, coins) o None."""
    if nombre == "BFS":
        camino = bfs_camino(grafo, inicio, objetivo)
    elif nombre == "DFS":
        camino = dfs_camino(grafo, inicio, objetivo)
    else:
        camino = ucs_camino(grafo, laberinto, inicio, objetivo)

    if camino is None:
        return None
    coins = calcular_coins_camino(laberinto, camino)
    return (nombre, camino, coins)


def imprimir_camino(camino):
    print("  Camino:", " -> ".join(str(c) for c in camino))



def mostrar_resultado_individual(resultado):
    nombre, camino, coins = resultado
    
    print(f"\n--- Resultado de {nombre} ---")
    imprimir_camino(camino)
    print(f"  Movimientos: {len(camino) - 1}")
    print(f"  Coins restantes: {coins:.2f}")

    if nombre == "BFS":
        print("  Criterio: menor cantidad de movimientos.")
        print("  Los coins no influyen en la búsqueda.")
    elif nombre == "DFS":
        print("  Criterio: exploración en profundidad.")
        print("  Los coins no influyen en la búsqueda.")
    else:
        print("  Criterio: menor costo acumulado.")
        print("  Los costos de las celdas sí influyen en la búsqueda.")



def mostrar_comparacion(resultados):
    print("\n--- Resultados de la comparación ---")

    # Detalle de cada algoritmo
    for nombre, camino, coins in resultados:
        print(f"\n{nombre}:")
        imprimir_camino(camino)
        print(f"  Movimientos: {len(camino) - 1}")
        print(f"  Coins restantes: {coins:.2f}")

        if nombre == "BFS":
            print("  Criterio: menor cantidad de movimientos.")
            print("  Los coins no guían la búsqueda.")

        elif nombre == "DFS":
            print("  Criterio: exploración en profundidad.")
            print("  Los coins no guían la búsqueda.")

        elif nombre == "UCS":
            print("  Criterio: menor costo acumulado.")
            print("  Los costos de las celdas guían la búsqueda.")

    # Tabla comparativa
    print("\n----- TABLA COMPARATIVA -----")
    print(f"{'Algoritmo':<12}{'Pasos':<10}{'Coins restantes':<18}")
    print("-" * 40)

    for nombre, camino, coins in resultados:
        print(f"{nombre:<12}{len(camino) - 1:<10}{coins:<18.2f}")

    # Comparación de pasos
    pasos = {
        nombre: len(camino) - 1
        for nombre, camino, coins in resultados
    }

    print("\n----- COMPARACIÓN DE RESULTADOS -----")

    min_pasos = min(pasos.values())
    max_pasos = max(pasos.values())

    print("\nPasos:")
    for nombre, p in pasos.items():
        diferencia = p - min_pasos

        if diferencia == 0:
            print(f"  {nombre}: {p} pasos (menor cantidad de pasos)")
        else:
            print(f"  {nombre}: {p} pasos ({diferencia} más que el mínimo)")

    print(
        "  Diferencia entre el mayor y el menor número de pasos:",
        max_pasos - min_pasos
    )

    # Comparación de coins restantes
    coins_dict = {
        nombre: coins
        for nombre, camino, coins in resultados
    }

    min_coins = min(coins_dict.values())
    max_coins = max(coins_dict.values())

    print("\nCoins restantes (calculados después del recorrido):")

    for nombre, coins in coins_dict.items():
        print(f"  {nombre}: {coins:.2f} coins")

    print(
        "  Diferencia entre el mayor y el menor saldo:",
        f"{max_coins - min_coins:.2f} coins"
    )

    print("\nInterpretación:")
    print("- BFS busca un camino con la menor cantidad de movimientos.")
    print("- DFS explora el laberinto en profundidad.")
    print("- UCS busca un camino de menor costo acumulado.")
    print("- BFS y DFS no utilizan los coins para elegir el camino.")
    print("- UCS sí utiliza los costos de las celdas para elegirlo.")
    print("- Los coins restantes permiten comparar el resultado económico")
    print("  de cada camino, pero no son un criterio de búsqueda para BFS y DFS.")


# PROGRAMA PRINCIPAL
grafo = construccion_grafo(laberinto)
inicio = (0, 0)
objetivo = (8, 8)

while True:
    print("\n----- LABERINTO------")
    print("Inicio:", inicio)
    print("Meta:", objetivo)

    print("\nSeleccione una opción:")
    print("1. BFS")
    print("2. DFS")
    print("3. UCS")
    print("4. Comparar los tres")
    print("5. Salir")

    opcion = input("Ingrese 1, 2, 3, 4 o 5: ").strip()

    if opcion == "5":
        print("\nSaliendo del programa")
        break

    elif opcion in ("1", "2", "3"):
        nombre = {"1": "BFS", "2": "DFS", "3": "UCS"}[opcion]
        resultado = ejecutar_algoritmo(nombre, grafo, laberinto, inicio, objetivo)
        if resultado:
            mostrar_resultado_individual(resultado)
        else:
            print(f"\n{nombre} no encontró camino hasta la meta.")

    elif opcion == "4":
        resultados = []
        for nombre in ("BFS", "DFS", "UCS"):
            resultado = ejecutar_algoritmo(nombre, grafo, laberinto, inicio, objetivo)
            if resultado:
                resultados.append(resultado)
            else:
                print(f"\n{nombre} no encontró camino.")

        if resultados:
            mostrar_comparacion(resultados)
        else:
            print("\nNingún algoritmo encontró camino.")

    else:
        print("\nOpción no válida. Intente de nuevo.")