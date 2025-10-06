# Flappy Bird NEAT

This is a Flappy Bird implementation that uses NEAT (NeuroEvolution of Augmenting Topologies) to evolve neural networks that can play the game automatically.

## What is NEAT?

NEAT is an evolutionary algorithm that evolves both the weights and topology of neural networks. It starts with simple networks and gradually adds complexity through mutations, creating more sophisticated behaviors over generations.

## Features

- **AI Training**: Evolves neural networks over 200 generations to play Flappy Bird
- **Demo Mode**: Watch the best evolved bird play automatically
- **Manual Mode**: Play the game yourself with keyboard controls
- **Fitness System**: Birds are rewarded for:
  - Distance traveled (2 points per frame)
  - Staying in the middle 50% of screen height (1 point per frame)
  - Passing through pipes (50 bonus points)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Train a New Bird
```bash
python flappy_bird.py train
```
This will run NEAT for 200 generations and save the best bird to `best_bird.pkl`.

### Watch the Best Bird Play
```bash
python flappy_bird.py demo
```
This loads the saved best bird and watches it play. Controls:
- **ESC**: Quit
- **R**: Restart
- Auto-restarts after bird dies
#### The very best bird: epic bird
Currently the demo runs the epic bird, which is the best bird i have trained and is stored in the epic_bird.pkl file.

### Play Manually
```bash
python flappy_bird.py manual
```
Control the bird yourself using the **SPACEBAR** to jump.

### Default Behavior
```bash
python flappy_bird.py
```
If a trained bird exists, it will demo. Otherwise, it will train first then demo.

## Neural Network Architecture

The neural network receives 5 inputs:
1. **Bird Y Position** (normalized 0-1)
2. **Bird Velocity** (normalized)
3. **Distance to Next Pipe** (normalized)
4. **Top Pipe Height** (normalized)
5. **Bottom Pipe Y Position** (normalized)

The network outputs a single value:
- **> 0.5**: Jump
- **≤ 0.5**: Don't jump

## NEAT Configuration

Key settings in [`neat_config.txt`](neat_config.txt):
- **Population Size**: 100 birds per generation
- **Generations**: 200 (no fitness threshold)
- **Mutation Rates**: High weight mutation (0.8) for exploration
- **Topology Evolution**: 20% chance to add nodes/connections
- **Species Protection**: Groups similar networks for diversity

## How It Works

1. **Generation 0**: 100 random neural networks control birds
2. **Evaluation**: Each bird plays until death, accumulating fitness
3. **Selection**: Best performers reproduce, worst are eliminated
4. **Mutation**: Offspring get mutated weights and sometimes new nodes/connections
5. **Repeat**: Process continues for 200 generations

The algorithm typically learns to:
- Navigate through pipes consistently
- Maintain stable flight patterns
- React appropriately to different pipe heights
- Achieve scores of 50+ pipes after training

## Files Generated

- **`best_bird.pkl`**: Saved best neural network (created after training)

## Project Structure

```
FlappyBird/
├── flappy_bird.py      # Main game and NEAT implementation
├── neat_config.txt     # NEAT algorithm configuration
├── requirements.txt    # Python dependencies
├── Readme.md          # This file
└── best_bird.pkl      # Generated: best trained bird
```

## Clone the project and play with different configurations in the `neat_config.txt` file, see if you can't beat the epic_bird!!