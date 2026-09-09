# Game board: snake movement, collisions, apple spawn
# Red apple as set; rewards from constants; optimized empty positions

import random

from environment.constants import (
    REWARD_GAME_OVER,
    REWARD_GREEN_APPLE,
    REWARD_NOTHING,
    REWARD_RED_APPLE,
)
from environment.direction import Direction
from environment.snake import Food, Position, Snake


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

        if not self.is_inside(new_head):
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

        previous_direction = self.snake.direction
        self.snake.move(action, food)

        if len(self.snake.body) == 0:
            self.game_over = True
            return REWARD_GAME_OVER, True

        base_reward = REWARD_NOTHING
        if food is Food.GREEN:
            base_reward = REWARD_GREEN_APPLE
        elif food is Food.RED:
            base_reward = REWARD_RED_APPLE

        reward = base_reward

        # Encourage turning when no green apple is visible.
        visible_apple = any(
            self.has_green_apple_on_ray(direction) for direction in Direction
        )
        if not visible_apple and action != previous_direction:
            reward -= 10.0

        if food is Food.RED:
            self.red_apple.clear()
            self._spawn_new_red_apple()
        elif food is Food.GREEN:
            self.green_apples.remove(new_head)
            self._spawn_new_green_apple()

        if len(self.snake) == 0:
            self.game_over = True
            return REWARD_GAME_OVER, True

        return reward, False

    def available_actions(self) -> tuple[Direction, ...]:
        return tuple(
            action
            for action in Direction
            if self.snake.can_change_direction(action)
        )

    def is_inside(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.size and 0 <= y < self.size

    def ray_positions(self, direction: Direction) -> tuple[Position, ...]:
        head_x, head_y = self.snake.head
        dx, dy = direction.value
        positions: list[Position] = []
        x, y = head_x + dx, head_y + dy
        while self.is_inside((x, y)):
            positions.append((x, y))
            x += dx
            y += dy
        return tuple(positions)

    def has_green_apple_on_ray(self, direction: Direction) -> bool:
        return any(
            position in self.green_apples
            for position in self.ray_positions(direction)
        )

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
