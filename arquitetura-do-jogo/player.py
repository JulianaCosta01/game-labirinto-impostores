# =============================================================================
# player.py: Módulo do Jogador e Projéteis
# =============================================================================


import pygame
import math
from config import (
    VELOCIDADE_JOGADOR, TAMANHO_JOGADOR,
    COOLDOWN_DISPARO, VELOCIDADE_PROJETIL, VIDA_PROJETIL,
    DURACAO_POWERUP, COR_JOGADOR, COR_JOGADOR_GUN
)
from tilemap import Labirinto


class Jogador:
    def __init__(self, coluna_inicio, linha_inicio):
        # Posição inicial do jogador
        self.x, self.y = Labirinto.tile_para_pixel_centro(coluna_inicio, linha_inicio)

        # Estado do jogador
        self.angulo    = 0.0
        self.vivo      = True
        self.tamanho   = TAMANHO_JOGADOR

        # Controle de disparo
        self.tempo_ultimo_disparo = 0

        # Timers dos power-ups
        self.powerups = {"velocidade": 0, "duplo": 0, "escudo": 0, "congelar": 0}

        # Estatísticas
        self.total_disparos = 0
        self.acertos        = 0

    def atualizar(self, teclas, pos_mouse, dt, projeteis, labirinto):
        """
        Atualiza movimento, rotação, power-ups e disparos do jogador.
        """
        if not self.vivo:
            return

        # Atualiza duração dos power-ups
        self._decrementar_powerups(dt)

        # Ajusta velocidade se houver boost
        velocidade = VELOCIDADE_JOGADOR * (
            1.7 if self.powerups["velocidade"] > 0 else 1.0
        )

        dx, dy = 0.0, 0.0

        # Entrada de movimento
        if teclas[pygame.K_LEFT]  or teclas[pygame.K_a]: dx -= 1
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: dx += 1
        if teclas[pygame.K_UP]    or teclas[pygame.K_w]: dy -= 1
        if teclas[pygame.K_DOWN]  or teclas[pygame.K_s]: dy += 1

        # Normaliza movimento diagonal
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        # Move com colisão e deslize
        self._mover_com_deslize(dx * velocidade, dy * velocidade, labirinto)

        # Rotação em direção ao mouse
        self.angulo = math.atan2(
            pos_mouse[1] - self.y,
            pos_mouse[0] - self.x
        )

        # Disparo
        botoes = pygame.mouse.get_pressed()
        if botoes[0] or teclas[pygame.K_SPACE]:
            self._tentar_disparar(projeteis)

    def _decrementar_powerups(self, dt):
        """
        Reduz o tempo restante dos power-ups ativos.
        """
        for tipo in self.powerups:
            if self.powerups[tipo] > 0:
                self.powerups[tipo] = max(0, self.powerups[tipo] - dt)

    def _mover_com_deslize(self, dx, dy, labirinto):
        """
        Move o jogador aplicando colisão e efeito de deslize.
        """
        # Movimento completo
        novo_x, novo_y = self.x + dx, self.y + dy

        if not labirinto.circulo_colide_parede(novo_x, novo_y, self.tamanho):
            self.x, self.y = novo_x, novo_y
            return

        # Tenta mover apenas no eixo X
        novo_x = self.x + dx
        if not labirinto.circulo_colide_parede(novo_x, self.y, self.tamanho):
            self.x = novo_x

        # Tenta mover apenas no eixo Y
        novo_y = self.y + dy
        if not labirinto.circulo_colide_parede(self.x, novo_y, self.tamanho):
            self.y = novo_y

    def _tentar_disparar(self, projeteis):
        """
        Cria projéteis respeitando o cooldown de disparo.
        """
        agora = pygame.time.get_ticks()

        if agora - self.tempo_ultimo_disparo < COOLDOWN_DISPARO:
            return

        self.tempo_ultimo_disparo = agora
        self.total_disparos += 1

        # Disparo duplo
        if self.powerups["duplo"] > 0:
            desl = 4

            px = -math.sin(self.angulo) * desl
            py =  math.cos(self.angulo) * desl

            projeteis.append(
                Projetil(self.x + px, self.y + py, self.angulo)
            )
            projeteis.append(
                Projetil(self.x - px, self.y - py, self.angulo)
            )

        # Disparo simples
        else:
            projeteis.append(
                Projetil(self.x, self.y, self.angulo)
            )

    def ativar_powerup(self, tipo):
        """
        Ativa ou renova power-up
        """
        if tipo in self.powerups:
            self.powerups[tipo] = DURACAO_POWERUP

    def desenhar(self, tela):
        """
        Desenha o jogador e seus efeitos visuais.
        """
        if not self.vivo:
            return

        tamanho = self.tamanho

        # Efeito visual do escudo
        if self.powerups["escudo"] > 0:
            pygame.draw.circle(
                tela,
                (0, 150, 200),
                (int(self.x), int(self.y)),
                tamanho + 8,
                2
            )

        # Modelo triangular da nave
        pontos_locais = [
            (0, -tamanho * 1.1),
            (-tamanho * 0.65, tamanho * 0.75),
            (tamanho * 0.65, tamanho * 0.75),
        ]

        # Rotaciona modelo
        cos_a = math.cos(self.angulo + math.pi / 2)
        sin_a = math.sin(self.angulo + math.pi / 2)

        pontos_mundo = [
            (
                lx * cos_a - ly * sin_a + self.x,
                lx * sin_a + ly * cos_a + self.y
            )
            for lx, ly in pontos_locais
        ]

        # Brilho do jogador
        glow = pygame.Surface(
            (tamanho * 4, tamanho * 4),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            glow,
            (0, 212, 255, 40),
            (tamanho * 2, tamanho * 2),
            tamanho * 2
        )

        tela.blit(
            glow,
            (int(self.x) - tamanho * 2,
             int(self.y) - tamanho * 2)
        )

        # Desenha jogador
        pygame.draw.polygon(tela, COR_JOGADOR_GUN, pontos_mundo)
        pygame.draw.polygon(tela, COR_JOGADOR, pontos_mundo)
        pygame.draw.polygon(tela, (180, 240, 255), pontos_mundo, 1)

        # Centro do jogador
        pygame.draw.circle(
            tela,
            (200, 255, 255),
            (int(self.x), int(self.y)),
            2
        )

    @property
    def tem_escudo(self):
        # Indica se o escudo está ativo
        return self.powerups["escudo"] > 0

    @property
    def precisao(self):
        # Calcula taxa de acerto
        if self.total_disparos == 0:
            return 0

        return int(
            self.acertos /
            self.total_disparos * 100
        )


