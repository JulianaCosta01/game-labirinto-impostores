<div align="center">

# 🎮 Labirinto dos Impostores

### Sobreviva ao caos. Elimine os impostores. Escape da Zona Vermelha.

<p align="center">
  <img src="screenshots/gameplay.gif" width="900">
</p>

Um jogo 2D de ação e sobrevivência desenvolvido em **Python** utilizando **Pygame-ce**, com arquitetura modular orientada a objetos, sistema de IA para inimigos, gerenciamento centralizado de estados, progressão dinâmica de dificuldade e persistência local de recordes.

<br>

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pygame-ce](https://img.shields.io/badge/Pygame--ce-2E8B57?style=for-the-badge)
![MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

</div>

---

# 🚀 Principais Funcionalidades

### Combate Dinâmico

Sistema de disparos rápidos com mira baseada no mouse.

### IA dos Inimigos

Impostores perseguem o jogador e aumentam sua velocidade conforme o progresso da partida.

### Zona Vermelha

Uma ameaça crescente que transforma cada partida em uma corrida contra o tempo.

### Power-ups Estratégicos

Itens especiais que alteram temporariamente as capacidades do jogador.

### Sistema de Combo

Eliminações consecutivas aumentam o multiplicador de pontuação.

### Dificuldade Progressiva

Os inimigos tornam-se mais rápidos a cada nova partida.

---

# 🏗️ Arquitetura

O projeto foi desenvolvido com foco em modularização, separação de responsabilidades e organização orientada a objetos.

| Módulo | Responsabilidade |
|---------|---------|
| `main.py` | Inicialização e loop principal |
| `game_state.py` | Gerenciamento central dos sistemas do jogo |
| `player.py` | Movimentação, disparos e projéteis |
| `enemy.py` | IA e comportamento dos inimigos |
| `tilemap.py` | Labirinto e sistema de colisões |
| `zone.py` | Zona Vermelha e power-ups |
| `hud.py` | Interface e informações da partida |
| `menu.py` | Navegação e menu inicial |

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

---

# 🎯 Objetivo

Elimine todos os impostores antes que eles ou a Zona Vermelha eliminem você.

Durante a partida:

- Encostar em um impostor resulta em derrota.
- A Zona Vermelha é letal.
- As paredes bloqueiam o movimento.
- Quanto mais tempo passa, maior o desafio.

---

# 🎮 Mecânicas

## Zona Vermelha

A Zona Vermelha é ativada quando:

- 30 segundos de partida se passam

**OU**

- Restam apenas 6 impostores

Após ativada, ela começa a dominar o mapa progressivamente.

---

## Sistema de Power-ups

| Power-up | Efeito |
|-----------|-----------|
| SPD | Aumenta a velocidade do jogador |
| DBL | Disparo duplo |
| SHD | Invulnerabilidade temporária |
| FRZ | Congela a expansão da Zona Vermelha |

---

## Sistema de Combo

Eliminar inimigos em sequência aumenta o multiplicador de pontos.

```text
x1 → x2 → x3 → ... → x10
```

Quanto maior a sequência, maior sua pontuação.

---

## Dificuldade Progressiva

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

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Clonar o repositório

```bash
git clone https://github.com/JulianaCosta01/game-labirinto-impostores.git
cd game-labirinto-impostores
```

### Instalar dependências

```bash
pip install pygame-ce
```

### Executar o projeto

```bash
python main.py
```

---

# 🛠️ Tecnologias Utilizadas

| Tecnologia | Utilização |
|------------|------------|
| Python | Linguagem principal |
| Pygame-ce | Framework para desenvolvimento do jogo |
| JSON | Persistência de recordes locais |
| Programação Orientada a Objetos | Organização e arquitetura do projeto |

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

# 📜 Licença

Este projeto está licenciado sob a licença **MIT**.

Consulte o arquivo **LICENSE** para mais informações.

---

<div align="center">

⭐ Se este projeto foi interessante para você, considere deixar uma estrela no repositório.

</div>