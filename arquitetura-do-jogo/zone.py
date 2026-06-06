# =============================================================================
# zone.py (Zona Vermelha, Partículas e Itens)
# =============================================================================

import pygame
import math
import random
from config import (
    MAP_W, MAP_H,
    ZONE_SHRINK_RATE, ZONE_THICKNESS,
    ZONE_TIME_TRIGGER, ZONE_ENEMY_TRIGGER,
    ITEM_META, ITEM_COLLECT_RADIUS,
    C_ZONE_FILL, C_ZONE_EDGE,
)
from tilemap import TileMap


'''
# 1. ZONA VERMELHA
'''

class Zone:
    """
    Zona de fechamento que avança dos 4 lados simultaneamente.

    'margin' é a espessura atual em pixels.
    A área segura é o retângulo central: [margin .. MAP_W-margin] x [margin .. MAP_H-margin].

    Ativação (qualquer condição suficiente):
      1. Tempo decorrido ≥ ZONE_TIME_TRIGGER
      2. Inimigos vivos ≤ ZONE_ENEMY_TRIGGER (e > 0)

    Uma vez ativa, a zona nunca retrocede (exceto se freeze ativo).
    """

    def __init__(self):
        self.margin = 0.0
        self.active = False
        self._pulse = 0.0   # fase da animação de pulsação

    def update(self, dt, elapsed_seconds, enemies_alive, freeze_active):
        """
        Avança a zona e verifica condições de ativação.

        Args:
            dt              (float): delta time em ms
            elapsed_seconds (float): segundos desde o início da partida
            enemies_alive   (int)  : inimigos ainda vivos
            freeze_active   (bool) : True se o power-up Freeze está ativo
        """
        self._verificar_ativacao(elapsed_seconds, enemies_alive)

        if self.active and not freeze_active:
            # Normaliza pela duração real de um frame a 60fps para velocidade constante
            self.margin += ZONE_SHRINK_RATE * (dt / 16.67)
            self.margin  = min(self.margin, self._max_margin())

        self._pulse += dt * 0.004

    def _verificar_ativacao(self, elapsed_seconds, enemies_alive):
        """Ativa a zona se alguma condição for satisfeita."""
        if self.active:
            return
        por_tempo    = elapsed_seconds >= ZONE_TIME_TRIGGER
        por_inimigos = 0 < enemies_alive <= ZONE_ENEMY_TRIGGER
        if por_tempo or por_inimigos:
            self.active = True

    @staticmethod
    def _max_margin():
        """Margem máxima antes de a zona cobrir o mapa inteiro."""
        return min(MAP_W, MAP_H) / 2 - 20

    def draw(self, screen):
        """
        Renderiza as quatro faixas da zona com pulsação de opacidade.
        A linha interna brilhante marca a "parede da morte".
        """
        if self.margin < 1:
            return

        m           = int(self.margin)
        alpha       = int(180 + 60 * math.sin(self._pulse))
        zone_surf   = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
        cor_pulsada = (*C_ZONE_FILL, alpha)

        # Quatro faixas cobrindo as bordas do mapa
        pygame.draw.rect(zone_surf, cor_pulsada, (0, 0, MAP_W, m + 8))                    # topo
        pygame.draw.rect(zone_surf, cor_pulsada, (0, MAP_H - m - 8, MAP_W, m + 8))        # base
        pygame.draw.rect(zone_surf, cor_pulsada, (0, m, m + 8, MAP_H - m * 2))            # esq
        pygame.draw.rect(zone_surf, cor_pulsada, (MAP_W - m - 8, m, m + 8, MAP_H - m * 2)) # dir

        screen.blit(zone_surf, (0, 0))
        self._draw_inner_edge(screen, m)

    def _draw_inner_edge(self, screen, m):
        """Linha brilhante na borda interna da zona."""
        brilho     = int(200 + 55 * math.sin(self._pulse * 1.5))
        cor_borda  = (255, brilho // 4, brilho // 4)
        espessura  = max(2, int(3 + 2 * math.sin(self._pulse)))
        pygame.draw.rect(screen, cor_borda, (m, m, MAP_W - m * 2, MAP_H - m * 2), espessura)

    def is_player_in_zone(self, px, py, player_size):
        """
        True se o jogador tocou a zona → game over.

        Verifica se algum ponto da borda do jogador ultrapassou a margem.
        """
        if self.margin <= 0:
            return False
        r = player_size
        return (
            px - r < self.margin or px + r > MAP_W - self.margin
            or py - r < self.margin or py + r > MAP_H - self.margin
        )

    @property
    def safe_rect(self):
        """pygame.Rect da área segura atual (usado pelo radar do HUD)."""
        m = int(self.margin)
        return pygame.Rect(m, m, MAP_W - m * 2, MAP_H - m * 2)


'''
# 2. PARTÍCULA (Efeito visual de curta duração que fica pulsando)
'''

class Particle:
    """
    Ponto colorido que se move, desacelera e desaparece gradualmente.

    Física simples por frame:
      posição  += velocidade x fator_dt
      velocidade *= atrito          (desacelera)
      vida     -= 0.025 x fator_dt  (fade out)
    """

    _ATRITO = 0.92   # fator de desaceleração por frame (0 = para imediatamente, 1 = sem atrito)

    def __init__(self, x, y, color, speed=None, size=None, life=None):
        self.x     = x
        self.y     = y
        self.color = color

        angulo  = random.uniform(0, 2 * math.pi)
        vel     = speed if speed is not None else random.uniform(1.5, 4.0)
        self.vx = math.cos(angulo) * vel
        self.vy = math.sin(angulo) * vel

        self.life     = life if life is not None else 1.0
        self.max_life = self.life
        self.size     = size if size is not None else random.uniform(1.5, 3.5)

    def update(self, dt):
        """Atualiza posição, velocidade e vida."""
        fator    = dt / 16.67   # normaliza para 60fps
        self.x  += self.vx * fator
        self.y  += self.vy * fator
        self.vx *= self._ATRITO
        self.vy *= self._ATRITO
        self.life = max(0.0, self.life - 0.025 * fator)

    def draw(self, screen):
        """Renderiza com opacidade e tamanho proporcionais à vida restante."""
        if self.life <= 0:
            return
        proporcao = self.life / self.max_life
        alpha     = int(proporcao * 255)
        raio      = max(1, int(self.size * proporcao))
        surf      = pygame.Surface((raio * 2 + 2, raio * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (raio + 1, raio + 1), raio)
        screen.blit(surf, (int(self.x) - raio - 1, int(self.y) - raio - 1))

    @property
    def is_dead(self):
        return self.life <= 0


'''
# 3. FÁBRICAS DE PARTÍCULAS 
'''

def spawn_kill_particles(x, y, cor_primaria, cor_secundaria):
    """
    Cria burst duplo de partículas ao eliminar um inimigo.

    Camada 1 (anel externo): 16 partículas rápidas e grandes.
    Camada 2 (brilho residual): 10 partículas lentas e duradouras.

    Returns:
        list[Particle]
    """
    burst = [
        Particle(x, y, cor_primaria,
                 speed=random.uniform(2, 5),
                 size=random.uniform(2, 4))
        for _ in range(16)
    ]
    residuo = [
        Particle(x, y, cor_secundaria,
                 speed=random.uniform(0.5, 2),
                 size=random.uniform(1, 2.5),
                 life=1.5)
        for _ in range(10)
    ]
    return burst + residuo


def spawn_collect_particles(x, y, cor):
    """
    Partículas ao coletar um item especial.

    Returns:
        list[Particle]
    """
    return [
        Particle(x, y, cor,
                 speed=random.uniform(1, 3),
                 size=random.uniform(1.5, 3))
        for _ in range(12)
    ]


'''
# 4. ITEM (Power-up coletável)
'''

class Item:
    """
    Power-up coletável espalhado pelo mapa.

    Tipos e efeitos (duração: POWERUP_DURATION ms):
      "speed"  → velocidade do jogador aumentada (×1.7)
      "double" → dois projéteis por disparo
      "shield" → invulnerável a inimigos e zona vermelha
      "freeze" → paralisa inimigos e congela a zona vermelha
    """

    # Fonte compartilhada entre todos os itens — inicializada na primeira instância
    _fonte: pygame.font.Font = None

    @classmethod
    def _get_fonte(cls):
        """Retorna a fonte do label, criando-a apenas uma vez."""
        if cls._fonte is None:
            cls._fonte = pygame.font.SysFont("Courier New", 8, bold=True)
        return cls._fonte

    def __init__(self, col, row, item_type):
        self.x, self.y = TileMap.tile_to_pixel_center(col, row)
        self.type   = item_type
        self.alive  = True
        self._pulse = random.uniform(0, math.pi * 2)   # fase individual de animação
        self.meta   = ITEM_META.get(item_type, ITEM_META["speed"])

    def update(self, dt):
        """Avança a animação de pulsação."""
        self._pulse += dt * 0.004

    def check_collect(self, player_x, player_y, player_size):
        """
        Verifica se o jogador está próximo o suficiente para coletar o item.

        Returns:
            bool: True se coletado (e marca self.alive = False)
        """
        dx = self.x - player_x
        dy = self.y - player_y
        raio_captura = player_size + ITEM_COLLECT_RADIUS
        if dx * dx + dy * dy < raio_captura * raio_captura:
            self.alive = False
            return True
        return False

    def draw(self, screen):
        """Renderiza o item de powe- up como losango pulsante com rótulo central."""
        if not self.alive:
            return

        cor   = self.meta["color"]
        label = self.meta["label"]
        cx, cy = int(self.x), int(self.y)
        r = int(10 + 2 * math.sin(self._pulse))   # raio que pulsa

        self._draw_item_glow(screen, cx, cy, r, cor)
        self._draw_diamond(screen, cx, cy, r, cor)
        self._draw_label(screen, cx, cy, label)

    def _draw_item_glow(self, screen, cx, cy, r, cor):
        """Halo difuso ao redor do item."""
        glow = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*cor, 40), (r * 2, r * 2), r * 2)
        screen.blit(glow, (cx - r * 2, cy - r * 2))

    @staticmethod
    def _draw_diamond(screen, cx, cy, r, cor):
        """Losango preenchido com borda."""
        pontos = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(screen, (*cor, 200), pontos)
        pygame.draw.polygon(screen, cor, pontos, 2)

    def _draw_label(self, screen, cx, cy, label):
        """Rótulo de texto centralizado no losango."""
        fonte     = self._get_fonte()
        texto     = fonte.render(label, True, (10, 10, 20))
        screen.blit(texto, (cx - texto.get_width() // 2, cy - texto.get_height() // 2))
