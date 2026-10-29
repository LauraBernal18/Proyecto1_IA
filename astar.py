# BUSQUEDA INFORMADA: A*

import heapq

from nim import es_objetivo, obtener_sucesores, costo_movimiento
from busqueda_no_informada import reconstruir_solucion


# ---------------------------------------------------------
# HEURISTICAS

# h1 - Fichas restantes.
def h_fichas(estado):

    return sum(estado)

# h2 - Montones que todavia tienen fichas.
def h_montones(estado):

    return sum(1 for fichas in estado if fichas > 0)

# Heuristica que usa A* por defecto.
HEURISTICA_POR_DEFECTO = h_fichas

#---------------------------------------------------------
# A*

def astar(inicio, heuristica=HEURISTICA_POR_DEFECTO):

    h_inicio = heuristica(inicio)

    # Cada elemento es (f, h, desempate, g, estado).
    # Si dos estados tienen igual f, sale primero el de menor h
    # (el que parece mas cerca de la meta). 'desempate' evita
    # comparar estados cuando todo lo demas es igual.
    contador = 0
    cola = [(h_inicio, h_inicio, contador, 0, inicio)]

    # Mejor costo g conocido para cada estado.
    costos = {inicio: 0}

    padres = {inicio: None}
    visitados = set()
    expandidos = 0

    while cola:

        f, h, _, g_actual, actual = heapq.heappop(cola)

        # Entrada antigua: ese estado ya se proceso con menor costo.
        if actual in visitados:
            continue

        visitados.add(actual)

        # Con h admisible, al sacar el objetivo su costo ya es minimo.
        if es_objetivo(actual):
            estados, movimientos = reconstruir_solucion(
                inicio, actual, padres
            )
            return estados, movimientos, expandidos

        expandidos += 1

        for siguiente, movimiento in obtener_sucesores(actual):

            nuevo_g = g_actual + costo_movimiento(movimiento)

            # Solo guardamos el camino si es mas barato que el conocido.
            if nuevo_g < costos.get(siguiente, float("inf")):
                costos[siguiente] = nuevo_g
                padres[siguiente] = (actual, movimiento)

                h_siguiente = heuristica(siguiente)
                contador += 1
                heapq.heappush(
                    cola,
                    (nuevo_g + h_siguiente, h_siguiente,
                     contador, nuevo_g, siguiente)
                )

    return None, None, expandidos

# PRUEBA RAPIDA
if __name__ == "__main__":

    import itertools
    from nim import ESTADO_INICIAL, calcular_costo_total
    from busqueda_no_informada import ucs

    print("Comparacion en el estado inicial", ESTADO_INICIAL)
    for nombre, algoritmo in (
        ("UCS", ucs),
        ("A* h_montones", lambda s: astar(s, h_montones)),
        ("A* h_fichas", lambda s: astar(s, h_fichas)),
    ):
        estados, movimientos, expandidos = algoritmo(ESTADO_INICIAL)
        print(f"  {nombre:<14} movimientos={len(movimientos):<3} "
              f"costo={calcular_costo_total(movimientos):<4} "
              f"expandidos={expandidos}")

    # Verificacion: A* debe dar el mismo costo que UCS en todos
    # los estados pequenos (prueba de que es optimo).
    errores = 0
    total = 0
    for estado in itertools.product(range(5), repeat=3):
        if es_objetivo(estado):
            continue
        costo_ucs = calcular_costo_total(ucs(estado)[1])
        for h in (h_fichas, h_montones):
            total += 1
            if calcular_costo_total(astar(estado, h)[1]) != costo_ucs:
                errores += 1
                print("ERROR en", estado, h.__name__)

    print()
    if errores:
        print(f"{errores} errores de {total}")
    else:
        print(f"A* da el mismo costo optimo que UCS en {total} pruebas")