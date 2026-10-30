# ============================================================
# BUSQUEDA ADVERSARIA: MINIMAX Y PODA ALFA-BETA (dos jugadores)
# ============================================================
# Nim clasico: quien toma la ultima ficha gana.
# Si a un jugador le toca mover y no quedan fichas, ese jugador perdio.
#
# Valores: +1 si gana MAX, -1 si gana MIN.
#
# La poda alfa-beta es minimax que deja de explorar las ramas que no
# pueden cambiar la decision: da el mismo resultado visitando menos nodos.
#
# minimax(...) y alfabeta(...) tienen la misma interfaz:
#   (estado, turno_max=True, profundidad_max=None, evaluar=evaluar_estado)
# y devuelven:
#   (mejor_movimiento, valor, nodos_visitados)
# mejor_movimiento = (indice_del_monton, fichas_a_quitar), o None si el
# estado ya es terminal.

import itertools
import time
from functools import reduce
from operator import xor

from nim import ESTADO_INICIAL, es_objetivo, obtener_sucesores


INFINITO = float("inf")


# ============================================================
# ESTADO TERMINAL Y FUNCION DE EVALUACION

# Valor de un estado terminal: el jugador que debe mover ya perdio.
def valor_terminal(turno_max):

    if turno_max:
        return -1
    return 1


# Evaluacion simple para cuando se corta por profundidad.
# Si queda un solo monton con fichas, el que mueve gana (se lo lleva todo).
# En cualquier otro caso no sabemos quien gana: 0.
def evaluar_estado(estado, turno_max):

    no_vacios = sum(1 for fichas in estado if fichas > 0)

    if no_vacios == 1:
        if turno_max:
            return 1
        return -1

    return 0


# Indica si hay que cortar la busqueda en esta profundidad.
def se_alcanzo_limite(profundidad, profundidad_max):

    return profundidad_max is not None and profundidad >= profundidad_max


# ============================================================
# MINIMAX PURO
# Recorre todo el arbol (hasta el limite de profundidad, si lo hay).

def _valor_minimax(estado, turno_max, profundidad, profundidad_max,
                   evaluar, contador):

    contador["nodos"] += 1

    if es_objetivo(estado):
        return valor_terminal(turno_max)

    if se_alcanzo_limite(profundidad, profundidad_max):
        return evaluar(estado, turno_max)

    valores = [
        _valor_minimax(siguiente, not turno_max, profundidad + 1,
                       profundidad_max, evaluar, contador)
        for siguiente, movimiento in obtener_sucesores(estado)
    ]

    if turno_max:
        return max(valores)
    return min(valores)


def minimax(estado, turno_max=True, profundidad_max=None,
            evaluar=evaluar_estado):

    # Contador local (no global) que comparten las llamadas recursivas.
    contador = {"nodos": 1}

    if es_objetivo(estado):
        return None, valor_terminal(turno_max), contador["nodos"]

    mejor_movimiento = None
    mejor_valor = -INFINITO if turno_max else INFINITO

    for siguiente, movimiento in obtener_sucesores(estado):
        valor = _valor_minimax(siguiente, not turno_max, 1,
                               profundidad_max, evaluar, contador)

        # MAX busca el mayor valor, MIN el menor.
        if (turno_max and valor > mejor_valor) or \
           (not turno_max and valor < mejor_valor):
            mejor_valor = valor
            mejor_movimiento = movimiento

    return mejor_movimiento, mejor_valor, contador["nodos"]


# ============================================================
# MINIMAX CON PODA ALFA-BETA
# alfa: mejor valor que MAX ya tiene asegurado.
# beta: mejor valor que MIN ya tiene asegurado.
# Si alfa >= beta, el resto de hermanos no puede cambiar la decision.

def _valor_alfabeta(estado, turno_max, alfa, beta, profundidad,
                    profundidad_max, evaluar, contador):

    contador["nodos"] += 1

    if es_objetivo(estado):
        return valor_terminal(turno_max)

    if se_alcanzo_limite(profundidad, profundidad_max):
        return evaluar(estado, turno_max)

    if turno_max:
        valor = -INFINITO
        for siguiente, movimiento in obtener_sucesores(estado):
            valor = max(valor, _valor_alfabeta(
                siguiente, False, alfa, beta, profundidad + 1,
                profundidad_max, evaluar, contador))
            alfa = max(alfa, valor)
            if alfa >= beta:
                break  # poda beta
        return valor

    valor = INFINITO
    for siguiente, movimiento in obtener_sucesores(estado):
        valor = min(valor, _valor_alfabeta(
            siguiente, True, alfa, beta, profundidad + 1,
            profundidad_max, evaluar, contador))
        beta = min(beta, valor)
        if alfa >= beta:
            break  # poda alfa
    return valor


