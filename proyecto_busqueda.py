
import tkinter as tk
from tkinter import ttk, messagebox
import heapq

# -----------------------------------------------------------
# DEFINICIÓN DEL PROBLEMA: LABERINTO DE 9 x 9
# 0 = libre, 1 = muro, 2 = penalización, 3 = premio, 9 = meta
# Inicio: (0, 0) | Meta: (8, 8)
#---------------------------------------------------------------------

LABERINTO = [
    [0, 0, 0, 0, 1, 2, 0, 0, 0],
    [0, 0, 2, 0, 1, 1, 0, 0, 0],
    [3, 0, 0, 1, 0, 0, 1, 0, 0],
    [0, 3, 0, 0, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 9]
]

INICIO = (0, 0)
META = (8, 8)
COINS_INICIALES = 25

FILAS = len(LABERINTO)
COLUMNAS = len(LABERINTO[0])


# --------------------------------------------
# MODELADO: ESTADOS, OPERADORES Y COSTOS
# ---------------------------------------------

def construccion_grafo(laberinto):
    """Cada celda transitable es un estado del grafo."""
    grafo = {}
    filas = len(laberinto)
    columnas = len(laberinto[0])

    for f in range(filas):
        for c in range(columnas):
            if laberinto[f][c] == 1:
                continue

            estado = (f, c)
            vecinos = []

            # Orden de movimientos: arriba, abajo, izquierda, derecha
            movimientos = [
                (-1, 0), (1, 0), (0, -1), (0, 1)
            ]

            for df, dc in movimientos:
                nf, nc = f + df, c + dc

                if (0 <= nf < filas and
                        0 <= nc < columnas and
                        laberinto[nf][nc] != 1):
                    vecinos.append((nf, nc))

            grafo[estado] = vecinos

    return grafo


def costo_celda(valor):
    """Devuelve el costo de entrar a una celda."""
    if valor == 0:
        return 1
    if valor == 2:
        return 3
    if valor == 3:
        return 0.25
    if valor == 9:
        return 0
    return float("inf")


def costo_camino(laberinto, camino):
    """Suma los costos sin cobrar por la celda inicial."""
    total = 0

    for f, c in camino[1:]:
        total += costo_celda(laberinto[f][c])

    return total


# ---------------------------------------------
# FUNCION PARA RECONSTRUIR LA RUTA
# ---------------------------------------------

def reconstruir_camino(predecesor, objetivo):
    camino = []
    nodo = objetivo

    while nodo is not None:
        camino.append(nodo)
        nodo = predecesor[nodo]

    camino.reverse()
    return camino


# ----------------------------------------
# BUSQUEDA EN AMPLITUD: BFS
# ----------------------------------------

def bfs_camino(grafo, inicio, objetivo):
    cola = [inicio]
    visitados = {inicio}
    predecesor = {inicio: None}
    expandidos = 0

    while cola:
        nodo = cola.pop(0)
        expandidos += 1

        if nodo == objetivo:
            camino = reconstruir_camino(predecesor, objetivo)
            return camino, expandidos

        for vecino in grafo[nodo]:
            if vecino not in visitados:
                visitados.add(vecino)
                predecesor[vecino] = nodo
                cola.append(vecino)

    return None, expandidos


# ----------------------------------------------
# BUSQUEDA EN PROFUNDIDAD: DFS
# -----------------------------------------------

def dfs_camino(grafo, inicio, objetivo):
    pila = [inicio]
    visitados = set()
    predecesor = {inicio: None}
    expandidos = 0

    while pila:
        nodo = pila.pop()

        if nodo not in visitados:
            visitados.add(nodo)
            expandidos += 1

            if nodo == objetivo:
                camino = reconstruir_camino(predecesor, objetivo)
                return camino, expandidos

            vecinos = grafo[nodo]
            
            # Se invierte el orden para explorar primero arriba,
            # abajo, izquierda y derecha, según el orden establecido.
            for vecino in reversed(vecinos):
                if vecino not in predecesor:
                    predecesor[vecino] = nodo
                    pila.append(vecino)

    return None, expandidos


# ------------------------------------------------
# BUSQUEDA DE COSTO UNIFORME: UCS
# -------------------------------------------------

def ucs_camino(grafo, laberinto, inicio, objetivo):
    cola = [(0, inicio)]
    costo_hasta = {inicio: 0}
    predecesor = {inicio: None}
    expandidos = 0

    while cola:
        costo_actual, nodo = heapq.heappop(cola)

        # Ignora entradas antiguas que ya fueron mejoradas.
        if costo_actual > costo_hasta[nodo]:
            continue

        expandidos += 1

        if nodo == objetivo:
            camino = reconstruir_camino(predecesor, objetivo)
            return camino, expandidos

        for vecino in grafo[nodo]:
            f, c = vecino
            nuevo_costo = costo_actual + costo_celda(laberinto[f][c])

            if nuevo_costo < costo_hasta.get(vecino, float("inf")):
                costo_hasta[vecino] = nuevo_costo
                predecesor[vecino] = nodo
                heapq.heappush(cola, (nuevo_costo, vecino))

    return None, expandidos


