#guardar resultados archivo excel
import csv
#medir ejecución
import time
#medir memoria
import tracemalloc
#donde se guardan los archivos
from pathlib import Path
#calcular mediana
from statistics import median

#importar algoritmos y minimax
from astar import astar, h_fichas, h_montones
from busqueda_no_informada import bfs, dfs, ucs
from busqueda_informada_minimax import alfabeta, describir, minimax
#calcular costo y validar rutas
from nim import calcular_costo_total, obtener_sucesores

#estados a probar con cada algoritmos (bus infor y no infor)
CASOS_BUSQUEDA = [
    (3,5,7),
    (1,1,1),
    (2,3,1),
    (2,2,2),
    (4,4,4),
    (1,4,7),
    (0,0,12),
]

#Registro de algoritmos a ejecutar
ALGORITMOS_BUSQUEDA =[
    ("BFS", bfs),
    ("DFS", dfs),
    ("UCS", ucs),
    ("A* h_fichas", None), #heuristica principal
    ("A* h_montones", None), #heuristica secundaria

]

CASOS_MINIMAX = [
    ((2,3,4), None), #No hay limite y hay condiciones pequeñas
    ((3,4,5), None),
    ((3,5,7), 6), #profundidad 6
    ((3,5,7), 4),
]

REPETICIONES_TIEMPO = 20 #Cantidad de mediciones de tiempo en cada condición
REPETICIONES_MEMORIA = 10 #Cantidad de mediciones de memoria
CARPETA_RESULTADOS = Path(__file__).parent / "resultados_experimentos"

#Ejecutar A* con heuristicas
def ejecutar_astar_fichas(estado):
    return astar(estado, h_fichas)

def ejecutar_astar_montones(estado):
    return astar(estado, h_montones)


#ejecutar variante de busqueda
def resolver_busqueda(nombre, algoritmo,estado):
    #con heuristicas
    if nombre == "A* h_fichas":
        return ejecutar_astar_fichas(estado)
    if nombre == "A* h_montones":
        return ejecutar_astar_montones(estado)
    #BFS, DFS, UCS con estado recibido
    return algoritmo(estado) 


#medir pico de memoria usada por una busqueda
def medir_memoria_busqueda (nombre, algoritmo, estado):
    picos_memoria = [] #lista con pico de memoria para cada repetición
    for repeticion in range (REPETICIONES_MEMORIA):
        #rastrear asignación de memoria
        tracemalloc.start()
        try:
            resolver_busqueda(nombre, algoritmo, estado)
            memoria_actual, memoria_pico = tracemalloc.get_traced_memory()
        #ejecutar si la busqueda es exitosa o si fracasa
        finally:
            tracemalloc.stop()
        picos_memoria.append(memoria_pico / 1024)
    return median(picos_memoria)

#ruta es valida
def validar_ruta(estado_inicial, estados, movimientos, nombre):
    if estados is None or movimientos is None:
        raise RuntimeError(nombre + "no se encontró solución para: " + str(estado_inicial))

    estado_objetivo = (0,) * len(estado_inicial)
    if estados[0] != estado_inicial:
        raise RuntimeError ("la ruta: " + nombre + "no empieza en estado inicial")
    if estados[-1] != estado_objetivo:
        raise RuntimeError("La ruta de: " + nombre + "no termina en el objetivo")
    if len(estados) != len(movimientos) + 1:
        raise RuntimeError("La ruta de: " + nombre + "tiene estados y movimientos inconsistentes")

    for indice in range (len(movimientos)):
        estado_actual = estados[indice]
        estado_siguiente = estados [indice + 1]
        movimiento_actual = movimientos[indice]
        sucesores_legales = obtener_sucesores(estado_actual)
        if (estado_siguiente, movimiento_actual) not in sucesores_legales:
            raise RuntimeError("La ruta de: "+ nombre + " tiene movimientos ilegales") 


#Medicion de tiempo, memoria, costo y expansiones de un algoritmo
def medir_busqueda(nombre, algoritmo, estado):
    #ejecutar una busqueda para guardar resultado esperado
    resultado_referencia = resolver_busqueda(nombre, algoritmo, estado)
    tiempos = []
    for repeticion in range(REPETICIONES_TIEMPO):
        inicio = time.perf_counter() #tiempo antes de iniciar busqueda
        resultado_actual = resolver_busqueda(nombre, algoritmo, estado) #ejecutar algoritmo
        fin = time.perf_counter() #tiempo luego de terminar busqueda
        tiempo_ms = (fin - inicio) * 1000
        tiempos.append(tiempo_ms)
        #comprobar que busqueda repetida de mismo resultado
        if resultado_actual != resultado_referencia:
            raise RuntimeError("El resultado de: " + nombre + "cambió entre repeticiones")
    estados, movimientos, expandidos = resultado_referencia
    validar_ruta(estado, estados, movimientos, nombre)
    costo = calcular_costo_total(movimientos)
    memoria_kib = medir_memoria_busqueda(nombre, algoritmo, estado)
    mediana_tiempo = median(tiempos)
    tiempo_minimo = min(tiempos)
    tiempo_maximo = max(tiempos)

        #Devolver datos en orden para las columnas
    return [str(estado), nombre, len(movimientos), costo, expandidos, round(mediana_tiempo,5), round(tiempo_minimo,5),
            round(tiempo_maximo,5), memoria_kib, REPETICIONES_TIEMPO, REPETICIONES_MEMORIA]



