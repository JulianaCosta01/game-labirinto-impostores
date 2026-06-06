# =============================================================================
# config.py (Configurações Globais do Jogo)
# =============================================================================
# Aqui ficam centralizadas TODAS as constantes. Modificar afeta o jogo inteiro

import os

'''
# 1. DIRETÓRIOS
'''
# Caminhos absolutos para garantir funcionamento em qualquer sistema operacional
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVE_FILE  = os.path.join(BASE_DIR, "save.json")

'''
# 2. JANELA E RENDERIZAÇÃO
'''
SCREEN_W = 800
SCREEN_H = 600
FPS      = 60
TITLE    = "Labirinto dos Impostores"

'''
# 3. LABIRINTO (TILE MAP)

O mapa é uma lista de strings onde cada caractere representa uma célula:
    '#' → parede sólida (intransponível)
    '.' → corredor transitável

Dimensões: 25 colunas × 19 linhas → 800 × 608 pixels no total.
TILE_SIZE define quantos pixels cada célula ocupa na tela.
'''

TILE_SIZE = 32

MAP_LAYOUT = [
    "#########################",
    "#.....#......#.....#....#",
    "#.##.#.####.#.###.#.##..#",
    "#.#...........#.........#",
    "#.#.######.#.##.######..#",
    "#...#....#...#...#......#",
    "###.#.##.#.#####.#.###..#",
    "#...#....#.......#......#",
    "#.######.#.######.####..#",
    "#........#.........#....#",
    "#.######.#########.#.#..#",
    "#.#....#.............#..#",
    "#.#.##.#.########.####..#",
    "#...#....#.......#...#..#",
    "##.##.##.#.###.#.#.###..#",
    "#......#...#...#.#......#",
    "#.####.###.#.###.#####..#",
    "#.#........#............#",
    "#########################",
]

# Derivados calculados automaticamente (favor, não editar diretamente)
MAP_ROWS = len(MAP_LAYOUT)
MAP_COLS = len(MAP_LAYOUT[0])
MAP_W    = MAP_COLS * TILE_SIZE   # 800 px
MAP_H    = MAP_ROWS * TILE_SIZE   # 608 px

'''
# 4. JOGADOR E PROJÉTEIS
'''

PLAYER_SPEED          = 2.8    # pixels avançados por frame na velocidade base
PLAYER_SIZE           = 9      # raio do círculo de colisão em pixels
PLAYER_SHOT_COOLDOWN  = 280    # intervalo mínimo entre disparos (ms)
PLAYER_SPEED_BOOST    = 1.7    # multiplicador de velocidade com power-up SPD
PLAYER_SPAWN_COL      = 1      # coluna inicial do jogador no mapa
PLAYER_SPAWN_ROW      = 1      # linha inicial do jogador no mapa

BULLET_SPEED          = 7.0    # pixels avançados por frame
BULLET_LIFE           = 1.0    # vida inicial; decai 0.02/frame (~50 frames = ~0.8s)
BULLET_DECAY_RATE     = 0.02   # quanto a vida decai por frame
BULLET_RADIUS         = 3      # raio visual e de colisão do projétil
DOUBLE_SHOT_OFFSET    = 4      # distância lateral entre os dois projéteis do tiro duplo

'''
# 5. INIMIGOS E SPAWNS
'''
ENEMY_SPEED_BASE = 2.0   # velocidade na primeira partida
ENEMY_SPEED_STEP = 0.3   # incremento por sessão
ENEMY_SPEED_MAX  = 5.0   # teto de velocidade
ENEMY_SIZE       = 9     # raio do círculo de colisão

# Intervalo entre mudanças espontâneas de direção do inimigo
ENEMY_DIRECTION_CHANGE_INTERVAL = 800   # ms
ENEMY_DIRECTION_CHANGE_CHANCE   = 0.35  # probabilidade (0–1) de mudar na janela
ENEMY_COLLISION_COOLDOWN        = 120   # ms de pausa após colidir com parede

