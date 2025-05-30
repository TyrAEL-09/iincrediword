import random
import os
from typing import List, Tuple, Set, Optional, Dict
from collections import Counter # Added, was implicitly used via BoggleGame's Counter import for letters

# Word Loading and Preparation
def cargar_palabras(filepath: str) -> List[str]:
    """Carga palabras desde un archivo."""
    try:
        with open(filepath, "r", encoding="utf-8") as archivo:
            all_words = [linea.strip().upper() for linea in archivo if linea.strip()]
        return all_words
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {filepath}")
        return []

def seleccionar_palabras_objetivo(
    all_words: List[str], 
    distribution: Dict[int, int], 
    num_objetivo: int,
    max_intentos: int = 20
) -> List[str]:
    """Selecciona un conjunto de palabras objetivo basado en la distribución de longitud."""
    words_by_length: Dict[int, List[str]] = {}
    for word in all_words:
        length = len(word)
        if length not in words_by_length:
            words_by_length[length] = []
        words_by_length[length].append(word)

    for intento in range(max_intentos):
        selected_words = []
        
        for longitud, cantidad in distribution.items():
            available = words_by_length.get(longitud, [])
            if len(available) >= cantidad:
                selected_words.extend(random.sample(available, cantidad))
            else:
                selected_words.extend(available)
        
        if len(selected_words) == num_objetivo:
            # _imprimir_distribucion_palabras(selected_words) # Optional: for debugging
            return selected_words
        
        if len(selected_words) < num_objetivo:
            longitudes_disponibles = sorted([l for l in words_by_length.keys() if l >= 4 and l <= 10])
            for longitud in longitudes_disponibles:
                if len(selected_words) >= num_objetivo:
                    break
                available = [w for w in words_by_length.get(longitud, []) if w not in selected_words]
                needed = num_objetivo - len(selected_words)
                if available:
                    to_add = min(needed, len(available))
                    selected_words.extend(random.sample(available, to_add))
        
        if len(selected_words) > num_objetivo:
            selected_words = random.sample(selected_words, num_objetivo)
        
        if len(selected_words) == num_objetivo:
            # _imprimir_distribucion_palabras(selected_words) # Optional: for debugging
            return selected_words
            
    print(f"Advertencia: Solo se pudieron seleccionar {len(selected_words)}/{num_objetivo} palabras tras {max_intentos} intentos.")
    return selected_words[:num_objetivo] if selected_words else []

# def _imprimir_distribucion_palabras(palabras: List[str]): # Helper, can be kept if debugging is needed
#     distribucion = {}
#     for palabra in palabras:
#         longitud = len(palabra)
#         if longitud not in distribucion:
#             distribucion[longitud] = []
#         distribucion[longitud].append(palabra)
#     for longitud in sorted(distribucion.keys(), reverse=True):
#         print(f"  {longitud} letras: {distribucion[longitud]}")

def clasificar_palabras_por_longitud(palabras: List[str]) -> Dict[int, List[str]]:
    """Clasifica una lista de palabras por su longitud."""
    palabras_por_longitud: Dict[int, List[str]] = {}
    for palabra in palabras:
        longitud = len(palabra)
        if longitud not in palabras_por_longitud:
            palabras_por_longitud[longitud] = []
        palabras_por_longitud[longitud].append(palabra)
    return palabras_por_longitud

# Board Generation
def crear_tablero_vacio(rows: int, cols: int) -> List[List[str]]:
    """Crea un tablero vacío (lista de listas)."""
    return [[' ' for _ in range(cols)] for _ in range(rows)]

def celdas_adyacentes(fila: int, col: int, filas: int, columnas: int) -> List[Tuple[int, int]]:
    """Obtiene las celdas adyacentes a una posición (solo arriba, abajo, izquierda, derecha)."""
    adyacentes = []
    direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Arriba, Abajo, Izquierda, Derecha
    for df, dc in direcciones:
        nf, nc = fila + df, col + dc
        if 0 <= nf < filas and 0 <= nc < columnas:
            adyacentes.append((nf, nc))
    return adyacentes

def encontrar_camino_palabra(
    tablero: List[List[str]], 
    palabra: str, 
    fila: int, 
    col: int, 
    visitado: Set[Tuple[int, int]]
) -> Optional[List[Tuple[int, int]]]:
    """Encuentra un camino válido para insertar una palabra."""
    if tablero[fila][col] != ' ' and tablero[fila][col] != palabra[0]:
        return None
    if len(palabra) == 1:
        return [(fila, col)]
    
    visitado.add((fila, col))
    filas, columnas = len(tablero), len(tablero[0])
    
    adyacentes_celdas = celdas_adyacentes(fila, col, filas, columnas)
    random.shuffle(adyacentes_celdas)
    
    for i, j in adyacentes_celdas:
        if (i, j) not in visitado:
            camino = encontrar_camino_palabra(tablero, palabra[1:], i, j, visitado.copy())
            if camino:
                return [(fila, col)] + camino
    return None

def calcular_complejidad_camino(camino: List[Tuple[int, int]]) -> int:
    """Calcula qué tan complejo/curvo es un camino."""
    if len(camino) < 3:
        return 0
    cambios_direccion = 0
    for i in range(1, len(camino) - 1):
        dir1 = (camino[i][0] - camino[i-1][0], camino[i][1] - camino[i-1][1])
        dir2 = (camino[i+1][0] - camino[i][0], camino[i+1][1] - camino[i][1])
        if dir1 != dir2:
            cambios_direccion += 1
    return cambios_direccion

