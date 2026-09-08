# Q-learning agent with compact ray vision (type, distance)
# State: direction + 4 first-visible (code, dist) tuples

import random
from pathlib import Path

from agent.qtable import QTable
from environment.board import Board
from environment.direction import Direction

State = tuple
VISION_WALL = 4


class Agent:
    def __init__(
        self,
        qtable: QTable | None = None,
        training: bool = False,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
        minimum_epsilon: float = 0.05,
    ):
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
        if not self.training:
            return
        if self._last_state is None or self._last_action is None:
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
            self.epsilon = max(self.minimum_epsilon, float(saved_epsilon))

    @classmethod
    def state(cls, board: Board) -> State:
        return (board.snake.direction,) + tuple(
            cls._ray(board, d) for d in (
                Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT,
            )
        )

    @staticmethod
    def _ray(board: Board, direction: Direction) -> tuple[int, int]:
        head_x, head_y = board.snake.head
        dx, dy = direction.value
        x, y = head_x + dx, head_y + dy
        dist = 1
        while board._is_inside((x, y)):
            pos = (x, y)
            if pos in board.snake.body:
                return (3, dist)
            if pos in board.green_apples:
                return (1, dist)
            if pos in board.red_apple:
                return (2, dist)
            x += dx
            y += dy
            dist += 1
        return (4, dist)
