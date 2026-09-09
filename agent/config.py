from dataclasses import dataclass


@dataclass(frozen=True)
class LearningConfig:
    learning_rate: float = 0.1
    discount_factor: float = 0.9
    epsilon: float = 1.0
    epsilon_decay: float = 0.9995
    minimum_epsilon: float = 0.02


DEFAULT_LEARNING_CONFIG = LearningConfig()