# Medir el pico de memoria de búsqueda de Minimax.
def medir_memoria_minimax(algoritmo, estado, profundidad):
    picos_memoria = []
    for repeticion in range(REPETICIONES_MEMORIA):
        tracemalloc.start()
        try:
            algoritmo(estado, True, profundidad)  # Ejecuta el algoritmo con MAX en turno y la profundidad indicada.
            memoria_actual, memoria_pico = tracemalloc.get_traced_memory()  # Obtiene el pico de memoria
        finally:  
            tracemalloc.stop()  
        picos_memoria.append(memoria_pico / 1024)
    return median(picos_memoria)



 # Mide una versión de Minimax bajo una condición determinada.
def medir_minimax(algoritmo, estado, profundidad): 
    resultado_referencia = algoritmo(estado, True, profundidad)  # Ejecuta la búsqueda con el mismo estado, turno y profundidad.
    tiempos = [] 
    for repeticion in range(REPETICIONES_TIEMPO):
        inicio = time.perf_counter()
        resultado_actual = algoritmo(estado, True, profundidad)  # Ejecuta Minimax sin poda o alfa-beta.
        fin = time.perf_counter()  
        tiempo_ms = (fin - inicio) * 1000 
        tiempos.append(tiempo_ms)  
        if resultado_actual != resultado_referencia:  
            raise RuntimeError("Minimax cambió el resultado entre repeticiones.")  # Detiene la medición si las ejecuciones no coinciden.
    movimiento, valor, nodos = resultado_referencia  # Separa la jugada, el valor de la posición y los nodos visitados.
    memoria_kib = medir_memoria_minimax(algoritmo, estado, profundidad)  # Mide la memoria
    mediana_tiempo = median(tiempos) 
    tiempo_minimo = min(tiempos)  
    tiempo_maximo = max(tiempos) 
    jugada = describir(movimiento)  # Convierte la jugada a una descripción que se pueda leer en el CSV

     # Devuelve las métricas en el orden definido para el CSV
    return [jugada, valor, nodos, round(mediana_tiempo,5), round(tiempo_minimo, 5), round(tiempo_maximo,5),
            memoria_kib, REPETICIONES_TIEMPO, REPETICIONES_MEMORIA]

def main():  # función principal 
    #carpeta de salida
    CARPETA_RESULTADOS.mkdir(exist_ok=True)
    filas_busqueda = []  # la lista que almacenará los resultados
    for estado in CASOS_BUSQUEDA:
        for nombre, algoritmo in ALGORITMOS_BUSQUEDA:  # Recorre cada algoritmo -> usa el mismo estado con todos.
            fila = medir_busqueda(nombre, algoritmo, estado)  # Ejecuta las repeticiones, calcula sus métricas.
            filas_busqueda.append(fila)
            print(estado, nombre, "movimientos:", fila[2], "costo:", fila[3], "expandidos:", fila[4], "mediana ms:", round(fila[5], 6), "memoria KiB:", round(fila[8], 2))
    archivo_busqueda = CARPETA_RESULTADOS / "metricas_busqueda.csv"  
    with archivo_busqueda.open("w", newline="", encoding="utf-8-sig") as archivo: 
        escritor = csv.writer(archivo)
        escritor.writerow(["estado", "algoritmo", "movimientos", "costo", "estados_expandidos", "tiempo_mediana_ms", "tiempo_minimo_ms",
                           "tiempo_maximo_ms", "memoria_pico_mediana_kib", "repeticiones_tiempo", "repeticiones_memoria"]) 
        escritor.writerows(filas_busqueda)  
    filas_minimax = [] 
    for estado, profundidad in CASOS_MINIMAX:  
        resultado_sin_poda = medir_minimax(minimax, estado, profundidad)  # Mide Minimax sin poda 
        resultado_con_poda = medir_minimax(alfabeta, estado, profundidad)  # Mide alfa-beta bajo la misma condición.
        nodos_sin_poda = resultado_sin_poda[2]  # nodos de la búsqueda sin poda.
        nodos_con_poda = resultado_con_poda[2]  # nodos de la búsqueda con poda.
        if resultado_sin_poda[1] != resultado_con_poda[1]:  
            raise RuntimeError("Minimax y alfa-beta dieron valores diferentes para " + str(estado)) 
        if nodos_sin_poda > 0:  
            reduccion = (nodos_sin_poda - nodos_con_poda) / nodos_sin_poda * 100  # Calcula qué porcentaje de nodos evitó alfa-beta.
        else:  # un conteo sin nodos.
            reduccion = 0 
        filas_minimax.append([str(estado), "Minimax sin poda", "completa" if profundidad is None else profundidad] + resultado_sin_poda + [""])  
        filas_minimax.append([str(estado), "Alfa-beta", "completa" if profundidad is None else profundidad] + resultado_con_poda + [round(reduccion,1)]) 
        print(estado, "profundidad:", "completa" if profundidad is None else profundidad, "nodos sin poda:", nodos_sin_poda, "nodos con poda:", nodos_con_poda, "reducción:", round(reduccion, 2), "%")  
    archivo_minimax = CARPETA_RESULTADOS / "metricas_minimax.csv" 
    with archivo_minimax.open("w", newline="", encoding="utf-8-sig") as archivo:  
        escritor = csv.writer(archivo) 
        escritor.writerow(["estado", "algoritmo", "profundidad", "mejor_jugada", "valor", "nodos_visitados",
                           "tiempo_mediana_ms", "tiempo_minimo_ms", "tiempo_maximo_ms", "memoria_pico_mediana_kib", "repeticiones_tiempo", "repeticiones_memoria", "reduccion_nodos_pct"])
        escritor.writerows(filas_minimax)  # todas las comparaciones de Minimax.
    print("Los archivos CSV quedaron guardados en:", CARPETA_RESULTADOS)  #  dónde se guardaron los resultados.

if __name__ == "__main__": 
    main()  