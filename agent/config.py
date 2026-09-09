from dataclasses import dataclass
from math import isfinite


def validate_learning_parameters(
    learning_rate: float,
    discount_factor: float,
    epsilon: float,
    epsilon_decay: float,
    minimum_epsilon: float,
) -> None:
    values = (
        learning_rate,
        discount_factor,
        epsilon,
        epsilon_decay,
        minimum_epsilon,
    )
    if not all(isfinite(value) for value in values):
        raise ValueError("Learning parameters must be finite numbers")
    if not 0 < learning_rate <= 1:
        raise ValueError("learning_rate must be between 0 and 1")
    if not 0 <= discount_factor <= 1:
        raise ValueError("discount_factor must be between 0 and 1")
    if not 0 <= epsilon <= 1:
        raise ValueError("epsilon must be between 0 and 1")
    if not 0 < epsilon_decay <= 1:
        raise ValueError("epsilon_decay must be greater than 0 and at most 1")
    if not 0 <= minimum_epsilon <= 1:
        raise ValueError("minimum_epsilon must be between 0 and 1")
    if minimum_epsilon > epsilon:
        raise ValueError("minimum_epsilon cannot exceed epsilon")


@dataclass(frozen=True)
class LearningConfig:
    learning_rate: float = 0.1
    discount_factor: float = 0.9
    epsilon: float = 1.0
    epsilon_decay: float = 0.9995
    minimum_epsilon: float = 0.02


DEFAULT_LEARNING_CONFIG = LearningConfig()
