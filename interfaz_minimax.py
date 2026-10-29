# ============================================================
# INTERFAZ DEL MODO DE DOS JUGADORES (Minimax con poda alfa-beta)
# ============================================================
# Pestaña "Jugar contra la máquina".
# La máquina es MAX y el humano es MIN.
# Quien toma la ultima ficha gana.
#
# El humano juega haciendo clic sobre una ficha: se quitan esa
# ficha y todas las que estan encima de ella en el mismo monton.
# Mientras la maquina piensa, el tablero y los controles se bloquean.
#
# Uso desde main.py:
#     from interfaz_minimax import crear_pestana_minimax
#     crear_pestana_minimax(pestana_juego)

import time
import tkinter as tk
from tkinter import ttk, messagebox

from nim import (
    ESTADO_INICIAL,
    leer_estado,
    es_objetivo,
    obtener_sucesores,
)
from interfaz import (
    COLOR_LIENZO,
    COLOR_BOTON,
    COLOR_BOTON_ACTIVO,
    COLOR_RETIRADA,
    COLORES_MONTONES,
    ALTO_FICHA,
    SEPARACION_FICHA,
    BASE_Y,
)
from busqueda_informada_minimax import (
    alfabeta,
    nim_sum,
    aplicar_movimiento,
    describir,
)


# Si el arbol completo del juego supera este numero de nodos y no hay
# limite de profundidad, se pregunta antes de empezar, porque la ventana
# se queda congelada mientras la maquina piensa.
# (Alfa-beta revisa mucho menos que el arbol completo, por eso es alto.)
LIMITE_ARBOL = 60_000_000

# Pausa antes de que mueva la maquina (ms), para ver la jugada del humano.
PAUSA_MAQUINA = 600

HUMANO = "Humano"
MAQUINA = "Máquina"


# Cuenta los nodos del arbol de juego completo desde 'estado'.
# Los estados con los mismos montones en otro orden tienen el mismo
# arbol, por eso se guardan ordenados en 'memo'.
def contar_nodos_arbol(estado, memo):

    clave = tuple(sorted(estado))

    if clave not in memo:
        memo[clave] = 1 + sum(
            contar_nodos_arbol(siguiente, memo)
            for siguiente, movimiento in obtener_sucesores(estado)
        )

    return memo[clave]


# Pregunta si se quiere seguir cuando la busqueda puede tardar mucho.
# Devuelve True si se puede buscar.
def confirmar_busqueda(estado, profundidad_max):

    if profundidad_max is not None:
        return True

    nodos = contar_nodos_arbol(estado, {})

    if nodos <= LIMITE_ARBOL:
        return True

    return messagebox.askyesno(
        "Búsqueda lenta",
        f"El árbol completo de {estado} tiene {nodos:,} nodos.\n"
        "Sin límite de profundidad la máquina puede tardar mucho "
        "y la ventana se quedará congelada.\n\n"
        "Sugerencia: pon un límite de profundidad.\n\n"
        "¿Continuar de todas formas?"
    )


def crear_pestana_minimax(padre):

    return JuegoMinimax(padre)


