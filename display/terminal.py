import sys

from environment.board import Board
from environment.constants import (
    CELL_BODY,
    CELL_EMPTY,
    CELL_GREEN,
    CELL_RED,
    CELL_WALL,
    CELL_HEAD,
)
from environment.direction import Direction

SYMBOL_COLORS = {
    CELL_HEAD: "\033[94m",
    CELL_BODY: "\033[96m",
    CELL_GREEN: "\033[92m",
    CELL_RED: "\033[91m",
    CELL_WALL: "\033[30;107m",
    CELL_EMPTY: "\033[2;37m",
}
RESET_COLOR = "\033[0m"
DIM_COLOR = "\033[2m"
MENU_COLOR = "\033[2;37m"
PROMPT_COLOR = "\033[93m"
GREEN_COLOR = "\033[92m"
RED_COLOR = "\033[91m"
WHITE_BOLD_COLOR = "\033[1;97m"
DIRECTION_COLOR = "\033[97m"
STATE_BEST_COLOR = "\033[97m"
STATE_OTHER_COLOR = "\033[90m"
STATE_VALUE_WIDTH = 19
DIRECTION_ARROWS = {
    Direction.UP: "↑",
    Direction.RIGHT: "→",
    Direction.DOWN: "↓",
    Direction.LEFT: "←",
}


class TerminalObserver:
    def render(
        self,
        board: Board,
        action: Direction,
        reward: float,
        done: bool,
        step: int,
        max_steps: int,
        qtable=None,
        step_by_step: bool = False,
    ) -> None:
        if len(board.snake.body) > 0:
            head_x, head_y = board.snake.head
        else:
            head_x, head_y = 0, 0
        reward_color = (
            GREEN_COLOR if reward > 0 else RED_COLOR if reward < 0 else DIM_COLOR
        )
        lines = [
            f"{WHITE_BOLD_COLOR}Learn2Slither - agent view{RESET_COLOR}",
            self.label_line(
                "Step",
                f"{step:>{len(str(max_steps))}}/{max_steps}",
            ),
            self.label_line(
                "Action",
                f"{DIRECTION_ARROWS[action]} {action.name:<5}",
                value_color=DIRECTION_COLOR,
            ),
            self.label_line("Head", f"({head_x:>2}, {head_y:>2})"),
            self.label_line("Length", f"{len(board.snake):>3}"),
            self.label_line("Reward", f"{reward:>7.1f}", reward_color),
            self.label_line("State", self.state_values(board, qtable)),
            "",
            self.legend_line(),
            "",
        ]
        visible = self.visible_positions(board)
        for y in range(-1, board.size + 1):
            row = []
            for x in range(-1, board.size + 1):
                pos = (x, y)
                if pos in visible:
                    symbol = self.cell_symbol(board, pos)
                else:
                    symbol = " "
                row.append(symbol)
            lines.append(" ".join(row))
        if done:
            lines.extend(["", "Episode finished."])
        elif step_by_step:
            lines.extend([
                "",
                f"{PROMPT_COLOR}Press a key in the game window "
                f"for the next step.{RESET_COLOR}",
            ])
        sys.stdout.write("\033[H\033[J" + "\n".join(lines) + "\n")
        sys.stdout.flush()

    def label_line(
        self,
        label: str,
        value: str,
        value_color: str = "",
    ) -> str:
        colored_value = f"{value_color}{value}{RESET_COLOR}" if value_color else value
        return f"{MENU_COLOR}{label}{RESET_COLOR}: {colored_value}"

    def legend_line(self) -> str:
        symbols = (
            (CELL_HEAD, "head"),
            (CELL_BODY, "snake"),
            (CELL_GREEN, "green"),
            (CELL_RED, "red"),
            (CELL_WALL, "wall"),
            (CELL_EMPTY, "empty"),
        )
        legend = " ".join(
            f"{self.color_symbol(symbol)}={name}"
            for symbol, name in symbols
        )
        return f"{MENU_COLOR}Legend{RESET_COLOR}: {legend}"

    def state_values(self, board: Board, qtable=None) -> str:
        from agent.agent import Agent

        state = Agent.state(board)
        values_by_direction = dict(zip(Direction, state[1:]))
        actions = set(board.available_actions())
        q_values = {
            direction: qtable.get(state, direction) if qtable is not None else 0.0
            for direction in actions
        }
        best_q = max(q_values.values())
        return " | ".join(
            self.state_action(
                direction,
                values_by_direction[direction] if direction in actions else None,
                q_values.get(direction),
                direction in actions and q_values[direction] == best_q,
            )
            for direction in Direction
        )

    def state_action(
        self,
        direction: Direction,
        state_value: tuple[str, int] | None,
        q_value: float | None,
        is_best: bool,
    ) -> str:
        if state_value is None or q_value is None:
            return (
                f"{STATE_OTHER_COLOR}{direction.name:<5}: "
                f"{' ' * STATE_VALUE_WIDTH}{RESET_COLOR}"
            )
        state_color = STATE_BEST_COLOR if is_best else STATE_OTHER_COLOR
        symbol = self.color_symbol(state_value[0])
        plain_value = f"({state_value[0]}, {state_value[1]:>2}, {q_value:>7.2f})"
        padding = " " * max(0, STATE_VALUE_WIDTH - len(plain_value))
        return (
            f"{state_color}{direction.name:<5}: "
            f"({symbol}{state_color}, {state_value[1]:>2}, "
            f"{q_value:>7.2f}){padding}{RESET_COLOR}"
        )

    @staticmethod
    def color_symbol(symbol: str) -> str:
        color = SYMBOL_COLORS.get(symbol, "")
        if not color:
            return symbol
        return f"{color}{symbol}{RESET_COLOR}"

    def visible_positions(self, board: Board) -> set[tuple[int, int]]:
        if len(board.snake.body) == 0:
            return set()
        head_x, head_y = board.snake.head
        positions = {(head_x, head_y)}
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            x, y = head_x, head_y
            while True:
                positions.add((x, y))
                if not board.is_inside((x, y)):
                    break
                x += dx
                y += dy
        return positions

    def cell_symbol(self, board: Board, position: tuple[int, int]) -> str:
        x, y = position
        if not board.is_inside(position):
            return self.color_symbol(CELL_WALL)
        if len(board.snake.body) > 0 and position == board.snake.head:
            return self.color_symbol(CELL_HEAD)
        if len(board.snake.body) > 0 and position in board.snake.body:
            return self.color_symbol(CELL_BODY)
        if position in board.green_apples:
            return self.color_symbol(CELL_GREEN)
        if position in board.red_apple:
            return self.color_symbol(CELL_RED)
        return self.color_symbol(CELL_EMPTY)
