# =============================================================================
# menu.py: Tela do Menu Principal
# =============================================================================


import pygame
import math
import sys
from config import (
    LARGURA_TELA, ALTURA_TELA,
    COR_PRETO, COR_HUD_DESTAQUE, COR_HUD_FRACO,
    COR_VITORIA, COR_DERROTA
)


class Botao:
    """
    Botão clicável para o menu.
    Detecta quando o mouse passa por cima (hover) e quando é clicado.
    Muda a aparência visual ao interagir.
    """

    def __init__(self, x, y, largura, altura, texto, cor_normal, cor_hover):
        """
        Args:
            x, y          : posição do canto superior esquerdo
            largura, altura: dimensões do botão em pixels
            texto         : texto exibido dentro do botão
            cor_normal    : cor da borda quando o mouse NÃO está em cima
            cor_hover     : cor da borda quando o mouse está em cima
        """
        self.rect       = pygame.Rect(x, y, largura, altura)
        self.texto      = texto
        self.cor_normal = cor_normal
        self.cor_hover  = cor_hover
        self.com_hover  = False   # True quando o mouse está sobre o botão
        self.fonte      = pygame.font.SysFont("couriernew", 16, bold=True)

    def atualizar(self, pos_mouse):
        """Verifica se o mouse está sobre o botão (para efeito hover)."""
        self.com_hover = self.rect.collidepoint(pos_mouse)

    def desenhar(self, tela):
        """Renderiza o botão com visual diferente se hover estiver ativo."""
        # Fundo escuro semi-transparente
        fundo = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        fundo.fill((10, 16, 32, 220))
        tela.blit(fundo, (self.rect.x, self.rect.y))

        # Borda: muda de cor quando o mouse está sobre o botão
        cor_borda = self.cor_hover if self.com_hover else self.cor_normal
        pygame.draw.rect(tela, cor_borda, self.rect, 2)

        # Texto centralizado dentro do botão
        cor_texto = self.cor_hover if self.com_hover else (180, 200, 240)
        surf_texto = self.fonte.render(self.texto, True, cor_texto)
        tx = self.rect.x + (self.rect.width  - surf_texto.get_width())  // 2
        ty = self.rect.y + (self.rect.height - surf_texto.get_height()) // 2
        tela.blit(surf_texto, (tx, ty))

    def foi_clicado(self, evento):
        """
        Verifica se este botão foi clicado.

        Args:
            evento: pygame.event para verificar

        Returns:
            bool: True se clique esquerdo do mouse dentro do botão
        """
        return (evento.type == pygame.MOUSEBUTTONDOWN and
                evento.button == 1 and
                self.rect.collidepoint(evento.pos))


def executar_menu(tela):
    """
    Executa o loop do menu principal.

    LOOP DO MENU:
      1. Captura eventos (fechar janela, teclas, cliques)
      2. Atualiza estado dos botões (hover)
      3. Renderiza o fundo e os elementos do menu
      4. Controla FPS

    Args:
        tela: pygame.Surface principal (800 x 600)

    Returns:
        bool: True → ir para o jogo, False → encerrar o programa
    """
    relogio = pygame.time.Clock()

    # Centro da tela
    cx = LARGURA_TELA // 2
    cy = ALTURA_TELA  // 2

    # Dimensões dos botões
    btn_l, btn_a = 220, 50

    # Botão "Jogar": verde, posicionado ligeiramente abaixo do centro
    btn_jogar = Botao(
        cx - btn_l // 2, cy + 20,
        btn_l, btn_a,
        "[ JOGAR ]",
        (0, 150, 100),   # Borda verde normal
        COR_VITORIA      # Borda verde brilhante ao hover
    )

    # Botão "Sair" — vermelho, abaixo do botão jogar
    btn_sair = Botao(
        cx - btn_l // 2, cy + 90,
        btn_l, btn_a,
        "[ SAIR ]",
        (120, 30, 30),   # Borda vermelha normal
        COR_DERROTA      # Borda vermelha brilhante ao hover
    )

    # Fontes para o menu
    fonte_titulo = pygame.font.SysFont("couriernew", 40, bold=True)
    fonte_sub    = pygame.font.SysFont("couriernew", 12)
    fonte_info   = pygame.font.SysFont("couriernew", 10)

    # Instruções de controle exibidas no menu
    controles = [
        "WASD / Setas — Mover     |     Mouse — Mirar",
        "Clique Esquerdo / Espaço — Atirar",
        "Elimine TODOS os impostores antes da zona vermelha fechar!",
    ]

    rodando = True
    while rodando:
        pos_mouse = pygame.mouse.get_pos()

        # Eventos 
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False  

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    return True    
                if evento.key == pygame.K_ESCAPE:
                    return False  
            # Clique nos botões
            if btn_jogar.foi_clicado(evento):
                return True
            if btn_sair.foi_clicado(evento):
                return False

        # Atualiza estado de hover dos botões
        btn_jogar.atualizar(pos_mouse)
        btn_sair.atualizar(pos_mouse)

        # Renderização 
        tela.fill(COR_PRETO)

        # Grade decorativa de fundo 
        _desenhar_grade_fundo(tela)

        # Título com brilho pulsante
        pulso       = abs(math.sin(pygame.time.get_ticks() * 0.0015))
        cor_titulo  = tuple(int(c * (0.7 + 0.3 * pulso)) for c in COR_HUD_DESTAQUE)
        surf_t1     = fonte_titulo.render("LABIRINTO DOS", True, cor_titulo)
        surf_t2     = fonte_titulo.render("IMPOSTORES",    True, cor_titulo)
        tela.blit(surf_t1, (cx - surf_t1.get_width() // 2, cy - 160))
        tela.blit(surf_t2, (cx - surf_t2.get_width() // 2, cy - 110))

        # Subtítulo
        sub = fonte_sub.render("MISSÃO CLASSIFICADA · AGENTE DESIGNADO", True, COR_HUD_FRACO)
        tela.blit(sub, (cx - sub.get_width() // 2, cy - 55))

        # Linha divisória decorativa
        pygame.draw.line(tela, COR_HUD_DESTAQUE,
                         (cx - 200, cy - 30), (cx + 200, cy - 30), 1)

        # Botões
        btn_jogar.desenhar(tela)
        btn_sair.desenhar(tela)

        # Instruções de controle
        for i, linha in enumerate(controles):
            surf = fonte_info.render(linha, True, COR_HUD_FRACO)
            tela.blit(surf, (cx - surf.get_width() // 2, cy + 162 + i * 16))

        # Rodapé com dica de teclado
        dica = fonte_info.render("[ ENTER ] para jogar  |  [ ESC ] para sair",
                                 True, (40, 60, 90))
        tela.blit(dica, (cx - dica.get_width() // 2, ALTURA_TELA - 24))

        pygame.display.flip()
        relogio.tick(60)

    return False


def _desenhar_grade_fundo(tela):
    """
    Desenha pontos decorativos em grade no fundo do menu.
    Cada ponto pulsa individualmente criando efeito de "onda".
    """
    cor_ponto    = (15, 25, 50)
    espacamento  = 32
    t            = pygame.time.get_ticks()

    for gx in range(0, LARGURA_TELA + espacamento, espacamento):
        for gy in range(0, ALTURA_TELA + espacamento, espacamento):
            # Pulso com base na posição — cria efeito de onda diagonal
            pulso = math.sin(t * 0.001 + gx * 0.05 + gy * 0.05)
            raio  = 1 if pulso < 0 else 2
            pygame.draw.circle(tela, cor_ponto, (gx, gy), raio)