class JuegoMinimax:

    def __init__(self, padre):

        self.padre = padre

        self.estado = ESTADO_INICIAL
        self.turno = None          # HUMANO, MAQUINA o None si no hay partida
        self.profundidad_max = None
        self.resaltado = None

        # Identificador de la jugada de la maquina programada con after().
        self.pendiente = None

        self.crear_controles()
        self.crear_tablero()
        self.crear_paneles()

        self.dibujar_montones(self.estado)

    # --------------------------------------------------------
    # CONTROLES
    # --------------------------------------------------------
    def crear_controles(self):

        marco = tk.LabelFrame(
            self.padre,
            text="Nueva partida",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=6
        )
        marco.pack(padx=12, pady=(10, 5), fill="x")

        # ---- Fila 1: montones y quien empieza ----
        tk.Label(marco, text="Montones:").grid(row=0, column=0, sticky="e")

        self.entrada = tk.Entry(
            marco,
            width=16,
            justify="center",
            font=("Arial", 11)
        )
        self.entrada.insert(0, ", ".join(str(n) for n in ESTADO_INICIAL))
        self.entrada.grid(row=0, column=1, padx=5, pady=2)

        tk.Label(marco, text="Empieza:").grid(row=0, column=2, sticky="e")

        self.selector_inicio = ttk.Combobox(
            marco,
            values=[HUMANO, MAQUINA],
            state="readonly",
            width=10
        )
        self.selector_inicio.set(HUMANO)
        self.selector_inicio.grid(row=0, column=3, padx=5, pady=2)

        self.boton_nueva = self.crear_boton(
            marco, "Nueva partida", self.nueva_partida
        )
        self.boton_nueva.grid(row=0, column=4, padx=6, pady=2)

        # ---- Fila 2: profundidad ----
        tk.Label(
            marco,
            text="Profundidad máx. (0 = sin límite):"
        ).grid(row=1, column=0, columnspan=2, sticky="e")

        self.selector_profundidad = tk.Spinbox(
            marco,
            from_=0,
            to=60,
            width=5,
            justify="center"
        )
        self.selector_profundidad.grid(row=1, column=2, sticky="w", padx=5, pady=2)

    def crear_boton(self, padre, texto, comando):

        return tk.Button(
            padre,
            text=texto,
            width=14,
            bg=COLOR_BOTON,
            fg="white",
            activebackground=COLOR_BOTON_ACTIVO,
            activeforeground="white",
            relief="flat",
            font=("Arial", 10, "bold"),
            command=comando
        )

    # Bloquea (o desbloquea) todo lo que el humano podria tocar
    # mientras la maquina piensa.
    def bloquear_controles(self, bloquear):

        estado_widget = "disabled" if bloquear else "normal"

        self.entrada.config(state=estado_widget)
        self.selector_profundidad.config(state=estado_widget)
        self.boton_nueva.config(state=estado_widget)
        self.selector_inicio.config(
            state="disabled" if bloquear else "readonly"
        )
        self.lienzo.config(cursor="watch" if bloquear else "hand2")

    # --------------------------------------------------------
    # TABLERO
    # --------------------------------------------------------
    def crear_tablero(self):

        self.lienzo = tk.Canvas(
            self.padre,
            height=270,
            background=COLOR_LIENZO,
            highlightthickness=0,
            cursor="hand2"
        )
        self.lienzo.pack(padx=12, pady=5, fill="x")
        self.lienzo.bind("<Configure>", self.redibujar)
        self.lienzo.bind("<Button-1>", self.clic_en_tablero)

        self.etiqueta_turno = tk.Label(
            self.padre,
            text="Pulsa «Nueva partida» para empezar.",
            font=("Arial", 12, "bold")
        )
        self.etiqueta_turno.pack()

    # --------------------------------------------------------
    # PANELES DE ANALISIS E HISTORIAL
    # --------------------------------------------------------
    def crear_paneles(self):

        marco_analisis = tk.LabelFrame(
            self.padre,
            text="Análisis de la máquina (alfa-beta)",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=4
        )
        marco_analisis.pack(padx=12, pady=5, fill="x")

        self.etiqueta_analisis = tk.Label(
            marco_analisis,
            text="",
            justify="left",
            anchor="w",
            font=("Consolas", 10)
        )
        self.etiqueta_analisis.pack(fill="x")

        marco_historial = tk.LabelFrame(
            self.padre,
            text="Historial",
            font=("Arial", 11, "bold"),
            padx=5,
            pady=5
        )
        marco_historial.pack(padx=12, pady=(5, 10), fill="both", expand=True)

        barra = tk.Scrollbar(marco_historial)
        barra.pack(side="right", fill="y")

        self.texto_historial = tk.Text(
            marco_historial,
            height=4,
            font=("Consolas", 10),
            yscrollcommand=barra.set,
            state="disabled"
        )
        self.texto_historial.pack(side="left", fill="both", expand=True)

        barra.config(command=self.texto_historial.yview)

    def agregar_historial(self, linea):

        self.texto_historial.config(state="normal")
        self.texto_historial.insert(tk.END, linea + "\n")
        self.texto_historial.see(tk.END)
        self.texto_historial.config(state="disabled")

    def limpiar_historial(self):

        self.texto_historial.config(state="normal")
        self.texto_historial.delete("1.0", tk.END)
        self.texto_historial.config(state="disabled")

    # --------------------------------------------------------
    # DIBUJAR LOS MONTONES (mismo estilo que la pestaña de búsqueda)
    # --------------------------------------------------------
    def dibujar_montones(self, estado, resaltado=None):

        self.resaltado = resaltado
        self.lienzo.delete("all")

        ancho = max(self.lienzo.winfo_width(), 600)
        separacion = ancho / len(estado)

        for i in range(len(estado)):

            cantidad = estado[i]
            centro = separacion * i + separacion / 2
            color = COLORES_MONTONES[i % len(COLORES_MONTONES)]

            for nivel in range(cantidad):
                self.dibujar_ficha(centro, nivel, color, "#333333", ())

            # Fichas quitadas en el ultimo movimiento.
            if resaltado is not None and resaltado[0] == i:
                for nivel in range(cantidad, cantidad + resaltado[1]):
                    self.dibujar_ficha(
                        centro, nivel, "", COLOR_RETIRADA, (4, 3)
                    )

            self.lienzo.create_text(
                centro,
                BASE_Y + 22,
                text=f"Montón {i + 1}",
                font=("Arial", 11, "bold")
            )

            self.lienzo.create_text(
                centro,
                BASE_Y + 40,
                text=f"{cantidad} fichas",
                font=("Arial", 10)
            )

    def dibujar_ficha(self, centro, nivel, relleno, borde, punteado):

        y_inferior = BASE_Y - nivel * SEPARACION_FICHA

        self.lienzo.create_oval(
            centro - 40,
            y_inferior - ALTO_FICHA,
            centro + 40,
            y_inferior,
            fill=relleno,
            outline=borde,
            width=2,
            dash=punteado
        )

    def redibujar(self, evento):

        self.dibujar_montones(self.estado, self.resaltado)

    # --------------------------------------------------------
    # LEER OPCIONES
    # --------------------------------------------------------
    # Devuelve la profundidad maxima (None = sin limite) o lanza ValueError.
    def leer_profundidad(self):

        texto = self.selector_profundidad.get().strip()

        if not texto.isdigit():
            raise ValueError("La profundidad debe ser un entero >= 0.")

        profundidad = int(texto)

        if profundidad == 0:
            return None
        return profundidad

    # --------------------------------------------------------
    # PARTIDA
    # --------------------------------------------------------
    def nueva_partida(self):

        try:
            estado = leer_estado(self.entrada.get())
            profundidad_max = self.leer_profundidad()

        except ValueError as error:
            messagebox.showerror("Entrada incorrecta", str(error))
            return

        if es_objetivo(estado):
            messagebox.showerror(
                "Entrada incorrecta", "Pon al menos una ficha."
            )
            return

        # El arbol solo se achica durante la partida: basta revisar el inicio.
        if not confirmar_busqueda(estado, profundidad_max):
            return

        self.cancelar_pendiente()

        self.estado = estado
        self.profundidad_max = profundidad_max

        self.dibujar_montones(self.estado)
        self.limpiar_historial()
        self.etiqueta_analisis.config(text="")

        limite = "sin límite" if profundidad_max is None else profundidad_max
        self.agregar_historial(
            f"Nueva partida: {estado} | alfa-beta, profundidad {limite}"
        )

        if self.selector_inicio.get() == MAQUINA:
            self.programar_maquina()
        else:
            self.dar_turno_humano()

    def dar_turno_humano(self):

        self.turno = HUMANO
        self.bloquear_controles(False)
        self.etiqueta_turno.config(
            text="Tu turno: haz clic en una ficha "
                 "(se quitan esa y las de encima).",
            fg="black"
        )

    def terminar(self, ganador):

        self.turno = None
        self.bloquear_controles(False)

        if ganador == HUMANO:
            texto = "¡Ganaste! Tomaste la última ficha."
            color = "#2A9D8F"
        else:
            texto = "Ganó la máquina: tomó la última ficha."
            color = COLOR_RETIRADA

        self.etiqueta_turno.config(text=texto, fg=color)
        self.agregar_historial(texto)

    # --------------------------------------------------------
    # JUGADA DEL HUMANO
    # --------------------------------------------------------
    # El clic se convierte en (monton, fichas a quitar).
    def clic_en_tablero(self, evento):

        # Solo se puede mover en el turno del humano.
        if self.turno != HUMANO:
            return

        ancho = max(self.lienzo.winfo_width(), 600)
        separacion = ancho / len(self.estado)
        monton = int(evento.x // separacion)

        if monton >= len(self.estado):
            return

        # Nivel de la ficha clicada (0 = la de abajo).
        nivel = int((BASE_Y - evento.y) // SEPARACION_FICHA)

        if nivel < 0 or nivel >= self.estado[monton]:
            return

        movimiento = (monton, self.estado[monton] - nivel)
        self.estado = aplicar_movimiento(self.estado, movimiento)
        self.dibujar_montones(self.estado, movimiento)

        self.agregar_historial(
            f"Humano:  {describir(movimiento):<26} -> {self.estado}"
        )

        if es_objetivo(self.estado):
            self.terminar(HUMANO)
            return

        self.programar_maquina()

    # --------------------------------------------------------
    # JUGADA DE LA MAQUINA (MAX)
    # --------------------------------------------------------
    def programar_maquina(self):

        # Desde aqui el humano ya no puede tocar nada.
        self.turno = MAQUINA
        self.bloquear_controles(True)
        self.etiqueta_turno.config(
            text="La máquina está pensando...", fg="black"
        )
        self.pendiente = self.padre.after(PAUSA_MAQUINA, self.jugar_maquina)

    def cancelar_pendiente(self):

        if self.pendiente is not None:
            self.padre.after_cancel(self.pendiente)
            self.pendiente = None

    def jugar_maquina(self):

        self.pendiente = None
        estado_antes = self.estado

        t0 = time.perf_counter()
        movimiento, valor, nodos = alfabeta(
            estado_antes, True, self.profundidad_max
        )
        milisegundos = (time.perf_counter() - t0) * 1000

        self.estado = aplicar_movimiento(estado_antes, movimiento)
        self.dibujar_montones(self.estado, movimiento)

        self.agregar_historial(
            f"Máquina: {describir(movimiento):<26} -> {self.estado}"
            f"   (valor {valor}, {nodos} nodos)"
        )

        if valor > 0:
            lectura = "la máquina gana con juego perfecto"
        elif valor < 0:
            lectura = "la máquina pierde si juegas perfecto"
        else:
            lectura = "incierto (se cortó por profundidad)"

        self.etiqueta_analisis.config(
            text=(
                f"Nodos visitados: {nodos}    "
                f"Tiempo: {milisegundos:.1f} ms\n"
                f"Jugada: {describir(movimiento)}    "
                f"Valor: {valor} ({lectura})\n"
                f"XOR antes: {nim_sum(estado_antes)}    "
                f"XOR después: {nim_sum(self.estado)}    "
                "(XOR 0 = posición perdedora para quien mueve)"
            )
        )

        # Los clics hechos mientras la ventana estaba congelada quedan en
        # cola. Se procesan ahora, todavia en turno de la maquina y con los
        # controles bloqueados, para que se descarten.
        self.padre.update()

        if es_objetivo(self.estado):
            self.terminar(MAQUINA)
            return

        self.dar_turno_humano()
