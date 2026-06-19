
import sys
import pygame

from config import LARGURA_TELA, ALTURA_TELA, FPS, TITULO, PASTA_SONS, PASTA_MUSICAS
from menu          import executar_menu
from game_state   import EstadoJogo
import os


def carregar_audio():
    '''
    Carrega todos os recursos de áudio do jogo.
    '''
    sons = {}

    # Música de fundo
    caminho_musica = os.path.join(PASTA_MUSICAS, "musica_fundo.ogg")
    if os.path.exists(caminho_musica):
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.set_volume(0.4)   # Volume moderado
        pygame.mixer.music.play(loops=-1)    # Loop infinito
    # else: sem música — jogo continua normalmente

    # Efeitos sonoros 
    nomes_sons = {
        "tiro":        "tiro.wav",
        "explosao":    "explosao.wav",
        "coleta":      "coleta.wav",
        "zona_alerta": "zona_alerta.wav",
        "vitoria":     "vitoria.wav",
        "derrota":     "derrota.wav",
    }

    for chave, arquivo in nomes_sons.items():
        caminho = os.path.join(PASTA_SONS, arquivo)
        if os.path.exists(caminho):
            try:
                sons[chave] = pygame.mixer.Sound(caminho)
                sons[chave].set_volume(0.6)
            except pygame.error:
                sons[chave] = None   # Falhou ao carregar (ignora)
        else:
            sons[chave] = None   # Arquivo não existe (sem efeito)

    return sons


def executar_jogo(tela, sons):
    """
    Executa o loop principal do jogo.

    Cria um EstadoJogo novo e roda até o jogador fechar a janela
    ou pressionar ESC na tela inicial.

    Args:
        tela: pygame.Surface principal
        sons: dicionário com sons carregados por carregar_audio()

    Returns:
        bool: True → voltar ao menu, False → encerrar o programa
    """
    relogio    = pygame.time.Clock()
    estado     = EstadoJogo()
    zona_ativa = False   # Controla quando tocar o alerta de zona

    rodando = True
    while rodando:

        eventos = pygame.event.get()
        for evento in eventos:
            if evento.type == pygame.QUIT:
                return False   # Fechou a janela → encerra o programa

            if evento.type == pygame.KEYDOWN:
                # ESC na tela inicial → volta ao menu
                if evento.key == pygame.K_ESCAPE and estado.estado == "inicio":
                    return True


        teclas    = pygame.key.get_pressed()
        pos_mouse = pygame.mouse.get_pos()


        '''
        # Delta time: tempo real desde o último frame
            # clock.tick(FPS) aguarda o necessário para manter 60fps.
            # Limitamos dt a 100ms para evitar saltos após pausas.
        '''
        dt = min(relogio.tick(FPS), 100)

       
        # Atualizar toda a lógica do jogo
        estado.atualizar(dt, teclas, pos_mouse, eventos)

      
        # Áudio dinâmico baseado no estado do jogo
        if estado.estado == "jogando" and estado.zona.ativa:
            if not zona_ativa:
                zona_ativa = True
                # Toca alerta quando a zona ativa pela primeira vez
                if sons.get("zona_alerta"):
                    sons["zona_alerta"].play()

        if estado.estado == "fim":
            if estado.vitoria and sons.get("vitoria"):
                sons["vitoria"].play()
            elif not estado.vitoria and sons.get("derrota"):
                sons["derrota"].play()
            zona_ativa = False   # Reseta para a próxima partida


        tela.fill((5, 8, 16))   # Cor de fundo padrão (quase preto)
        estado.desenhar(tela)

        pygame.display.flip()

    return True


def main():
    """
    Função principal — inicializa o Pygame e alterna entre menu e jogo.
    """

    pygame.init()

    # Inicializa o sistema de som separadamente
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    # Configura o título da janela
    pygame.display.set_caption(TITULO)

    tela = pygame.display.set_mode(
        (LARGURA_TELA, ALTURA_TELA),
        pygame.HWSURFACE | pygame.DOUBLEBUF
    )

    # Carrega todos os recursos de áudio
    sons = carregar_audio()

    while True:
        deve_jogar = executar_menu(tela)

        if not deve_jogar:
            break   

        # Para a música do menu e inicia a do jogo (se tiver)
        pygame.mixer.music.stop()
        caminho_jogo = os.path.join(PASTA_MUSICAS, "musica_jogo.ogg")
        if os.path.exists(caminho_jogo):
            pygame.mixer.music.load(caminho_jogo)
            pygame.mixer.music.play(loops=-1)

        # Executa o jogo
        deve_continuar = executar_jogo(tela, sons)

        if not deve_continuar:
            break   


    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
