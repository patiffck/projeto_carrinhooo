import pygame
import math


PISTAS = [
    {
        "nome":        "NEON CITY",
        "cor":         (0, 255, 200),       
        "fundo":       (5, 5, 16),         
        "cor_linha":   (0, 255, 200, 40),   
        "pontos": [
            (120, 100), (680, 100), (730, 150),
            (730, 290), (680, 330), (500, 330),
            (500, 430), (680, 430), (730, 470),
            (730, 560), (680, 600), (120, 600),
            (70,  560), (70,  150), (120, 100),
        ],
        "largura":     52,
        "voltas":      3,
        "dificuldade": "FACIL",
    },
    {
        "nome":        "DESERT RUN",
        "cor":         (255, 170, 0),      
        "fundo":       (18, 12, 5),         
        "cor_linha":   (255, 170, 0, 40),
        "pontos": [
            (100, 80),  (410, 80),  (510, 130),
            (710, 80),  (760, 200), (710, 310),
            (610, 285), (555, 405), (710, 490),
            (710, 570), (100, 570), (55,  455),
            (205, 355), (75,  250), (100, 80),
        ],
        "largura":     46,
        "voltas":      3,
        "dificuldade": "MEDIO",
    },
    {
        "nome":        "ICEBLAZE",
        "cor":         (96, 208, 255),      
        "fundo":       (5, 8, 20),         
        "cor_linha":   (96, 208, 255, 40),
        "pontos": [
            (120, 55),  (710, 55),  (760, 100),
            (760, 210), (605, 245), (655, 350),
            (760, 385), (760, 510), (710, 550),
            (505, 550), (405, 465), (305, 550),
            (100, 550), (45,  505), (45,  100),
            (120, 55),
        ],
        "largura":     42,
        "voltas":      4,
        "dificuldade": "DIFICIL",
    },
]

def desenhar_pista(tela, pista):
    pts     = pista["pontos"]
    largura = pista["largura"]
    cor     = pista["cor"]

    _desenhar_segmentos(tela, pts, largura * 2 + 14,
                    (*cor, 30),   
                    arredondado=True)
    
    _desenhar_segmentos(tela, pts, largura * 2,
                        (22, 22, 45),
                        arredondado=True)
    
    _desenhar_segmentos(tela, pts, largura * 2 + 5,
                        (*cor, 60),
                        arredondado=True)
    
    _desenhar_linha_pontilhada(tela, pts, cor)

    _desenhar_largada(tela, pts)

def _desenhar_segmentos(tela, pts, espessura, cor, arredondado=False):
    if len(cor) == 4:  
        surf = pygame.Surface(tela.get_size(), pygame.SRCALPHA)
        for i in range(len(pts) - 1):
            pygame.draw.line(surf, cor, pts[i], pts[i + 1], espessura)
        pygame.draw.line(surf, cor, pts[-1], pts[0], espessura)
        tela.blit(surf, (0, 0))
    else:
        for i in range(len(pts) - 1):
            pygame.draw.line(tela, cor, pts[i], pts[i + 1], espessura)
        pygame.draw.line(tela, cor, pts[-1], pts[0], espessura)

def _desenhar_linha_pontilhada(tela, pts, cor):
    cor_fraca = (cor[0] // 4, cor[1] // 4, cor[2] // 4)
    todos_pts = list(pts) + [pts[0]]  
    for i in range(len(todos_pts) - 1):
        x1, y1 = todos_pts[i]
        x2, y2 = todos_pts[i + 1]
        dist   = math.hypot(x2 - x1, y2 - y1)
        passos = int(dist // 20) 

        for j in range(passos):
            if j % 2 == 0:
                t1 = j / passos
                t2 = (j + 1) / passos
                px1 = int(x1 + (x2 - x1) * t1)
                py1 = int(y1 + (y2 - y1) * t1)
                px2 = int(x1 + (x2 - x1) * t2)
                py2 = int(y1 + (y2 - y1) * t2)
                pygame.draw.line(tela, cor_fraca, (px1, py1), (px2, py2), 2)

def _desenhar_largada(tela, pts):
    if len(pts) < 2:
        return
 
    x1, y1 = pts[0]
    x2, y2 = pts[1]

    angulo = math.atan2(y2 - y1, x2 - x1)

    perp_x = -math.sin(angulo)
    perp_y =  math.cos(angulo)

    tam  = 12
    qtd  = 5
    for i in range(-qtd, qtd):
        cor_quad = (255, 255, 255) if i % 2 == 0 else (30, 30, 30)
        
        cx = x1 + perp_x * (i * tam)
        cy = y1 + perp_y * (i * tam)
       
        dir_x = math.cos(angulo) * tam
        dir_y = math.sin(angulo) * tam
        pontos_quad = [
            (cx - perp_x * tam // 2 - dir_x // 2,
             cy - perp_y * tam // 2 - dir_y // 2),
            (cx + perp_x * tam // 2 - dir_x // 2,
             cy + perp_y * tam // 2 - dir_y // 2),
            (cx + perp_x * tam // 2 + dir_x // 2,
             cy + perp_y * tam // 2 + dir_y // 2),
            (cx - perp_x * tam // 2 + dir_x // 2,
             cy - perp_y * tam // 2 + dir_y // 2),
        ]
        pygame.draw.polygon(tela, cor_quad, pontos_quad)

def esta_na_pista(x, y, pista):
    pts     = pista["pontos"]
    largura = pista["largura"]
 
    todos = list(pts) + [pts[0]]  
 
    for i in range(len(todos) - 1):
        ax, ay = todos[i]
        bx, by = todos[i + 1]
 
        dx = bx - ax
        dy = by - ay
        len2 = dx * dx + dy * dy  
 
        if len2 == 0:
            continue

        t = ((x - ax) * dx + (y - ay) * dy) / len2
        t = max(0.0, min(1.0, t)) 

        qx = ax + t * dx
        qy = ay + t * dy

        dist = math.hypot(x - qx, y - qy)
 
        if dist < largura + 6:
            return True
 
    return False

def desenhar_minimap(tela, pista, carro_x, carro_y, pos_x, pos_y, tamanho=110):
    pts = pista["pontos"]
    cor = pista["cor"]

    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    margem = 10
    area   = tamanho - margem * 2

    escala = min(area / (max_x - min_x), area / (max_y - min_y))

    def mapear(px, py): 
        mx = int((px - min_x) * escala + pos_x + margem + (area - (max_x - min_x) * escala) / 2)
        my = int((py - min_y) * escala + pos_y + margem + (area - (max_y - min_y) * escala) / 2)
        return mx, my
    
    fundo_surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
    pygame.draw.rect(fundo_surf, (0, 0, 0, 160), (0, 0, tamanho, tamanho), border_radius=8)
    tela.blit(fundo_surf, (pos_x, pos_y))

    pygame.draw.rect(tela, (*cor, 80), (pos_x, pos_y, tamanho, tamanho),
                     width=1, border_radius=8)
    
    pts_map = [mapear(p[0], p[1]) for p in pts]
    if len(pts_map) > 1:
        pygame.draw.lines(tela, (*cor, 120), True, pts_map, 3)

    cx, cy = mapear(carro_x, carro_y)
    pygame.draw.circle(tela, cor, (cx, cy), 5)
    
    halo = pygame.Surface((20, 20), pygame.SRCALPHA)
    pygame.draw.circle(halo, (*cor, 60), (10, 10), 9)
    tela.blit(halo, (cx - 10, cy - 10))

