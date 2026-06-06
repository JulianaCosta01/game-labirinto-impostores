# =============================================================================
# tilemap.py (Labirinto e Sistema de Colisão com Paredes)
# =============================================================================

import pygame
from config import (
    MAP_LAYOUT, MAP_ROWS, MAP_COLS, TILE_SIZE,
    C_WALL, C_WALL_BORDER, C_WALL_SHINE, C_FLOOR, C_FLOOR_ALT,
)


class TileMap:
    """
    Representa o labirinto como grade 2D e gerencia colisões com paredes.

    Coordenadas de tile  → (coluna, linha) na grade discreta
    Coordenadas de pixel → (x, y) contínuos na tela
    Conversão            → pixel_x = coluna * TILE_SIZE + offset
    """

    def __init__(self):
        largura = MAP_COLS * TILE_SIZE
        altura  = MAP_ROWS * TILE_SIZE

        # Surface estática onde o labirinto é pré-renderizado
        self.surface = pygame.Surface((largura, altura))
        self._bake()

    '''
    # 1. RENDERIZAÇÃO
    '''

    def _bake(self):
        """
        Pré-renderiza todos os tiles na Surface interna.
        Chamado apenas uma vez no __init__ (nunca durante o jogo)
        """
        self.surface.fill(C_FLOOR)

        for linha in range(MAP_ROWS):
            for coluna in range(MAP_COLS):
                self._draw_tile(coluna, linha)

    def _draw_tile(self, coluna, linha):
        """Renderiza um único tile na Surface interna."""
        x    = coluna * TILE_SIZE
        y    = linha  * TILE_SIZE
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        if MAP_LAYOUT[linha][coluna] == '#':
            self._draw_wall_tile(rect, x, y)
        else:
            self._draw_floor_tile(rect, linha, coluna)

    def _draw_wall_tile(self, rect, x, y):
        """Renderiza uma parede com borda e brilho sutil no topo."""
        pygame.draw.rect(self.surface, C_WALL, rect)

        # Borda interna fina — cria sensação de profundidade
        borda = pygame.Rect(x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
        pygame.draw.rect(self.surface, C_WALL_BORDER, borda, 1)

        # Faixa brilhante no topo — efeito 3D sutil
        topo = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, 2)
        pygame.draw.rect(self.surface, C_WALL_SHINE, topo)

    def _draw_floor_tile(self, rect, linha, coluna):
        """Renderiza o piso com padrão xadrez muito sutil."""
        # Alterna entre duas cores quase idênticas para criar textura
        cor = C_FLOOR_ALT if (linha + coluna) % 2 == 0 else C_FLOOR
        pygame.draw.rect(self.surface, cor, rect)

    def draw(self, screen):
        """Copia a Surface pré-renderizada para a tela."""
        screen.blit(self.surface, (0, 0))

    '''
    # 2. COLISÃO COM PAREDES
    '''

    @staticmethod
    def is_wall(coluna, linha):
        """
        Verifica se uma célula é parede ou está fora dos limites do mapa.

        Tratar as bordas externas como parede impede entidades de sair do mapa.
        """
        fora_dos_limites = (
            coluna < 0 or linha < 0
            or coluna >= MAP_COLS
            or linha  >= MAP_ROWS
        )
        if fora_dos_limites:
            return True
        return MAP_LAYOUT[linha][coluna] == '#'

    @staticmethod
    def circle_collides_wall(cx, cy, raio):
        """
        Verifica se um círculo colide com alguma parede do labirinto.

        Estratégia de 8 pontos:
        Testa os 4 pontos cardeais e 4 diagonais ao redor da borda
        do círculo. Eficiente para raios menores que TILE_SIZE/2.

        O raio é reduzido em 1 pixel internamente para evitar que
        entidades fiquem presas exatamente na borda de uma parede.

        Args:
            cx, cy (float): centro do círculo em pixels
            raio    (int) : raio do círculo em pixels

        Returns:
            bool: True se há colisão com parede
        """
        r = raio - 1   # margem interna anti-stuck

        # Fator de diagonal: cos(45°) ≈ 0.707
        d = r * 0.707

        pontos = [
            (cx - r, cy),       # esquerda
            (cx + r, cy),       # direita
            (cx,     cy - r),   # cima
            (cx,     cy + r),   # baixo
            (cx - d, cy - d),   # diagonal sup-esq
            (cx + d, cy - d),   # diagonal sup-dir
            (cx - d, cy + d),   # diagonal inf-esq
            (cx + d, cy + d),   # diagonal inf-dir
        ]

        return any(
            TileMap.is_wall(*TileMap.pixel_to_tile(px, py))
            for px, py in pontos
        )

    '''
    # 3. CONVERSÃO DE COORDENADAS
    '''

    @staticmethod
    def pixel_to_tile(px, py):
        """Converte pixel (px, py) para tile (coluna, linha)."""
        return int(px // TILE_SIZE), int(py // TILE_SIZE)

    @staticmethod
    def tile_to_pixel_center(coluna, linha):
        """
        Retorna as coordenadas do centro de um tile em pixels.
        Usado para posicionar entidades exatamente no meio de uma célula.
        """
        cx = coluna * TILE_SIZE + TILE_SIZE / 2
        cy = linha  * TILE_SIZE + TILE_SIZE / 2
        return cx, cy
