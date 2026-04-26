# ==============================================================
# hud.py  —  INTERFACE DO JOGO (HUD)
# ==============================================================
# HUD = Heads-Up Display (tudo que aparece sobre o jogo:
# tempo, volta, recorde, barra de velocidade, etc.)
# ==============================================================

import pygame


# ==============================================================
# CORES USADAS NO HUD
# ==============================================================
BRANCO      = (255, 255, 255)
PRETO       = (0,   0,   0)
CIANO       = (0,   255, 200)
VERMELHO    = (255, 64,  96)
AMARELO     = (255, 215, 0)
CINZA_CLARO = (180, 180, 180)


# ==============================================================
# FUNÇÃO AUXILIAR: formatar tempo
# ==============================================================

def formatar_tempo(ms):
    """
    Converte milissegundos em texto legível: 'M:SS.mmm'

    Exemplos:
        65000  → '1:05.000'
        3752   → '0:03.752'
        -1     → '--:--.---'
    """
    if ms < 0:
        return "--:--.---"
    minutos    = ms // 60000
    segundos   = (ms % 60000) // 1000
    milisegund = ms % 1000
    return f"{minutos}:{segundos:02d}.{milisegund:03d}"


# ==============================================================
# CLASSE HUD
# ==============================================================

class HUD:
    """
    Gerencia e desenha todos os elementos da interface em jogo.
    """

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura  = altura

        # ----------------------------------------------------------
        # FONTES
        # Pygame carrega fontes do sistema. Usamos None = fonte padrão
        # Se quiser usar fonte personalizada:
        #   pygame.font.Font("caminho/fonte.ttf", tamanho)
        # ----------------------------------------------------------
        self.fonte_pequena  = pygame.font.SysFont("consolas", 13, bold=True)
        self.fonte_media    = pygame.font.SysFont("consolas", 20, bold=True)
        self.fonte_grande   = pygame.font.SysFont("consolas", 30, bold=True)
        self.fonte_gigante  = pygame.font.SysFont("consolas", 52, bold=True)
        self.fonte_titulo   = pygame.font.SysFont("consolas", 42, bold=True)

        # Estado de "piscada" do HUD ao completar volta
        self._piscar_timer  = 0
        self._piscar_ligado = False

    # ==========================================================
    # DESENHAR HUD EM JOGO
    # ==========================================================

    def desenhar_jogo(self, tela, tempo_ms, volta_texto, recorde_ms,
                      velocidade_pct, cor_pista):
        """
        Desenha todos os elementos do HUD durante a corrida.

        Parâmetros:
            tempo_ms       → tempo atual da corrida em ms
            volta_texto    → ex: 'VOLTA 2 / 3'
            recorde_ms     → recorde salvo em ms (-1 se não houver)
            velocidade_pct → float de 0.0 a 1.0
            cor_pista      → cor RGB da pista atual
        """
        self._desenhar_caixa_tempo(tela, tempo_ms, cor_pista)
        self._desenhar_caixa_volta(tela, volta_texto, cor_pista)
        self._desenhar_caixa_recorde(tela, recorde_ms, cor_pista)
        self._desenhar_barra_velocidade(tela, velocidade_pct)
        self._desenhar_controles(tela)

    def _caixa_hud(self, tela, x, y, largura, altura, cor):
        """Desenha uma caixinha semitransparente para o HUD."""
        surf = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*cor, 18), (0, 0, largura, altura), border_radius=8)
        pygame.draw.rect(surf, (*cor, 65), (0, 0, largura, altura),
                         width=1, border_radius=8)
        tela.blit(surf, (x, y))

    def _desenhar_caixa_tempo(self, tela, tempo_ms, cor):
        """Caixa superior esquerda: tempo atual."""
        self._caixa_hud(tela, 12, 12, 180, 52, cor)
        # Label pequeno
        label = self.fonte_pequena.render("TEMPO", True, (*cor, 130))
        tela.blit(label, (22, 18))
        # Valor grande
        # Pisca vermelho ao completar volta
        cor_val = VERMELHO if self._piscar_ligado else cor
        val = self.fonte_media.render(formatar_tempo(tempo_ms), True, cor_val)
        tela.blit(val, (22, 32))

    def _desenhar_caixa_volta(self, tela, volta_texto, cor):
        """Caixa superior centro: número da volta."""
        cx = self.largura // 2
        self._caixa_hud(tela, cx - 90, 12, 180, 52, cor)
        label = self.fonte_pequena.render("CORRIDA", True, (*cor, 130))
        tela.blit(label, (cx - 80, 18))
        val = self.fonte_media.render(volta_texto, True, cor)
        tela.blit(val, (cx - 80, 32))

    def _desenhar_caixa_recorde(self, tela, recorde_ms, cor):
        """Caixa superior direita: recorde da pista."""
        self._caixa_hud(tela, self.largura - 192, 12, 180, 52, cor)
        label = self.fonte_pequena.render("RECORDE", True, (*cor, 130))
        tela.blit(label, (self.largura - 182, 18))
        texto_rec = formatar_tempo(recorde_ms) if recorde_ms >= 0 else "--:--.---"
        val = self.fonte_media.render(texto_rec, True, cor)
        tela.blit(val, (self.largura - 182, 32))

    def _desenhar_barra_velocidade(self, tela, pct):
        """Barra de velocidade na parte inferior central."""
        bw = 160
        bh = 6
        bx = self.largura // 2 - bw // 2
        by = self.altura - 28

        # Label
        label = self.fonte_pequena.render("VELOCIDADE", True, (80, 120, 100))
        tela.blit(label, (bx, by - 16))

        # Trilho (fundo)
        pygame.draw.rect(tela, (30, 40, 35), (bx, by, bw, bh), border_radius=3)

        # Preenchimento: cor muda de verde → vermelho conforme sobe
        if pct > 0:
            fill_w = int(bw * pct)
            # Interpolação de cor: (0, 255, 200) → (255, 64, 96)
            r = int(0   + (255 - 0)   * pct)
            g = int(255 + (64  - 255) * pct)
            b = int(200 + (96  - 200) * pct)
            pygame.draw.rect(tela, (r, g, b), (bx, by, fill_w, bh), border_radius=3)

    def _desenhar_controles(self, tela):
        """Dica de controles no canto inferior esquerdo."""
        teclas = ["↑", "↓", "←", "→"]
        x = 14
        y = self.altura - 36
        for tecla in teclas:
            surf = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.rect(surf, (0, 255, 200, 25), (0, 0, 24, 24), border_radius=4)
            pygame.draw.rect(surf, (0, 255, 200, 70), (0, 0, 24, 24),
                             width=1, border_radius=4)
            tela.blit(surf, (x, y))
            t = self.fonte_pequena.render(tecla, True, (0, 200, 160))
            tela.blit(t, (x + 6, y + 5))
            x += 30
        hint = self.fonte_pequena.render("CONTROLES", True, (40, 80, 65))
        tela.blit(hint, (x + 4, y + 5))

    # ==========================================================
    # EFEITO DE PISCAR (ao completar volta)
    # ==========================================================

    def iniciar_piscar(self):
        """Ativa o efeito de piscar do tempo."""
        self._piscar_timer  = 6   # frames que vai piscar
        self._piscar_ligado = True

    def atualizar_piscar(self):
        """Chama todo frame para atualizar o estado de piscada."""
        if self._piscar_timer > 0:
            self._piscar_timer  -= 1
            self._piscar_ligado  = (self._piscar_timer % 2 == 0)
        else:
            self._piscar_ligado = False

    # ==========================================================
    # TELA DE CONTAGEM REGRESSIVA
    # ==========================================================

    def desenhar_contagem(self, tela, numero):
        """
        Desenha o número grande da contagem regressiva no centro.
        numero pode ser 3, 2, 1 ou 0 (= 'GO!').
        """
        # Fundo semitransparente
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((5, 5, 16, 180))
        tela.blit(overlay, (0, 0))

        texto = str(numero) if numero > 0 else "GO!"
        cor   = CIANO if numero > 0 else AMARELO

        surface = self.fonte_gigante.render(texto, True, cor)
        rect    = surface.get_rect(center=(self.largura // 2, self.altura // 2))
        tela.blit(surface, rect)

    # ==========================================================
    # TELA DE FIM DE CORRIDA
    # ==========================================================

    def desenhar_fim(self, tela, tempo_total_ms, recorde_ms, novo_recorde):
        """
        Exibe a tela de resultado ao terminar a corrida.
        """
        # Fundo escuro
        overlay = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        overlay.fill((5, 5, 16, 230))
        tela.blit(overlay, (0, 0))

        cx = self.largura  // 2
        cy = self.altura   // 2

        # Sub-título
        sub = self.fonte_pequena.render("CORRIDA CONCLUÍDA", True, (0, 180, 140))
        tela.blit(sub, sub.get_rect(center=(cx, cy - 80)))

        # "TEMPO FINAL"
        titulo = self.fonte_grande.render("TEMPO FINAL", True, CIANO)
        tela.blit(titulo, titulo.get_rect(center=(cx, cy - 50)))

        # Tempo em destaque
        t_surf = self.fonte_gigante.render(formatar_tempo(tempo_total_ms), True, BRANCO)
        tela.blit(t_surf, t_surf.get_rect(center=(cx, cy + 10)))

        # Badge de recorde
        if novo_recorde:
            rec = self.fonte_grande.render("⚡ NOVO RECORDE!", True, AMARELO)
            tela.blit(rec, rec.get_rect(center=(cx, cy + 60)))
        elif recorde_ms >= 0:
            diff = tempo_total_ms - recorde_ms
            diff_txt = f"Recorde: {formatar_tempo(recorde_ms)}  |  +{formatar_tempo(diff)}"
            diff_s = self.fonte_pequena.render(diff_txt, True, (100, 140, 120))
            tela.blit(diff_s, diff_s.get_rect(center=(cx, cy + 60)))

        # Instruções
        op1 = self.fonte_pequena.render("[R] TENTAR NOVAMENTE", True, (0, 200, 160))
        op2 = self.fonte_pequena.render("[ESC] VOLTAR AO MENU",  True, (0, 200, 160))
        tela.blit(op1, op1.get_rect(center=(cx, cy + 100)))
        tela.blit(op2, op2.get_rect(center=(cx, cy + 122)))

    # ==========================================================
    # TELA DE MENU PRINCIPAL
    # ==========================================================

    def desenhar_menu(self, tela, pistas, pista_sel, recordes):
        """
        Desenha a tela de seleção de pista / menu inicial.
        """
        # Fundo
        tela.fill((5, 5, 16))
        self._desenhar_grade_fundo(tela, (0, 255, 200))

        cx = self.largura // 2

        # Título
        t1 = self.fonte_titulo.render("TURBOX", True, (0, 255, 200))
        t2 = self.fonte_titulo.render("Racing", True, (255, 64, 96))
        tela.blit(t1, t1.get_rect(center=(cx - 50, 70)))
        tela.blit(t2, t2.get_rect(center=(cx + 55, 70)))

        sub = self.fonte_pequena.render("RACING CIRCUIT — SELECIONE UMA PISTA", True, (40, 100, 80))
        tela.blit(sub, sub.get_rect(center=(cx, 110)))

        # Botões de pista
        btn_w, btn_h = 200, 80
        total_w = len(pistas) * btn_w + (len(pistas) - 1) * 20
        start_x = cx - total_w // 2

        for i, pista in enumerate(pistas):
            bx = start_x + i * (btn_w + 20)
            by = 150
            sel = (i == pista_sel)
            cor_p = pista["cor"]

            # Fundo do botão
            surf_btn = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            alpha_fundo = 50 if sel else 15
            pygame.draw.rect(surf_btn, (*cor_p, alpha_fundo),
                             (0, 0, btn_w, btn_h), border_radius=10)
            alpha_borda = 200 if sel else 60
            pygame.draw.rect(surf_btn, (*cor_p, alpha_borda),
                             (0, 0, btn_w, btn_h), width=2 if sel else 1, border_radius=10)
            tela.blit(surf_btn, (bx, by))

            # Texto do botão
            nome_s = self.fonte_media.render(pista["nome"], True, cor_p)
            diff_s = self.fonte_pequena.render(pista["dificuldade"], True,
                                               (*cor_p[:3], 150))
            rec_ms = recordes.get(pista["nome"], -1)
            rec_s  = self.fonte_pequena.render(
                formatar_tempo(rec_ms) if rec_ms >= 0 else "SEM RECORDE",
                True, (100, 160, 130)
            )
            tela.blit(nome_s, nome_s.get_rect(center=(bx + btn_w // 2, by + 22)))
            tela.blit(diff_s, diff_s.get_rect(center=(bx + btn_w // 2, by + 45)))
            tela.blit(rec_s,  rec_s.get_rect( center=(bx + btn_w // 2, by + 64)))

        # Tabela de recordes
        # IMPORTANTE: pygame.draw.rect não suporta alpha direto na tela.
        # Criamos uma Surface separada com SRCALPHA para ter transparência.
        ry      = 265
        box_w   = 400
        box_h   = len(pistas) * 28 + 40
        box_x   = cx - 200
        surf_rec = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        pygame.draw.rect(surf_rec, (0, 255, 200, 20),  (0, 0, box_w, box_h), border_radius=10)
        pygame.draw.rect(surf_rec, (0, 255, 200, 70),  (0, 0, box_w, box_h), width=1, border_radius=10)
        tela.blit(surf_rec, (box_x, ry))

        rec_titulo = self.fonte_pequena.render("▶  RECORDES POR PISTA", True, (0, 160, 120))
        tela.blit(rec_titulo, (cx - 185, ry + 10))

        for i, pista in enumerate(pistas):
            rec_ms = recordes.get(pista["nome"], -1)
            ny = ry + 35 + i * 28
            nome_r = self.fonte_pequena.render(pista["nome"], True, (100, 180, 150))
            val_r  = self.fonte_media.render(
                formatar_tempo(rec_ms) if rec_ms >= 0 else "--:--.---",
                True, (0, 255, 200)
            )
            tela.blit(nome_r, (cx - 185, ny))
            tela.blit(val_r,  val_r.get_rect(right=cx + 185, top=ny - 4))

        # Instrução para iniciar
        iy = ry + len(pistas) * 28 + 70
        teclas_txt = self.fonte_pequena.render(
            "← → ESCOLHER PISTA    |    ENTER INICIAR    |    1 / 2 / 3 SELECIONAR",
            True, (40, 100, 80)
        )
        tela.blit(teclas_txt, teclas_txt.get_rect(center=(cx, iy)))

    def _desenhar_grade_fundo(self, tela, cor):
        """Grade sutil de fundo (efeito visual)."""
        surf = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        for x in range(0, self.largura, 40):
            pygame.draw.line(surf, (*cor, 8), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 40):
            pygame.draw.line(surf, (*cor, 8), (0, y), (self.largura, y))
        tela.blit(surf, (0, 0))