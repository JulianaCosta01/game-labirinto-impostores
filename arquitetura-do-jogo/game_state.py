# =============================================================================
# game_state.py — Coordenador Central do Jogo
# =============================================================================
# Função: manipular todos os subsistemas.
#
# O GameState não implementa lógica de física, renderização...
# ele delega isso a cada classe especializada (Player, Enemy, Zone, etc.) e coordena as interações entre elas (colisões, pontuação, fim de jogo).


import json
import os

import pygame

from config import (
    ENEMY_SPAWN_POSITIONS, ITEM_SPAWN_POSITIONS,
    ENEMY_SPEED_BASE, ENEMY_SPEED_STEP, ENEMY_SPEED_MAX,
    PLAYER_SPAWN_COL, PLAYER_SPAWN_ROW,
    SCORE_PER_KILL, COMBO_WINDOW_MS, COMBO_MAX,
    VICTORY_TIME_BONUS, VICTORY_MAX_TIME,
    SAVE_FILE,
    C_ENEMY, C_ENEMY_GLOW,
)
from tilemap    import TileMap
from player     import Player, Bullet
from enemy      import Enemy
from zone       import Zone, Item, spawn_kill_particles, spawn_collect_particles
from hud        import HUD, draw_end_screen, draw_start_screen


'''
# 1. PERSISTÊNCIA — Recorde local
'''

