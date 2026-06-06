# =============================================================================
# enemy.py (Impostores)
# =============================================================================

import pygame
import math
import random
from config import (
    ENEMY_SIZE, MAP_W, MAP_H,
    ENEMY_DIRECTION_CHANGE_INTERVAL,
    ENEMY_DIRECTION_CHANGE_CHANCE,
    ENEMY_COLLISION_COOLDOWN,
    C_ENEMY, C_ENEMY_CORE, C_ENEMY_GLOW, C_ENEMY_PUPIL,
)
from tilemap import TileMap

# Quantos frames consecutivos com slide parcial indicam que o inimigo está preso
_STUCK_THRESHOLD = 8

class Enemy:
    """
    Impostor (entidade inimiga que patrulha o labirinto)

    Matar o impostor: usar o projétil do jogador → hit()
    Morrer pela zona: verificado em update() → self.alive = False
    Game over: impostor encosta no jogador (verificado em GameState)
    """

    def __init__(self, col, row, speed):
        """
        Args:
            col   (int)  : coluna de spawn no mapa
            row   (int)  : linha de spawn no mapa
            speed (float): pixels avançados por frame (varia por sessão)
        """
        self.x, self.y = TileMap.tile_to_pixel_center(col, row)
        self.speed      = speed
        self.size       = ENEMY_SIZE
        self.alive      = True

        # Direção de movimento: vetor unitário aleatório inicial
        self.dx, self.dy = self._random_unit_vector()

        # Timers automatizados
        self._timer_direcao    = 0   # ms desde a última mudança de direção
        self._cooldown_colisao = 0   # ms de espera após colidir
        self._frames_travado   = 0   # contador anti-stuck

        # Animação de flutuação (bob senoidal)
        self._bob_fase  = random.uniform(0, math.pi * 2)   # fase individual
        self._bob_timer = 0.0

        # Variação de cor individual (efeito de impostores ligeiramente distintos) 
        self.color = self._gerar_cor_individual()

    '''
    # 1. ATUALIZAÇÃO (chamado uma vez por frame)
    '''

    def update(self, dt, zone_margin, freeze_active):
        """
        Atualiza posição, automatização e animações do inimigo.

        Args:
            dt           (float): delta time em ms
            zone_margin  (float): margem atual da zona vermelha em pixels
            freeze_active (bool): True se o power-up Freeze está ativo
        """
        if not self.alive:
            return

        self._bob_timer += dt * 0.003   # Animação de flutuação (independe do freeze)

        if freeze_active:
            return   # Congelado (não move, não morre pela zona)

        self._atualizar_timers(dt)
        self._considerar_mudanca_espontanea()
        self._executar_movimento()
        self._verificar_zona(zone_margin)

    def _atualizar_timers(self, dt):
        """Incrementa o timer de direção e decrementa o cooldown de colisão."""
        self._timer_direcao    += dt
        self._cooldown_colisao  = max(0, self._cooldown_colisao - dt)

    def _considerar_mudanca_espontanea(self):
        """
        A cada DIRECTION_CHANGE_INTERVAL ms, há chance de mudança voluntária.
        Cria comportamento imprevisível nos inimigos.
        """
        if self._timer_direcao >= ENEMY_DIRECTION_CHANGE_INTERVAL:
            self._timer_direcao = 0
            if random.random() < ENEMY_DIRECTION_CHANGE_CHANCE:
                self._pick_random_direction()

    def _executar_movimento(self):
        """
        Tenta mover o inimigo. SE travar ou acumular slides, força nova direção.

        'slide' significa que apenas um eixo moveu: o inimigo está encostado
        em uma parede lateral. Após STUCK_THRESHOLD frames assim, a direção
        atual está claramente ruim e trocamos por uma aleatória (não pela
        função away_from_wall, que poderia repetir o mesmo padrão).
        """
        resultado = self._try_move()

        if resultado == "livre":
            self._frames_travado = 0

        elif resultado == "slide":
            self._frames_travado += 1
            if self._frames_travado >= _STUCK_THRESHOLD:
                # Usa direção aleatória pura (evita que o mesmo viés se repita)
                self._pick_random_direction()
                self._frames_travado = 0

        else:  # 'impostor travado'
            if self._cooldown_colisao <= 0:
                self._pick_direction_away_from_wall()
                self._cooldown_colisao = ENEMY_COLLISION_COOLDOWN
            self._frames_travado = 0

    def _try_move(self):
        """
        Tenta mover na direção atual.

        Returns:
            str: "livre"  → movimento completo bem-sucedido
                 "slide"  → só um dos eixos funcionou (parede lateral)
                 "travado" → nenhum eixo funcionou
        """
        mx = self.dx * self.speed
        my = self.dy * self.speed

        # Movimento completo (caso ideal)
        if not TileMap.circle_collides_wall(self.x + mx, self.y + my, self.size):
            self.x += mx
            self.y += my
            return "livre"

        # Slide apenas no eixo X
        moveu_x = False
        if not TileMap.circle_collides_wall(self.x + mx, self.y, self.size):
            self.x  += mx
            moveu_x  = True

        # Slide apenas no eixo Y
        moveu_y = False
        if not TileMap.circle_collides_wall(self.x, self.y + my, self.size):
            self.y  += my
            moveu_y  = True

        if moveu_x or moveu_y:
            return "slide"
        return "travado"

    def _verificar_zona(self, zone_margin):
        """Mata o inimigo se ele entrar na zona vermelha."""
        if zone_margin > 0 and self._esta_na_zona(zone_margin):
            self.alive = False

    def _esta_na_zona(self, zone_margin):
        """
        True se o inimigo saiu da área segura delimitada pela zona.
        Área segura: [margin+size .. MAP_W-margin-size] em X e Y.
        """
        margem = zone_margin + self.size
        return (
            self.x < margem or self.x > MAP_W - margem
            or self.y < margem or self.y > MAP_H - margem
        )

    '''
    # 2. DIREÇÃO
    '''

    def _pick_random_direction(self):
        """Escolhe uma nova direção completamente aleatória."""
        self.dx, self.dy     = self._random_unit_vector()
        self._timer_direcao  = 0

    def _pick_direction_away_from_wall(self):
        """
        Escolhe uma direção livre de colisão sem viés direcional.

        Gera 16 ângulos igualmente espaçados, EMBARALHA antes de testar,
        e usa o primeiro livre. O embaralhamento é essencial: pois sem ele os
        ângulos seriam testados sempre em ordem (0°, 22°, 45°...) criando
        viés acumulado — todos os inimigos derivariam para o mesmo lado do mapa.
        """
        angulos = [(i / 16) * 2 * math.pi for i in range(16)]
        random.shuffle(angulos)

        for angulo in angulos:
            teste_x = self.x + math.cos(angulo) * self.speed * 4
            teste_y = self.y + math.sin(angulo) * self.speed * 4
            if not TileMap.circle_collides_wall(teste_x, teste_y, self.size):
                self.dx = math.cos(angulo)
                self.dy = math.sin(angulo)
                self._timer_direcao = 0
                return

        # Nenhum ângulo livre — direção aleatória pura
        self.dx, self.dy = self._random_unit_vector()
        self._timer_direcao = 0

    @staticmethod
    def _random_unit_vector():
        """Retorna um vetor unitário com ângulo aleatório."""
        angulo = random.uniform(0, 2 * math.pi)
        return math.cos(angulo), math.sin(angulo)

    '''
    # 3. COLISÃO
    '''

    def collides_with_player(self, px, py, player_size):
        """
        Colisão circular com o jogador.
        Usa distância ao quadrado para evitar sqrt (mais eficiente).

        Returns:
            bool: True se o inimigo encostou no jogador
        """
        dx = self.x - px
        dy = self.y - py
        dist_minima = self.size + player_size
        return dx * dx + dy * dy < dist_minima * dist_minima

    def collides_with_bullet(self, bx, by):
        """
        Verifica se um projétil atingiu este inimigo.

        O raio de colisão do projétil (3px) é somado ao raio do inimigo
        para uma hitbox (dá a sensação de acerto preciso).
        """
        dx = self.x - bx
        dy = self.y - by
        raio_colisao = self.size + 3   # +3 = raio do projétil
        return dx * dx + dy * dy < raio_colisao * raio_colisao

    def hit(self):
        """Marca o inimigo como eliminado por projétil."""
        self.alive = False

    '''
    # 4. RENDERIZAÇÃO
    '''

    def draw(self, screen):
        """
        Renderiza o inimigo como estrela de 8 pontas com brilho neon.
        Flutua suavemente em onda senoidal para aparência animada
        """
        if not self.alive:
            return

        # Offset vertical da flutuação
        flutuacao_y = math.sin(self._bob_timer + self._bob_fase) * 2.0
        cx = int(self.x)
        cy = int(self.y + flutuacao_y)

        self._draw_glow(screen, cx, cy)
        self._draw_star(screen, cx, cy)
        self._draw_core(screen, cx, cy)

    def _draw_glow(self, screen, cx, cy):
        """Halo neon ao redor do inimigo."""
        r         = self.size + 6
        glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*C_ENEMY_GLOW, 50), (r, r), r)
        screen.blit(glow_surf, (cx - r, cy - r))

    def _draw_star(self, screen, cx, cy):
        """Estrela de 8 pontas alternando raio externo e interno."""
        pontos = []
        for i in range(16):   # 8 pontos externos + 8 internos alternados
            angulo = (i * math.pi / 8) - math.pi / 2
            r      = self.size if i % 2 == 0 else int(self.size * 0.5)
            pontos.append((cx + math.cos(angulo) * r, cy + math.sin(angulo) * r))

        pygame.draw.polygon(screen, self.color, pontos)
        pygame.draw.polygon(screen, C_ENEMY_GLOW, pontos, 1)

    def _draw_core(self, screen, cx, cy):
        """Olho central que aponta na direção de movimento."""
        pygame.draw.circle(screen, C_ENEMY_CORE, (cx, cy), 3)
        # Pupila que fica se deslocando na direção do movimento
        pygame.draw.circle(
            screen, C_ENEMY_PUPIL,
            (cx + int(self.dx * 2), cy + int(self.dy * 2)), 1,
        )

    '''
    # 5. AUXILIARES
    '''

    @staticmethod
    def _gerar_cor_individual():
        """
        Gera uma variação sutil da cor base do inimigo.
        Impostores ficam visualmente distintos entre si.
        """
        variacao = random.randint(-20, 20)
        r = min(255, max(0, C_ENEMY[0] + variacao))
        g = min(255, max(0, C_ENEMY[1] + variacao // 4))
        b = min(255, max(0, C_ENEMY[2] + variacao // 4))
        return (r, g, b)
