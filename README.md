## Learn2Slither

Projet de snake avec une interface Pygame.

### Organisation

- `main.py` : point d'entrée minimal.
- `runtime/` : exécution de l'application et parsing CLI.
- `agent/` : apprentissage par renforcement (`QTable`, `Trainer`).
- `environment/` : règles et état du jeu (`Board`, `Snake`, `Direction`, `Game`).
- `display/` : fenêtre, événements et rendu Pygame (`GUI`).

Les modes train et view utilisent la même boucle `Game` et la même classe
`Agent`. En mode train, `Agent(training=True)` explore et met à jour la
Q-table sans ouvrir de fenêtre. En mode view, `Agent(training=False)` charge
la Q-table sans la modifier et `Game` active le GUI.

### Entraînement

Lancer un entraînement Q-learning sans ouvrir de fenêtre :

```bash
uv run python main.py --train --episodes 10000 --max-steps 500
```

Sauvegarder le modèle appris :

```bash
uv run python main.py --train --episodes 10000 --save-model models/snake.json
```

Reprendre l'entraînement d'un modèle existant :

```bash
uv run python main.py --train --episodes 10000 \
	--load-model models/snake.json \
	--save-model models/snake.json
```

`--load-model` est facultatif en mode train. S'il est fourni, le modèle est
chargé avant le nombre d'épisodes demandé. `--save-model` enregistre le modèle
à la fin de l'entraînement.

### Visualisation

Charger un modèle et afficher le snake qui joue automatiquement :

```bash
uv run python main.py --view --load-model models/snake.json
```

Le mode view ne modifie pas le modèle. La partie s'arrête après `--max-steps`
étapes ou lorsqu'une collision termine la partie.

Pendant la visualisation, le terminal affiche en direct la direction choisie,
la position et la vision en croix du serpent. L'écran est réécrit à chaque
étape au lieu d'ajouter une nouvelle ligne.

Le nombre d'épisodes et la taille de la carte peuvent être adaptés :

```bash
uv run python main.py -map-size 15 --train --episodes 5000
```
