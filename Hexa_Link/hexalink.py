import pygame
import sys
import math
import time
import os
from collections import defaultdict
from Hexa_Link.partida import guardar_partida
from Hexa_Link.gestor_palabras import generar_palabras_y_letras

ANCHO = 1000
ALTO = 600
HEX_SIZE = 50
CENTRO = (400, ALTO // 2)

pygame.init()
pygame.font.init()
FUENTE = pygame.font.SysFont("arial", 24)
FUENTE_GRANDE = pygame.font.SysFont("arial", 36)

COLOR_FONDO = (30, 30, 30)
COLOR_TEXTO = (255, 255, 255)
COLOR_HEX = (100, 100, 255)
COLOR_CENTRAL = (255, 100, 100)
COLOR_BOTON = (70, 70, 70)
COLOR_BOTON_TEXTO = (255, 255, 255)
COLOR_CORRECTO = (0, 255, 0)
COLOR_INCORRECTO = (255, 0, 0)


def dibujar_hexagono(surface, color, pos, size, ancho=0):
    puntos = []
    for i in range(6):
        ang = math.radians(60 * i - 30)
        x = pos[0] + size * math.cos(ang)
        y = pos[1] + size * math.sin(ang)
        puntos.append((x, y))
    pygame.draw.polygon(surface, color, puntos, ancho)
    return puntos


def iniciar_hexalink(estado, usuario):
    pygame.display.set_caption("HexaLink")
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    reloj = pygame.time.Clock()

    letras = estado["letras"]
    central = estado["central"]
    palabras_objetivo = estado["palabras_objetivo"]
    encontradas = estado.get("encontradas", [])
    tiempo_jugado = estado.get("tiempo", 0)

    letra_actual = ""
    inicio_tiempo = time.time()
    mensaje = ""
    color_mensaje = COLOR_CORRECTO
    tiempo_mensaje = 0
    hex_positions = {}

    def calcular_tiempo():
        total = int(tiempo_jugado + (time.time() - inicio_tiempo))
        minutos = total // 60
        segundos = total % 60
        return f"Tiempo: {minutos:02}:{segundos:02}"

    def dibujar_letras():
        pantalla.fill(COLOR_FONDO)
        angulo = 0
        paso = 360 / 6
        for i, letra in enumerate(letras):
            if letra == central:
                pos = CENTRO
                color = COLOR_CENTRAL
            else:
                rad = math.radians(angulo)
                dx = math.cos(rad) * HEX_SIZE * 2
                dy = math.sin(rad) * HEX_SIZE * 2
                pos = (CENTRO[0] + dx, CENTRO[1] + dy)
                color = COLOR_HEX
                angulo += paso
            puntos = dibujar_hexagono(pantalla, color, pos, HEX_SIZE, ancho=0)
            hex_positions[letra] = puntos
            txt = FUENTE.render(letra.upper(), True, COLOR_TEXTO)
            rect = txt.get_rect(center=pos)
            pantalla.blit(txt, rect)

    def dentro_hexagono(puntos, pos):
        return pygame.draw.polygon(pantalla, (0,0,0), puntos).collidepoint(pos)

    def dibujar_botonera():
        botones = ["Pausar", "Records", "Guardar", "Salir"]
        for i, texto in enumerate(botones):
            x = 20 + i * 120
            y = 20
            pygame.draw.rect(pantalla, COLOR_BOTON, (x, y, 100, 40))
            t = FUENTE.render(texto, True, COLOR_BOTON_TEXTO)
            pantalla.blit(t, (x + 10, y + 8))

    def dibujar_derecha():
        porcentaje = (len(encontradas) / len(palabras_objetivo)) * 100
        txt = FUENTE.render(f"Progreso: {porcentaje:.1f}%", True, COLOR_TEXTO)
        pantalla.blit(txt, (750, 50))

        agrupadas = defaultdict(list)
        for palabra in encontradas:
            agrupadas[palabra[0].upper()].append(palabra)

        y = 90
        for letra, lista in sorted(agrupadas.items()):
            header = FUENTE.render(f"{letra}: ({len(lista)}/{sum(p.startswith(letra.lower()) for p in palabras_objetivo)})", True, COLOR_TEXTO)
            pantalla.blit(header, (700, y))
            y += 30
            detalle = FUENTE.render(", ".join([p.capitalize() for p in lista]), True, COLOR_TEXTO)
            pantalla.blit(detalle, (700, y))
            y += 30

    def dibujar_palabra_actual(palabra):
        txt = FUENTE.render(f"Palabra: {palabra.upper()}", True, COLOR_TEXTO)
        pantalla.blit(txt, (20, ALTO - 40))

    def dibujar_mensaje():
        nonlocal mensaje, tiempo_mensaje
        if mensaje and time.time() - tiempo_mensaje < 2:
            txt = FUENTE_GRANDE.render(mensaje, True, color_mensaje)
            pantalla.blit(txt, (ANCHO // 2 - txt.get_width() // 2, 20))
        else:
            mensaje = ""

    ejecutando = True
    while ejecutando:
        pantalla.fill(COLOR_FONDO)
        dibujar_letras()
        dibujar_botonera()
        dibujar_palabra_actual(letra_actual)
        dibujar_derecha()
        dibujar_mensaje()
        txt_tiempo = FUENTE.render(calcular_tiempo(), True, COLOR_TEXTO)
        pantalla.blit(txt_tiempo, (20, ALTO - 70))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_BACKSPACE:
                    letra_actual = letra_actual[:-1]
                elif evento.key == pygame.K_RETURN:
                    if len(letra_actual) >= 3 and central in letra_actual and letra_actual in palabras_objetivo and letra_actual not in encontradas:
                        encontradas.append(letra_actual)
                        mensaje = "\u00a1Correcto!"
                        color_mensaje = COLOR_CORRECTO
                    else:
                        mensaje = "\u00a1Incorrecto!"
                        color_mensaje = COLOR_INCORRECTO
                    tiempo_mensaje = time.time()
                    letra_actual = ""
                else:
                    letra = evento.unicode.lower()
                    if letra in letras:
                        letra_actual += letra
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                x, y = evento.pos
                if 20 <= y <= 60:
                    if 20 <= x <= 120:
                        ejecutando = False  # Simula pausar
                    elif 140 <= x <= 240:
                        pass
                    elif 260 <= x <= 360:
                        estado["tiempo"] = int(tiempo_jugado + (time.time() - inicio_tiempo))
                        estado["encontradas"] = encontradas
                        guardar_partida(usuario, estado)
                    elif 380 <= x <= 480:
                        ejecutando = False
                else:
                    for letra, puntos in hex_positions.items():
                        if dentro_hexagono(puntos, evento.pos):
                            letra_actual += letra

        reloj.tick(30)

    estado["tiempo"] = int(tiempo_jugado + (time.time() - inicio_tiempo))
    estado["encontradas"] = encontradas
    return estado
