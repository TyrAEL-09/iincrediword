import random
import pygame
import tkinter as tk
from datetime import datetime
from typing import List, Tuple, Set, Optional

# Inicializar pygame mixer
pygame.mixer.init()

class BoggleGame:
    """Juego estilo Boggle con interfaz gráfica mejorada"""
    
    # Constantes de configuración
    GRID_SIZE = (6, 7)  # filas, columnas (aumentado para 7 palabras)
    COLORS = {
        'bg': "#1a1a1a",
        'fg': "#ffffff", 
        'grid': "#333333",
        'button_bg': "#464646",
        'button_fg': "#ffffff"
    }
    
    # Configuración de palabras objetivo
    PALABRAS_OBJETIVO = 7
    DISTRIBUCION_PALABRAS = {
        9: 1,  # 1 palabra de 9 letras
        8: 1,  # 1 palabra de 8 letras
        7: 1,  # 1 palabra de 7 letras
        6: 2,  # 2 palabras de 6 letras
        5: 2   # 2 palabras de 5 letras
    }
    
    def __init__(self, archivo_palabras: str):
        self.archivo_palabras = archivo_palabras
        self.palabras: List[str] = []
        self.palabras_por_longitud: dict = {}
        self.found_words: Set[str] = set()
        self.hint_labels: dict = {}
        self.timer_running = False
        self.time_elapsed = 0
        self.paused_time = 0
        self.score = 0
        self.game_active = False
        
        self._setup_ui()
    
    def reproducir_sonido(self, sonido):
        """Reproduce un sonido si está disponible"""
        if sonido:
            sonido.play()

    def iniciar_musica(self):
        """Inicia la música de fondo"""
        if self.musica_fondo:
            try:
                pygame.mixer.music.load(self.musica_fondo)
                pygame.mixer.music.play(-1)  # -1 para loop infinito
                print("Música de fondo iniciada")
            except pygame.error as e:
                print(f"Error reproduciendo música: {e}")

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self.root = tk.Tk()
        self.root.title("Juego estilo Boggle")
        self.root.configure(bg=self.COLORS['bg'])
        
        # Cargando sonidos a la clase
        try:
            self.sonido_incorrecto = pygame.mixer.Sound("SONIDOS/roblox_muerte.mp3")
            self.sonido_correcto = pygame.mixer.Sound("SONIDOS/correcto2.mp3")
            self.musica_fondo = "SONIDOS/lofi_sample.mp3"

            print("Sonidos cargados correctamente")
        except pygame.error as e:
            print(f"Error cargando sonidos: {e}")
            # Crear sonidos vacíos si hay error
            self.sonido_click = None
            self.musica_fondo = None
        
        # Configurar grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self._create_frames()
        self._create_widgets()
        self.iniciar_musica()

    def _create_frames(self):
        """Crea los marcos principales"""
        self.frame_sopa = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.frame_sopa.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        self.frame_input = tk.Frame(self.root, bg=self.COLORS['bg'])
        
        self.frame_lista = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.frame_lista.grid(row=0, column=1, rowspan=2, sticky='ns', padx=20, pady=20)
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Botón de iniciar
        self.boton_iniciar = tk.Button(
            self.root, text="Iniciar Juego", command=self.iniciar_juego,
            bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'], 
            font=("Arial", 12)
        )
        self.boton_iniciar.grid(row=2, column=0, columnspan=2, pady=10)
        
        # Widgets del área de input
        self._create_input_widgets()
    
    def _create_input_widgets(self):
        """Crea los widgets del área de entrada"""
        self.label_status = tk.Label(
            self.frame_input, text="Palabras: 0/7 | Puntuación: 0",
            font=("Arial", 12), bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        self.label_status.grid(row=0, column=0, columnspan=2)
        
        self.label_timer = tk.Label(
            self.frame_input, text="Tiempo: 0s", 
            font=("Arial", 12), bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        self.label_timer.grid(row=0, column=2, padx=5)
        
        self.entry = tk.Entry(
            self.frame_input, font=("Arial", 12), 
            bg=self.COLORS['grid'], fg=self.COLORS['fg'], 
            insertbackground=self.COLORS['fg']
        )
        self.entry.grid(row=1, column=0, padx=5)
        self.entry.bind('<Return>', lambda e: self.check_word())
        
        self.button_submit = tk.Button(
            self.frame_input, text="Enviar", command=self.check_word,
            font=("Arial", 12), bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg']
        )
        self.button_submit.grid(row=1, column=1, padx=5)
        
        self.button_pause = tk.Button(
            self.frame_input, text="Pausar", command=self.toggle_pause,
            font=("Arial", 12), bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg']
        )
        
        self.label_message = tk.Label(
            self.frame_input, text="", font=("Arial", 12), 
            bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        self.label_message.grid(row=2, column=0, columnspan=3)
        
        self.frame_input.grid_columnconfigure(0, weight=1)

        # Botón para pausar/reiniciar música de fondo
        self.button_music = tk.Button(
            self.frame_input, text="Pausar Música", command=self.toggle_music,
            font=("Arial", 12), bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg']
        )
        self.button_music.grid(row=3, column=1, columnspan=2, pady=5)


    # Lógica del tablero
    def _crear_tablero(self, filas: int, columnas: int) -> List[List[str]]:
        """Crea un tablero vacío"""
        return [[' ' for _ in range(columnas)] for _ in range(filas)]
    
    def _celdas_adyacentes(self, fila: int, col: int, filas: int, columnas: int) -> List[Tuple[int, int]]:
        """Obtiene las celdas adyacentes a una posición (solo arriba, abajo, izquierda, derecha)"""
        adyacentes = []
        
        # Solo las 4 direcciones principales (sin diagonales)
        direcciones = [
            (-1, 0),  # Arriba
            (1, 0),   # Abajo
            (0, -1),  # Izquierda
            (0, 1)    # Derecha
        ]
        
        for df, dc in direcciones:
            nf, nc = fila + df, col + dc
            if 0 <= nf < filas and 0 <= nc < columnas:
                adyacentes.append((nf, nc))
        
        return adyacentes
    
    def _encontrar_camino_palabra(self, tablero: List[List[str]], palabra: str, fila: int, col: int, visitado: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """Encuentra un camino válido para insertar una palabra, priorizando caminos curvos"""
        if tablero[fila][col] != ' ' and tablero[fila][col] != palabra[0]:
            return None
        if len(palabra) == 1:
            return [(fila, col)]
        
        visitado.add((fila, col))
        filas, columnas = len(tablero), len(tablero[0])
        
        # Obtener adyacentes y mezclarlos para crear caminos más aleatorios
        adyacentes = self._celdas_adyacentes(fila, col, filas, columnas)
        random.shuffle(adyacentes)  # Esto hace que las palabras tomen rutas más impredecibles
        
        for i, j in adyacentes:
            if (i, j) not in visitado:
                camino = self._encontrar_camino_palabra(tablero, palabra[1:], i, j, visitado.copy())
                if camino:
                    return [(fila, col)] + camino
        return None
    
    def _insertar_palabra(self, tablero: List[List[str]], palabra: str, max_intentos: int = 500) -> bool:
        """Intenta insertar una palabra en el tablero con más intentos para encontrar mejores ubicaciones"""
        filas, columnas = len(tablero), len(tablero[0])
        palabra = palabra.upper()
        
        mejores_caminos = []
        
        for _ in range(max_intentos):
            inicio_fila = random.randint(0, filas - 1)
            inicio_columna = random.randint(0, columnas - 1)
            camino = self._encontrar_camino_palabra(tablero, palabra, inicio_fila, inicio_columna, set())
            
            if camino:
                # Calcular "complejidad" del camino (más cambios de dirección = más escondido)
                complejidad = self._calcular_complejidad_camino(camino)
                mejores_caminos.append((camino, complejidad))
                
                # Si tenemos varios caminos, elegir uno de los más complejos
                if len(mejores_caminos) >= 20:  # Evaluar varios caminos antes de elegir
                    break
        
        if mejores_caminos:
            # Ordenar por complejidad y elegir uno de los más complejos
            mejores_caminos.sort(key=lambda x: x[1], reverse=True)
            mejor_camino = mejores_caminos[0][0]
            
            for (i, j), letra in zip(mejor_camino, palabra):
                tablero[i][j] = letra
            return True
        
        return False
    
    def _calcular_complejidad_camino(self, camino: List[Tuple[int, int]]) -> int:
        """Calcula qué tan complejo/curvo es un camino (más cambios de dirección = más complejo)"""
        if len(camino) < 3:
            return 0
        
        cambios_direccion = 0
        for i in range(1, len(camino) - 1):
            # Direcciones entre puntos consecutivos
            dir1 = (camino[i][0] - camino[i-1][0], camino[i][1] - camino[i-1][1])
            dir2 = (camino[i+1][0] - camino[i][0], camino[i+1][1] - camino[i][1])
            
            # Si cambia de dirección, suma complejidad
            if dir1 != dir2:
                cambios_direccion += 1
        
        return cambios_direccion

    def _rellenar_tablero(self, tablero: List[List[str]]):
        """Rellena las celdas vacías con letras que confundan más"""
        # Usar más frecuentemente las letras que aparecen en las palabras ocultas
        letras_palabras = set()
        for palabra in self.palabras:
            letras_palabras.update(palabra)
        
        # Mezclar letras de las palabras con letras comunes para confundir
        letras_comunes = 'AEIOURSTLNMCDPBFGHVJKQWXYZ'
        letras_confusas = list(letras_palabras) * 3 + list(letras_comunes)
        
        for i in range(len(tablero)):
            for j in range(len(tablero[0])):
                if tablero[i][j] == ' ':
                    tablero[i][j] = random.choice(letras_confusas)

    
    def _crear_sopa_letras(self, palabras: List[str]) -> List[List[str]]:
        """Crea la sopa de letras con las palabras dadas"""
        filas, columnas = self.GRID_SIZE
        max_intentos_tablero = 10
        
        for intento in range(max_intentos_tablero):
            tablero = self._crear_tablero(filas, columnas)
            palabras_insertadas = []
            
            # Ordenar palabras por longitud (más largas primero)
            palabras_ordenadas = sorted(palabras, key=len, reverse=True)
            
            for palabra in palabras_ordenadas:
                if self._insertar_palabra(tablero, palabra):
                    palabras_insertadas.append(palabra)
                else:
                    print(f"Intento {intento + 1}: No se pudo insertar '{palabra}'")
                    break
            
            if len(palabras_insertadas) == self.PALABRAS_OBJETIVO:
                self._rellenar_tablero(tablero)
                self.palabras = palabras_insertadas
                self._clasificar_palabras_por_longitud()
                print(f"¡Tablero creado exitosamente con {len(palabras_insertadas)} palabras!")
                return tablero
            
            print(f"Intento {intento + 1}: Solo se insertaron {len(palabras_insertadas)}/{self.PALABRAS_OBJETIVO} palabras")
        
        print("Advertencia: No se pudo crear un tablero con todas las palabras")
        if palabras_insertadas:
            self._rellenar_tablero(tablero)
            self.palabras = palabras_insertadas
            self._clasificar_palabras_por_longitud()
        return tablero
    
    def _clasificar_palabras_por_longitud(self):
        """Clasifica las palabras por su longitud"""
        self.palabras_por_longitud = {}
        for palabra in self.palabras:
            longitud = len(palabra)
            if longitud not in self.palabras_por_longitud:
                self.palabras_por_longitud[longitud] = []
            self.palabras_por_longitud[longitud].append(palabra)
    
    # Manejo de palabras
    def _cargar_palabras(self) -> List[str]:
        """Carga y selecciona exactamente 7 palabras del archivo"""
        try:
            with open(self.archivo_palabras, "r", encoding="utf-8") as archivo:
                all_words = [linea.strip().upper() for linea in archivo if linea.strip()]
            
            # Separar palabras por longitud
            words_by_length = {}
            for word in all_words:
                length = len(word)
                if length not in words_by_length:
                    words_by_length[length] = []
                words_by_length[length].append(word)
            
            return self._seleccionar_7_palabras(words_by_length)
            
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.archivo_palabras}")
            return []
    
    def _seleccionar_7_palabras(self, words_by_length: dict, max_intentos: int = 20) -> List[str]:
        """Selecciona exactamente 7 palabras según la distribución configurada"""
        
        for intento in range(max_intentos):
            selected_words = []
            
            # Intentar seleccionar según la distribución ideal
            for longitud, cantidad in self.DISTRIBUCION_PALABRAS.items():
                available = words_by_length.get(longitud, [])
                if len(available) >= cantidad:
                    selected_words.extend(random.sample(available, cantidad))
                else:
                    # Si no hay suficientes de esta longitud, tomar las que haya
                    selected_words.extend(available)
            
            # Si tenemos exactamente 7, perfecto
            if len(selected_words) == self.PALABRAS_OBJETIVO:
                print(f"Palabras seleccionadas (intento {intento + 1}):")
                self._imprimir_distribucion_palabras(selected_words)
                return selected_words
            
            # Si tenemos menos de 7, completar con palabras de otras longitudes
            if len(selected_words) < self.PALABRAS_OBJETIVO:
                longitudes_disponibles = sorted([l for l in words_by_length.keys() if l >= 4 and l <= 10])
                
                for longitud in longitudes_disponibles:
                    if len(selected_words) >= self.PALABRAS_OBJETIVO:
                        break
                    
                    available = [w for w in words_by_length[longitud] if w not in selected_words]
                    needed = self.PALABRAS_OBJETIVO - len(selected_words)
                    
                    if available:
                        to_add = min(needed, len(available))
                        selected_words.extend(random.sample(available, to_add))
            
            # Si tenemos más de 7, recortar aleatoriamente
            if len(selected_words) > self.PALABRAS_OBJETIVO:
                selected_words = random.sample(selected_words, self.PALABRAS_OBJETIVO)
            
            if len(selected_words) == self.PALABRAS_OBJETIVO:
                print(f"Palabras seleccionadas (intento {intento + 1} - ajustado):")
                self._imprimir_distribucion_palabras(selected_words)
                return selected_words
            
            print(f"Intento {intento + 1}: Solo se pudieron seleccionar {len(selected_words)} palabras")
        
        print("Advertencia: No se pudieron seleccionar exactamente 7 palabras")
        return selected_words[:self.PALABRAS_OBJETIVO] if selected_words else []
    
    def _imprimir_distribucion_palabras(self, palabras: List[str]):
        """Imprime la distribución de palabras por longitud"""
        distribucion = {}
        for palabra in palabras:
            longitud = len(palabra)
            if longitud not in distribucion:
                distribucion[longitud] = []
            distribucion[longitud].append(palabra)
        
        for longitud in sorted(distribucion.keys(), reverse=True):
            print(f"  {longitud} letras: {distribucion[longitud]}")
    
    # Interfaz gráfica
    def _mostrar_tablero(self, tablero: List[List[str]]):
        """Muestra el tablero en la interfaz"""
        for widget in self.frame_sopa.winfo_children():
            widget.destroy()
            
        for i, fila in enumerate(tablero):
            for j, letra in enumerate(fila):
                label = tk.Label(
                    self.frame_sopa, text=letra, font=("Arial", 20), 
                    width=3, height=2, borderwidth=1, relief="solid",
                    bg=self.COLORS['grid'], fg=self.COLORS['fg']
                )
                label.grid(row=i, column=j)
    
    def _mostrar_lista_palabras(self):
        """Muestra la lista de palabras clasificadas por longitud"""
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        
        # Título
        titulo = tk.Label(
            self.frame_lista, text="Palabras a encontrar:", 
            font=("Arial", 14, "bold"),
            bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        titulo.pack(pady=(0, 10))
        
        self.hint_labels.clear()
        
        # Mostrar palabras agrupadas por longitud
        for longitud in sorted(self.palabras_por_longitud.keys(), reverse=True):
            # Subtítulo por longitud
            subtitulo = tk.Label(
                self.frame_lista, text=f"{longitud} letras:", 
                font=("Arial", 12, "bold"),
                bg=self.COLORS['bg'], fg="#cccccc"
            )
            subtitulo.pack(pady=(10, 5))
            
            # Palabras de esta longitud
            for palabra in sorted(self.palabras_por_longitud[longitud]):
                hint = palabra[0] + ' _' * (len(palabra) - 1)
                label = tk.Label(
                    self.frame_lista, text=hint, font=("Arial", 16),
                    bg=self.COLORS['bg'], fg=self.COLORS['fg']
                )
                label.pack(pady=2)
                self.hint_labels[palabra] = label
    
    # Lógica del juego
    def iniciar_juego(self):
        """Inicia una nueva partida"""
        print("Iniciando nuevo juego...")
        palabras_candidatas = self._cargar_palabras()
        
        if len(palabras_candidatas) < self.PALABRAS_OBJETIVO:
            print(f"Error: Solo se encontraron {len(palabras_candidatas)} palabras, se necesitan {self.PALABRAS_OBJETIVO}")
            return
        
        # Crear tablero (esto actualiza self.palabras con las que se insertaron)
        tablero = self._crear_sopa_letras(palabras_candidatas)
        
        if len(self.palabras) == 0:
            print("Error: No se pudieron insertar palabras en el tablero")
            return
        
        # Resetear estado del juego
        self._reset_game_state()
        
        # Actualizar interfaz
        self._mostrar_tablero(tablero)
        self._mostrar_lista_palabras()
        self._show_game_interface()
        
        print(f"Juego iniciado con {len(self.palabras)} palabras")
    
    def _reset_game_state(self):
        """Resetea el estado del juego"""
        self.found_words.clear()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = True
        self.game_active = True
        
        self._update_status()
        self.label_timer.config(text="Tiempo: 0s")
        self.label_message.config(text="")
        
        self.root.after(1000, self._update_timer)
    
    def _show_game_interface(self):
        """Muestra la interfaz del juego activo"""
        self.boton_iniciar.grid_forget()
        self.frame_input.grid(row=1, column=0, sticky='ew', padx=20, pady=10)
        self.button_pause.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.entry.config(state='normal')
        self.button_submit.config(state='normal')
    
    def check_word(self):
        """Verifica si una palabra ingresada es válida"""
        if not self.game_active or not self.timer_running:
            return
        
        word = self.entry.get().strip().upper()
        self.entry.delete(0, tk.END)
        
        if not word:
            return
        
        if word in self.palabras and word not in self.found_words:
            self._word_found(word)
        elif word in self.found_words:
            self._show_message("Palabra ya encontrada")
        else:
            self.reproducir_sonido(self.sonido_incorrecto)
            self._show_message("Palabra no está en la lista")
    
    def _word_found(self, word: str):
        """Procesa una palabra encontrada"""
        self.found_words.add(word)
        self.hint_labels[word].config(text=word, fg="#90EE90")  # Verde claro para palabras encontradas
        
        # Calcular puntuación basada en longitud y tiempo
        base_score = len(word) * 100
        time_bonus = max(1000 - (self.time_elapsed * 5), 100)
        word_score = base_score + time_bonus
        self.score += word_score
        
        self._update_status()
        self.sonido_correcto.play()  # Reproducir sonido de palabra correcta
        self._show_message(f"¡Palabra encontrada! +{word_score} puntos")
        
        if len(self.found_words) == len(self.palabras):
            self._end_game()
    
    def _update_status(self):
        """Actualiza el estado mostrado"""
        self.label_status.config(
            text=f"Palabras: {len(self.found_words)}/{len(self.palabras)} | Puntuación: {self.score}"
        )
    
    def _show_message(self, message: str, duration: int = 2000):
        """Muestra un mensaje temporal"""
        self.label_message.config(text=message)
        self.root.after(duration, lambda: self.label_message.config(text=""))
    
    # Control del temporizador
    def _update_timer(self):
        """Actualiza el temporizador"""
        if self.timer_running:
            self.time_elapsed += 1
            self.label_timer.config(text=f"Tiempo: {self.time_elapsed}s")
            self.root.after(1000, self._update_timer)
    
    def toggle_pause(self):
        """Alterna entre pausar y reanudar el juego"""
        if self.timer_running:
            self._pause_game()
        else:
            self._resume_game()
    
    def toggle_music(self):
        """Pausa o reanuda la música de fondo"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.button_music.config(text="Reanudar Música")
        else:
            pygame.mixer.music.unpause()
            self.button_music.config(text="Pausar Música")
    
    def _pause_game(self):
        """Pausa el juego"""
        self.timer_running = False
        self.paused_time = self.time_elapsed
        self.label_timer.config(text=f"Pausado: {self.paused_time}s")
        self.button_pause.config(text="Reanudar")
        self.entry.config(state='disabled')
        self.button_submit.config(state='disabled')
    
    def _resume_game(self):
        """Reanuda el juego"""
        self.timer_running = True
        self.time_elapsed = self.paused_time
        self.label_timer.config(text=f"Tiempo: {self.time_elapsed}s")
        self.button_pause.config(text="Pausar")
        self.entry.config(state='normal')
        self.button_submit.config(state='normal')
        self.root.after(1000, self._update_timer)
    
    def _end_game(self):
        """Termina el juego"""
        self.game_active = False
        self.timer_running = False
        self.entry.config(state='disabled')
        self.button_submit.config(state='disabled')
        self.label_message.config(text=f"¡Felicitaciones! Todas las palabras encontradas. Puntuación final: {self.score}")
    
    def run(self):
        """Ejecuta el juego"""
        self.root.mainloop()


# Punto de entrada
if __name__ == "__main__":
    # Cambia esta ruta por la ruta de tu archivo de palabras
    archivo_palabras = "palabras.txt"
    
    juego = BoggleGame(archivo_palabras)
    juego.run()
