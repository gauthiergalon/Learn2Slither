import random
from math import ceil
from pathlib import Path

from agent.config import (
    DEFAULT_LEARNING_CONFIG,
    validate_learning_parameters,
)
from agent.qtable import ModelError, QTable
from environment.board import Board
from environment.direction import Direction

State = tuple
VISION_WALL = 4
DISTANCE_BUCKETS = 10


class Agent:
    def __init__(
        self,
        qtable: QTable | None = None,
        training: bool = False,
        learning_rate: float = DEFAULT_LEARNING_CONFIG.learning_rate,
        discount_factor: float = DEFAULT_LEARNING_CONFIG.discount_factor,
        epsilon: float = DEFAULT_LEARNING_CONFIG.epsilon,
        epsilon_decay: float = DEFAULT_LEARNING_CONFIG.epsilon_decay,
        minimum_epsilon: float = DEFAULT_LEARNING_CONFIG.minimum_epsilon,
    ):
        validate_learning_parameters(
            learning_rate,
            discount_factor,
            epsilon,
            epsilon_decay,
            minimum_epsilon,
        )
        self.qtable = qtable or QTable()
        self.training = training
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.minimum_epsilon = minimum_epsilon
        self._last_state: State | None = None
        self._last_action: Direction | None = None

    def choose_action(self, board: Board) -> Direction:
        state = self.state(board)
        available_actions = board.available_actions()
        if self.training and random.random() < self.epsilon:
            action = random.choice(available_actions)
        else:
            action = self.qtable.best_action(state, available_actions)
        self._last_state = state
        self._last_action = action
        return action

    def observe(self, board: Board, reward: float, done: bool) -> None:
        if (
            not self.training
            or self._last_state is None
            or self._last_action is None
        ):
            return
        if done:
            next_value = 0.0
        else:
            next_state = self.state(board)
            next_value = max(
                self.qtable.get(next_state, action)
                for action in board.available_actions()
            )
        current = self.qtable.get(self._last_state, self._last_action)
        target = reward + self.discount_factor * next_value
        self.qtable.set(
            self._last_state,
            self._last_action,
            current + self.learning_rate * (target - current),
        )

    def end_episode(self) -> None:
        if self.training:
            self.epsilon = max(
                self.minimum_epsilon,
                self.epsilon * self.epsilon_decay,
            )
        self._last_state = None
        self._last_action = None

    def save_model(self, path: str | Path) -> None:
        self.qtable.metadata["epsilon"] = self.epsilon
        self.qtable.save(path)

    def load_model(self, path: str | Path) -> None:
        self.qtable = QTable.load(path)
        saved_epsilon = self.qtable.metadata.get("epsilon")
        if saved_epsilon is not None:
            try:
                loaded_epsilon = float(saved_epsilon)
            except (TypeError, ValueError) as error:
                raise ModelError(
                    "Model metadata contains an invalid epsilon"
                ) from error
            if not 0 <= loaded_epsilon <= 1:
                raise ModelError(
                    "Model metadata epsilon must be between 0 and 1"
                )
            self.epsilon = max(self.minimum_epsilon, loaded_epsilon)

    @classmethod
    def state(cls, board: Board) -> State:
        return (board.snake.direction,) + tuple(
            cls._ray(board, d)
            for d in (
                Direction.UP,
                Direction.RIGHT,
                Direction.DOWN,
                Direction.LEFT,
            )
        )

    @staticmethod
    def _ray(board: Board, direction: Direction) -> tuple[int, int]:
        positions = board.ray_positions(direction)
        for dist, pos in enumerate(positions, start=1):
            norm = max(
                1,
                ceil(dist / max(board.size, 1) * DISTANCE_BUCKETS),
            )
            if pos in board.snake.body:
                return (3, norm)
            if pos in board.green_apples:
                return (1, norm)
            if pos in board.red_apple:
                return (2, norm)
        norm = max(
            1,
            ceil(
                (len(positions) + 1) / max(board.size, 1) * DISTANCE_BUCKETS,
            ),
        )
        return (VISION_WALL, min(DISTANCE_BUCKETS, norm))