# ------------------------------------------------
# Función común para ejecutar los algoritmos
# ------------------------------------------------

def ejecutar_algoritmo(nombre):
    grafo = construccion_grafo(LABERINTO)

    if nombre == "BFS":
        camino, expandidos = bfs_camino(grafo, INICIO, META)
    elif nombre == "DFS":
        camino, expandidos = dfs_camino(grafo, INICIO, META)
    elif nombre == "BCU":
        camino, expandidos = ucs_camino(
            grafo, LABERINTO, INICIO, META
        )
    else:
        raise ValueError("Algoritmo no disponible.")

    if camino is None:
        return None

    costo = costo_camino(LABERINTO, camino)

    return {
        "nombre": nombre,
        "camino": camino,
        "movimientos": len(camino) - 1,
        "costo": costo,
        "coins": COINS_INICIALES - costo,
        "expandidos": expandidos
    }


# -----------------------------------
# INTERFAZ GRAFICA CON TKINTER
# -------------------------------

class AplicacionLaberinto:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Proyecto de busqueda en IA")
        self.ventana.resizable(False, False)

        self.botones_celdas = {}
        self.camino_actual = []

        titulo = ttk.Label(
            ventana,
            text="Laberinto: algoritmos de busqueda",
            font=("Arial", 16, "bold")
        )
        titulo.pack(pady=(12, 4))

        descripcion = ttk.Label(
            ventana,
            text="Selecciona BFS, DFS o BCU para encontrar una ruta."
        )
        descripcion.pack(pady=4)

        # Tablero visual
        tablero = ttk.Frame(ventana, padding=8)
        tablero.pack()

        for f in range(FILAS):
            for c in range(COLUMNAS):
                boton = tk.Label(
                    tablero,
                    width=4,
                    height=2,
                    relief="solid",
                    borderwidth=1,
                    font=("Arial", 10, "bold")
                )
                boton.grid(row=f, column=c, padx=1, pady=1)
                self.botones_celdas[(f, c)] = boton

        # Botones para seleccionar el algoritmo
        controles = ttk.Frame(ventana, padding=5)
        controles.pack()

        for nombre in ("BFS", "DFS", "BCU"):
            ttk.Button(
                controles,
                text=nombre,
                command=lambda n=nombre: self.resolver(n)
            ).pack(side="left", padx=5)

        ttk.Button(
            controles,
            text="Limpiar ruta",
            command=self.limpiar
        ).pack(side="left", padx=5)

        self.resultado = ttk.Label(
            ventana,
            text="Selecciona un algoritmo para comenzar.",
            justify="left",
            font=("Arial", 10)
        )
        self.resultado.pack(pady=8)

        leyenda = ttk.Label(
            ventana,
            text=(
                "Verde: inicio | Rojo: meta | Negro: muro\n"
                "Azul: ruta | Amarillo: premio | Naranja: penalizacion"
            ),
            justify="center"
        )
        leyenda.pack(pady=(0, 12))

        self.dibujar_tablero()

    def dibujar_tablero(self):
        """Dibuja el laberinto y resalta la ruta encontrada."""
        for f in range(FILAS):
            for c in range(COLUMNAS):
                valor = LABERINTO[f][c]
                celda = self.botones_celdas[(f, c)]

                colores = {
                    0: "white",
                    1: "black",
                    2: "orange",
                    3: "gold",
                    9: "tomato"
                }

                color = colores[valor]
                texto = str(valor)

                if (f, c) == INICIO:
                    color = "lightgreen"
                    texto = "I"
                elif (f, c) == META:
                    color = "tomato"
                    texto = "M"
                elif (f, c) in self.camino_actual:
                    color = "lightblue"
                    texto = "*"

                celda.config(
                    bg=color,
                    text=texto,
                    fg="white" if valor == 1 else "black"
                )

    def resolver(self, nombre):
        resultado = ejecutar_algoritmo(nombre)

        if resultado is None:
            messagebox.showinfo(
                "Resultado",
                "No se encontro una ruta hasta la meta."
            )
            return

        self.camino_actual = resultado["camino"]
        self.dibujar_tablero()

        ruta_texto = " -> ".join(
            f"({f},{c})" for f, c in resultado["camino"]
        )

        self.resultado.config(
            text=(
                f"Algoritmo: {nombre}\n"
                f"Movimientos: {resultado['movimientos']}\n"
                f"Costo total: {resultado['costo']:.2f}\n"
                f"Coins restantes: {resultado['coins']:.2f}\n"
                f"Estados expandidos: {resultado['expandidos']}\n"
                f"Ruta: {ruta_texto}"
            )
        )

    def limpiar(self):
        self.camino_actual = []
        self.dibujar_tablero()
        self.resultado.config(
            text="Selecciona un algoritmo para comenzar."
        )


# -----------------------
# INICIO DEL PROGRAMA
# ----------------------

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionLaberinto(ventana)
    ventana.mainloop()
