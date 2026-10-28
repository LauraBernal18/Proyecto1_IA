# REGLAS DEL JUEGO DE NIM
# ============================================================
# Este archivo contiene lo que todos los algoritmos comparten:
# como se representa el juego, que movimientos existen y
# cuanto cuesta cada movimiento.
#

# El estado se representa con una tupla.
# Ejemplo: (3, 5, 7) significa:
# Monton 1: 3 fichas, Monton 2: 5 fichas, Monton 3: 7 fichas
ESTADO_INICIAL = (3, 5, 7)

# Limites para que la búsqueda no se vuelva demasiado lenta.
MAX_MONTONES = 5
MAX_FICHAS = 12
LIMITE_ESTADOS = 50000


# El objetivo es dejar todos los montones en cero.
# Funciona con cualquier cantidad de montones.
def es_objetivo(estado):

    return sum(estado) == 0


# Genera todos los movimientos posibles.
# En cada movimiento se quita una o más fichas de un solo montón.
# Devuelve una lista de (nuevo_estado, movimiento), donde
# movimiento = (indice_del_monton, cantidad_quitada).
def obtener_sucesores(estado):

    sucesores = []

    for i in range(len(estado)):
        for quitar in range(1, estado[i] + 1):
            nuevo_estado = list(estado)
            nuevo_estado[i] = nuevo_estado[i] - quitar
            sucesores.append((tuple(nuevo_estado), (i, quitar)))
            
    return sucesores


# Costo usado por UCS (y por A* despues):
# quitar k fichas cuesta k al cuadrado.
# Es una regla definida para el proyecto, no del Nim original.
def costo_movimiento(movimiento):
    monton, quitar = movimiento
    return quitar * quitar


def calcular_costo_total(movimientos):
    costo_total = 0
    
    for movimiento in movimientos:
        costo_total += costo_movimiento(movimiento)
        
    return costo_total


# Convierte el texto escrito por el usuario (ej: "3, 5, 7")
# en un estado. Si algo esta mal, lanza ValueError con un mensaje.
def leer_estado(texto):

    partes = texto.replace(" ", "").split(",")
    montones = []

    for parte in partes:
        if not parte.isdigit():
            raise ValueError(
                "Escribe números enteros separados por comas.\n"
                "Ejemplo: 3, 5, 7"
            )
        montones.append(int(parte))

    if len(montones) > MAX_MONTONES:
        raise ValueError(f"Maximo {MAX_MONTONES} montones.")

    if max(montones) > MAX_FICHAS:
        raise ValueError(f"Maximo {MAX_FICHAS} fichas por monton.")

    # Cantidad total de estados posibles del juego.
    total_estados = 1

    for cantidad in montones:
        total_estados = total_estados * (cantidad + 1)

    if total_estados > LIMITE_ESTADOS:
        raise ValueError(
            "El juego tiene demasiados estados "
            f"({total_estados}) y la búsqueda sería muy lenta.\n"
            "Usa menos montones o menos fichas."
        )

    return tuple(montones)