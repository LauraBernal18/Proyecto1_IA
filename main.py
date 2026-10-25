# ============================================================
# PROYECTO DE INTELIGENCIA ARTIFICIAL - JUEGO DE NIM
#
# Este archivo solo junta las piezas:
#   nim.py                    -> reglas del juego
#   busqueda_no_informada.py  -> BFS, DFS, UCS
#   astar.py                  -> A*        (pendiente)
#   minimax.py                -> Minimax   (pendiente)
#   interfaz.py               -> ventana Tkinter

import tkinter as tk

from interfaz import AplicacionNim
from busqueda_no_informada import bfs, dfs, ucs

#cuando exista astar.py, descomentar esta linea:
# from astar import astar

# Cada algoritmo de busqueda se registra aqui con su nombre.
# La interfaz crea un botón por cada uno automáticamente.
ALGORITMOS = {
    "BFS": bfs,
    "DFS": dfs,
    "UCS": ucs,
    #cuando exista astar.py, descomentar esta linea:
    # "A*": astar,
}


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionNim(ventana, ALGORITMOS)

    # Pestaña del modo de dos jugadores (Minimax).
    # Cuando exista su interfaz, reemplazar el Label por su codigo, por ejemplo:
    #     from interfaz_minimax import crear_pestana_minimax
    #     crear_pestana_minimax(pestana_juego)
    pestana_juego = app.agregar_pestana("Jugar contra la máquina")

    tk.Label(
        pestana_juego,
        text="Modo de dos jugadores (Minimax): pendiente",
        font=("Arial", 14)
    ).pack(pady=80)

    ventana.mainloop()