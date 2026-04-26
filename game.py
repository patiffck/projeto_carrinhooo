# ==============================================================
# game.py  —  CLASSE PRINCIPAL DO JOGO
# ==============================================================
# Esta classe é o "cérebro" do jogo. Ela:
#   1. Controla os estados (menu, contagem, corrida, fim)
#   2. Conecta todos os outros módulos
#   3. Roda o loop principal (events → update → draw)
#
# ESTADOS DO JOGO:
#   "menu"      → tela de seleção de pista
#   "contagem"  → 3... 2... 1... GO!
#   "corrida"   → jogando
#   "fim"       → tela de resultado
# ==============================================================

import pygame
import time

from pistas      import PISTAS, desenhar_pista, esta_na_pista, desenhar_minimap
from carros       import Carro
from checkpoints import GerenciadorVoltas
from hud         import HUD, formatar_tempo
from recordes    import carregar, verificar_e_salvar


class Game:
    """
    Classe central do jogo. Criada no main.py.
    """

    FPS = 60   # frames por segundo desejados

    def __init__(self, tela, largura, altura):
        self.tela    = tela
        self.largura = largura
        self.altura  = altura
        self.clock   = pygame.time.Clock()   # controla o FPS

        # Carrega os recordes salvos do disco
        self.recordes = carregar()

        # Cria os módulos
        self.hud = HUD(largura, altura)

        # Estado inicial
        self.estado    = "menu"
        self.pista_sel = 0    # índice da pista selecionada

        # Objetos que serão criados ao iniciar a corrida
        self.carro     = None
        self.gv        = None   # GerenciadorVoltas

        # Tempo
        self.tempo_inicio    = 0    # timestamp (ms) do início da corrida
        self.tempo_total     = 0    # tempo final da corrida

        # Contagem regressiva
        self.contagem_num    = 3    # começa em 3
        self.contagem_inicio = 0    # quando começou

        # Resultado da corrida
        self.novo_recorde = False

    # ==========================================================
    # LOOP PRINCIPAL
    # Roda indefinidamente até o jogador fechar o jogo.
    # ==========================================================

    def rodar(self):
        """Loop principal: events → update → draw, 60x por segundo."""
        rodando = True
        while rodando:
            # 1. Limita a 60 FPS
            self.clock.tick(self.FPS)

            # 2. Processa eventos (teclado, fechar janela, etc.)
            rodando = self._processar_eventos()

            # 3. Atualiza a lógica do estado atual
            self._atualizar()

            # 4. Desenha tudo na tela
            self._desenhar()

            # 5. Exibe o frame desenhado
            pygame.display.flip()

    # ==========================================================
    # PROCESSAMENTO DE EVENTOS
    # ==========================================================

    def _processar_eventos(self):
        """
        Lê a fila de eventos do Pygame.
        Retorna False se o jogador quiser fechar o jogo.
        """
        for evento in pygame.event.get():

            # Fechou a janela → sai
            if evento.type == pygame.QUIT:
                return False

            # Tecla pressionada
            if evento.type == pygame.KEYDOWN:
                self._tecla_pressionada(evento.key)

        return True   # continua rodando

    def _tecla_pressionada(self, tecla):
        """Reage a teclas específicas conforme o estado atual."""

        # ------ MENU ------
        if self.estado == "menu":
            if tecla == pygame.K_LEFT:
                self.pista_sel = (self.pista_sel - 1) % len(PISTAS)
            elif tecla == pygame.K_RIGHT:
                self.pista_sel = (self.pista_sel + 1) % len(PISTAS)
            elif tecla == pygame.K_1:
                self.pista_sel = 0
            elif tecla == pygame.K_2:
                self.pista_sel = 1
            elif tecla == pygame.K_3:
                self.pista_sel = 2
            elif tecla in (pygame.K_RETURN, pygame.K_SPACE):
                self._iniciar_contagem()
            elif tecla == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

        # ------ FIM ------
        elif self.estado == "fim":
            if tecla == pygame.K_r:
                self._iniciar_contagem()   # tenta de novo
            elif tecla == pygame.K_ESCAPE:
                self.estado = "menu"

        # ------ CORRIDA ------
        elif self.estado == "corrida":
            if tecla == pygame.K_ESCAPE:
                self.estado = "menu"

    # ==========================================================
    # INICIAR CORRIDA
    # ==========================================================

    def _iniciar_contagem(self):
        """Prepara tudo e começa a contagem regressiva."""
        pista = PISTAS[self.pista_sel]

        # Cria o carro e o posiciona na largada
        self.carro = Carro(0, 0)
        self.carro.posicionar_largada(pista)

        # Cria o gerenciador de voltas
        self.gv = GerenciadorVoltas(pista)

        # Inicia a contagem
        self.contagem_num    = 3
        self.contagem_inicio = pygame.time.get_ticks()
        self.estado          = "contagem"

    # ==========================================================
    # ATUALIZAÇÃO DA LÓGICA
    # ==========================================================

    def _atualizar(self):
        """Atualiza a lógica conforme o estado atual."""

        if self.estado == "contagem":
            self._atualizar_contagem()

        elif self.estado == "corrida":
            self._atualizar_corrida()

        # Atualiza o piscar do HUD (ativo em qualquer estado)
        self.hud.atualizar_piscar()

    def _atualizar_contagem(self):
        """
        A contagem regressiva usa o tempo real para avançar:
        a cada 900ms, decrementa o número.
        Sequência: 3 → 2 → 1 → 0 (GO!) → inicia corrida
        """
        agora   = pygame.time.get_ticks()
        passado = agora - self.contagem_inicio

        # Calcula o número atual (3, 2, 1, 0=GO)
        # Após 3600ms (4 × 900ms) a corrida começa
        numero = 3 - int(passado // 900)
        self.contagem_num = max(numero, 0)  # não deixa ir abaixo de 0

        if passado >= 4 * 900:  # 3600ms = fim da contagem
            # Contagem terminou: inicia a corrida!
            self.estado       = "corrida"
            self.tempo_inicio = pygame.time.get_ticks()

    def _atualizar_corrida(self):
        """Atualiza física do carro, checkpoints e HUD."""

        # Lê todas as teclas pressionadas neste frame
        teclas = pygame.key.get_pressed()

        pista     = PISTAS[self.pista_sel]
        na_pista  = esta_na_pista(self.carro.x, self.carro.y, pista)

        # Atualiza o carro
        self.carro.atualizar(teclas, na_pista, self.largura, self.altura)

        # Verifica checkpoints e volta
        agora = pygame.time.get_ticks()
        volta_completa = self.gv.atualizar(self.carro.x, self.carro.y, agora)

        if volta_completa:
            self.hud.iniciar_piscar()

            # Corrida terminou!
            if self.gv.corrida_fim:
                self.tempo_total  = agora - self.tempo_inicio
                nome_pista        = pista["nome"]
                rec_atual         = self.recordes.get(nome_pista, -1)
                self.novo_recorde = verificar_e_salvar(
                    self.recordes, nome_pista, self.tempo_total
                )
                self.estado = "fim"

    # ==========================================================
    # DESENHO
    # ==========================================================

    def _desenhar(self):
        """Chama a função de desenho correta para o estado atual."""

        if self.estado == "menu":
            self.hud.desenhar_menu(self.tela, PISTAS, self.pista_sel, self.recordes)

        elif self.estado == "contagem":
            self._desenhar_corrida()
            if self.contagem_num >= 0:
                self.hud.desenhar_contagem(self.tela, self.contagem_num)

        elif self.estado == "corrida":
            self._desenhar_corrida()

        elif self.estado == "fim":
            self._desenhar_corrida()   # mostra a pista por baixo
            pista     = PISTAS[self.pista_sel]
            rec_atual = self.recordes.get(pista["nome"], -1)
            self.hud.desenhar_fim(
                self.tela,
                self.tempo_total,
                rec_atual,
                self.novo_recorde
            )

    def _desenhar_corrida(self):
        """Desenha fundo, pista, carro, minimap e HUD."""
        pista = PISTAS[self.pista_sel]

        # Fundo
        self.tela.fill(pista["fundo"])
        self._desenhar_grade(pista["cor"])

        # Pista
        desenhar_pista(self.tela, pista)

        # Carro (só se existir)
        if self.carro:
            self.carro.desenhar(self.tela, pista["cor"])

        # HUD em jogo
        if self.estado in ("corrida", "contagem", "fim"):
            tempo_ms = 0
            if self.estado == "corrida":
                tempo_ms = pygame.time.get_ticks() - self.tempo_inicio
            elif self.estado == "fim":
                tempo_ms = self.tempo_total

            rec_ms = self.recordes.get(pista["nome"], -1)
            self.hud.desenhar_jogo(
                self.tela,
                tempo_ms,
                self.gv.progresso_texto if self.gv else "VOLTA 1 / 3",
                rec_ms,
                self.carro.velocidade_percentual if self.carro else 0.0,
                pista["cor"]
            )

        # Minimap
        if self.carro:
            desenhar_minimap(
                self.tela, pista,
                self.carro.x, self.carro.y,
                self.largura - 125, self.altura - 125
            )

    def _desenhar_grade(self, cor):
        """Grade sutil de fundo."""
        surf = pygame.Surface((self.largura, self.altura), pygame.SRCALPHA)
        for x in range(0, self.largura, 40):
            pygame.draw.line(surf, (*cor, 8), (x, 0), (x, self.altura))
        for y in range(0, self.altura, 40):
            pygame.draw.line(surf, (*cor, 8), (0, y), (self.largura, y))
        self.tela.blit(surf, (0, 0))