# ==============================================================
# carro.py  —  CLASSE DO CARRO E FÍSICA
# ==============================================================
# Aqui fica tudo relacionado ao carro:
#   - Posição e ângulo
#   - Física (aceleração, frenagem, curva, atrito)
#   - Rastro visual
#   - Desenho do carro na tela
# ==============================================================

import pygame
import math


class Carro:
    """
    Representa o carro do jogador.

    Atributos principais:
        x, y      → posição no mundo
        angulo    → direção em radianos (0 = direita, π/2 = baixo)
        velocidade→ velocidade atual (px por frame)
        rastro    → lista de posições antigas para o efeito visual
    """

    # ----------------------------------------------------------
    # CONSTANTES DE FÍSICA
    # Experimente mudar esses valores para sentir a diferença!
    # ----------------------------------------------------------
    VELOCIDADE_MAX   = 4.5   # máximo de pixels por frame
    ACELERACAO       = 0.14  # quanto acelera por frame (↑)
    FRENAGEM         = 0.20  # quanto freia por frame (↓)
    ATRITO           = 0.965 # desaceleração natural (0.96 = lento, 0.99 = escorregadio)
    VELOCIDADE_CURVA = 0.048 # ângulo girado por frame (maior = curva mais fechada)

    def __init__(self, x, y, angulo=0):
        # Posição inicial
        self.x      = float(x)
        self.y      = float(y)
        self.angulo = angulo   # em radianos

        # Velocidade começa em zero
        self.velocidade = 0.0

        # Rastro visual: lista de dicts {x, y, alpha}
        self.rastro = []

        # Tamanho do carro para desenho
        self.largura = 22
        self.altura  = 12

    # ==========================================================
    # ATUALIZAÇÃO FÍSICA (chamada todo frame)
    # ==========================================================

    def atualizar(self, teclas, na_pista, largura_tela, altura_tela):
        """
        Atualiza posição e velocidade com base nas teclas pressionadas.

        Parâmetros:
            teclas      → dict de teclas pressionadas (pygame.key.get_pressed)
            na_pista    → bool: se o carro está no asfalto
            largura_tela, altura_tela → limites da janela
        """

        # ----------------------------------------------------------
        # Fora da pista: velocidade máxima reduzida (terra/grama)
        # ----------------------------------------------------------
        fator      = 1.0 if na_pista else 0.45
        vel_max    = self.VELOCIDADE_MAX * (1.0 if na_pista else 0.55)

        # ----------------------------------------------------------
        # ACELERAÇÃO / FRENAGEM
        # ----------------------------------------------------------
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            # Aumenta velocidade até o máximo
            self.velocidade = min(self.velocidade + self.ACELERACAO * fator, vel_max)

        elif teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            # Freia (pode até dar ré: velocidade negativa)
            self.velocidade = max(self.velocidade - self.FRENAGEM, -(vel_max * 0.4))

        else:
            # Sem tecla: atrito desacelera naturalmente
            self.velocidade *= self.ATRITO
            # Se muito lento, para completamente (evita "deslizar")
            if abs(self.velocidade) < 0.05:
                self.velocidade = 0.0

        # ----------------------------------------------------------
        # DIREÇÃO (só vira se estiver em movimento)
        # ----------------------------------------------------------
        if abs(self.velocidade) > 0.2:
            # Fator de curva proporcional à velocidade
            curva = self.VELOCIDADE_CURVA * (self.velocidade / self.VELOCIDADE_MAX)

            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
                self.angulo -= curva
            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
                self.angulo += curva

        # ----------------------------------------------------------
        # MOVIMENTO
        # Decompõe a velocidade em X e Y usando trigonometria:
        #   componente_x = velocidade * cos(angulo)
        #   componente_y = velocidade * sen(angulo)
        # ----------------------------------------------------------
        self.x += math.cos(self.angulo) * self.velocidade
        self.y += math.sin(self.angulo) * self.velocidade

        # ----------------------------------------------------------
        # LIMITES DA TELA (não sai pela borda)
        # ----------------------------------------------------------
        self.x = max(15.0, min(float(largura_tela - 15), self.x))
        self.y = max(15.0, min(float(altura_tela  - 15), self.y))

        # ----------------------------------------------------------
        # RASTRO VISUAL
        # Guarda a posição atual com alpha inicial alto,
        # e vai diminuindo o alpha dos pontos antigos.
        # ----------------------------------------------------------
        if abs(self.velocidade) > 0.4:
            self.rastro.append({
                "x": self.x,
                "y": self.y,
                "alpha": 200
            })

        # Máximo de 30 pontos no rastro
        if len(self.rastro) > 30:
            self.rastro.pop(0)

        # Diminui o alpha de todos os pontos (vai sumindo)
        for ponto in self.rastro:
            ponto["alpha"] = max(0, ponto["alpha"] - 8)

    # ==========================================================
    # DESENHO
    # ==========================================================

    def desenhar(self, tela, cor_pista):
        """
        Desenha o rastro e depois o carro na tela.
        O carro é rotacionado de acordo com seu ângulo.
        """
        self._desenhar_rastro(tela, cor_pista)
        self._desenhar_corpo(tela, cor_pista)

    def _desenhar_rastro(self, tela, cor):
        """Desenha os círculos do rastro com transparência crescente."""
        for i, ponto in enumerate(self.rastro):
            if ponto["alpha"] <= 0:
                continue
            # Tamanho do rastro diminui com a distância
            raio = max(1, int(4 * (i / len(self.rastro))))
            surf = pygame.Surface((raio * 2 + 2, raio * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*cor, ponto["alpha"] // 3),
                (raio + 1, raio + 1),
                raio
            )
            tela.blit(surf, (int(ponto["x"]) - raio, int(ponto["y"]) - raio))

    def _desenhar_corpo(self, tela, cor):
        """
        Desenha o carro como um retângulo rotacionado.
        Usamos uma Surface separada, desenhamos o carro nela,
        e depois rotacionamos com pygame.transform.rotate().
        """
        larg = self.largura
        alt  = self.altura

        # Cria uma surface transparente para o carro
        surf_carro = pygame.Surface((larg + 10, alt + 10), pygame.SRCALPHA)
        cx = (larg + 10) // 2
        cy = (alt  + 10) // 2

        # --- Brilho (halo) ao redor do carro ---
        halo_surf = pygame.Surface((larg + 10, alt + 10), pygame.SRCALPHA)
        pygame.draw.rect(
            halo_surf,
            (*cor, 40),
            (cx - larg // 2 - 3, cy - alt // 2 - 3, larg + 6, alt + 6),
            border_radius=5
        )
        surf_carro.blit(halo_surf, (0, 0))

        # --- Corpo principal do carro ---
        pygame.draw.rect(
            surf_carro,
            cor,
            (cx - larg // 2, cy - alt // 2, larg, alt),
            border_radius=4
        )

        # --- Cockpit (janela escura no meio) ---
        pygame.draw.rect(
            surf_carro,
            (0, 0, 0, 180),
            (cx - 2, cy - alt // 2 + 2, larg // 2, alt - 4),
            border_radius=2
        )

        # --- Rodas (4 retângulos pequenos) ---
        cor_roda = (30, 30, 30)
        rodas = [
            (cx - larg // 2 + 2, cy - alt // 2),      # frente esquerda
            (cx + larg // 2 - 8, cy - alt // 2),      # frente direita
            (cx - larg // 2 + 2, cy + alt // 2 - 3),  # trás esquerda
            (cx + larg // 2 - 8, cy + alt // 2 - 3),  # trás direita
        ]
        for rx, ry in rodas:
            pygame.draw.rect(surf_carro, cor_roda, (rx, ry, 6, 3))

        # --- Faróis (frente do carro) ---
        pygame.draw.rect(surf_carro, (255, 255, 220), (cx + larg // 2 - 3, cy - 3, 4, 2))
        pygame.draw.rect(surf_carro, (255, 255, 220), (cx + larg // 2 - 3, cy + 1, 4, 2))

        # ----------------------------------------------------------
        # ROTAÇÃO
        # Converte o ângulo de radianos para graus (Pygame usa graus)
        # e inverte o sinal porque Pygame rotaciona no sentido anti-horário
        # ----------------------------------------------------------
        graus = -math.degrees(self.angulo)
        surf_rot = pygame.transform.rotate(surf_carro, graus)

        # Centraliza a surface rotacionada no ponto do carro
        rect_rot = surf_rot.get_rect(center=(int(self.x), int(self.y)))
        tela.blit(surf_rot, rect_rot.topleft)

    # ==========================================================
    # PROPRIEDADE: velocidade_percentual
    # Retorna de 0.0 a 1.0 para a barra de velocidade
    # ==========================================================

    @property
    def velocidade_percentual(self):
        return min(1.0, abs(self.velocidade) / self.VELOCIDADE_MAX)

    # ==========================================================
    # POSICIONAR NO INÍCIO DA PISTA
    # ==========================================================

    def posicionar_largada(self, pista):
        """
        Coloca o carro no primeiro ponto da pista,
        apontando para o segundo ponto.
        """
        p0 = pista["pontos"][0]
        p1 = pista["pontos"][1]
        self.x      = float(p0[0])
        self.y      = float(p0[1])
        self.angulo = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        self.velocidade = 0.0
        self.rastro = []