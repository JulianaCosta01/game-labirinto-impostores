<div align="center">

# 🎮 Labirinto dos Impostores

### Sobreviva ao caos. Elimine os impostores. Escape da Zona Vermelha.

<p align="center">
  <img src="screenshots/gameplay.gif" width="900">
</p>

Um jogo **2D de ação e sobrevivência** desenvolvido com **Python** e **Pygame**, ambientado em um universo cyberpunk neon onde cada segundo importa.

Elimine todos os impostores antes que a **Zona Vermelha** domine completamente o mapa.

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Development-2E8B57?style=for-the-badge)
![MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

</div>

---

# ✨ Destaques

### ⚡ Combate Dinâmico
Sistema de disparos rápidos com mira baseada no mouse.

### 🤖 IA dos Inimigos
Impostores perseguem o jogador e aumentam sua velocidade conforme o progresso.

### 🔥 Zona Vermelha
Uma ameaça crescente que transforma cada partida em uma corrida contra o tempo.

### 💎 Power-ups Estratégicos
Colete habilidades especiais para aumentar suas chances de sobrevivência.

### 🏆 Sistema de Combo
Eliminações consecutivas aumentam seu multiplicador de pontuação.

### 📈 Dificuldade Progressiva
Cada nova partida se torna mais desafiadora.

---

# 📸 Galeria

<p align="center">
  <img src="screenshots/print1.png" width="48%">
  <img src="screenshots/print2.png" width="48%">
</p>

<p align="center">
  <img src="screenshots/print3.png" width="48%">
  <img src="screenshots/print4.png" width="48%">
</p>

> Sugestão:
>
> - Print 1 → Menu Inicial
> - Print 2 → Gameplay
> - Print 3 → Zona Vermelha
> - Print 4 → Power-ups / Combo

---

# 🎯 Objetivo

Elimine todos os impostores antes que eles ou a Zona Vermelha eliminem você.

Durante a partida:

- 👾 Encostar em um impostor resulta em derrota.
- 🔥 A Zona Vermelha é letal.
- 🧱 As paredes bloqueiam o movimento.
- ⏳ Quanto mais tempo passa, maior o desafio.

---

# 🎮 Mecânicas

## 🔥 Zona Vermelha

A Zona Vermelha é ativada quando:

- ⏱️ 30 segundos de partida se passam

**OU**

- 👾 Restam apenas 6 impostores

Após ativada, ela começa a dominar o mapa progressivamente.

---

## 💎 Sistema de Power-ups

| Power-up | Efeito |
|-----------|-----------|
| SPD | Aumenta a velocidade do jogador |
| DBL | Disparo duplo |
| SHD | Invulnerabilidade temporária |
| FRZ | Congela a expansão da Zona Vermelha |

---

## 🏆 Sistema de Combo

Eliminar inimigos em sequência aumenta o multiplicador de pontos.

```text
x1 → x2 → x3 → ... → x10
```

Quanto maior a sequência, maior sua pontuação.

---

## 📈 Dificuldade Progressiva

A cada nova partida:

- Os impostores ficam mais rápidos.
- A pressão aumenta constantemente.
- O limite de velocidade chega a:

```text
5.0
```

---

# 🕹️ Controles

| Tecla | Ação |
|--------|--------|
| W A S D | Movimentação |
| ↑ ↓ ← → | Movimentação |
| Mouse | Mira |
| Clique Esquerdo | Atirar |
| Espaço | Atirar |
| Enter | Iniciar / Reiniciar |
| ESC | Retornar ao Menu |

---

# ⚙️ Instalação

## Clone o repositório

```bash
git clone https://github.com/seu-usuario/labirinto-impostores.git
```

## Entre na pasta

```bash
cd labirinto-impostores
```

## Instale as dependências

```bash
pip install pygame
```

## Execute o jogo

```bash
python main.py
```

---

# 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
|------------|---------|
| Python | Linguagem principal |
| Pygame | Desenvolvimento do jogo |
| JSON | Salvamento de recordes |
| POO | Estrutura e organização do código |

---

# 📂 Estrutura do Projeto

```text
labirinto_impostores/
│
├── main.py
├── menu.py
├── game_state.py
├── config.py
├── tilemap.py
├── player.py
├── enemy.py
├── zone.py
├── hud.py
├── save.json
│
└── assets/
    ├── images/
    ├── sounds/
    └── music/
```

---

# 🚀 Melhorias Implementadas

- ✅ Correção de colisões indevidas com paredes
- ✅ Reorganização completa da estrutura do projeto
- ✅ Sistema de Menu independente
- ✅ Fluxo Menu → Jogo → Menu
- ✅ Sistema de recordes locais
- ✅ HUD aprimorada
- ✅ Sistema de Combo
- ✅ Power-ups especiais
- ✅ Dificuldade progressiva

---

# 🔮 Melhorias Futuras

- [ ] Novos tipos de impostores
- [ ] Boss Fights
- [ ] Sistema de conquistas
- [ ] Ranking online
- [ ] Novos mapas
- [ ] Trilha sonora personalizada
- [ ] Suporte a Gamepad

---

# 📜 Licença

Este projeto está licenciado sob a licença **MIT**.

Consulte o arquivo **LICENSE** para mais informações.

---

<div align="center">

### Desenvolvido com ❤️ usando Python e Pygame

⭐ Se gostou do projeto, considere deixar uma estrela no repositório.

</div>