# =============================================================================
# menu.py — Tela de Menu Principal
# =============================================================================
# Exibe a tela inicial com BOTÕES "Jogar" e "Sair".
#
# Separado de main.py para manter o ponto de entrada limpo e facilitar a futura adição de sub-menus (configurações, créditos, etc.)

import pygame
import math
import sys
from config import SCREEN_W, SCREEN_H, C_BLACK, C_HUD_ACCENT, C_HUD_DIM, C_WIN, C_LOSE


class Button:
    """
    Botão interativo com estado de hover e feedback visual.
    Detecta se o mouse está sobre o botão e muda a cor da borda.
    """

    def __init__(self, x, y, largura, altura, texto, cor_normal, cor_hover):
        self.rect       = pygame.Rect(x, y, largura, altura)
        self.texto      = texto
        self.cor_normal = cor_normal
        self.cor_hover  = cor_hover
        self.hovered    = False
        self._font      = pygame.font.SysFont("couriernew", 16, bold=True)

    def update(self, mouse_pos):
        """Atualiza o estado de hover."""
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        """Renderiza o botão com feedback de hover."""
        # Fundo semi-transparente
        fundo = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        fundo.fill((10, 16, 32, 220))
        screen.blit(fundo, (self.rect.topleft))

        # Borda (muda de cor ao passar o mouse)
        cor_borda = self.cor_hover if self.hovered else self.cor_normal
        pygame.draw.rect(screen, cor_borda, self.rect, 2)

        # Texto centralizado
        cor_texto = self.cor_hover if self.hovered else (180, 200, 240)
        surf      = self._font.render(self.texto, True, cor_texto)
        tx = self.rect.x + (self.rect.width  - surf.get_width())  // 2
        ty = self.rect.y + (self.rect.height - surf.get_height()) // 2
        screen.blit(surf, (tx, ty))

    def foi_clicado(self, event):
        """True se o evento é um clique esquerdo sobre este botão."""
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


def run_menu(screen):
    """
    Executa o loop do menu principal.

    Returns:
        bool: True → o jogador quer jogar, False → encerrar o programa
    """
    clock = pygame.time.Clock()

    cx, cy  = SCREEN_W // 2, SCREEN_H // 2
    btn_w   = 220
    btn_h   = 50

    btn_jogar = Button(cx - btn_w // 2, cy + 20,  btn_w, btn_h, "[ JOGAR ]", (0, 150, 100), C_WIN)
    btn_sair  = Button(cx - btn_w // 2, cy + 90,  btn_w, btn_h, "[ SAIR ]",  (120, 30, 30), C_LOSE)

    font_titulo   = pygame.font.SysFont("couriernew", 40, bold=True)
    font_subtitulo = pygame.font.SysFont("couriernew", 12)
    font_info     = pygame.font.SysFont("couriernew", 10)

    controles = [
        "WASD / Setas — Mover     |     Mouse — Mirar",
        "Clique Esquerdo / Espaço — Atirar",
        "Elimine TODOS os impostores antes da zona vermelha fechar!",
    ]

    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return True
                if event.key == pygame.K_ESCAPE: return False
            if btn_jogar.foi_clicado(event): return True
            if btn_sair.foi_clicado(event):  return False

        btn_jogar.update(mouse_pos)
        btn_sair.update(mouse_pos)

        screen.fill(C_BLACK)
        _draw_grid_bg(screen)

        # Título pulsante
        pulse      = abs(math.sin(pygame.time.get_ticks() * 0.0015))
        cor_titulo = tuple(int(c * (0.7 + 0.3 * pulse)) for c in C_HUD_ACCENT)
        t1 = font_titulo.render("LABIRINTO DOS", True, cor_titulo)
        t2 = font_titulo.render("IMPOSTORES",    True, cor_titulo)
        screen.blit(t1, (cx - t1.get_width() // 2, cy - 160))
        screen.blit(t2, (cx - t2.get_width() // 2, cy - 110))

        # Subtítulo e divisória
        sub = font_subtitulo.render("MISSÃO CLASSIFICADA · AGENTE DESIGNADO", True, C_HUD_DIM)
        screen.blit(sub, (cx - sub.get_width() // 2, cy - 55))
        pygame.draw.line(screen, C_HUD_ACCENT, (cx - 200, cy - 30), (cx + 200, cy - 30), 1)

        # Botões
        btn_jogar.draw(screen)
        btn_sair.draw(screen)

        # Controles
        for i, linha in enumerate(controles):
            surf = font_info.render(linha, True, C_HUD_DIM)
            screen.blit(surf, (cx - surf.get_width() // 2, cy + 162 + i * 16))

        # Dica de teclado no rodapé
        tip = font_info.render("[ ENTER ] jogar  |  [ ESC ] sair", True, (40, 60, 90))
        screen.blit(tip, (cx - tip.get_width() // 2, SCREEN_H - 24))

        pygame.display.flip()
        clock.tick(60)


def _draw_grid_bg(screen):
    """Grade decorativa de pontos animados no fundo do menu (estética circuito)."""
    t = pygame.time.get_ticks()
    for gx in range(0, SCREEN_W + 32, 32):
        for gy in range(0, SCREEN_H + 32, 32):
            pulso = math.sin(t * 0.001 + gx * 0.05 + gy * 0.05)
            r     = 1 if pulso < 0 else 2
            pygame.draw.circle(screen, (15, 25, 50), (gx, gy), r)
