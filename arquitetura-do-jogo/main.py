
import sys
import pygame

from config     import SCREEN_W, SCREEN_H, FPS, TITLE
from menu       import run_menu
from game_state import GameState


def _inicializar_pygame():
    """Inicializa o Pygame e cria a janela principal."""
    pygame.init()
    pygame.display.set_caption(TITLE)
    return pygame.display.set_mode(
        (SCREEN_W, SCREEN_H),
        pygame.HWSURFACE | pygame.DOUBLEBUF,
    )


def _executar_partida(screen):
    """
    Executa o loop do jogo até o jogador fechar a janela ou
    retornar ao menu (ESC na tela inicial).

    Returns:
        bool: True → voltar ao menu, False → encerrar o programa

    Delta Time (dt):
        O tempo real entre dois frames (em ms) é passado para todos os sistemas
        que envolvem tempo. Isso garante que o jogo rode na mesma velocidade
        em computadores lentos (30fps) e rápidos (144fps)
    """
    clock = pygame.time.Clock()
    jogo  = GameState()

    while True:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                return False   # Fechar janela → encerra o programa
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                    and jogo.state == "start"):
                return True    # ESC na tela inicial → volta ao menu

        keys      = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()

        # Limita dt a 100ms para evitar saltos após pausas (ex: janela minimizada)
        dt = min(clock.tick(FPS), 100)

        jogo.update(dt, keys, mouse_pos, events)

        screen.fill((5, 8, 16))
        jogo.draw(screen)

        pygame.display.flip()


def main():
    """Ponto de entrada: inicializa e alterna entre menu e jogo."""
    screen = _inicializar_pygame()

    while True:
        deve_jogar = run_menu(screen)
        if not deve_jogar:
            break

        deve_continuar = _executar_partida(screen)
        if not deve_continuar:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
