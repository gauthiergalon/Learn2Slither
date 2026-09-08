# Game board: snake movement, collisions, apple spawn
# Red apple as set; rewards from constants; optimized empty positions

import random

from environment.direction import Direction
from environment.snake import Food, Position, Snake
from environment.constants import (
    REWARD_GAME_OVER, REWARD_GREEN_APPLE, REWARD_RED_APPLE, REWARD_NOTHING,
)


class Board:
    def __init__(self, size: int):
        self.size = size
        self.reset()

    def reset(self) -> None:
        self.game_over = False
        self.snake = Snake([(self.size // 2, self.size // 2)])
        self.green_apples: list[Position] = []
        self.red_apple: set[Position] = set()
        self._spawn_new_green_apple()
        self._spawn_new_green_apple()
        self._spawn_new_red_apple()

    def step(self, action: Direction) -> tuple[float, bool]:
        if self.game_over:
            return REWARD_GAME_OVER, True

        dx, dy = action.value
        head_x, head_y = self.snake.head
        new_head = (head_x + dx, head_y + dy)

        if not self._is_inside(new_head):
            self.game_over = True
            return REWARD_GAME_OVER, True

        if new_head in self.snake.body[:-1]:
            self.game_over = True
            return REWARD_GAME_OVER, True

        if new_head in self.green_apples:
            food = Food.GREEN
        elif new_head in self.red_apple:
            food = Food.RED
        else:
            food = Food.NOTHING

        self.snake.move(action, food)

        if food is Food.RED:
            self.red_apple.clear()
            self._spawn_new_red_apple()
        elif food is Food.GREEN:
            self.green_apples.remove(new_head)
            self._spawn_new_green_apple()

        if len(self.snake) == 0:
            self.game_over = True
            return REWARD_GAME_OVER, True

        if food is Food.GREEN:
            return REWARD_GREEN_APPLE, False
        if food is Food.RED:
            return REWARD_RED_APPLE, False
        return REWARD_NOTHING, False

    def available_actions(self) -> tuple[Direction, ...]:
        return tuple(
            action
            for action in Direction
            if self.snake.can_change_direction(action)
        )

    def _is_inside(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size

    def _empty_positions(self) -> list[Position]:
        occupied = set(self.snake.body)
        occupied.update(self.green_apples)
        occupied.update(self.red_apple)
        return [
            (x, y)
            for x in range(self.size)
            for y in range(self.size)
            if (x, y) not in occupied
        ]

    def _spawn_new_green_apple(self) -> None:
        empty = self._empty_positions()
        if empty:
            self.green_apples.append(random.choice(empty))

    def _spawn_new_red_apple(self) -> None:
        empty = self._empty_positions()
        if empty:
            self.red_apple.add(random.choice(empty))
