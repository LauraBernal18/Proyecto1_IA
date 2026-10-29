# ============================================================
# PROYECTO DE INTELIGENCIA ARTIFICIAL - JUEGO DE NIM
#
# Este archivo solo junta las piezas:
#   nim.py                    -> reglas del juego
#   busqueda_no_informada.py  -> BFS, DFS, UCS
#   astar.py                  -> A* 
#   busqueda_informada_minimax.py -> Minimax y poda alfa-beta
#   interfaz_minimax.py       -> pestaña "Jugar contra la máquina"
#   interfaz.py               -> ventana Tkinter

import tkinter as tk

from interfaz import AplicacionNim
from busqueda_no_informada import bfs, dfs, ucs
from interfaz_minimax import crear_pestana_minimax
from astar import astar

#cuando exista astar.py, descomentar esta linea:
# from astar import astar

# Cada algoritmo de busqueda se registra aqui con su nombre.
# La interfaz crea un botón por cada uno automáticamente.
ALGORITMOS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    "A*": astar,
}


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionNim(ventana, ALGORITMOS)

    # Pestaña del modo de dos jugadores (Minimax / Alfa-beta).
    pestana_juego = app.agregar_pestana("Jugar contra la máquina")
    crear_pestana_minimax(pestana_juego)

    ventana.mainloop()