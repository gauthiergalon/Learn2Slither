## Learn2Slither

A Snake game with a Pygame interface.

### Installation

Install `uv` with the official installer:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Restart the terminal, then install the project dependencies:

```bash
uv sync
```

### Organization

- `main.py`: minimal entry point.
- `runtime/`: application execution and CLI parsing.
- `agent/`: reinforcement learning (`Agent`, `QTable`, `Trainer`, and
	`LearningConfig`).
- `environment/`: game rules and state (`Board`, `Snake`, `Direction`,
	`Game`).
- `display/`: Pygame window, events, and rendering (`GUI`).

The train and view modes use the same `Game` loop and `Agent` class. In train
mode, `Agent(training=True)` explores and updates the Q-table without opening
a window. In view mode, `Agent(training=False)` loads the Q-table without
modifying it and `Game` enables the GUI.

The default learning hyperparameters are centralized in `agent/config.py`:
learning rate `0.1`, discount factor `0.9`, initial epsilon `1.0`, epsilon
decay `0.9995`, and minimum epsilon `0.02`.

### Training


Run Q-learning training without opening a window and save the trained model:

```bash
uv run python main.py --train --map-size 10 --episodes 100000 \
	--max-steps 500 --save-model models/snake.pkl
```

Resume training from an existing model:

```bash
uv run python main.py --train --map-size 10 --episodes 100000 \
	--max-steps 500 \
	--load-model models/snake.pkl \
	--save-model models/snake.pkl
```

`--load-model` is optional in train mode. When provided, the model is loaded
before the requested number of episodes. `--save-model` saves the model at the
end of training.

Models are saved in Pickle format. The `.pkl` extension is recommended, even
though the path can be customized. The Q-table depends on the state
representation. Vision distances use fixed buckets (`1`, `2`, and `3+`), so
the same model can be used on different map sizes. Models created with an
older state representation must be retrained.

For a larger map, train directly with the target map size:

```bash
uv run python main.py --train --map-size 20 --episodes 300000 \
	--max-steps 1500 --save-model models/snake_20.pkl
```

### Visualisation

Load a model and display the Snake playing automatically:

```bash
uv run python main.py --view --map-size 10 \
	--load-model models/snake.pkl
```

To advance one step at a time, wait for the terminal prompt and press Enter:

```bash
uv run python main.py --view --step --map-size 10 \
	--load-model models/snake.pkl
```

View mode does not modify the model. The game stops after `--max-steps` steps
or when a collision ends the episode.

During visualization, the terminal displays the selected direction, position,
the three available state values (the opposite direction is ignored), and the
Snake's cross-shaped vision in real time. The screen is rewritten at each step
instead of adding a new line.

The number of episodes and map size can be adjusted:

```bash
uv run python main.py --map-size 15 --train --episodes 50000
```

### Uninstallation

To uninstall `uv` and remove the executables installed by the official
installer:

```bash
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
rm ~/.local/bin/uv ~/.local/bin/uvx
```
