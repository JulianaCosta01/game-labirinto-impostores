# =============================================================================
# hud.py (Interface do Usuário (HUD) e Telas de Início / Fim de Jogo)
# =============================================================================

import pygame
import math
from config import (
    SCREEN_W, SCREEN_H, MAP_W, MAP_H,
    POWERUP_DURATION,
    C_HUD_BG, C_HUD_DIM, C_HUD_ACCENT,
    C_COMBO, C_ENEMY, C_PLAYER, C_ZONE_EDGE,
    C_WIN, C_LOSE, C_WHITE, C_BLACK,
    ITEM_META,
)


class HUD:
    """
    Renderiza a interface do jogo sobre a cena.

    Elementos:
      - Barra superior: pontos, tempo, inimigos, progresso, combo, recorde
      - Indicadores de power-up (canto inferior esquerdo)
      - Aviso de zona fechando (centro superior)
      - Mini-radar (canto inferior direito)
    """

    # Layout da barra superior: posição X de cada coluna
    _COLUNAS_HUD = [10, 140, 260, 370, 530, 660]
    _ALTURA_BARRA = 44
    _TAMANHO_RADAR = 90

    def __init__(self):
        # Fontes monoespaçadas (parte estética)
        self.font_large  = pygame.font.SysFont("couriernew", 20, bold=True)
        self.font_medium = pygame.font.SysFont("couriernew", 14, bold=True)
        self.font_small  = pygame.font.SysFont("couriernew", 11)
        self.font_tiny   = pygame.font.SysFont("couriernew",  9)

        # Fontes do combo separadas por tamanho (evitar criação dinâmica a cada frame)
        self._font_combo_normal = pygame.font.SysFont("couriernew", 16, bold=True)
        self._font_combo_grande = pygame.font.SysFont("couriernew", 20, bold=True)

        # Posições fixas do radar
        self.bar_h   = self._ALTURA_BARRA
        self._radar_x = SCREEN_W - self._TAMANHO_RADAR - 8
        self._radar_y = SCREEN_H - self._TAMANHO_RADAR - 8

        # Labels de power-up e suas cores (lidos de ITEM_META para DRY)
        self._powerup_labels = {k: v["label"] for k, v in ITEM_META.items()}
        self._powerup_colors = {k: v["color"] for k, v in ITEM_META.items()}

    '''
    # 1. PONTO DE ENTRADA
    '''

    def draw(self, screen, gs):
        """
        Renderiza todos os elementos do HUD.

        Args:
            screen : pygame.Surface principal
            gs     : GameState com acesso a todos os dados do jogo
        """
        self._draw_top_bar(screen, gs)
        self._draw_radar(screen, gs)
        self._draw_powerup_indicators(screen, gs)
        if gs.zone.active:
            self._draw_zone_warning(screen, gs)

    '''
    # 2. BARRA SUPERIOR
    '''

    def _draw_top_bar(self, screen, gs):
        """Barra translúcida com todos os indicadores de status."""
        self._draw_bar_background(screen)

        cols     = self._COLUNAS_HUD
        alive    = sum(1 for e in gs.enemies if e.alive)
        elapsed  = gs.elapsed_seconds
        min_part = int(elapsed // 60)
        seg_part = int(elapsed % 60)

        self._label(screen, "PONTOS",   cols[0], 4)
        self._value(screen, str(gs.score), cols[0], 18)

        self._label(screen, "TEMPO",    cols[1], 4)
        self._value(screen, f"{min_part:02d}:{seg_part:02d}", cols[1], 18)

        self._label(screen, "INIMIGOS", cols[2], 4)
        cor_inimigos = C_ENEMY if alive > 0 else C_WIN
        self._value(screen, f"{alive}/{gs.total_inimigos}", cols[2], 18, color=cor_inimigos)

        self._label(screen, "PROGRESSO", cols[3], 4)
        self._draw_progress_bar(screen, cols[3], alive, gs.total_inimigos)

        self._label(screen, "COMBO",    cols[4], 4)
        self._draw_combo(screen, cols[4], gs.combo)

        self._label(screen, "RECORDE",  cols[5], 4)
        self._value(screen, str(gs.high_score), cols[5], 18, color=C_HUD_DIM)

    def _draw_bar_background(self, screen):
        """Fundo semi-transparente e linha divisória da barra superior."""
        fundo = pygame.Surface((SCREEN_W, self.bar_h), pygame.SRCALPHA)
        fundo.fill((*C_HUD_BG, 210))
        screen.blit(fundo, (0, 0))
        pygame.draw.line(screen, C_HUD_ACCENT, (0, self.bar_h - 1), (SCREEN_W, self.bar_h - 1), 1)

    def _draw_progress_bar(self, screen, x, alive, total):
        """Barra de progresso de eliminação dos inimigos."""
        rect_fundo = pygame.Rect(x, 20, 140, 12)
        pygame.draw.rect(screen, (20, 30, 50), rect_fundo, border_radius=3)
        if total > 0:
            pct        = (total - alive) / total
            rect_fill  = pygame.Rect(x, 20, int(140 * pct), 12)
            pygame.draw.rect(screen, self._progress_color(pct), rect_fill, border_radius=3)
        pygame.draw.rect(screen, C_HUD_DIM, rect_fundo, 1, border_radius=3)

    def _draw_combo(self, screen, x, combo):
        """Multiplicador de combo (fonte maior quando combo aumenta)"""
        cor  = C_COMBO if combo > 1 else C_HUD_DIM
        font = self._font_combo_grande if combo > 3 else self._font_combo_normal
        surf = font.render(f"x{combo}", True, cor)
        screen.blit(surf, (x, 16))

    def _label(self, screen, texto, x, y):
        """Rótulo pequeno e discreto (categoria)"""
        surf = self.font_tiny.render(texto, True, C_HUD_DIM)
        screen.blit(surf, (x, y))

    def _value(self, screen, texto, x, y, color=None):
        """Valor destacado em ciano."""
        surf = self.font_medium.render(texto, True, color or C_HUD_ACCENT)
        screen.blit(surf, (x, y))

    @staticmethod
    def _progress_color(pct):
        """Interpolação de cor: ciano (0%) → verde (100%)."""
        if pct < 0.5:
            return (0, 160 + int(pct * 190), 200)
        return (0, 200, int((1 - pct) * 200))

    '''
    # 3. INDICADORES DE POWER-UP
    '''

    def _draw_powerup_indicators(self, screen, gs):
        """Exibe ícones dos power-ups ativos no canto inferior esquerdo."""
        ativos = [(tipo, restante)
                  for tipo, restante in gs.player.powerups.items()
                  if restante > 0]
        if not ativos:
            return

        base_y = SCREEN_H - 28
        for i, (tipo, restante) in enumerate(ativos):
            self._draw_single_powerup(screen, i, tipo, restante, base_y)

    def _draw_single_powerup(self, screen, indice, tipo, restante, base_y):
        """Renderiza o ícone e barra de duração de um único power-up."""
        x   = 8 + indice * 54
        cor = self._powerup_colors.get(tipo, C_HUD_ACCENT)

        # Caixa de fundo
        caixa = pygame.Surface((50, 22), pygame.SRCALPHA)
        caixa.fill((*C_HUD_BG, 200))
        screen.blit(caixa, (x, base_y))
        pygame.draw.rect(screen, cor, (x, base_y, 50, 22), 1)

        # Rótulo do power-ups(SPD, DBL, SHD, FRZ) | obs: 'tipo,???' é para caso dê algum bug
        label = self.font_tiny.render(self._powerup_labels.get(tipo, "???"), True, cor)
        screen.blit(label, (x + 3, base_y + 2))

        # Barra de duração restante
        pct_restante = restante / POWERUP_DURATION
        pygame.draw.rect(screen, (20, 30, 50), (x + 2, base_y + 14, 46, 5))
        pygame.draw.rect(screen, cor, (x + 2, base_y + 14, int(46 * pct_restante), 5))

    '''
    # 4. AVISO DE ZONA
    '''

    def _draw_zone_warning(self, screen, gs):
        """Texto pulsante de aviso quando a zona está avançando significativamente."""
        if gs.zone.margin < 30:
            return
        pulse     = abs(math.sin(pygame.time.get_ticks() * 0.004))
        alpha     = int(100 + 155 * pulse)
        surf      = self.font_medium.render("⚠ ZONA FECHANDO", True, C_ZONE_EDGE)
        warn_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        warn_surf.blit(surf, (0, 0))
        warn_surf.set_alpha(alpha)
        x = (SCREEN_W - surf.get_width()) // 2
        screen.blit(warn_surf, (x, self.bar_h + 4))

    '''
    # 5. MINI-RADAR
    '''

    def _draw_radar(self, screen, gs):
        """
        Mini-mapa no canto inferior direito.

        Mostra jogador (ciano), inimigos (vermelho) e zona (vermelha)
        em escala proporcional ao mapa real.
        Escala: radar_size / MAP_SIZE x posição_real → posição_no_radar
        """
        rs   = self._TAMANHO_RADAR
        rx   = self._radar_x
        ry   = self._radar_y
        sx   = rs / MAP_W   # fator de escala X
        sy   = rs / MAP_H   # fator de escala Y

        fundo = pygame.Surface((rs, rs), pygame.SRCALPHA)
        fundo.fill((*C_HUD_BG, 200))

        self._draw_radar_zone(fundo, gs.zone, rs, sx, sy)
        self._draw_radar_enemies(fundo, gs.enemies, sx, sy)
        self._draw_radar_player(fundo, gs.player, sx, sy)

        screen.blit(fundo, (rx, ry))
        pygame.draw.rect(screen, C_HUD_DIM, (rx - 1, ry - 1, rs + 2, rs + 2), 1)

        rotulo = self.font_tiny.render("RADAR", True, C_HUD_DIM)
        screen.blit(rotulo, (rx + rs // 2 - rotulo.get_width() // 2, ry - 13))

    @staticmethod
    def _draw_radar_zone(surf, zone, rs, sx, sy):
        """Retângulo da área segura no radar."""
        if zone.margin <= 0:
            return
        m  = zone.margin
        zx = int(m * sx)
        zy = int(m * sy)
        zw = int((MAP_W - m * 2) * sx)
        zh = int((MAP_H - m * 2) * sy)
        pygame.draw.rect(surf, (180, 30, 30, 120), (zx, zy, zw, zh))
        pygame.draw.rect(surf, (*C_ZONE_EDGE, 200), (zx, zy, zw, zh), 1)

    @staticmethod
    def _draw_radar_enemies(surf, inimigos, sx, sy):
        """Pontos vermelhos para cada inimigo vivo."""
        for inimigo in inimigos:
            if inimigo.alive:
                pygame.draw.circle(
                    surf, C_ENEMY,
                    (int(inimigo.x * sx), int(inimigo.y * sy)), 2,
                )

    @staticmethod
    def _draw_radar_player(surf, player, sx, sy):
        """Ponto ciano maior para o jogador."""
        px = int(player.x * sx)
        py = int(player.y * sy)
        pygame.draw.circle(surf, C_PLAYER, (px, py), 3)
        pygame.draw.circle(surf, C_WHITE,  (px, py), 1)


'''
# 6. TELA INICIAL
'''

def draw_start_screen(screen):
    """
    Exibe a tela de boas-vindas com título, controles e instrução de início.
    Animação de pulsação no texto de ENTER.
    """
    screen.fill(C_BLACK)

    font_titulo   = pygame.font.SysFont("couriernew", 36, bold=True)
    font_subtitulo = pygame.font.SysFont("couriernew", 12)
    font_ctrl     = pygame.font.SysFont("couriernew", 11)

    cx   = SCREEN_W // 2
    cy   = SCREEN_H // 2
    agora = pygame.time.get_ticks()

    # Título
    titulo1 = font_titulo.render("LABIRINTO DOS", True, C_HUD_ACCENT)
    titulo2 = font_titulo.render("IMPOSTORES",    True, C_HUD_ACCENT)
    screen.blit(titulo1, (cx - titulo1.get_width() // 2, cy - 160))
    screen.blit(titulo2, (cx - titulo2.get_width() // 2, cy - 110))

    # Subtítulo
    sub = font_subtitulo.render("MISSÃO CLASSIFICADA · AGENTE DESIGNADO", True, C_HUD_DIM)
    screen.blit(sub, (cx - sub.get_width() // 2, cy - 56))

    # Linha divisória
    pygame.draw.line(screen, C_HUD_ACCENT, (cx - 180, cy - 32), (cx + 180, cy - 32), 1)

    # Controles
    controles = [
        "WASD / Setas   →   Mover",
        "Mouse          →   Mirar",
        "Clique / Espaço →  Atirar",
        "Não toque nos impostores nem na zona vermelha",
    ]
    for i, linha in enumerate(controles):
        surf = font_ctrl.render(linha, True, C_HUD_DIM)
        screen.blit(surf, (cx - surf.get_width() // 2, cy + i * 18))

    # Instrução pulsante
    pulse = abs(math.sin(agora * 0.002))
    cor_enter = tuple(int(c + (255 - c) * pulse) for c in C_HUD_ACCENT)
    enter_surf = font_subtitulo.render("[ ENTER ] para iniciar", True, cor_enter)
    screen.blit(enter_surf, (cx - enter_surf.get_width() // 2, cy + 100))


'''
# 7. TELA DE FIM DE JOGO
'''

def draw_end_screen(screen, font_large, font_medium, font_small,
                    won, score, high_score, elapsed_secs,
                    kills, total, accuracy, session_count):
    """
    Overlay de resultado com estatísticas da partida encerrada

    Args:
        screen        : pygame.Surface principal
        font_*        : fontes pré-carregadas do HUD
        won           : True = vitória, False = derrota
        score         : pontuação final
        high_score    : melhor pontuação histórica
        elapsed_secs  : duração da partida em segundos
        kills         : inimigos eliminados
        total         : total de inimigos na partida
        accuracy      : precisão dos tiros em %
        session_count : número da sessão atual
    """
    _draw_end_overlay(screen)
    painel_x, painel_y, painel_w, painel_h = _draw_end_panel(screen, won)
    _draw_end_title(screen, painel_x, painel_y, painel_w, won)
    _draw_end_stats(screen, painel_x, painel_y, painel_w,
                    font_medium, font_small,
                    score, high_score, elapsed_secs, kills, total, accuracy, session_count)
    _draw_end_instructions(screen, painel_x, painel_y, painel_w, painel_h, font_small)


def _draw_end_overlay(screen):
    """Camada semi-transparente escura sobre o jogo."""
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((5, 8, 16, 220))
    screen.blit(overlay, (0, 0))


def _draw_end_panel(screen, won):
    """Painel central com borda colorida que retorna (x, y, w, h)."""
    w, h = 420, 320
    x    = (SCREEN_W - w) // 2
    y    = (SCREEN_H - h) // 2
    cor  = C_WIN if won else C_LOSE

    painel = pygame.Surface((w, h), pygame.SRCALPHA)
    painel.fill((10, 16, 32, 240))
    screen.blit(painel, (x, y))
    pygame.draw.rect(screen, cor, (x, y, w, h), 2)
    return x, y, w, h


def _draw_end_title(screen, px, py, pw, won):
    """Título de resultado no topo do painel."""
    cor      = C_WIN if won else C_LOSE
    texto    = "MISSÃO COMPLETA" if won else "MISSÃO FALHOU"
    subtexto = "Todos os impostores eliminados." if won else "O agente foi comprometido."

    font_titulo = pygame.font.SysFont("couriernew", 28, bold=True)
    font_sub    = pygame.font.SysFont("couriernew", 11)

    t  = font_titulo.render(texto, True, cor)
    st = font_sub.render(subtexto, True, C_HUD_DIM)

    screen.blit(t,  (px + (pw - t.get_width())  // 2, py + 20))
    screen.blit(st, (px + (pw - st.get_width()) // 2, py + 56))
    pygame.draw.line(screen, (30, 50, 90), (px + 20, py + 74), (px + pw - 20, py + 74), 1)


def _draw_end_stats(screen, px, py, pw, font_medium, font_small,
                    score, high_score, elapsed_secs, kills, total, accuracy, session_count):
    """Tabela de estatísticas no corpo do painel."""
    m  = int(elapsed_secs // 60)
    s  = int(elapsed_secs % 60)
    linhas = [
        ("TEMPO",       f"{m:02d}:{s:02d}"),
        ("PONTUAÇÃO",   str(score)),
        ("ELIMINAÇÕES", f"{kills}/{total}"),
        ("PRECISÃO",    f"{accuracy}%"),
        ("RECORDE",     str(high_score)),
        ("SESSÃO Nº",   str(session_count)),
    ]

    inicio_y = py + 88
    for i, (rotulo, valor) in enumerate(linhas):
        y_linha  = inicio_y + i * 28
        x_rotulo = px + 30
        x_valor  = px + pw - 30

        surf_r = font_small.render(rotulo, True, C_HUD_DIM)
        surf_v = font_medium.render(valor,  True, C_HUD_ACCENT)
        screen.blit(surf_r, (x_rotulo, y_linha))
        screen.blit(surf_v, (x_valor - surf_v.get_width(), y_linha))

        # Linha pontilhada entre rótulo e valor
        inicio_dot = x_rotulo + surf_r.get_width() + 6
        fim_dot    = x_valor  - surf_v.get_width() - 6
        for dot_x in range(inicio_dot, fim_dot, 6):
            pygame.draw.circle(screen, (30, 50, 80), (dot_x, y_linha + 7), 1)


def _draw_end_instructions(screen, px, py, pw, ph, font_small):
    """Instrução de tecla no rodapé do painel"""
    surf = font_small.render("[ENTER] Nova Missão   [ESC] Menu", True, C_HUD_DIM)
    screen.blit(surf, (px + (pw - surf.get_width()) // 2, py + ph - 28))