def insertar_palabra_en_tablero(
    tablero: List[List[str]], 
    palabra: str, 
    max_intentos_posicion: int = 500, # Renamed from max_intentos for clarity
    min_caminos_evaluar: int = 20
) -> bool:
    """Intenta insertar una palabra en el tablero."""
    filas, columnas = len(tablero), len(tablero[0])
    palabra_upper = palabra.upper() # Ensure word is uppercase
    
    mejores_caminos: List[Tuple[List[Tuple[int,int]], int]] = []
    
    for _ in range(max_intentos_posicion):
        inicio_fila = random.randint(0, filas - 1)
        inicio_columna = random.randint(0, columnas - 1)
        camino = encontrar_camino_palabra(tablero, palabra_upper, inicio_fila, inicio_columna, set())
        
        if camino:
            complejidad = calcular_complejidad_camino(camino)
            mejores_caminos.append((camino, complejidad))
            if len(mejores_caminos) >= min_caminos_evaluar:
                break
    
    if mejores_caminos:
        mejores_caminos.sort(key=lambda x: x[1], reverse=True)
        mejor_camino_coords = mejores_caminos[0][0]
        for (i, j), letra in zip(mejor_camino_coords, palabra_upper):
            tablero[i][j] = letra
        return True
    return False

def rellenar_celdas_vacias(tablero: List[List[str]], palabras_ocultas: List[str]):
    """Rellena las celdas vacías del tablero con letras aleatorias."""
    letras_palabras = set()
    for palabra in palabras_ocultas:
        letras_palabras.update(palabra.upper())
    
    letras_comunes = 'AEIOURSTLNMCDPBFGHVJKQWXYZ' # Ensure uppercase
    letras_confusas = list(letras_palabras) * 3 + list(letras_comunes)
    random.shuffle(letras_confusas) # Shuffle for more randomness
    
    for i in range(len(tablero)):
        for j in range(len(tablero[0])):
            if tablero[i][j] == ' ':
                tablero[i][j] = random.choice(letras_confusas)

def generar_sopa_letras(
    palabras_objetivo_originales: List[str], 
    grid_size: Tuple[int, int],
    num_palabras_deseadas: int # Added parameter
) -> Tuple[Optional[List[List[str]]], List[str]]:
    """
    Crea la sopa de letras.
    Returns el tablero y la lista de palabras que SÍ fueron insertadas.
    """
    filas, columnas = grid_size
    max_intentos_tablero = 10
    palabras_insertadas_final = []
    tablero_final = None

    for intento_tablero in range(max_intentos_tablero):
        tablero_actual = crear_tablero_vacio(filas, columnas)
        palabras_insertadas_intento = []
        
        # Ordenar palabras por longitud (más largas primero) para mejorar la inserción
        palabras_a_insertar = sorted(palabras_objetivo_originales, key=len, reverse=True)
        
        for palabra in palabras_a_insertar:
            if insertar_palabra_en_tablero(tablero_actual, palabra):
                palabras_insertadas_intento.append(palabra)
            else:
                # print(f"Intento Tablero {intento_tablero + 1}: No se pudo insertar '{palabra}'") # Debug
                pass # No es necesario un break, intentar insertar las demás
        
        # Si este intento es mejor (más palabras insertadas) o igual pero con potencial, guardarlo
        if len(palabras_insertadas_intento) > len(palabras_insertadas_final):
            palabras_insertadas_final = list(palabras_insertadas_intento) # list() for a new copy
            tablero_final = [row[:] for row in tablero_actual] # Deep copy

        # Si se insertaron todas las deseadas, es un éxito
        if len(palabras_insertadas_final) == num_palabras_deseadas:
            # print(f"¡Tablero creado exitosamente con {len(palabras_insertadas_final)} palabras en intento {intento_tablero+1}!") # Debug
            break 
            
    if tablero_final and palabras_insertadas_final:
        rellenar_celdas_vacias(tablero_final, palabras_insertadas_final)
        print(f"Generación finalizó. Se insertaron {len(palabras_insertadas_final)}/{num_palabras_deseadas} palabras.")
        return tablero_final, palabras_insertadas_final
    
    print("Advertencia: No se pudo crear un tablero con suficientes palabras después de varios intentos.")
    return None, []


# Game State / Rules
def calcular_puntuacion_palabra(palabra: str, tiempo_transcurrido: int) -> int:
    """Calcula la puntuación para una palabra encontrada."""
    base_score = len(palabra) * 100
    time_bonus = max(1000 - (tiempo_transcurrido * 5), 100) # Mínimo 100 puntos de bonus
    return base_score + time_bonus

def verificar_palabra(palabra_ingresada: str, palabras_objetivo: List[str], palabras_encontradas: Set[str]) -> str:
    """Verifica el estado de una palabra ingresada."""
    palabra_upper = palabra_ingresada.strip().upper()
    if not palabra_upper:
        return "VACIA"
    if palabra_upper in palabras_encontradas:
        return "YA_ENCONTRADA"
    if palabra_upper in palabras_objetivo: # palabras_objetivo son las que SÍ están en el tablero
        return "VALIDA"
    return "INVALIDA"

```
