# =============================================================================
# player.py (Jogador e Projéteis)
# =============================================================================


import pygame
import math
from config import (
    PLAYER_SPEED, PLAYER_SIZE, PLAYER_SHOT_COOLDOWN,
    PLAYER_SPEED_BOOST, PLAYER_SPAWN_COL, PLAYER_SPAWN_ROW,
    BULLET_SPEED, BULLET_LIFE, BULLET_DECAY_RATE,
    BULLET_RADIUS, DOUBLE_SHOT_OFFSET,
    POWERUP_DURATION,
    C_PLAYER, C_PLAYER_GUN, C_PLAYER_GLOW, C_PLAYER_CORE,
    C_BULLET, C_BULLET_CORE, C_SHIELD_RING,
)
from tilemap import TileMap


class Player:
    """
    Personagem controlado pelo jogador.

    Estado interno:
        x, y          → posição do centro (pixels)
        angle         → ângulo de mira (radianos; 0 = direita)
        alive         → False quando o jogo termina
        powerups      → dicionário {tipo: ms_restantes}
        total_shots   → total de projéteis disparados (para calcular precisão)
        hits          → projéteis que acertaram inimigos
    """

    # Tipos de power-up válidos e seus valores iniciais
    _POWERUP_DEFAULTS = {
        "speed":  0,   # Velocidade 1.7× por POWERUP_DURATION ms
        "double": 0,   # Dois projéteis por disparo
        "shield": 0,   # Invulnerável a inimigos e zona vermelha
        "freeze": 0,   # Paralisa todos os inimigos e a zona
    }

    def __init__(self, start_col=PLAYER_SPAWN_COL, start_row=PLAYER_SPAWN_ROW):
        self.x, self.y = TileMap.tile_to_pixel_center(start_col, start_row)
        self.angle      = 0.0
        self.alive      = True
        self.size       = PLAYER_SIZE

        self.last_shot_time = 0
        self.powerups       = dict(self._POWERUP_DEFAULTS)   # cópia mutável

        # Estatísticas da partida
        self.total_shots = 0
        self.hits        = 0

    '''
    # 1. ATUALIZAÇÃO — chamado uma vez por frame
    '''

    def update(self, keys, mouse_pos, dt, projeteis):
        """
        Processa input, move o jogador, atualiza mira e dispara.

        Args:
            keys       : pygame.key.get_pressed()
            mouse_pos  : (x, y) do cursor
            dt         : delta time em ms
            projeteis  : lista onde novos Bullet serão adicionados
        """
        if not self.alive:
            return

        self._tick_powerups(dt)
        self._handle_movement(keys)
        self._update_aim(mouse_pos)
        self._handle_shooting(keys, projeteis)

    def _tick_powerups(self, dt):
        """Decrementa o tempo restante de cada power-up ativo."""
        for tipo in self.powerups:
            if self.powerups[tipo] > 0:
                self.powerups[tipo] = max(0, self.powerups[tipo] - dt)

    def _handle_movement(self, keys):
        """Lê as teclas e move o jogador com wall-sliding."""
        velocidade = PLAYER_SPEED * (PLAYER_SPEED_BOOST if self.powerups["speed"] > 0 else 1.0)

        dx, dy = self._get_input_direction(keys)
        if dx != 0 and dy != 0:
            # Normaliza diagonal para evitar velocidade ~41% maior
            fator = math.sqrt(2)
            dx   /= fator
            dy   /= fator

        self._move_with_slide(dx * velocidade, dy * velocidade)

    @staticmethod
    def _get_input_direction(keys):
        """Retorna o vetor de direção bruto (dx, dy) a partir das teclas."""
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN]  or keys[pygame.K_s]) - (keys[pygame.K_UP]   or keys[pygame.K_w])
        return float(dx), float(dy)

    def _move_with_slide(self, dx, dy):
        """
        Move o jogador aplicando wall-sliding nos dois eixos.

        Tenta mover combinado primeiro. SE COLIDIR:
          - Tenta apenas o eixo X (desliza verticalmente na parede)
          - Tenta apenas o eixo Y (desliza horizontalmente na parede)
        Isso evita que o jogador trave completamente ao encostar em cantos.
        """
        novo_x = self.x + dx
        novo_y = self.y + dy

        # Movimento combinado (caso ideal — sem colisão)
        if not TileMap.circle_collides_wall(novo_x, novo_y, self.size):
            self.x, self.y = novo_x, novo_y
            return

        # Slide no eixo X
        if not TileMap.circle_collides_wall(novo_x, self.y, self.size):
            self.x = novo_x

        # Slide no eixo Y
        if not TileMap.circle_collides_wall(self.x, novo_y, self.size):
            self.y = novo_y

    def _update_aim(self, mouse_pos):
        """
        Atualiza o ângulo de mira em direção ao cursor do mouse.
        # que é calculado com atan2 entre o jogador e o mouse, de forma que o jogador aponte sempre para o cursor.
        """
        self.angle = math.atan2(mouse_pos[1] - self.y, mouse_pos[0] - self.x)

    def _handle_shooting(self, keys, projeteis):
        """Dispara se o cooldown foi respeitado e o botão está pressionado."""
        atirando = pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]
        if atirando:
            self._try_shoot(projeteis)

    def _try_shoot(self, projeteis):
        """
        Adiciona projéteis à lista se o cooldown foi respeitado.

        Com power-up "double" ativo, dispara dois projéteis paralelos
        separados perpendicularmente ao ângulo de mira.
        """
        agora = pygame.time.get_ticks()
        if agora - self.last_shot_time < PLAYER_SHOT_COOLDOWN:
            return

        self.last_shot_time = agora
        self.total_shots   += 1

        if self.powerups["double"] > 0:
            # Vetor perpendicular ao ângulo de mira para separar os projéteis
            perp_x = -math.sin(self.angle) * DOUBLE_SHOT_OFFSET
            perp_y =  math.cos(self.angle) * DOUBLE_SHOT_OFFSET
            projeteis.append(Bullet(self.x + perp_x, self.y + perp_y, self.angle))
            projeteis.append(Bullet(self.x - perp_x, self.y - perp_y, self.angle))
        else:
            projeteis.append(Bullet(self.x, self.y, self.angle))

    '''
    # 2. POWER-UPS
    '''

    def activate_powerup(self, tipo):
        """
        Ativa um power-up e define sua duração.

        Se o jogador coletar o mesmo power-up enquanto ele já estiver ativo, o tempo de duração é reiniciado (não acumula)
        """
        if tipo in self.powerups:
            self.powerups[tipo] = POWERUP_DURATION

    '''
    # 3. PROPRIEDADES
    '''

    @property
    def has_shield(self):
        """True se o escudo está ativo (invulnerável)."""
        return self.powerups["shield"] > 0

    @property
    def accuracy(self):
        """Precisão de acerto em porcentagem. Retorna 0 se não atirou."""
        if self.total_shots == 0:
            return 0
        return int(self.hits / self.total_shots * 100)

    '''
    # 4. RENDERIZAÇÃO
    '''

    def draw(self, screen):
        """
        Renderiza o jogador como triângulo neon rotacionado para o mouse.
        Se o escudo estiver ativo, exibe um anel ciano ao redor.
        """
        if not self.alive:
            return

        self._draw_glow(screen)

        if self.has_shield:
            self._draw_shield_ring(screen)

        self._draw_body(screen)

    def _draw_glow(self, screen):
        """Brilho ao redor do jogador."""
        tamanho = self.size * 4
        glow_surf = pygame.Surface((tamanho, tamanho), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (*C_PLAYER_GLOW, 40),
            (tamanho // 2, tamanho // 2),
            self.size * 2,
        )
        screen.blit(glow_surf, (int(self.x) - tamanho // 2, int(self.y) - tamanho // 2))

    def _draw_shield_ring(self, screen):
        """Anel de escudo ativo ao redor do jogador."""
        pygame.draw.circle(
            screen, C_SHIELD_RING,
            (int(self.x), int(self.y)),
            self.size + 8, 2,
        )

    def _draw_body(self, screen):
        """Triângulo principal rotacionado para o ângulo de mira."""
        s = self.size
        # Pontos do triângulo no espaço local (origem = centro do jogador)
        pontos_locais = [
            (0,        -s * 1.1),   # ponta frontal
            (-s * 0.65, s * 0.75),  # traseira esquerda
            ( s * 0.65, s * 0.75),  # traseira direita
        ]

        # Rotaciona e translada cada ponto para o espaço da tela
        ang  = self.angle + math.pi / 2
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        pontos_mundo = [
            (lx * cos_a - ly * sin_a + self.x,
             lx * sin_a + ly * cos_a + self.y)
            for lx, ly in pontos_locais
        ]

        pygame.draw.polygon(screen, C_PLAYER_GUN, pontos_mundo)
        pygame.draw.polygon(screen, C_PLAYER,     pontos_mundo, 0)
        pygame.draw.polygon(screen, (180, 240, 255), pontos_mundo, 1)

        # Ponto central de energia
        pygame.draw.circle(screen, C_PLAYER_CORE, (int(self.x), int(self.y)), 2)


'''
# 5. Bullet (Projétil disparado pelo jogador)
'''

class Bullet:
    """
    Projétil que se move em linha reta com velocidade constante.

    Ciclo de vida:
      - Criado por Player._try_shoot()
      - Atualizado a cada frame por Bullet.update()
      - Removido de projeteis quando alive == False

    Motivos para alive = False:
      1. Colidiu com uma parede
      2. Vida chegou a zero (distância máxima percorrida)
      3. Acertou um inimigo (marcado em GameState)
    """

    def __init__(self, x, y, angle):
        self.x  = x
        self.y  = y
        # Decompõe o ângulo em velocidade vetorial (vx, vy)
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.life  = BULLET_LIFE
        self.alive = True

    def update(self):
        """Avança o projétil e verifica expiração por parede ou vida."""
        self.x    += self.vx
        self.y    += self.vy
        self.life -= BULLET_DECAY_RATE

        coluna, linha = TileMap.pixel_to_tile(self.x, self.y)
        if TileMap.is_wall(coluna, linha) or self.life <= 0:
            self.alive = False

    def draw(self, screen):
        """Renderiza o projétil com brilho proporcional à vida restante."""
        if not self.alive:
            return

        alpha = int(self.life * 255)
        cx, cy = int(self.x), int(self.y)

        # Halo externo semi-transparente
        glow = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*C_BULLET, alpha // 3), (7, 7), 7)
        screen.blit(glow, (cx - 7, cy - 7))

        # Núcleo sólido
        pygame.draw.circle(screen, C_BULLET,      (cx, cy), BULLET_RADIUS)
        pygame.draw.circle(screen, C_BULLET_CORE, (cx, cy), 1)