class Projetil:
    def __init__(self, x, y, angulo):
        """
        Inicializa um projétil na posição e direção informadas.
        """
        # Posição inicial
        self.x = x
        self.y = y

        # Velocidade baseada no ângulo
        self.vel_x = math.cos(angulo) * VELOCIDADE_PROJETIL
        self.vel_y = math.sin(angulo) * VELOCIDADE_PROJETIL

        # Tempo de vida
        self.vida = VIDA_PROJETIL
        self.ativo = True

    def atualizar(self):
        # Atualiza posição
        self.x += self.vel_x
        self.y += self.vel_y

        # Consome vida
        self.vida -= 0.02

        # Colisão com parede
        col, lin = Labirinto.pixel_para_tile(self.x, self.y)

        if Labirinto.e_parede(col, lin):
            self.ativo = False
            return

        # Remove ao expirar
        if self.vida <= 0:
            self.ativo = False

    def desenhar(self, tela):
        """
        Desenha o projétil e seu efeito de brilho.
        """
        if not self.ativo:
            return

        # Intensidade do brilho
        opacidade = int(self.vida * 255)

        # Glow do projétil
        glow = pygame.Surface((14, 14), pygame.SRCALPHA)

        pygame.draw.circle(
            glow,
            (*COR_JOGADOR, opacidade // 3),
            (7, 7),
            7
        )

        tela.blit(glow, (int(self.x) - 7, int(self.y) - 7))

        # Corpo do projétil
        pygame.draw.circle(
            tela,
            COR_JOGADOR,
            (int(self.x), int(self.y)),
            3
        )

        pygame.draw.circle(
            tela,
            (200, 255, 255),
            (int(self.x), int(self.y)),
            1
        )