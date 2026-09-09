from dataclasses import dataclass
from pathlib import Path

from agent.agent import Agent
from agent.config import (
    DEFAULT_LEARNING_CONFIG,
    validate_learning_parameters,
)
from environment.game import Game


@dataclass(frozen=True)
class TrainingStats:
    episodes: int
    average_reward: float
    best_score: int


class Trainer:
    def __init__(
        self,
        map_size: int,
        learning_rate: float = DEFAULT_LEARNING_CONFIG.learning_rate,
        discount_factor: float = DEFAULT_LEARNING_CONFIG.discount_factor,
        epsilon: float = DEFAULT_LEARNING_CONFIG.epsilon,
        epsilon_decay: float = DEFAULT_LEARNING_CONFIG.epsilon_decay,
        minimum_epsilon: float = DEFAULT_LEARNING_CONFIG.minimum_epsilon,
        max_steps: int = 500,
    ):
        if not 8 <= map_size <= 100:
            raise ValueError("map_size must be between 8 and 100")
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        validate_learning_parameters(
            learning_rate,
            discount_factor,
            epsilon,
            epsilon_decay,
            minimum_epsilon,
        )
        self.agent = Agent(
            training=True,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon=epsilon,
            epsilon_decay=epsilon_decay,
            minimum_epsilon=minimum_epsilon,
        )
        self.game = Game(
            map_size,
            agent=self.agent,
            max_steps=max_steps,
            render_enabled=False,
        )

    @property
    def qtable(self):
        return self.agent.qtable

    def save_model(self, path: str | Path) -> None:
        self.agent.save_model(path)

    def load_model(self, path: str | Path) -> None:
        self.agent.load_model(path)

    def train(self, episodes: int) -> TrainingStats:
        if episodes < 1:
            raise ValueError("episodes must be positive")
        rewards: list[float] = []
        best_score = 0

        for _ in range(episodes):
            stats = self.game.run_episode()
            rewards.append(stats.reward)
            best_score = max(best_score, stats.best_length)

        average_reward = sum(rewards) / len(rewards) if rewards else 0.0
        return TrainingStats(episodes, average_reward, best_score)
