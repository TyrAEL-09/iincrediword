# game/word_generator.py
import random
from typing import List, Tuple, Set, Optional, Dict

class WordGenerator:
    """
    Gestiona la carga de palabras, selección de palabras objetivo
    y la generación del tablero de letras (sopa de letras).
    """
    def __init__(self, game_settings):
        self.game_settings = game_settings
        self.all_words_by_length: Dict[int, List[str]] = {}
        self.selected_target_words: List[str] = [] # Las palabras que deben ser encontradas
        self.generated_board: Optional[List[List[str]]] = None

    def _load_words_from_file(self, filename: str) -> bool:
        """Carga palabras desde un archivo y las clasifica por longitud."""
        try:
            with open(filename, "r", encoding="utf-8") as file:
                all_words_list = [line.strip().upper() for line in file if line.strip() and len(line.strip()) > 1]
            self.all_words_by_length.clear()
            for word in all_words_list:
                length = len(word)
                self.all_words_by_length.setdefault(length, []).append(word)
            # Convertir sets a listas para que sean mutables si se desea remover palabras
            # Aunque en este caso se usa una copia temporal en select_candidate_words
            for length in self.all_words_by_length:
                random.shuffle(self.all_words_by_length[length])
            return True
        except FileNotFoundError:
            print(f"Error Crítico: No se encontró el archivo de palabras '{filename}'.")
            return False

    def _select_candidate_words(self) -> List[str]:
        """
        Selecciona las palabras objetivo basándose en la distribución deseada.
        Intenta cumplir la distribución y si no, completa con palabras aleatorias.
        """
        selected_words_set = set()
        temp_words_by_length = {k: list(v) for k, v in self.all_words_by_length.items()}

        for length, desired_count in self.game_settings.WORD_DISTRIBUTION.items():
            available_for_length = temp_words_by_length.get(length, [])
            random.shuffle(available_for_length) # Mezclar para una selección aleatoria
            count_added = 0
            for word in available_for_length:
                if count_added < desired_count and word not in selected_words_set:
                    selected_words_set.add(word)
                    count_added += 1
            if count_added < desired_count:
                print(f"Advertencia: No se pudieron seleccionar {desired_count} palabras de {length} letras. Se encontraron {count_added}.")

        # Si el número de palabras seleccionadas no coincide con el objetivo, ajustar
        if len(selected_words_set) < self.game_settings.TARGET_WORDS_COUNT:
            needed_more = self.game_settings.TARGET_WORDS_COUNT - len(selected_words_set)
            all_remaining_flat = []
            for l_val in sorted(temp_words_by_length.keys(), reverse=True):
                for w_rem in temp_words_by_length.get(l_val, []):
                    if w_rem not in selected_words_set:
                        all_remaining_flat.append(w_rem)
            random.shuffle(all_remaining_flat)
            selected_words_set.update(all_remaining_flat[:needed_more])
        elif len(selected_words_set) > self.game_settings.TARGET_WORDS_COUNT:
            return random.sample(list(selected_words_set), self.game_settings.TARGET_WORDS_COUNT)

        return list(selected_words_set)

    def _create_empty_board(self, rows: int, cols: int) -> List[List[str]]:
        """Crea un tablero vacío de un tamaño dado."""
        return [[' ' for _ in range(cols)] for _ in range(rows)]

    def _get_adjacent_cells(self, r: int, c: int, rows: int, cols: int) -> List[Tuple[int, int]]:
        """Devuelve las celdas adyacentes a una posición (r, c)."""
        adjacents = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Arriba, Abajo, Izquierda, Derecha
        # También se pueden incluir diagonales si el juego lo permite:
        # directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                adjacents.append((nr, nc))
        return adjacents

    def _find_word_path(self, board: List[List[str]], word: str, row: int, col: int, visited: Set[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """
        Intenta encontrar un camino para colocar una palabra en el tablero
        a partir de una celda inicial, evitando ciclos y celdas ya visitadas.
        """
        if board[row][col] != ' ' and board[row][col] != word[0]:
            return None # La primera letra no coincide y la celda no está vacía

        if len(word) == 1:
            return [(row, col)] # Se encontró un camino para la última letra

        visited_copy = visited.copy()
        visited_copy.add((row, col))

        rows, cols = len(board), len(board[0])
        adjacents = self._get_adjacent_cells(row, col, rows, cols)
        random.shuffle(adjacents) # Aleatorizar la búsqueda de caminos

        for next_r, next_c in adjacents:
            if (next_r, next_c) not in visited_copy:
                path = self._find_word_path(board, word[1:], next_r, next_c, visited_copy)
                if path:
                    return [(row, col)] + path
        return None

    def _place_word_on_board(self, board: List[List[str]], word: str, max_attempts: int = 200) -> bool:
        """
        Intenta insertar una palabra en el tablero en un camino válido.
        Prioriza celdas vacías o que ya contengan la letra correcta.
        """
        rows, cols = len(board), len(board[0])
        word_upper = word.upper()

        possible_starts = []
        for r_idx in range(rows):
            for c_idx in range(cols):
                if board[r_idx][c_idx] == ' ' or board[r_idx][c_idx] == word_upper[0]:
                    possible_starts.append((r_idx, c_idx))
        random.shuffle(possible_starts)

        attempts_made = 0
        for start_row, start_col in possible_starts:
            attempts_made += 1
            if attempts_made > max_attempts:
                break # Demasiados intentos para esta palabra

            path = self._find_word_path(board, word_upper, start_row, start_col, set())
            if path:
                # Verificar si el camino es válido para escribir (no sobreescribir letras diferentes)
                is_valid_to_write = True
                for (path_r, path_c), char_in_word in zip(path, word_upper):
                    if board[path_r][path_c] != ' ' and board[path_r][path_c] != char_in_word:
                        is_valid_to_write = False
                        break
                if is_valid_to_write:
                    # Escribir la palabra en el tablero
                    for (path_r, path_c), char_in_word in zip(path, word_upper):
                        board[path_r][path_c] = char_in_word
                    return True
        return False

    def _fill_empty_cells(self, board: List[List[str]]):
        """Rellena las celdas vacías del tablero con letras aleatorias."""
        common_letters = 'AEIOULNSTRDCMBPGVHFYQJZXKW' # Frecuencia común en español
        all_letters_in_target_words = set()
        for word in self.selected_target_words:
            all_letters_in_target_words.update(word.upper())

        # Pool de letras para relleno, priorizando las del vocabulario del juego
        fill_letter_pool = list(all_letters_in_target_words) * 2 + list('AEIOU') * 2 + list(common_letters)
        random.shuffle(fill_letter_pool)

        for r_idx in range(len(board)):
            for c_idx in range(len(board[0])):
                if board[r_idx][c_idx] == ' ':
                    if fill_letter_pool:
                        board[r_idx][c_idx] = random.choice(fill_letter_pool)
                    else: # Si se acaban las letras del pool, usar las comunes
                        board[r_idx][c_idx] = random.choice(common_letters)

    def generate_game_board(self) -> Optional[List[List[str]]]:
        """
        Intenta generar un tablero de sopa de letras con las palabras objetivo.
        Retorna el tablero generado o None si falla tras múltiples intentos.
        """
        if not self._load_words_from_file(self.game_settings.WORD_FILE):
            return None

        for global_attempt_idx in range(self.game_settings.MAX_GLOBAL_GENERATION_ATTEMPTS):
            print(f"Intento global de generación de tablero: {global_attempt_idx + 1}")
            self.selected_target_words = self._select_candidate_words()
            if not self.selected_target_words or len(self.selected_target_words) != self.game_settings.TARGET_WORDS_COUNT:
                print(f"No se pudieron seleccionar {self.game_settings.TARGET_WORDS_COUNT} palabras objetivo en este intento global.")
                continue # Reintentar con otra selección de palabras

            rows, cols = self.game_settings.GRID_SIZE
            current_board = self._create_empty_board(rows, cols)
            words_successfully_placed = []
            all_words_placed_in_current_attempt = True

            # Ordenar palabras por longitud descendente para intentar colocar las más largas primero
            words_to_place_ordered = sorted(list(set(self.selected_target_words)), key=len, reverse=True)

            for original_word_for_slot in words_to_place_ordered:
                word_placed_for_slot = False
                words_already_tried_for_this_slot = {original_word_for_slot}

                for replacement_attempt in range(self.game_settings.MAX_REPLACEMENTS_PER_SLOT + 1):
                    word_to_attempt_placement = original_word_for_slot
                    if replacement_attempt > 0: # Para intentos de reemplazo, buscar otra palabra
                        length_needed = len(original_word_for_slot)
                        possible_replacements = [
                            w for w in self.all_words_by_length.get(length_needed, [])
                            if w not in words_successfully_placed and
                               w not in words_already_tried_for_this_slot
                        ]
                        random.shuffle(possible_replacements)
                        if possible_replacements:
                            word_to_attempt_placement = possible_replacements[0]
                            words_already_tried_for_this_slot.add(word_to_attempt_placement)
                        else:
                            # No hay más reemplazos disponibles para esta longitud
                            break

                    if self._place_word_on_board(current_board, word_to_attempt_placement):
                        words_successfully_placed.append(word_to_attempt_placement)
                        word_placed_for_slot = True
                        break # Palabra colocada, pasar a la siguiente ranura

                if not word_placed_for_slot:
                    all_words_placed_in_current_attempt = False
                    break # No se pudo colocar esta palabra ni sus reemplazos, falló el intento

            if all_words_placed_in_current_attempt and \
               len(set(words_successfully_placed)) == len(set(self.selected_target_words)):
                self.selected_target_words = list(set(words_successfully_placed)) # Actualizar con las que realmente se colocaron
                self._fill_empty_cells(current_board)
                self.generated_board = current_board
                print(f"Tablero generado exitosamente en el intento global {global_attempt_idx + 1}.")
                self._print_word_distribution(self.selected_target_words)
                return self.generated_board

        print(f"Falló la generación del tablero tras {self.game_settings.MAX_GLOBAL_GENERATION_ATTEMPTS} intentos globales.")
        self.selected_target_words = [] # Limpiar palabras objetivo si no se pudo generar el tablero
        return None

    def get_target_words(self) -> List[str]:
        """Devuelve la lista de palabras objetivo seleccionadas para el tablero actual."""
        return self.selected_target_words

    def _print_word_distribution(self, words_to_print: List[str]):
        """Imprime la distribución de palabras seleccionadas para el tablero."""
        distribution = {}
        for word_str in words_to_print:
            length = len(word_str)
            distribution.setdefault(length, []).append(word_str)
        print("--- Distribución de Palabras Objetivo en el Tablero ---")
        for length_val in sorted(distribution.keys(), reverse=True):
            print(f"  {length_val} letras ({len(distribution[length_val])}): {', '.join(sorted(distribution[length_val]))}")
        print("--------------------------------------------------")