def alfabeta(estado, turno_max=True, profundidad_max=None,
             evaluar=evaluar_estado):

    # Contador local (no global) que comparten las llamadas recursivas.
    contador = {"nodos": 1}

    if es_objetivo(estado):
        return None, valor_terminal(turno_max), contador["nodos"]

    alfa = -INFINITO
    beta = INFINITO
    mejor_movimiento = None
    mejor_valor = -INFINITO if turno_max else INFINITO

    for siguiente, movimiento in obtener_sucesores(estado):
        valor = _valor_alfabeta(siguiente, not turno_max, alfa, beta, 1,
                                profundidad_max, evaluar, contador)

        # En la raiz se actualiza la ventana para podar a los hermanos.
        if turno_max and valor > mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
            alfa = max(alfa, valor)
        elif not turno_max and valor < mejor_valor:
            mejor_valor = valor
            mejor_movimiento = movimiento
            beta = min(beta, valor)

    return mejor_movimiento, mejor_valor, contador["nodos"]


# ============================================================
# VERIFICACION CON LA SOLUCION MATEMATICA (XOR)
# Teoria del Nim: el jugador que mueve gana si y solo si el XOR
# de los montones (nim-sum) es distinto de 0. La jugada ganadora
# es la que deja el XOR en 0.

def nim_sum(estado):

    return reduce(xor, estado, 0)


def aplicar_movimiento(estado, movimiento):

    monton, quitar = movimiento
    nuevo_estado = list(estado)
    nuevo_estado[monton] = nuevo_estado[monton] - quitar
    return tuple(nuevo_estado)


# Prueba todos los estados con 'montones' montones de 0 a 'max_fichas'
# fichas, sin limite de profundidad y con ambos jugadores en turno.
# Devuelve (estados_probados, lista_de_errores).
def verificar_contra_xor(algoritmo=alfabeta, montones=3, max_fichas=4):

    errores = []
    probados = 0

    for estado in itertools.product(range(max_fichas + 1), repeat=montones):

        if es_objetivo(estado):
            continue

        for turno_max in (True, False):

            movimiento, valor, nodos = algoritmo(estado, turno_max)
            probados += 1

            # Si el XOR es distinto de 0, gana el jugador que mueve.
            gana_el_que_mueve = nim_sum(estado) != 0
            gana_max = gana_el_que_mueve == turno_max
            valor_esperado = 1 if gana_max else -1

            if valor != valor_esperado:
                errores.append((estado, turno_max, "valor", valor))

            # En posicion ganadora, la jugada debe dejar el XOR en 0.
            elif gana_el_que_mueve and \
                    nim_sum(aplicar_movimiento(estado, movimiento)) != 0:
                errores.append((estado, turno_max, "movimiento", movimiento))

    return probados, errores


def describir(movimiento):

    if movimiento is None:
        return "ninguno (estado terminal)"
    monton, quitar = movimiento
    return f"quitar {quitar} del monton {monton + 1}"


if __name__ == "__main__":

    algoritmos = (("Minimax", minimax), ("Alfa-beta", alfabeta))

    # ---- 1. Sin limite de profundidad ----
    # El arbol completo de (3, 5, 7) tiene unos 40 millones de nodos,
    # por eso minimax puro se compara con un estado mas chico.
    estado = (2, 3, 4)
    for nombre, algoritmo in algoritmos:
        t0 = time.perf_counter()
        movimiento, valor, nodos = algoritmo(estado)
        milisegundos = (time.perf_counter() - t0) * 1000
        print(f"{nombre:<10} en {estado}: {describir(movimiento)}, "
              f"valor {valor}, {nodos} nodos, {milisegundos:.2f} ms "
              f"(XOR = {nim_sum(estado)})")

    # ---- 2. Con limite de profundidad ----
    print()
    for limite in (2, 4):
        for nombre, algoritmo in algoritmos:
            movimiento, valor, nodos = algoritmo(ESTADO_INICIAL, True, limite)
            print(f"{nombre:<10} profundidad {limite}: {describir(movimiento)}, "
                  f"valor {valor}, {nodos} nodos")

    # ---- 3. Verificacion contra el XOR ----
    print()
    for nombre, algoritmo in algoritmos:
        probados, errores = verificar_contra_xor(algoritmo)
        if errores:
            print(f"{nombre}: {len(errores)} errores de {probados}. "
                  f"Primero: {errores[0]}")
        else:
            print(f"{nombre}: correcto en {probados} posiciones "
                  f"(3 montones de 0 a 4 fichas, ambos turnos)")
