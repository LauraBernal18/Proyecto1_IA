# ============================================================
# BUSQUEDA NO INFORMADA: BFS, DFS y UCS
# Las tres funciones reciben el estado inicial y devuelven:
# (estados, movimientos, expandidos)
#
# estados : lista de estados desde el inicio hasta el objetivo
# movimientos : lista de movimientos (montón, cantidad quitada)
# expandidos : cuantos estados se expandieron (sin contar el objetivo)
#
# Si no hay solución devuelven (None, None, expandidos).

from collections import deque
import heapq

from nim import es_objetivo, obtener_sucesores, costo_movimiento


# ============================================================
# RECONSTRUIR LA SOLUCION

# Los algoritmos guardan de que estado viene cada estado.
# Con eso se reconstruye el camino desde el objetivo hasta el inicio.
# (A* tambien puede usar esta funcion.)

def reconstruir_solucion(inicio, objetivo, padres):

    estados = []
    movimientos = []
    actual = objetivo

    while actual != inicio:
        estados.append(actual)
        estado_anterior, movimiento = padres[actual]
        movimientos.append(movimiento)
        actual = estado_anterior

    estados.append(inicio)
    estados.reverse()
    movimientos.reverse()

    return estados, movimientos


# ============================================================
# BFS - Busqueda en amplitud (cola)
# Explora por niveles. Como cada movimiento cuenta igual,
# encuentra la solución con MENOS MOVIMIENTOS.

def bfs(inicio):

    cola = deque([inicio])
    visitados = {inicio}
    padres = {inicio: None}
    expandidos = 0

    while cola:

        # Sale el estado que lleva mas tiempo esperando.
        actual = cola.popleft()
        if es_objetivo(actual):

            estados, movimientos = reconstruir_solucion(
                inicio, actual, padres
            )
            return estados, movimientos, expandidos
        expandidos += 1

        for siguiente, movimiento in obtener_sucesores(actual):
            if siguiente not in visitados:
                visitados.add(siguiente)
                padres[siguiente] = (actual, movimiento)
                cola.append(siguiente)

    return None, None, expandidos


# ============================================================
# DFS - Busqueda en profundidad (pila)
# ============================================================
# Sigue una rama hasta el final antes de probar otra.
# Encuentra UNA solución, no necesariamente corta ni barata.
#
# Igual que en el laberinto de clase:
# - se recorren los sucesores en orden inverso para que el primero
#   sea el primero en salir de la pila.
# - un estado se marca como visitado cuando SALE de la pila.
# - el padre se actualiza cada vez que otro estado lo vuelve a apilar,
#   asi el camino final es el que realmente siguio el recorrido.

def dfs(inicio):

    pila = [inicio]
    visitados = set()
    padres = {inicio: None}
    expandidos = 0

    while pila:

        # Sale el ultimo estado que se agrego.
        actual = pila.pop()

        if actual in visitados:
            continue

        visitados.add(actual)

        if es_objetivo(actual):
            estados, movimientos = reconstruir_solucion(
                inicio, actual, padres
            )
            return estados, movimientos, expandidos

        expandidos += 1
        sucesores = obtener_sucesores(actual)

        for siguiente, movimiento in reversed(sucesores):
            if siguiente not in visitados:
                padres[siguiente] = (actual, movimiento)
                pila.append(siguiente)

    return None, None, expandidos


# ============================================================
# UCS - Busqueda de costo uniforme (cola de prioridad)
# Siempre expande el estado con MENOR COSTO ACUMULADO.
# Encuentra la solución de menor costo total.

def ucs(inicio):

    # Cada elemento es (costo acumulado, estado).
    cola = [(0, inicio)]

    # Mejor costo conocido para cada estado.
    costos = {inicio: 0}

    padres = {inicio: None}
    visitados = set()
    expandidos = 0

    while cola:

        costo_actual, actual = heapq.heappop(cola)

        # Entrada antigua: ese estado ya se proceso con menor costo.
        if actual in visitados:
            continue

        visitados.add(actual)

        # Al sacar el objetivo de la cola su costo ya es el minimo.
        if es_objetivo(actual):
            estados, movimientos = reconstruir_solucion(
                inicio, actual, padres
            )
            return estados, movimientos, expandidos

        expandidos += 1

        for siguiente, movimiento in obtener_sucesores(actual):
            nuevo_costo = costo_actual + costo_movimiento(movimiento)
            # Solo guardamos el camino si es mas barato que el conocido.
            if nuevo_costo < costos.get(siguiente, float("inf")):
                costos[siguiente] = nuevo_costo
                padres[siguiente] = (actual, movimiento)
                heapq.heappush(cola, (nuevo_costo, siguiente))

    return None, None, expandidos