def _carregar_recorde():
    """Lê o recorde do arquivo JSON(para o recorde sempre ficar salvo). Retorna 0 se não existir ou corrompido."""
    try:
        with open(SAVE_FILE, "r") as f:
            return json.load(f).get("high_score", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def _salvar_recorde(pontuacao):
    """Só atualiza o recorde se o jogador foi melhor do que antes."""
    if pontuacao > _carregar_recorde():
        with open(SAVE_FILE, "w") as f:
            json.dump({"high_score": pontuacao}, f)

'''
# 2. GAMESTATE
'''

class GameState:
    """
    Coordenador central: mantém o estado completo de uma partida e
    cuida da atualização e renderização de todos os subsistemas.
    """

    def __init__(self):
        # Subsistemas persistentes (sobrevivem entre partidas)
        self.tilemap = TileMap()
        self.hud     = HUD()

        # Recorde e contador de sessões (persistem enquanto o programa roda)
        self.recorde       = _carregar_recorde()
        self.num_sessoes   = 0
        self.state         = "start"

        # Subsistemas de partida (inicializados em new_game() )
        self.player    = None
        self.inimigos  = []
        self.projeteis = []
        self.particulas = []
        self.itens     = []
        self.zone      = None

        # Dados da partida atual
        self.pontuacao      = 0
        self.combo          = 1
        self._ultimo_kill   = 0    # ms do último kill (controle de combo)
        self.total_inimigos = 0
        self.venceu         = False
        self._inicio_ms     = 0

    '''
    # 3. NOVA PARTIDA
    '''

    def new_game(self):
        """
        Inicializa/ reinicia todos os subsistemas para uma nova partida.

        Dificuldade progressiva: a velocidade dos inimigos aumenta
        ENEMY_SPEED_STEP por sessão, até o máximo ENEMY_SPEED_MAX.
        """
        self.num_sessoes += 1

        velocidade_inimigos = min(
            ENEMY_SPEED_BASE + (self.num_sessoes - 1) * ENEMY_SPEED_STEP,
            ENEMY_SPEED_MAX,
        )

        self._resetar_dados_partida()
        self._criar_entidades(velocidade_inimigos)

        self._inicio_ms = pygame.time.get_ticks()
        self.state      = "playing"

    def _resetar_dados_partida(self):
        """Zera os contadores e flags da partida anterior."""
        self.pontuacao    = 0
        self.combo        = 1
        self._ultimo_kill = 0
        self.venceu       = False

    def _criar_entidades(self, velocidade_inimigos):
        """Jogador, inimigos, itens e zona para a nova partida."""
        self.player = Player(PLAYER_SPAWN_COL, PLAYER_SPAWN_ROW)

        self.inimigos = [
            Enemy(col=col, row=row, speed=velocidade_inimigos)
            for (row, col) in ENEMY_SPAWN_POSITIONS
        ]
        self.total_inimigos = len(self.inimigos)

        self.itens = [
            Item(col=col, row=row, item_type=tipo)
            for (row, col, tipo) in ITEM_SPAWN_POSITIONS
        ]

        self.projeteis  = []
        self.particulas = []
        self.zone       = Zone()

    '''
    # 4. TEMPO
    '''

    @property
    def elapsed_ms(self):
        """Milissegundos decorridos desde o início da partida atual."""
        return pygame.time.get_ticks() - self._inicio_ms

    @property
    def elapsed_seconds(self):
        """Segundos decorridos desde o início da partida atual."""
        return self.elapsed_ms / 1000.0

    '''
    # 5. ATUALIZAÇÃO — chamado uma vez por frame
    '''

    def update(self, dt, keys, mouse_pos, events):
        """
        Processa eventos globais e atualiza toda a lógica do jogo.

        Sequência por frame:
          1. Eventos de navegação (Enter / ESC)
          2. Jogador (movimento, mira, disparo)
          3. Inimigos (automatização de movimento)
          4. Projéteis (física, expiração por parede)
          5. Colisões: projétil → inimigo
          6. Colisão: jogador → inimigo (se sem escudo)
          7. Colisão: jogador → zona vermelha
          8. Coleta de itens
          9. Animações: partículas e itens
          10. Zona vermelha (crescimento e ativação)
          11. Verificação de condição de vitória
        """
        self._processar_eventos(events)

        if self.state != "playing":
            return

        vivos_antes    = self._contar_vivos()
        freeze_ativo   = self.player.powerups["freeze"] > 0

        self.player.update(keys, mouse_pos, dt, self.projeteis)

        for inimigo in self.inimigos:
            inimigo.update(dt, self.zone.margin, freeze_ativo)

        for projetil in self.projeteis:
            projetil.update()
        self.projeteis = [p for p in self.projeteis if p.alive]

        self._verificar_colisoes_projetil_inimigo()

        if not self.player.has_shield:
            self._verificar_colisao_jogador_inimigo()

        if self.player.alive:
            self._verificar_colisao_jogador_zona()

        self._verificar_coleta_itens()

        for item in self.itens:
            item.update(dt)
        self.particulas = [p for p in self.particulas if not p.is_dead]
        for p in self.particulas:
            p.update(dt)

        # Usa a contagem APÓS a atualização dos inimigos
        vivos_depois = self._contar_vivos()
        self.zone.update(dt, self.elapsed_seconds, vivos_depois, freeze_ativo)

        if vivos_depois == 0 and self.player.alive:
            self._acionar_vitoria()

    def _processar_eventos(self, events):
        """Trata eventos de navegação entre telas."""
        for event in events:
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_RETURN and self.state in ("start", "end"):
                self.new_game()
            if event.key == pygame.K_ESCAPE and self.state == "end":
                self.state = "start"

    def _contar_vivos(self):
        """Retorna o número de inimigos ainda vivos."""
        return sum(1 for e in self.inimigos if e.alive)

    '''
    # 6. COLISÕES
    '''

    def _verificar_colisoes_projetil_inimigo(self):
        """
        Detecta acertos de projéteis em inimigos.

        Ao acertar: projétil e inimigo são marcados como mortos,
        a pontuação é atualizada com o multiplicador de combo,
        e partículas de explosão são geradas.
        """
        for projetil in self.projeteis:
            if not projetil.alive:
                continue
            for inimigo in self.inimigos:
                if not inimigo.alive:
                    continue
                if inimigo.collides_with_bullet(projetil.x, projetil.y):
                    self._registrar_acerto(projetil, inimigo)
                    break   # um projétil elimina no máximo um inimigo

    def _registrar_acerto(self, projetil, inimigo):
        """Processa as consequências de um projétil acertar um inimigo."""
        projetil.alive = False
        inimigo.hit()
        self.player.hits += 1
        self._atualizar_combo_e_pontuacao()
        self.particulas.extend(
            spawn_kill_particles(inimigo.x, inimigo.y, C_ENEMY, C_ENEMY_GLOW)
        )

    def _atualizar_combo_e_pontuacao(self):
        """Incrementa o combo SE estiver dentro da janela de tempo, SENÃO reseta."""
        agora = pygame.time.get_ticks()
        if agora - self._ultimo_kill < COMBO_WINDOW_MS:
            self.combo = min(self.combo + 1, COMBO_MAX)
        else:
            self.combo = 1
        self._ultimo_kill = agora
        self.pontuacao   += SCORE_PER_KILL * self.combo

    def _verificar_colisao_jogador_inimigo(self):
        """Derrota por contato com inimigo (SEM escudo ativo)."""
        if not self.player.alive:
            return
        for inimigo in self.inimigos:
            if inimigo.alive and inimigo.collides_with_player(
                self.player.x, self.player.y, self.player.size
            ):
                self._acionar_derrota()
                return

    def _verificar_colisao_jogador_zona(self):
        """Derrota por contato com a zona vermelha."""
        if not self.player.alive:
            return
        if self.zone.is_player_in_zone(self.player.x, self.player.y, self.player.size):
            self._acionar_derrota()

    def _verificar_coleta_itens(self):
        """Coleta power-ups e gera partículas de confirmação."""
        for item in self.itens:
            if item.alive and item.check_collect(
                self.player.x, self.player.y, self.player.size
            ):
                self.player.activate_powerup(item.type)
                self.particulas.extend(
                    spawn_collect_particles(item.x, item.y, item.meta["color"])
                )

    '''
    # 7. FIM DE JOGO
    '''

    def _acionar_derrota(self):
        """Encerra a partida por derrota."""
        self.player.alive = False
        self.venceu       = False
        self._finalizar_partida()

    def _acionar_vitoria(self):
        """Encerra a partida por vitória e aplica bônus de tempo."""
        self.venceu     = True
        tempo_restante  = max(0.0, VICTORY_MAX_TIME - self.elapsed_seconds)
        self.pontuacao += int(tempo_restante * VICTORY_TIME_BONUS)
        self._finalizar_partida()

    def _finalizar_partida(self):
        """Procedimentos comuns ao encerrar a partida (vitória ou derrota)."""
        _salvar_recorde(self.pontuacao)
        self.recorde = _carregar_recorde()
        self.combo   = 1
        self.state   = "end"

    '''
    # 8. RENDERIZAÇÃO: chamado após update()
    '''

    def draw(self, screen):
        """
        Renderiza todos os elementos na ordem correta (painter's algorithm).

        Ordem (de trás para frente):
          1. Labirinto       (camada base estática)
          2. Itens           (no chão)
          3. Inimigos        (entidades)
          4. Projéteis       (sobre as entidades)
          5. Partículas      (efeitos visuais)
          6. Jogador         (sempre visível acima)
          7. Zona vermelha   (semi-transparente, cobre tudo)
          8. HUD             (interface, acima de tudo)
          9. Overlay de fim  (tela de resultado)
        """
        if self.state == "start":
            draw_start_screen(screen)
            return

        self.tilemap.draw(screen)

        for item     in self.itens:     item.draw(screen)
        for inimigo  in self.inimigos:  inimigo.draw(screen)
        for projetil in self.projeteis: projetil.draw(screen)
        for p        in self.particulas: p.draw(screen)

        self.player.draw(screen)
        self.zone.draw(screen)

        if self.state == "playing":
            self.hud.draw(screen, self)

        if self.state == "end":
            self._desenhar_tela_fim(screen)

    def _desenhar_tela_fim(self, screen):
        """Monta e chama draw_end_screen com os dados da partida encerrada."""
        kills = sum(1 for e in self.inimigos if not e.alive)
        draw_end_screen(
            screen,
            self.hud.font_large, self.hud.font_medium, self.hud.font_small,
            won           = self.venceu,
            score         = self.pontuacao,
            high_score    = self.recorde,
            elapsed_secs  = self.elapsed_seconds,
            kills         = kills,
            total         = self.total_inimigos,
            accuracy      = self.player.accuracy,
            session_count = self.num_sessoes,
        )

    '''
    # 9. PROPRIEDADES DE COMPATIBILIDADE COM HUD

    As propriedades abaixo garantem compatibilidade sem quebrar o HUD.
    '''

    @property
    def score(self):
        return self.pontuacao

    @property
    def high_score(self):
        return self.recorde

    @property
    def enemies(self):
        return self.inimigos

    @property
    def bullets(self):
        return self.projeteis
