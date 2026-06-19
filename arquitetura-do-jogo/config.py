# =============================================================================
# config.py: Configurações Globais do Jogo
# =============================================================================

import os

PASTA_BASE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_ASSETS = os.path.join(PASTA_BASE, "assets")

# Subpastas de assets 
PASTA_IMAGENS = os.path.join(PASTA_ASSETS, "images")
PASTA_SONS    = os.path.join(PASTA_ASSETS, "sounds")
PASTA_MUSICAS = os.path.join(PASTA_ASSETS, "music")


# CONFIGURAÇÕES DA JANELA DO JOGO
LARGURA_TELA = 800        
ALTURA_TELA  = 600        
FPS          = 60        
TITULO       = "Labirinto dos Impostores" 


TAMANHO_TILE = 32   # Tamanho de cada célula do labirinto em pixels

LAYOUT_MAPA = [
    "#########################",
    "#.....#............#SSI.#",  
    "#.##..#.####.####.####..#",  
    "#.#...........#.........#",  
    "#.#.#####..#.###.#####..#",  
    "#...#........#CC.#......#",  
    "###.#.##.#...###.#.###..#", 
    "#...#....#.......#......#",
    "#.######.#D######.####..#",
    "#........#.........#....#",
    "#.######.###ETTE##.#.#..#",  
    "#.#....#.D...TT......#..#", 
    "#.#.##.#.##.......####..#",  
    "#........#Q......#...#..#", 
    "#..GGGGG.#######D#.#....#",  
    "##.GpppG.#...#.#.#.###..#",  
    "#..#ppp#...#.....#......#",
    "#########################",
]

# Dimensões 
LINHAS_MAPA  = len(LAYOUT_MAPA)
COLUNAS_MAPA = len(LAYOUT_MAPA[0])
LARGURA_MAPA = COLUNAS_MAPA * TAMANHO_TILE   
ALTURA_MAPA  = LINHAS_MAPA  * TAMANHO_TILE   


# CONFIGURAÇÕES DO JOGADOR
VELOCIDADE_JOGADOR     = 2.8   
TAMANHO_JOGADOR        = 9     # Raio de colisão do jogador em pixels
COOLDOWN_DISPARO       = 280   # Tempo mínimo entre disparos (ms)
VELOCIDADE_PROJETIL    = 7.0   
VIDA_PROJETIL          = 1.0   # Vida do projétil (decai 0.02 por frame → ~50 frames)


# CONFIGURAÇÕES DOS IMPOSTORES (INIMIGOS)
VELOCIDADE_INIMIGO_BASE = 2.0   # Velocidade inicial dos inimigos
VELOCIDADE_INIMIGO_PASSO = 0.3  # Aumento de velocidade a cada nova partida
VELOCIDADE_INIMIGO_MAX   = 5.0  # Velocidade máxima permitida
TAMANHO_INIMIGO          = 9    # Raio de colisão do inimigo em pixels

# Posições iniciais dos impostores no mapa [linha, coluna]
POSICOES_INIMIGOS = [
    (1, 18), (1, 12), (1,  4),
    (3, 22), (3, 10),
    (5,  5), (5, 18),
    (7, 12), (7, 22),
    (9,  2), (9, 16),
    (11,10), (11,22),
    (13, 5), (13,20),
    (15,14), (15, 2),
    (15,18), (16, 9),
]

# Posições dos itens especiais [linha, coluna, tipo]
POSICOES_ITENS = [
    (3,  6, "velocidade"),
    (7,  5, "duplo"),
    (11, 5, "escudo"),
    (15,10, "congelar"),
]

# POWER-UPS (ITENS ESPECIAIS)
DURACAO_POWERUP = 5000  

# ZONA VERMELHA (ÁREA DE FECHAMENTO)
TEMPO_ATIVAR_ZONA    = 30     
INIMIGOS_ATIVAR_ZONA = 6      
VELOCIDADE_ZONA      = 0.008  # Pixels que a zona avança por frame (cresce devagar)
ESPESSURA_ZONA       = 40     


# SISTEMA DE PONTUAÇÃO
PONTOS_POR_KILL   = 100    # Pontos base por eliminar um impostor
JANELA_COMBO_MS   = 2000   # Tempo máximo entre kills para manter o combo (ms)


'''
# PALETA DE CORES 
'''
# Cores base do cenário
COR_PRETO        = (  5,   8,  16)   # Fundo escuro do jogo
COR_PAREDE       = ( 10,  15,  30)   # Cor de fallback dos blocos de parede (sem sprite)
COR_BORDA_PAREDE = ( 26,  42,  74)   # Borda das paredes (detalhe visual)
COR_PISO         = (  6,  12,  28)   # Cor do piso do corredor (mantido escuro/discreto)
COR_PISO_ALT     = (  8,  16,  36)   # Cor alternada do piso (xadrez sutil)

# Cores do jogador
COR_JOGADOR      = (  0, 212, 255)   # Ciano brilhante — corpo do jogador
COR_JOGADOR_GUN  = (  0, 160, 200)   # Azul mais escuro — detalhe frontal
COR_PROJETIL     = (  0, 255, 200)   # Verde-ciano — projéteis disparados