# Posições de spawn: (linha, coluna), com distribuição uniforme no labirinto
ENEMY_SPAWN_POSITIONS = [
    (1, 18), (1, 12), (1,  4),
    (3, 22), (3, 10),
    (5,  5), (5, 18),   
    (7, 12), (7, 22),
    (9,  2), (9, 16),
    (11,10), (11,22),
    (13, 5), (13,20),
    (15,14), (15, 2),
    (17,18), (17, 9),
]

# Posições dos itens: (linha, coluna, tipo)
ITEM_SPAWN_POSITIONS = [
    (3,  6, "speed"),
    (7,  5, "double"),
    (11, 5, "shield"),
    (15,10, "freeze"),
]

# Metadados visuais dos itens (cor e rótulo exibido na tela)
ITEM_META = {
    "speed":  {"color": (255, 221,  68), "label": "SPD"},
    "double": {"color": (255, 107,  53), "label": "DBL"},
    "shield": {"color": (  0, 212, 255), "label": "SHD"},
    "freeze": {"color": (136, 238, 255), "label": "FRZ"},
}

ITEM_COLLECT_RADIUS = 14   # raio de captura além do raio do jogador

'''
# 6. ZONA VERMELHA

A zona avança dos 4 lados simultaneamente.
Ativação por qualquer uma das duas condições abaixo.
'''

ZONE_TIME_TRIGGER  = 30      # segundos decorridos para ativar (condição 1)
ZONE_ENEMY_TRIGGER = 6       # inimigos restantes para ativar (condição 2)
ZONE_SHRINK_RATE   = 0.008   # pixels que a margem avança por frame (normalizado a 60fps)
ZONE_THICKNESS     = 40      # espessura visual mínima da faixa vermelha

'''
# 7. PONTUAÇÃO E PROGRESSÃO
'''

SCORE_PER_KILL      = 100    # pontos base por eliminação de inimigo
COMBO_WINDOW_MS     = 2000   # janela para encadear combo (ms)
COMBO_MAX           = 10     # multiplicador máximo de combo
VICTORY_TIME_BONUS  = 10     # pontos por segundo restante abaixo de MAX_EXPECTED_TIME
VICTORY_MAX_TIME    = 120.0  # tempo máximo esperado para calcular bônus (segundos)

'''
# 8. POWER-UPS
'''

POWERUP_DURATION = 5000   # duração de qualquer power-up em ms

'''
# 9. PALETA DE CORES 

Explicação de nomes:
  C_<ALVO>         → cor principal do elemento
  C_<ALVO>_<DETALHE> → variação do elemento
'''
# Labirinto
C_BLACK        = (  5,   8,  16)
C_WALL         = ( 10,  15,  30)
C_WALL_BORDER  = ( 26,  42,  74)
C_WALL_SHINE   = ( 30,  50,  90)   # brilho do topo das paredes
C_FLOOR        = (  6,  12,  28)
C_FLOOR_ALT    = (  8,  16,  36)

# Jogador
C_PLAYER       = (  0, 212, 255)
C_PLAYER_GUN   = (  0, 160, 200)
C_PLAYER_GLOW  = (  0, 212, 255)   # alfa 40 aplicado no draw
C_PLAYER_CORE  = (200, 255, 255)
C_SHIELD_RING  = (  0, 150, 200)

# Projétil
C_BULLET       = (  0, 255, 200)
C_BULLET_CORE  = (200, 255, 255)

# Inimigos
C_ENEMY        = (255,  34,  68)
C_ENEMY_CORE   = (255, 180, 180)
C_ENEMY_GLOW   = (200,   0,  30)
C_ENEMY_PUPIL  = ( 80,   0,   0)

# Zona vermelha
C_ZONE_FILL    = (180,   0,  20)
C_ZONE_EDGE    = (255,  30,  60)

# HUD
C_HUD_BG       = (  8,  12,  22)
C_HUD_TEXT     = (224, 232, 255)
C_HUD_DIM      = ( 74, 111, 165)
C_HUD_ACCENT   = (  0, 212, 255)

# Itens e efeitos especiais
C_COMBO        = (255, 221,  68)

# Telas de resultado
C_WIN          = (  0, 255, 180)
C_LOSE         = (255,  34,  68)
C_WHITE        = (255, 255, 255)
