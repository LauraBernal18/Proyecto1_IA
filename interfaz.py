# 
# INTERFAZ GRÁFICA (Tkinter)
# ============================================================
# La interfaz NO conoce los algoritmos uno por uno.
# Recibe un diccionario {nombre: funcion} desde main.py y crea
# un boton por cada uno. Asi, para agregar A* solo hay que
# registrarlo en main.py; este archivo no se toca.
#
# Tambien tiene pestanas: cada companero puede agregar la suya
# con agregar_pestana().

import time
import tkinter as tk
from tkinter import ttk, messagebox

from nim import (
    ESTADO_INICIAL,
    MAX_MONTONES,
    MAX_FICHAS,
    leer_estado,
    costo_movimiento,
    calcular_costo_total,
)


# ------------------------------------------------------------
# Colores y medidas
# ------------------------------------------------------------
COLOR_FONDO = "#1F2A44"
COLOR_LIENZO = "#F4F1EA"
COLOR_BOTON = "#2A9D8F"
COLOR_BOTON_ACTIVO = "#21867A"
COLOR_RETIRADA = "#C1121F"
COLORES_MONTONES = ["#E76F51", "#2A9D8F", "#E9C46A", "#6A4C93", "#457B9D"]

ALTO_FICHA = 16
SEPARACION_FICHA = 18
BASE_Y = 225