# Cores dos impostores
COR_INIMIGO      = (255,  34,  68)   # Vermelho neon — corpo do inimigo
COR_NUCLEO_INIMIGO = (255, 180, 180)   # Rosa claro — núcleo central (olho)
COR_BRILHO_INIMIGO = (200,  0,  30)  # Vermelho escuro — brilho ao redor

# Cores da zona vermelha
COR_ZONA_FILL  = (180,   0,  20)   # Vermelho escuro — preenchimento da zona
COR_ZONA_BORDA = (255,  30,  60)   # Vermelho brilhante — borda da zona

# Cores do HUD (interface)
COR_HUD_BG     = (  8,  12,  22)   # Fundo escuro da barra de status
COR_HUD_TEXTO  = (224, 232, 255)   # Texto claro — informações gerais
COR_HUD_FRACO  = ( 74, 111, 165)   # Azul apagado — labels e rodapés
COR_HUD_DESTAQUE = (0, 212, 255)   # Ciano — valores importantes

# Cores especiais
COR_COMBO        = (255, 221,  68)  # Amarelo — indicador de combo
COR_ITEM_VELOC   = (255, 221,  68)  # Amarelo — item de velocidade
COR_ITEM_DUPLO   = (255, 107,  53)  # Laranja — item de tiro duplo
COR_ITEM_ESCUDO  = (  0, 212, 255)  # Ciano — item de escudo
COR_ITEM_CONGEL  = (136, 238, 255)  # Azul claro — item de congelamento

# Cores de resultado
COR_VITORIA  = (  0, 255, 180)   # Verde — tela de vitória
COR_DERROTA  = (255,  34,  68)   # Vermelho — tela de derrota
COR_BRANCO   = (255, 255, 255)   # Branco puro — destaques finais

'''
# ASSETS DE TILES — Laboratório Abandonado 
#   Todos os arquivos têm 32x32 pixels (exceto o tanque, que tem 32x64).
'''
PASTA_TILES = os.path.join(PASTA_IMAGENS, "tiles")

SPRITE_PAREDE          = os.path.join(PASTA_TILES, "parede.png")         
SPRITE_PAREDE_CLARA    = os.path.join(PASTA_TILES, "parede_clara.png")    
SPRITE_TANQUE          = os.path.join(PASTA_TILES, "tanque.png")          
SPRITE_CONSOLE         = os.path.join(PASTA_TILES, "console.png")        
SPRITE_PAINEL          = os.path.join(PASTA_TILES, "painel.png")          
SPRITE_CAIXA           = os.path.join(PASTA_TILES, "caixa.png")           
SPRITE_LIQUIDO_RADIOATIVO = os.path.join(PASTA_TILES, "liquido_radioativo.png")  

SPRITE_PAINEL_PEQUENO   = os.path.join(PASTA_TILES, "painel_pequeno.png")   
SPRITE_PAINEL_ALERTA    = os.path.join(PASTA_TILES, "painel_alerta.png")   
SPRITE_SERVIDOR         = os.path.join(PASTA_TILES, "servidor.png")         
SPRITE_ARMARIO          = os.path.join(PASTA_TILES, "armario.png")         
SPRITE_ESTANTE_QUIMICA = os.path.join(PASTA_TILES, "estante_quimica_torre.png")
SPRITE_BANCADA_QUIMICA = os.path.join(PASTA_TILES, "bancada_quimica.png")

SPRITE_GRADE_VERMELHA  = os.path.join(PASTA_TILES, "grade_vermelha.png")  
SPRITE_PLACA_RADIACAO  = os.path.join(PASTA_TILES, "placa_radiacao.png")   

'''
# Cada letra que aparece no LAYOUT_MAPA mapeia para um tipo de objeto:
#   letra: (nome_sprite, tem_colisao, largura_tiles, altura_tiles)
'''
TILES_DECORATIVOS = {
    'T': ("tanque",          True,  1, 2),
    'C': ("console",         True,  2, 2),
    'A': ("painel_alerta",   True,  1, 2),
    'P': ("painel_pequeno",  True,  1, 2),
    'S': ("servidor",        True,  1, 2),
    'E': ("estante_quimica", True,  1, 2),
    'R': ("armario",         True,  1, 3),
    'G': ("grade_vermelha",  True,  1, 1),
    'X': ("placa_radiacao",  True,  1, 1),
    'B': ("caixa",           True,  1, 1),
    'I': ("painel",          True,  1, 1),
    'Q': ("bancada_quimica", True,  1, 1),
}


RAIO_ATIVACAO_PORTA   = 70     # Distância em pixels para a porta começar a abrir
VELOCIDADE_PORTA      = 0.08   

COR_BRILHO_PISCINA = (80, 255, 140)   # Cor do brilho pulsante sobre a piscina

COR_DEMARCACAO_PISO = (90, 80, 50)   

DEMARCACOES_PISO = [
    (22, 2, 2, 5),    # GRUPO 1 — Painéis+Servidores: painel_alerta|painel_pequeno + gap + servidor (L2-6, cols 22-23)
    (22, 10, 2, 2),   # GRUPO 2 — Equipamentos: estante_quimica (L10-11, cols 22-23)
    (22, 13, 2, 3),   # GRUPO 3 — Armazenamento: armario (L13-15, cols 22-23)
]

