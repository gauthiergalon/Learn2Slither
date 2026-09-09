from enum import Enum
from typing import Tuple

from environment.direction import Direction

Position = Tuple[int, int]


class Food(Enum):
    NOTHING = 0
    GREEN = 1
    RED = 2


class Snake:
    def __init__(self, body: list[Position]):
        self.body = body
        self.direction = Direction.RIGHT

    def can_change_direction(self, direction: Direction) -> bool:
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = direction.value
        return (new_dx, new_dy) != (-current_dx, -current_dy)

    def __len__(self) -> int:
        return len(self.body)

    @property
    def head(self) -> Position:
        return self.body[0]

    def move(self, direction: Direction, food: Food = Food.NOTHING) -> None:
        if self.can_change_direction(direction):
            self.direction = direction
        dx, dy = self.direction.value
        new_head = (self.head[0] + dx, self.head[1] + dy)

        self.body.insert(0, new_head)
        if food is not Food.GREEN:
            self.body.pop()
        if food is Food.RED:
            self.shrink()

    def shrink(self) -> None:
        if len(self.body) > 0:
            self.body.pop()