class AplicacionNim:

    def __init__(self, ventana, algoritmos):

        self.ventana = ventana

        # Diccionario {"BFS": bfs, "DFS": dfs, ...}
        self.algoritmos = algoritmos

        self.estado_inicial = ESTADO_INICIAL

        # Lo ultimo que se dibujo (para redibujar al cambiar el tamaño).
        self.estado_dibujado = ESTADO_INICIAL
        self.resaltado = None

        # Identificador de la animación en curso.
        self.animacion = None

        self.ventana.title("Proyecto IA - Juego de Nim")
        self.ventana.geometry("960x720")
        self.ventana.minsize(700, 500)
        self.ventana.configure(bg=COLOR_FONDO)

        self.crear_encabezado()

        self.pestanas = ttk.Notebook(self.ventana)
        self.pestanas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        pestana_busqueda = self.agregar_pestana("Búsqueda de soluciones")
        self.crear_pestana_busqueda(pestana_busqueda)

    # --------------------------------------------------------
    # PESTAÑAS
    # --------------------------------------------------------
    # Crea una pestaña vacía y la devuelve para que se llene.
    def agregar_pestana(self, titulo):

        marco = tk.Frame(self.pestanas)
        self.pestanas.add(marco, text=titulo)

        return marco

    # --------------------------------------------------------
    # ENCABEZADO
    # --------------------------------------------------------
    def crear_encabezado(self):

        encabezado = tk.Frame(self.ventana, bg=COLOR_FONDO)
        encabezado.pack(fill="x", pady=10)

        tk.Label(
            encabezado,
            text="JUEGO DE NIM",
            font=("Arial", 24, "bold"),
            bg=COLOR_FONDO,
            fg="white"
        ).pack()

        tk.Label(
            encabezado,
            text="Inteligencia Artificial · Búsqueda informada y no informada · Proyecto 1",
            font=("Arial", 10),
            bg=COLOR_FONDO,
            fg="#A8B2D1"
        ).pack()

    # --------------------------------------------------------
    # PESTAÑA DE BÚSQUEDA
    # --------------------------------------------------------
    # Crea una zona con barra de desplazamiento (scrollbar) vertical.
    def crear_marco_desplazable(self, padre):

        lienzo = tk.Canvas(padre, highlightthickness=0)
        barra = tk.Scrollbar(
            padre,
            orient="vertical",
            command=lienzo.yview
        )

        lienzo.configure(yscrollcommand=barra.set)

        barra.pack(side="right", fill="y")
        lienzo.pack(side="left", fill="both", expand=True)

        # Marco interior que vive dentro del lienzo.
        interior = tk.Frame(lienzo)

        ventana_interior = lienzo.create_window(
            (0, 0),
            window=interior,
            anchor="nw"
        )

        # Cuando el contenido cambia de tamaÑo, se actualiza
        # la zona que la barra puede recorrer.
        interior.bind(
            "<Configure>",
            lambda evento: lienzo.configure(
                scrollregion=lienzo.bbox("all")
            )
        )

        # El marco interior siempre ocupa todo el ancho disponible.
        lienzo.bind(
            "<Configure>",
            lambda evento: lienzo.itemconfig(
                ventana_interior, width=evento.width
            )
        )

        # Rueda del mouse (Windows/Mac: MouseWheel, Linux: Button-4/5).
        # Si el mouse esta sobre el cuadro de texto, ese cuadro
        # usa la rueda para su propio desplazamiento.
        def mover_con_rueda(evento):

            if isinstance(evento.widget, tk.Text):
                return

            if evento.num == 4 or evento.delta > 0:
                lienzo.yview_scroll(-1, "units")
            else:
                lienzo.yview_scroll(1, "units")

        self.ventana.bind_all("<MouseWheel>", mover_con_rueda)
        self.ventana.bind_all("<Button-4>", mover_con_rueda)
        self.ventana.bind_all("<Button-5>", mover_con_rueda)

        return interior

    def crear_pestana_busqueda(self, marco):

        # Todo el contenido de esta pestana va dentro de un marco
        # con barra de desplazamiento.
        marco = self.crear_marco_desplazable(marco)

        # ---- Estado inicial ----
        marco_inicial = tk.LabelFrame(
            marco,
            text="Estado inicial",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=8
        )
        marco_inicial.pack(padx=12, pady=(10, 5), fill="x")

        tk.Label(
            marco_inicial,
            text="Fichas por montón (separadas por comas):"
        ).grid(row=0, column=0, padx=5)

        self.entrada = tk.Entry(
            marco_inicial,
            width=20,
            justify="center",
            font=("Arial", 11)
        )
        self.entrada.insert(0, ", ".join(str(n) for n in self.estado_inicial))
        self.entrada.grid(row=0, column=1, padx=5)

        tk.Button(
            marco_inicial,
            text="Actualizar montones",
            command=self.actualizar_estado
        ).grid(row=0, column=2, padx=5)

        tk.Label(
            marco_inicial,
            text=f"Entre 1 y {MAX_MONTONES} montones, "
                 f"hasta {MAX_FICHAS} fichas cada uno.",
            font=("Arial", 8),
            fg="gray"
        ).grid(row=1, column=0, columnspan=3, pady=(4, 0))

        # ---- Lienzo con los montones ----
        self.lienzo = tk.Canvas(
            marco,
            height=280,
            background=COLOR_LIENZO,
            highlightthickness=0
        )
        self.lienzo.pack(padx=12, pady=5, fill="x")
        self.lienzo.bind("<Configure>", self.redibujar)

        self.etiqueta_paso = tk.Label(
            marco,
            text="",
            font=("Arial", 10, "italic")
        )
        self.etiqueta_paso.pack()

        # ---- Botones de algoritmos (uno por cada algoritmo registrado) ----
        marco_algoritmos = tk.LabelFrame(
            marco,
            text="Seleccionar algoritmo",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=8
        )
        marco_algoritmos.pack(padx=12, pady=5, fill="x")

        columna = 0

        for nombre in self.algoritmos:

            self.crear_boton(
                marco_algoritmos,
                f"Ejecutar {nombre}",
                lambda n=nombre: self.ejecutar_algoritmo(n)
            ).grid(row=0, column=columna, padx=6, pady=4)

            columna += 1

        self.crear_boton(
            marco_algoritmos,
            "Comparar todos",
            self.comparar_todos
        ).grid(row=0, column=columna, padx=6, pady=4)

        tk.Label(
            marco_algoritmos,
            text="Pausa entre pasos (ms):"
        ).grid(row=1, column=0, columnspan=2, pady=(6, 0))

        self.velocidad = tk.Scale(
            marco_algoritmos,
            from_=100,
            to=1500,
            resolution=100,
            orient="horizontal",
            length=250
        )
        self.velocidad.set(500)
        self.velocidad.grid(row=1, column=2, columnspan=3, pady=(0, 4))

        # ---- Resultados ----
        marco_resultados = tk.LabelFrame(
            marco,
            text="Resultados",
            font=("Arial", 11, "bold"),
            padx=10,
            pady=5
        )
        marco_resultados.pack(padx=12, pady=5, fill="x")

        self.etiqueta_resultados = tk.Label(
            marco_resultados,
            text="Selecciona un algoritmo para comenzar.",
            justify="left",
            anchor="w",
            font=("Arial", 10)
        )
        self.etiqueta_resultados.pack(fill="x", pady=3)

        # ---- Secuencia de movimientos ----
        marco_solucion = tk.LabelFrame(
            marco,
            text="Secuencia de movimientos",
            font=("Arial", 11, "bold"),
            padx=5,
            pady=5
        )
        marco_solucion.pack(padx=12, pady=(5, 10), fill="both", expand=True)

        barra = tk.Scrollbar(marco_solucion)
        barra.pack(side="right", fill="y")

        self.texto_solucion = tk.Text(
            marco_solucion,
            height=12,
            width=80,
            font=("Consolas", 10),
            yscrollcommand=barra.set,
            state="disabled"
        )
        self.texto_solucion.pack(side="left", fill="both", expand=True)

        barra.config(command=self.texto_solucion.yview)

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

    # --------------------------------------------------------
    # LEER EL ESTADO INICIAL
    # --------------------------------------------------------
    # Devuelve True si el texto era valido.
    def actualizar_estado(self):
        try:
            self.estado_inicial = leer_estado(self.entrada.get())

        except ValueError as error:
            messagebox.showerror("Entrada incorrecta", str(error))
            return False

        self.detener_animacion()
        self.dibujar_montones(self.estado_inicial)
        self.etiqueta_paso.config(text="")
        self.etiqueta_resultados.config(text="Estado inicial actualizado.")
        self.mostrar_texto("")

        return True

    # --------------------------------------------------------
    # DIBUJAR LOS MONTONES
    # --------------------------------------------------------
    # Cada ficha es un ovalo. Las fichas que se acaban de quitar
    # se dibujan en rojo con linea punteada encima del monton.

    def dibujar_montones(self, estado, resaltado=None):
        self.estado_dibujado = estado
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

        self.dibujar_montones(self.estado_dibujado, self.resaltado)

    # --------------------------------------------------------
    # ANIMACION DE LA SOLUCION
    # --------------------------------------------------------
    # Muestra la solucion paso a paso usando after().

    def animar(self, estados, movimientos, paso=0):

        if paso == 0:
            self.dibujar_montones(estados[0])
            self.etiqueta_paso.config(text="Estado inicial")

        else:
            monton, quitar = movimientos[paso - 1]
            self.dibujar_montones(estados[paso], (monton, quitar))
            self.etiqueta_paso.config(
                text=f"Paso {paso} de {len(movimientos)}: "
                     f"quitar {quitar} ficha(s) del montón {monton + 1}"
            )

        if paso < len(movimientos):
            self.animacion = self.ventana.after(
                self.velocidad.get(),
                self.animar,
                estados,
                movimientos,
                paso + 1
            )

        else:
            self.animacion = None

    def detener_animacion(self):

        if self.animacion is not None:
            self.ventana.after_cancel(self.animacion)
            self.animacion = None

    # --------------------------------------------------------
    # EJECUTAR UN ALGORITMO
    # --------------------------------------------------------

    # Ejecuta el algoritmo y mide cuanto tarda.
    def medir(self, nombre, inicio):

        algoritmo = self.algoritmos[nombre]
        t0 = time.perf_counter()
        estados, movimientos, expandidos = algoritmo(inicio)
        milisegundos = (time.perf_counter() - t0) * 1000
        return estados, movimientos, expandidos, milisegundos

    def ejecutar_algoritmo(self, nombre):

        # Lee lo que haya escrito en la caja de texto.
        if not self.actualizar_estado():
            return
        inicio = self.estado_inicial
        try:
            estados, movimientos, expandidos, ms = self.medir(nombre, inicio)

        except NotImplementedError:

            messagebox.showinfo(
                "Pendiente",
                f"El algoritmo {nombre} todavía no está implementado."
            )
            return

        if estados is None:

            self.etiqueta_resultados.config(text="No se encontró una solución.")
            self.mostrar_texto("No se encontró una solución.")
            return

        cantidad_movimientos = len(movimientos)
        costo_total = calcular_costo_total(movimientos)

        self.etiqueta_resultados.config(
            text=(
                f"Algoritmo: {nombre}\n"
                f"Estado inicial: {inicio}\n"
                f"Movimientos: {cantidad_movimientos}\n"
                f"Costo total: {costo_total}\n"
                f"Estados expandidos: {expandidos}\n"
                f"Tiempo: {ms:.2f} ms"
            )
        )

        # Secuencia completa en el cuadro de texto.
        lineas = [
            f"Algoritmo seleccionado: {nombre}",
            f"Estado inicial: {inicio}",
            ""
        ]

        for i in range(cantidad_movimientos):

            monton, quitar = movimientos[i]

            lineas.append(
                f"Paso {i + 1}: quitar {quitar} ficha(s) del montón {monton + 1}"
            )
            lineas.append(f"    Estado siguiente: {estados[i + 1]}")
            lineas.append(
                f"    Costo del movimiento: {costo_movimiento(movimientos[i])}"
            )
            lineas.append("")

        lineas.append(f"Estado final: {estados[-1]}")
        lineas.append(f"Movimientos totales: {cantidad_movimientos}")
        lineas.append(f"Costo acumulado: {costo_total}")
        lineas.append(f"Estados expandidos: {expandidos}")

        self.mostrar_texto("\n".join(lineas))

        # Animamos la solucion.
        self.animar(estados, movimientos)

    # --------------------------------------------------------
    # COMPARAR TODOS LOS ALGORITMOS
    # --------------------------------------------------------
    # Util para el informe: misma entrada, una tabla con las metricas.

    def comparar_todos(self):

        if not self.actualizar_estado():
            return

        inicio = self.estado_inicial

        lineas = [
            f"Estado inicial: {inicio}",
            "",
            f"{'Algoritmo':<12}{'Movimientos':<14}{'Costo':<10}"
            f"{'Expandidos':<14}{'Tiempo (ms)':<12}",
            "-" * 62
        ]

        for nombre in self.algoritmos:

            try:
                estados, movimientos, expandidos, ms = self.medir(nombre, inicio)

            except NotImplementedError:

                lineas.append(f"{nombre:<12}pendiente de implementar")
                continue

            if estados is None:

                lineas.append(f"{nombre:<12}sin solución")
                continue

            costo = calcular_costo_total(movimientos)

            lineas.append(
                f"{nombre:<12}{len(movimientos):<14}{costo:<10}"
                f"{expandidos:<14}{ms:<12.2f}"
            )

        self.etiqueta_resultados.config(
            text="Comparación de todos los algoritmos (ver tabla abajo)."
        )

        self.mostrar_texto("\n".join(lineas))

    # --------------------------------------------------------
    # ESCRIBIR EN EL AREA DE TEXTO
    # --------------------------------------------------------

    def mostrar_texto(self, contenido):

        self.texto_solucion.config(state="normal")
        self.texto_solucion.delete("1.0", tk.END)
        self.texto_solucion.insert("1.0", contenido)
        self.texto_solucion.config(state="disabled")