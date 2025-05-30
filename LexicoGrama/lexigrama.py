def iniciar_lexicograma(usuario):
    print(f"Iniciando Lexicograma para {usuario}")
    # Aquí puedes lanzar la ventana del juego...
import random
import pygame
import tkinter as tk
from tkinter import PhotoImage, Frame, Label, Button, Entry, SOLID, RAISED, DISABLED, NORMAL, END # Explicit imports for clarity
from datetime import datetime
from typing import List, Tuple, Set, Optional, Dict # Added Dict
from PIL import Image, ImageTk

# Inicializar pygame mixer
pygame.mixer.init()

class BoggleGame:
    """Clase principal del juego Lexicograma"""

    # --- Estilo y Fuentes ---
    MAIN_FONT_FAMILY = "Tahoma"
    GRID_LETTER_FONT_SIZE = 22
    UI_FONT_SIZE = 15
    LOGO_MAX_WIDTH = 500
    LOGO_MAX_HEIGHT = 300


    # Constantes de configuración
    GRID_SIZE = (5, 6)
    COLORS = {
        'bg': "#1a1a1a",
        'fg': "#FFFFFF",
        'grid': "#333333",
        'grid_fg': "#FFFFFF",
        'button_bg': "#464646",
        'button_fg': "#FFFFFF",
        'found_word_fg': "#F2FF00",
        'hint_fg': "#A0A0A0",
        'selected_cell_bg': "#FFA500", # RQ3: Color para celda seleccionada
        'hint_box_bg': "#2a2a2a", # RQ2: Color para cajas de pistas
        'hint_box_fg': "#FFFFFF", # RQ2: Color para texto en cajas de pistas
        'hint_box_border': "#444444" # RQ2: Color para borde de cajas de pistas
    }
    PALABRAS_OBJETIVO = 7
    DISTRIBUCION_PALABRAS = { 9: 1, 8: 1, 7: 1, 6: 2, 5: 2 }
    MAX_REEMPLAZOS_POR_SLOT = 100
    MAX_INTENTOS_GLOBALES_GENERACION = 10
    MAX_INTENTOS_TABLERO_INTERNO = 20

    def __init__(self, archivo_palabras: str, logo_path: str = "imagenes/logo.png"):
        self.archivo_palabras = archivo_palabras
        self.logo_path = logo_path
        self.logo_tk_image = None
        self.all_words_by_length: dict = {}
        self.palabras: List[str] = []
        self.palabras_por_longitud: dict = {}
        self.found_words: Set[str] = set()
        self.hint_labels: dict = {} # RQ2: Esto almacenará listas de Labels (cajas) por palabra
        self.timer_running = False
        self.time_elapsed = 0
        self.paused_time = 0
        self.score = 0
        self.game_active = False
        self._music_paused_by_game = False
        self._message_after_id = None # Para el control de mensajes temporales

        # RQ3: Variables de estado para la selección en la grilla
        self.current_selection_path: List[Tuple[int, int]] = []
        self.current_selected_word: str = ""
        self.grid_cell_widgets: List[List[Optional[tk.Button]]] = [] # Almacenará los botones de la grilla
        self.default_cell_bg_color = self.COLORS['grid'] # Color por defecto de las celdas
        self.selected_cell_bg_color = self.COLORS['selected_cell_bg'] # Color para celdas seleccionadas

        self._setup_ui()

    # RQ1: Método Auxiliar para Geometría de Ventana
    def _set_window_geometry(self, width: int, height: int):
        """Establece el tamaño y centra la ventana principal."""
        self.root.update_idletasks() 
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int(screen_width / 2 - width / 2)
        center_y = int(screen_height / 2 - height / 2)
        self.root.geometry(f'{width}x{height}+{center_x}+{center_y}')

    def _format_time(self, total_seconds: int) -> str:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def reproducir_sonido(self, sonido):
        if sonido:
            sonido.play()

    def iniciar_musica(self):
        if hasattr(self, 'musica_fondo') and self.musica_fondo:
            try:
                pygame.mixer.music.load(self.musica_fondo)
                pygame.mixer.music.play(-1)
                print("Música de fondo iniciada")
                if hasattr(self, 'button_music_game') and self.button_music_game.winfo_exists():
                    self.button_music_game.config(text="Música: ON")
                if hasattr(self, 'button_music_menu') and self.button_music_menu.winfo_exists():
                    self.button_music_menu.config(text="Música: ON")
            except pygame.error as e:
                print(f"Error reproduciendo música: {e}")
                if hasattr(self, 'button_music_game') and self.button_music_game.winfo_exists():
                    self.button_music_game.config(text="Música: ERR")
                if hasattr(self, 'button_music_menu') and self.button_music_menu.winfo_exists():
                    self.button_music_menu.config(text="Música: ERR")
        else:
            print("Atributo musica_fondo no definido o es None.")
            if hasattr(self, 'button_music_game') and self.button_music_game.winfo_exists():
                self.button_music_game.config(text="Música: N/A")
            if hasattr(self, 'button_music_menu') and self.button_music_menu.winfo_exists():
                self.button_music_menu.config(text="Música: N/A")


    def _setup_ui(self):
        self.root = tk.Tk()
        self.root.title("Lexigrama")
        self.root.configure(bg=self.COLORS['bg'])
        try:
            icon_image = PhotoImage(file="imagenes/icon.png")
            self.root.iconphoto(False, icon_image)
        except tk.TclError:
            print("Advertencia: No se pudo cargar 'icon.png'. Usando icono por defecto.")

        try:
            self.sonido_incorrecto = pygame.mixer.Sound("sonidos/roblox_muerte.mp3")
            self.sonido_correcto = pygame.mixer.Sound("sonidos/correcto2.mp3")
            self.musica_fondo = "sonidos/lofi_sample.mp3"
            print("Sonidos cargados correctamente")
        except pygame.error as e:
            print(f"Error cargando sonidos: {e}")
            self.sonido_incorrecto = None
            self.sonido_correcto = None
            self.musica_fondo = None
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self._create_frames()
        self._create_menu_widgets()
        self._create_game_widgets()
        
        self._show_menu_interface()
        self.iniciar_musica()

    def _create_frames(self):
        self.frame_menu = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.frame_sopa = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.frame_input = tk.Frame(self.root, bg=self.COLORS['bg'])
        self.frame_lista = tk.Frame(self.root, bg=self.COLORS['bg'])

    def _create_menu_widgets(self):
        font_ui_bold_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE, "bold")
        try:
            pil_image = Image.open(self.logo_path)
            img_width, img_height = pil_image.size
            ratio = min(self.LOGO_MAX_WIDTH / img_width, self.LOGO_MAX_HEIGHT / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            resized_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.logo_tk_image = ImageTk.PhotoImage(resized_image)
            self.label_logo = tk.Label(self.frame_menu, image=self.logo_tk_image, bg=self.COLORS['bg'])
            self.label_logo.pack(pady=(20, 10))
        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo de logo '{self.logo_path}'.")
            self.label_logo_fallback = tk.Label(self.frame_menu, text="LEXIGRAMA",
                                                font=(self.MAIN_FONT_FAMILY, 30, "bold"),
                                                bg=self.COLORS['bg'], fg=self.COLORS['fg'])
            self.label_logo_fallback.pack(pady=(20,10))
        except Exception as e:
            print(f"Error al cargar el logo '{self.logo_path}': {e}")
            self.label_logo_fallback = tk.Label(self.frame_menu, text="LEXIGRAMA",
                                                font=(self.MAIN_FONT_FAMILY, 30, "bold"),
                                                bg=self.COLORS['bg'], fg=self.COLORS['fg'])
            self.label_logo_fallback.pack(pady=(20,10))

        self.boton_iniciar_menu = tk.Button(
            self.frame_menu, text="Iniciar Juego", command=self.iniciar_juego,
            bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            font=font_ui_bold_tuple, relief=tk.RAISED, borderwidth=2, width=20, height=2
        )
        self.boton_iniciar_menu.pack(pady=10)

        initial_music_text = "Música: ON" if pygame.mixer.music.get_busy() else "Música: OFF"
        if not self.musica_fondo: initial_music_text = "Música: N/A"
        self.button_music_menu = tk.Button(
            self.frame_menu, text=initial_music_text, command=self.toggle_music,
            font=font_ui_bold_tuple, bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=15
        )
        self.button_music_menu.pack(pady=5)

        self.button_volver_menu = tk.Button(
            self.frame_menu, text="Volver", command=self._accion_volver_menu,
            font=font_ui_bold_tuple, bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2, width=15
        )
        self.button_volver_menu.pack(pady=(5, 20))
        self.button_volver_menu.config(state='disabled')


    def _create_game_widgets(self):
        font_ui_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE)
        font_ui_bold_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE, "bold")
        
        self.label_status = tk.Label(
            self.frame_input, text=f"Palabras: 0/{self.PALABRAS_OBJETIVO} | Puntuación: 0",
            font=font_ui_tuple, bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        self.label_status.grid(row=0, column=0, columnspan=2, pady=(0,5), sticky="w")

        self.label_timer = tk.Label(
            self.frame_input, text=f"Tiempo: {self._format_time(0)}",
            font=font_ui_tuple, bg=self.COLORS['bg'], fg=self.COLORS['fg']
        )
        self.label_timer.grid(row=0, column=2, padx=5, pady=(0,5), sticky="e")

        self.entry = tk.Entry(
            self.frame_input, font=font_ui_tuple,
            bg=self.COLORS['grid'], fg=self.COLORS['fg'],
            insertbackground=self.COLORS['fg'], relief=tk.SOLID, borderwidth=1
        )
        self.entry.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        self.entry.bind('<Return>', lambda e: self.check_word())

        self.button_submit = tk.Button(
            self.frame_input, text="Enviar", command=self.check_word,
            font=font_ui_bold_tuple, bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
        self.button_submit.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.button_pause_game = tk.Button(
            self.frame_input, text="Pausar", command=self.toggle_pause,
            font=font_ui_bold_tuple, bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )

        self.label_message = tk.Label(
            self.frame_input, text="", font=font_ui_tuple,
            bg=self.COLORS['bg'], fg=self.COLORS['fg'], wraplength=350
        )
        self.label_message.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")
        self.frame_input.grid_columnconfigure(0, weight=1)
        self.frame_input.grid_columnconfigure(1, weight=1)
        self.frame_input.grid_columnconfigure(2, weight=1)

        initial_music_text_game = "Música: ON" if pygame.mixer.music.get_busy() else "Música: OFF"
        if not self.musica_fondo: initial_music_text_game = "Música: N/A"
        self.button_music_game = tk.Button(
            self.frame_input, text=initial_music_text_game, command=self.toggle_music,
            font=font_ui_bold_tuple, bg=self.COLORS['button_bg'], fg=self.COLORS['button_fg'],
            relief=tk.RAISED, borderwidth=2
        )
    
    def _accion_volver_menu(self):
        print("Botón 'Volver' del menú presionado.")

    def _show_menu_interface(self):
        # RQ1: Ajustar tamaño y centrar ventana al mostrar el menú
        self._set_window_geometry(800, 600) 

        if self.frame_sopa.winfo_ismapped(): self.frame_sopa.grid_remove()
        if self.frame_lista.winfo_ismapped(): self.frame_lista.grid_remove()
        if self.frame_input.winfo_ismapped(): self.frame_input.grid_remove()

        self.frame_menu.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        if hasattr(self, 'boton_iniciar_menu'):
            self.boton_iniciar_menu.config(state='normal')
        
        self._show_message("", 1)


    def _show_game_interface(self):
        if self.frame_menu.winfo_ismapped(): self.frame_menu.grid_remove()

        self.frame_sopa.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.frame_lista.grid(row=0, column=1, rowspan=2, sticky='ns', padx=10, pady=10)
        self.frame_input.grid(row=1, column=0, sticky='ew', padx=10, pady=(5,10))
        
        self.root.grid_columnconfigure(0, weight=3)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=3)
        self.root.grid_rowconfigure(1, weight=1)

        self.button_pause_game.grid(row=3, column=0, columnspan=1, pady=5, sticky="ew", padx=(5,2))
        self.button_music_game.grid(row=3, column=1, columnspan=2, pady=5, sticky="ew", padx=(2,5)) 
        
        self.entry.config(state='normal')
        self.button_submit.config(state='normal')
        self.entry.focus_set()

    def _crear_tablero(self, filas: int, columnas: int) -> List[List[str]]:
        return [[' ' for _ in range(columnas)] for _ in range(filas)]

    def _celdas_adyacentes(self, fila: int, col: int, filas: int, columnas: int) -> List[Tuple[int, int]]:
        adyacentes = []
        direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for df, dc in direcciones:
            nf, nc = fila + df, col + dc
            if 0 <= nf < filas and 0 <= nc < columnas:
                adyacentes.append((nf, nc))
        return adyacentes

    def _encontrar_camino_palabra(self, tablero: List[List[str]], palabra: str, fila: int, col: int, visitado: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        if tablero[fila][col] != ' ' and tablero[fila][col] != palabra[0]:
            return None
        if len(palabra) == 1:
            if tablero[fila][col] == ' ' or tablero[fila][col] == palabra[0]:
                return [(fila, col)]
            return None
        visitado_actual = visitado.copy()
        visitado_actual.add((fila, col))
        filas_tablero, columnas_tablero = len(tablero), len(tablero[0])
        adyacentes = self._celdas_adyacentes(fila, col, filas_tablero, columnas_tablero)
        random.shuffle(adyacentes)
        for i_ady, j_ady in adyacentes:
            if (i_ady, j_ady) not in visitado_actual:
                camino = self._encontrar_camino_palabra(tablero, palabra[1:], i_ady, j_ady, visitado_actual)
                if camino:
                    return [(fila, col)] + camino
        return None

    def _insertar_palabra(self, tablero: List[List[str]], palabra: str, max_intentos_posicion: int = 200) -> bool:
        filas, columnas = len(tablero), len(tablero[0])
        palabra_upper = palabra.upper()
        
        posibles_inicios = []
        for r_idx in range(filas):
            for c_idx in range(columnas):
                if tablero[r_idx][c_idx] == ' ' or tablero[r_idx][c_idx] == palabra_upper[0]:
                    posibles_inicios.append((r_idx,c_idx))
        random.shuffle(posibles_inicios)

        intentos_reales = 0
        for inicio_fila, inicio_columna in posibles_inicios:
            intentos_reales +=1
            if intentos_reales > max_intentos_posicion:
                break
            camino = self._encontrar_camino_palabra(tablero, palabra_upper, inicio_fila, inicio_columna, set())
            if camino:
                valido_para_escribir = True
                for k, ((r_camino, c_camino), letra_palabra) in enumerate(zip(camino, palabra_upper)):
                    if tablero[r_camino][c_camino] != ' ' and tablero[r_camino][c_camino] != letra_palabra:
                        valido_para_escribir = False
                        break
                if valido_para_escribir:
                    for (r_final, c_final), letra in zip(camino, palabra_upper):
                        tablero[r_final][c_final] = letra
                    return True
        return False

    def _calcular_complejidad_camino(self, camino: List[Tuple[int, int]]) -> int:
        if len(camino) < 3: return 0
        cambios_direccion = 0
        for i in range(1, len(camino) - 1):
            dir1 = (camino[i][0] - camino[i-1][0], camino[i][1] - camino[i-1][1])
            dir2 = (camino[i+1][0] - camino[i][0], camino[i+1][1] - camino[i][1])
            if dir1 != dir2: 
                cambios_direccion += 1
        return cambios_direccion

    def _rellenar_tablero(self, tablero: List[List[str]]):
        letras_palabras_ocultas = set()
        for palabra_oculta in self.palabras:
            letras_palabras_ocultas.update(palabra_oculta.upper())
        letras_comunes = 'AEIOULNSTRDCMBPGVHFYQJZXKW'
        letras_relleno_pool = list(letras_palabras_ocultas) * 3 + list('AEIOU') * 2 + list(letras_comunes)
        random.shuffle(letras_relleno_pool)
        for i in range(len(tablero)):
            for j in range(len(tablero[0])):
                if tablero[i][j] == ' ':
                    if letras_relleno_pool:
                        tablero[i][j] = random.choice(letras_relleno_pool)
                    else:
                        tablero[i][j] = random.choice(letras_comunes)
    
    def _crear_sopa_letras(self, palabras_candidatas_iniciales: List[str]) -> Optional[List[List[str]]]:
        filas, columnas = self.GRID_SIZE
        for _intento_tablero_idx in range(self.MAX_INTENTOS_TABLERO_INTERNO):
            tablero = self._crear_tablero(filas, columnas)
            palabras_colocadas_en_intento_actual = []
            palabras_a_intentar_ordenadas = sorted(list(set(palabras_candidatas_iniciales)), key=len, reverse=True)
            todas_las_palabras_de_este_intento_colocadas = True

            for palabra_original_del_slot in palabras_a_intentar_ordenadas:
                palabra_actual_a_colocar = palabra_original_del_slot
                slot_llenado = False
                palabras_ya_probadas_para_este_slot = {palabra_original_del_slot}

                for _intento_reemplazo in range(self.MAX_REEMPLAZOS_POR_SLOT + 1): 
                    if self._insertar_palabra(tablero, palabra_actual_a_colocar):
                        palabras_colocadas_en_intento_actual.append(palabra_actual_a_colocar)
                        slot_llenado = True
                        break 
                    else:
                        if _intento_reemplazo < self.MAX_REEMPLAZOS_POR_SLOT:
                            longitud_necesaria = len(palabra_original_del_slot)
                            posibles_reemplazos = [
                                w for w in self.all_words_by_length.get(longitud_necesaria, [])
                                if w not in palabras_colocadas_en_intento_actual and \
                                   w not in palabras_ya_probadas_para_este_slot and \
                                   w != palabra_original_del_slot
                            ]
                            random.shuffle(posibles_reemplazos)
                            if posibles_reemplazos:
                                palabra_actual_a_colocar = posibles_reemplazos[0]
                                palabras_ya_probadas_para_este_slot.add(palabra_actual_a_colocar)
                            else:
                                slot_llenado = False
                                break 
                        else: 
                            slot_llenado = False 
                if not slot_llenado:
                    todas_las_palabras_de_este_intento_colocadas = False
                    break 
            
            if todas_las_palabras_de_este_intento_colocadas and \
               len(set(palabras_colocadas_en_intento_actual)) == len(set(palabras_candidatas_iniciales)):
                self.palabras = list(set(palabras_colocadas_en_intento_actual))
                self._rellenar_tablero(tablero)
                self._clasificar_palabras_por_longitud()
                return tablero
        
        self.palabras = [] 
        return None

    def _clasificar_palabras_por_longitud(self):
        self.palabras_por_longitud = {}
        for palabra_str in self.palabras:
            longitud = len(palabra_str)
            self.palabras_por_longitud.setdefault(longitud, []).append(palabra_str)

    def _cargar_palabras(self) -> List[str]:
        try:
            with open(self.archivo_palabras, "r", encoding="utf-8") as archivo:
                all_words_list = [linea.strip().upper() for linea in archivo if linea.strip() and len(linea.strip()) > 1]
            self.all_words_by_length = {}
            for word in all_words_list:
                length = len(word)
                self.all_words_by_length.setdefault(length, set()).add(word)
            for length in self.all_words_by_length:
                self.all_words_by_length[length] = list(self.all_words_by_length[length])

            for length_needed, count_needed in self.DISTRIBUCION_PALABRAS.items():
                available_count = len(self.all_words_by_length.get(length_needed, []))
                if available_count < count_needed:
                    print(f"Advertencia: Se necesitan {count_needed} palabras de longitud {length_needed}, pero solo hay {available_count} disponibles en '{self.archivo_palabras}'.")
            return self._seleccionar_palabras_candidatas(self.all_words_by_length)
        except FileNotFoundError:
            print(f"Error Crítico: No se encontró el archivo de palabras '{self.archivo_palabras}'. El juego no puede continuar.")
            return []

    def _seleccionar_palabras_candidatas(self, words_by_length_source: Dict[int, List[str]], max_intentos: int = 30) -> List[str]:
        objetivo_calculado = sum(self.DISTRIBUCION_PALABRAS.values())
        if self.PALABRAS_OBJETIVO != objetivo_calculado:
            print(f"Advertencia: PALABRAS_OBJETIVO ({self.PALABRAS_OBJETIVO}) no coincide con la suma de DISTRIBUCION_PALABRAS ({objetivo_calculado}). Ajustando PALABRAS_OBJETIVO.")
            self.PALABRAS_OBJETIVO = objetivo_calculado

        for _intento_seleccion in range(max_intentos):
            selected_words_set = set()
            temp_words_by_length = {k: list(v) for k, v in words_by_length_source.items()} 

            for longitud, cantidad_deseada in self.DISTRIBUCION_PALABRAS.items():
                disponibles_esta_longitud = temp_words_by_length.get(longitud, [])
                random.shuffle(disponibles_esta_longitud)
                count_added_for_length = 0
                # Usar una copia para iterar si se modifica la lista original (disponibles_esta_longitud)
                for word_to_add in list(disponibles_esta_longitud): 
                    if count_added_for_length < cantidad_deseada:
                        if word_to_add not in selected_words_set:
                             selected_words_set.add(word_to_add)
                             disponibles_esta_longitud.remove(word_to_add) # Remover de la lista temporal
                             count_added_for_length +=1
                    else:
                        break
            
            if len(selected_words_set) == self.PALABRAS_OBJETIVO:
                return list(selected_words_set)
            if len(selected_words_set) > self.PALABRAS_OBJETIVO:
                 return random.sample(list(selected_words_set), self.PALABRAS_OBJETIVO)

            if len(selected_words_set) < self.PALABRAS_OBJETIVO:
                needed_more = self.PALABRAS_OBJETIVO - len(selected_words_set)
                all_remaining_flat = []
                for l_val in sorted(temp_words_by_length.keys(), reverse=True):
                    for w_rem in temp_words_by_length.get(l_val, []):
                        if w_rem not in selected_words_set: 
                            all_remaining_flat.append(w_rem)
                random.shuffle(all_remaining_flat)
                if len(all_remaining_flat) >= needed_more:
                    selected_words_set.update(all_remaining_flat[:needed_more])
                else:
                    selected_words_set.update(all_remaining_flat)

            if len(selected_words_set) == self.PALABRAS_OBJETIVO:
                return list(selected_words_set)
        
        print(f"Advertencia: No se pudieron seleccionar exactamente {self.PALABRAS_OBJETIVO} palabras candidatas tras {max_intentos} intentos. Se seleccionaron {len(selected_words_set)}.")
        final_list = list(selected_words_set)
        if len(final_list) > self.PALABRAS_OBJETIVO:
            return random.sample(final_list, self.PALABRAS_OBJETIVO)
        elif len(final_list) < self.PALABRAS_OBJETIVO:
            all_flat_total_unique = list(set(w for sublist in words_by_length_source.values() for w in sublist))
            needed_desperately = self.PALABRAS_OBJETIVO - len(final_list)
            if needed_desperately > 0:
                potential_fillers = [w for w in all_flat_total_unique if w not in final_list]
                random.shuffle(potential_fillers)
                final_list.extend(potential_fillers[:needed_desperately])
        
        final_list = list(set(final_list))
        if len(final_list) > self.PALABRAS_OBJETIVO:
            return random.sample(final_list, self.PALABRAS_OBJETIVO)
        return final_list


    def _imprimir_distribucion_palabras(self, palabras_a_imprimir: List[str]):
        distribucion = {}
        for palabra_str in palabras_a_imprimir:
            longitud = len(palabra_str)
            distribucion.setdefault(longitud, []).append(palabra_str)
        print("--- Distribución de Palabras en el Tablero ---")
        for longitud_val in sorted(distribucion.keys(), reverse=True):
            print(f"  {longitud_val} letras ({len(distribucion[longitud_val])}): {', '.join(sorted(distribucion[longitud_val]))}")
        print("---------------------------------------------")

    def _on_grid_cell_click(self, row: int, col: int, letter: str):
        if not self.game_active or not self.timer_running: return

        clicked_cell_widget = self.grid_cell_widgets[row][col]

        if self.current_selection_path and self.current_selection_path[-1] == (row, col):
            self.current_selection_path.pop()
            self.current_selected_word = self.current_selected_word[:-1]
            if clicked_cell_widget:
                 clicked_cell_widget.config(bg=self.default_cell_bg_color)
        elif (row, col) not in self.current_selection_path:
            is_valid_next_step = False
            if not self.current_selection_path:
                is_valid_next_step = True
            else:
                last_r, last_c = self.current_selection_path[-1]
                if (row, col) in self._celdas_adyacentes(last_r, last_c, self.GRID_SIZE[0], self.GRID_SIZE[1]):
                    is_valid_next_step = True
            if is_valid_next_step:
                self.current_selection_path.append((row, col))
                self.current_selected_word += letter
                if clicked_cell_widget:
                    clicked_cell_widget.config(bg=self.selected_cell_bg_color)
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.current_selected_word)

    def _reset_grid_selection(self):
        for r_idx in range(self.GRID_SIZE[0]):
            for c_idx in range(self.GRID_SIZE[1]):
                if self.grid_cell_widgets and \
                   r_idx < len(self.grid_cell_widgets) and \
                   c_idx < len(self.grid_cell_widgets[r_idx]) and \
                   self.grid_cell_widgets[r_idx][c_idx]:
                    self.grid_cell_widgets[r_idx][c_idx].config(bg=self.default_cell_bg_color)
        self.current_selection_path.clear()
        self.current_selected_word = ""
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            self.entry.delete(0, tk.END)

    def _mostrar_tablero(self, tablero: List[List[str]]):
        for widget in self.frame_sopa.winfo_children(): 
            widget.destroy()
        self.grid_cell_widgets = [[None for _ in range(self.GRID_SIZE[1])] for _ in range(self.GRID_SIZE[0])]
        font_grid_tuple = (self.MAIN_FONT_FAMILY, self.GRID_LETTER_FONT_SIZE, "bold")

        for i, fila_letras in enumerate(tablero): 
            self.frame_sopa.grid_rowconfigure(i, weight=1)
            for j, letra in enumerate(fila_letras):
                self.frame_sopa.grid_columnconfigure(j, weight=1)
                cell_button = tk.Button(
                    self.frame_sopa, text=letra, 
                    font=font_grid_tuple,
                    borderwidth=1, relief=tk.SOLID, 
                    bg=self.default_cell_bg_color, 
                    fg=self.COLORS['grid_fg'],
                    activebackground=self.selected_cell_bg_color,
                    activeforeground=self.COLORS['grid_fg'],
                    command=lambda r=i, c=j, l=letra: self._on_grid_cell_click(r, c, l)
                )
                cell_button.grid(row=i, column=j, padx=1, pady=1, sticky="nsew")
                self.grid_cell_widgets[i][j] = cell_button

    def _mostrar_lista_palabras(self):
        for widget in self.frame_lista.winfo_children(): widget.destroy()
        font_ui_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE)
        font_ui_bold_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE, "bold")
        font_hint_box_tuple = (self.MAIN_FONT_FAMILY, self.UI_FONT_SIZE - 1, "bold")

        titulo = tk.Label(self.frame_lista, text="Palabras:", font=font_ui_bold_tuple, bg=self.COLORS['bg'], fg=self.COLORS['fg'])
        titulo.pack(pady=(0, 10), anchor="w")
        self.hint_labels.clear()

        if not self.palabras_por_longitud:
            info_label = tk.Label(self.frame_lista, text="No hay palabras...", font=font_ui_tuple, bg=self.COLORS['bg'], fg=self.COLORS['hint_fg'])
            info_label.pack(anchor="w")
            return

        for longitud in sorted(self.palabras_por_longitud.keys(), reverse=True):
            subtitulo_text = f"{longitud} letras:"
            subtitulo = tk.Label(self.frame_lista, text=subtitulo_text, font=font_ui_tuple, bg=self.COLORS['bg'], fg=self.COLORS['hint_fg'] )
            subtitulo.pack(pady=(8, 3), anchor="w")
            for palabra_str in sorted(self.palabras_por_longitud[longitud]): 
                word_hint_container = tk.Frame(self.frame_lista, bg=self.COLORS['bg'])
                word_hint_container.pack(pady=2, padx=5, anchor="w")
                letter_box_labels_for_word = []
                for idx, char_in_palabra in enumerate(palabra_str): 
                    box_text = ""
                    if idx == 0:
                        box_text = palabra_str[0].upper()
                    letter_box_label = tk.Label(
                        word_hint_container, text=box_text, font=font_hint_box_tuple, 
                        bg=self.COLORS['hint_box_bg'], fg=self.COLORS['hint_box_fg'], 
                        borderwidth=1, relief=tk.SOLID, width=2, height=1, anchor='center'
                    )
                    letter_box_label.pack(side=tk.LEFT, padx=1)
                    letter_box_labels_for_word.append(letter_box_label)
                self.hint_labels[palabra_str.upper()] = letter_box_labels_for_word
    
    def iniciar_juego(self):
        if hasattr(self, 'boton_iniciar_menu'):
            self.boton_iniciar_menu.config(state='disabled')
        self.root.update_idletasks() 
        print("Iniciando nuevo juego...")
        self._show_message("Cargando palabras...", 0)
        self.root.update()
        palabras_candidatas = self._cargar_palabras()

        if not palabras_candidatas or len(palabras_candidatas) < self.PALABRAS_OBJETIVO:
            msg = ""
            if not palabras_candidatas: msg = f"Error: No se pudo cargar/seleccionar palabras desde '{self.archivo_palabras}'."
            else: msg = f"Error: Palabras insuficientes ({len(palabras_candidatas)} de {self.PALABRAS_OBJETIVO} requeridas)."
            print(msg)
            self._show_message(msg, 7000)
            if hasattr(self, 'boton_iniciar_menu'): self.boton_iniciar_menu.config(state='normal')
            self._show_menu_interface()
            return
        
        tablero_generado = None
        intentos_globales_actual = 0
        while intentos_globales_actual < self.MAX_INTENTOS_GLOBALES_GENERACION:
            intentos_globales_actual += 1
            self._show_message(f"Generando tablero... Intento {intentos_globales_actual}/{self.MAX_INTENTOS_GLOBALES_GENERACION}", 0) 
            self.root.update() 
            tablero_generado = self._crear_sopa_letras(palabras_candidatas)
            if tablero_generado is not None and self.palabras and len(self.palabras) == self.PALABRAS_OBJETIVO: 
                print(f"Tablero generado exitosamente en el intento global {intentos_globales_actual}.")
                self._imprimir_distribucion_palabras(self.palabras)
                break 
            else: 
                self.palabras = [] 
                if intentos_globales_actual < self.MAX_INTENTOS_GLOBALES_GENERACION:
                    print(f"Intento global {intentos_globales_actual} fallido. Reintentando...")
                    self.root.after(100) 
                    self.root.update()

        if tablero_generado is None or not self.palabras or len(self.palabras) != self.PALABRAS_OBJETIVO:
            msg = f"No se pudo crear un tablero válido tras {intentos_globales_actual} intentos globales."
            print(msg)
            self._show_message(msg, 7000)
            if hasattr(self, 'boton_iniciar_menu'): self.boton_iniciar_menu.config(state='normal')
            self._show_menu_interface()
            return

        self._reset_game_state()
        self._mostrar_tablero(tablero_generado)
        self._mostrar_lista_palabras()
        self._show_game_interface() 
        self._update_status()
        self._show_message("¡Juego Iniciado! Encuentra las palabras.", 3000)
        print(f"Juego iniciado con {len(self.palabras)} palabras en el tablero.")

    def _reset_game_state(self):
        self.found_words.clear()
        self.score = 0
        self.time_elapsed = 0
        self.timer_running = True
        self.game_active = True   
        self._reset_grid_selection()
        self._update_status()
        self.label_timer.config(text=f"Tiempo: {self._format_time(self.time_elapsed)}")
        if hasattr(self, '_timer_after_id'): 
            self.root.after_cancel(self._timer_after_id)
        self._timer_after_id = self.root.after(1000, self._update_timer)

    def check_word(self):
        if not self.game_active or not self.timer_running: return
        word_input = self.entry.get().strip().upper()
        if not word_input: 
            self._reset_grid_selection() 
            return

        if word_input in self.palabras and word_input not in self.found_words:
            self._word_found(word_input)
        elif word_input in self.found_words:
            self._show_message(f"'{word_input}' ya fue encontrada.", 2000)
            self.reproducir_sonido(self.sonido_incorrecto)
        else: 
            self._show_message(f"'{word_input}' no es correcta.", 2000)
            self.reproducir_sonido(self.sonido_incorrecto)
        self._reset_grid_selection()

    def _word_found(self, word: str):
        self.found_words.add(word)
        if word in self.hint_labels: 
            letter_boxes = self.hint_labels[word]
            for i, box_label in enumerate(letter_boxes):
                if i < len(word):
                    box_label.config(text=word[i], fg=self.COLORS['found_word_fg'])
        else: 
            print(f"Advertencia crítica: Palabra '{word}' encontrada pero no existe en self.hint_labels.")

        base_score = len(word) * 100
        time_bonus = max(300 - (self.time_elapsed // (len(word) if len(word)>0 else 1)), 50) 
        word_score = base_score + time_bonus
        self.score += word_score
        self._update_status()
        self.reproducir_sonido(self.sonido_correcto)
        self._show_message(f"¡'{word}' encontrada! +{word_score} puntos", 2500)
        if len(self.found_words) == len(self.palabras):
            self._end_game()

    def _update_status(self):
        num_total_palabras_objetivo = len(self.palabras) if self.palabras else self.PALABRAS_OBJETIVO
        status_text = f"Palabras: {len(self.found_words)}/{num_total_palabras_objetivo} | Puntos: {self.score}"
        if hasattr(self, 'label_status') and self.label_status.winfo_exists():
             self.label_status.config(text=status_text)

    def _show_message(self, message: str, duration: int = 2000):
        if hasattr(self, 'label_message') and self.label_message.winfo_exists():
            self.label_message.config(text=message)
            if self._message_after_id is not None:
                self.root.after_cancel(self._message_after_id)
                self._message_after_id = None
            if duration > 0:
                # Corregido: Usar una lambda simple para limpiar el texto.
                self._message_after_id = self.root.after(duration, lambda: self.label_message.config(text=""))

    def _update_timer(self):
        if self.timer_running and self.game_active:
            self.time_elapsed += 1
            if hasattr(self, 'label_timer') and self.label_timer.winfo_exists():
                self.label_timer.config(text=f"Tiempo: {self._format_time(self.time_elapsed)}")
            self._timer_after_id = self.root.after(1000, self._update_timer)

    def toggle_pause(self):
        if not self.game_active: return 
        if self.timer_running: 
            self._pause_game()
        else: 
             if self.game_active:
                self._resume_game()

    def toggle_music(self):
        button_texts = {"ON": "Música: ON", "OFF": "Música: OFF", "ERR": "Música: ERR", "N/A": "Música: N/A"}
        current_status_text_key = "OFF"

        if not self.musica_fondo:
            current_status_text_key = "N/A"
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            current_status_text_key = "OFF"
        else: 
            current_pos = pygame.mixer.music.get_pos()
            # Pygame's get_pos can return -1 if never played or after stopping. 
            # It returns milliseconds while playing/paused.
            was_paused = current_pos > 0 # Check if it was paused (had a position)
            
            if was_paused : 
                 pygame.mixer.music.unpause()
                 current_status_text_key = "ON"
            else: # Not playing and not paused (i.e., stopped or never started)
                try:
                    pygame.mixer.music.load(self.musica_fondo)
                    pygame.mixer.music.play(-1)
                    current_status_text_key = "ON"
                except pygame.error as e:
                    print(f"Error al intentar reproducir música: {e}")
                    current_status_text_key = "ERR"
        
        if hasattr(self, 'button_music_game') and self.button_music_game.winfo_exists():
            self.button_music_game.config(text=button_texts[current_status_text_key])
        if hasattr(self, 'button_music_menu') and self.button_music_menu.winfo_exists():
            self.button_music_menu.config(text=button_texts[current_status_text_key])

    def _pause_game(self):
        if not self.game_active: return
        self.timer_running = False
        if hasattr(self, 'button_pause_game') and self.button_pause_game.winfo_exists():
            self.button_pause_game.config(text="Reanudar")
        if hasattr(self, 'entry') and self.entry.winfo_exists(): self.entry.config(state='disabled')
        if hasattr(self, 'button_submit') and self.button_submit.winfo_exists(): self.button_submit.config(state='disabled')
        if hasattr(self, 'grid_cell_widgets'):
            for row_widgets in self.grid_cell_widgets:
                for widget_cell in row_widgets:
                    if widget_cell and widget_cell.winfo_exists(): widget_cell.config(state='disabled')

    def _resume_game(self):
        if not self.game_active: return 
        self.timer_running = True
        if hasattr(self, '_timer_after_id'):
             self.root.after_cancel(self._timer_after_id)
        self._timer_after_id = self.root.after(1000, self._update_timer)

        if hasattr(self, 'label_timer') and self.label_timer.winfo_exists():
             self.label_timer.config(text=f"Tiempo: {self._format_time(self.time_elapsed)}")
        if hasattr(self, 'button_pause_game') and self.button_pause_game.winfo_exists():
            self.button_pause_game.config(text="Pausar")
        if hasattr(self, 'entry') and self.entry.winfo_exists():
            self.entry.config(state='normal')
            self.entry.focus_set()
        if hasattr(self, 'button_submit') and self.button_submit.winfo_exists():
            self.button_submit.config(state='normal')
        if hasattr(self, 'grid_cell_widgets'):
            for row_widgets in self.grid_cell_widgets:
                for widget_cell in row_widgets:
                    if widget_cell and widget_cell.winfo_exists(): widget_cell.config(state='normal')
        
    def _end_game(self):
        self.game_active = False
        self.timer_running = False
        if hasattr(self, '_timer_after_id') and self._timer_after_id is not None:
            self.root.after_cancel(self._timer_after_id)
            self._timer_after_id = None
        
        final_message = f"¡Juego Completado!\nPuntuación Final: {self.score}\nTiempo Total: {self._format_time(self.time_elapsed)}"
        self._show_message(final_message, 0)
        
        if hasattr(self, 'entry') and self.entry.winfo_exists(): self.entry.config(state='disabled')
        if hasattr(self, 'button_submit') and self.button_submit.winfo_exists(): self.button_submit.config(state='disabled')
        if hasattr(self, 'button_pause_game') and self.button_pause_game.winfo_exists(): self.button_pause_game.config(state='disabled')
        if hasattr(self, 'grid_cell_widgets'):
            for row_widgets in self.grid_cell_widgets:
                for widget_cell in row_widgets:
                    if widget_cell and widget_cell.winfo_exists(): widget_cell.config(state='disabled')
        self.root.after(5000, self._show_menu_interface_after_game_end)

    def _show_menu_interface_after_game_end(self):
        if hasattr(self, 'entry') and self.entry.winfo_exists(): self.entry.config(state='disabled')
        if hasattr(self, 'button_submit') and self.button_submit.winfo_exists(): self.button_submit.config(state='disabled')
        self._show_menu_interface()

    def run(self):
        self._set_window_geometry(800, 600) 
        self.root.mainloop()
        pygame.mixer.quit()

if __name__ == "__main__":
    # Rutas a los archivos como estaban originalmente en tu código
    archivo_palabras = "palabras.txt" 
    logo_file = "imagenes/lexigrama.png" 
    
    # Instanciar y correr el juego
    juego = BoggleGame(archivo_palabras, logo_path=logo_file)
    juego.run()
