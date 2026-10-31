# Proyecto 1 · Algoritmos de búsqueda y teoría de juegos en Nim

Implementación y comparación de algoritmos de búsqueda informada y no informada, y de búsqueda adversaria, aplicados al juego de **Nim**. Incluye una interfaz gráfica en Tkinter para ejecutar los algoritmos, ver las secuencias de movimientos animadas y jugar contra la máquina.

**Curso:** Inteligencia Artificial · Escuela de Ingeniería de Sistemas y Computación, Universidad del Valle (Cali, 2026)

**Autores:** Dana Sofia Gómez Manrique · Hilary Herrera Erazo · Luis Santiago Arenas Hincapié · Laura Valentina Bernal Lozada

**Docente:** Andrés Mauricio Valencia Restrepo

---

## Contenido

- [Descripción](#descripción)
- [Requisitos](#requisitos)
- [Ejecución](#ejecución)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelado del problema](#modelado-del-problema)
- [Algoritmos implementados](#algoritmos-implementados)
- [Uso de la interfaz](#uso-de-la-interfaz)
- [Pruebas rápidas por consola](#pruebas-rápidas-por-consola)

---

## Descripción

El proyecto aborda Nim desde dos modalidades que comparten la representación de los montones y las acciones permitidas:

1. **Búsqueda de soluciones:** se busca una secuencia de movimientos que deje todos los montones vacíos, usando **BFS, DFS, UCS y A\***, y se comparan por número de movimientos, costo, estados expandidos y tiempo.
2. **Partida entre dos jugadores:** el humano juega contra la máquina, que elige sus jugadas con **Minimax** o **Minimax con poda alfa-beta**.

## Requisitos

- **Python 3** (el proyecto se desarrolló y probó con Python 3.12 y 3.14).
- **Tkinter**, que trae Python en Windows y macOS. En Linux (Ubuntu/Debian) se instala con:
  ```bash
  sudo apt install python3-tk
  ```
- No se necesita instalar ninguna librería adicional (no hay `requirements.txt`): solo se usa la biblioteca estándar.

Para comprobar que Tkinter está disponible:

```bash
python -m tkinter
```

Debe abrirse una ventana pequeña de prueba. Si aparece `No module named 'tkinter'`, hay que instalarlo como se indica arriba.

> En Linux y macOS el comando suele ser `python3` en lugar de `python`; en los pasos siguientes se puede usar cualquiera de los dos.

## Ejecución

1. Descomprimir el proyecto (o clonar el repositorio) y abrir una terminal **dentro de la carpeta del proyecto**, la que contiene `main.py`:
   ```bash
   cd Proyecto1_IA-main
   ```
2. Ejecutar la aplicación:
   ```bash
   python main.py
   ```
3. Se abre la ventana **"Proyecto IA - Juego de Nim"** con dos pestañas: la de búsqueda de soluciones y **"Jugar contra la máquina"**. No hace falta modificar ningún archivo.

Los comandos deben ejecutarse desde esa carpeta, porque los módulos se importan entre sí por nombre (`from nim import ...`).

## Estructura del proyecto

| Archivo | Descripción |
|---|---|
| `main.py` | Punto de entrada. Registra los algoritmos y abre la ventana. |
| `nim.py` | Reglas del juego: estado inicial, sucesores, prueba de meta, costo de los movimientos y validación de la entrada. |
| `busqueda_no_informada.py` | BFS, DFS, UCS y `reconstruir_solucion`. |
| `astar.py` | A\* con dos heurísticas (`h_fichas` y `h_montones`). |
| `busqueda_informada_minimax.py` | Minimax, poda alfa-beta, función de evaluación y verificación contra la solución matemática (XOR). |
| `interfaz.py` | Ventana principal en Tkinter: entrada de montones, botones de algoritmos, animación, resultados y tabla comparativa. |
| `interfaz_minimax.py` | Pestaña del modo de dos jugadores. |

## Modelado del problema

**Estado:** tupla de enteros no negativos, una posición por montón. Por defecto `ESTADO_INICIAL = (3, 5, 7)`.

**Acción:** elegir un montón y retirar entre 1 y todas sus fichas. Se representa como `(índice_del_montón, cantidad_quitada)`, con índices desde 0.

**Meta (búsqueda):** todos los montones vacíos, `(0, 0, 0)`.

**Costo (búsqueda):** retirar `k` fichas cuesta `k²`. Es una decisión de modelado del proyecto, no una regla del Nim original; permite que BFS (menos movimientos) y UCS (menos costo) encuentren rutas distintas.

**Límites de entrada:** máximo 5 montones, 12 fichas por montón y 50.000 estados posibles (producto de `nᵢ + 1`). Se validan en `leer_estado`.

**Modo adversario:** Nim clásico, gana quien toma la última ficha. Si a un jugador le toca mover y no quedan fichas, ese jugador perdió. La máquina es MAX y el humano es MIN, con valores `+1` si gana MAX y `-1` si gana MIN. No se usa la función de costo `k²`, pues el objetivo es ganar.

## Algoritmos implementados

**Búsqueda no informada** (`busqueda_no_informada.py`)

- **BFS:** cola FIFO; encuentra la solución con menos movimientos.
- **DFS:** pila LIFO; no garantiza optimalidad.
- **UCS:** cola de prioridad por costo acumulado `g`; encuentra la solución de costo mínimo.

**Búsqueda informada** (`astar.py`)

- **A\*:** cola de prioridad ordenada por `f = g + h`, con desempate por menor `h`. Heurísticas disponibles:
  - `h_fichas`: total de fichas restantes (por defecto).
  - `h_montones`: cantidad de montones que aún tienen fichas.

  Ambas son admisibles y consistentes con el costo `k²`, por lo que A\* conserva la optimalidad; `h_fichas` es la más informada.

Todos los algoritmos de búsqueda devuelven `(estados, movimientos, expandidos)`, o `(None, None, expandidos)` si no hay solución.

**Búsqueda adversaria** (`busqueda_informada_minimax.py`)

- **Minimax:** recorre el árbol del juego completo (o hasta una profundidad límite).
- **Alfa-beta:** mismo resultado que Minimax visitando menos nodos, al descartar ramas que no pueden cambiar la decisión.
- **Evaluación al cortar por profundidad:** si queda un solo montón con fichas, gana quien mueve; en otro caso el valor es `0`.
- Ambos devuelven `(mejor_movimiento, valor, nodos_visitados)`.

## Uso de la interfaz

**Pestaña de búsqueda**

1. Escribir las fichas de cada montón separadas por comas (por ejemplo `3, 5, 7`) y pulsar **Actualizar montones**.
2. Pulsar **Ejecutar BFS / DFS / UCS / A\*** para ver la secuencia de movimientos animada, el costo y los estados expandidos. La pausa entre pasos es ajustable.
3. Pulsar **Comparar todos** para obtener una tabla con movimientos, costo, expandidos y tiempo de cada algoritmo.

**Pestaña "Jugar contra la máquina"**

1. Definir los montones, quién empieza (humano o máquina), el algoritmo (Alfa-beta o Minimax) y la profundidad máxima (`0` = sin límite).
2. Pulsar **Nueva partida**. El humano juega haciendo clic sobre una ficha: se retiran esa ficha y las que están encima de ella en el mismo montón.
3. El panel de análisis muestra la jugada de la máquina, su valor y los nodos visitados; el historial registra la partida.
4. **Comparar** ejecuta Minimax y alfa-beta sobre el estado actual y muestra nodos y tiempo de cada uno.

> Con estados grandes y sin límite de profundidad, la interfaz pide confirmación antes de buscar, porque la ventana queda congelada mientras la máquina piensa. Alfa-beta tolera árboles mucho más grandes que Minimax puro; si la partida tarda demasiado, basta con definir una profundidad máxima (por ejemplo 4).

## Pruebas rápidas por consola

Cada módulo de algoritmos incluye una prueba que se ejecuta directamente (también desde la carpeta del proyecto y sin abrir la interfaz):

```bash
python astar.py
python busqueda_informada_minimax.py
```

**`python astar.py`** compara UCS y A\* en `(3, 5, 7)` y verifica que A\* obtiene el mismo costo óptimo que UCS en todos los estados de 3 montones con hasta 4 fichas. Salida esperada:

```
Comparacion en el estado inicial (3, 5, 7)
  UCS            movimientos=15  costo=15   expandidos=191
  A* h_montones  movimientos=15  costo=15   expandidos=185
  A* h_fichas    movimientos=15  costo=15   expandidos=15

A* da el mismo costo optimo que UCS en 248 pruebas
```

**`python busqueda_informada_minimax.py`** compara Minimax y alfa-beta (nodos y tiempo) y verifica ambos contra la solución matemática de Nim (nim-sum o XOR de los montones). Salida esperada (los milisegundos varían según el equipo):

```
Minimax    en (2, 3, 4): quitar 3 del monton 3, valor 1, 20652 nodos, ... ms (XOR = 5)
Alfa-beta  en (2, 3, 4): quitar 3 del monton 3, valor 1, 6018 nodos, ... ms (XOR = 5)

Minimax    profundidad 2: quitar 1 del monton 1, valor 0, 192 nodos
Alfa-beta  profundidad 2: quitar 1 del monton 1, valor 0, 44 nodos
Minimax    profundidad 4: quitar 1 del monton 1, valor 0, 12766 nodos
Alfa-beta  profundidad 4: quitar 1 del monton 1, valor 0, 552 nodos

Minimax: correcto en 248 posiciones (3 montones de 0 a 4 fichas, ambos turnos)
Alfa-beta: correcto en 248 posiciones (3 montones de 0 a 4 fichas, ambos turnos)
```