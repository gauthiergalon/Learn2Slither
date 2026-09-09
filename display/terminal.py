import sys

from environment.board import Board
from environment.direction import Direction


class TerminalObserver:
    def render(
        self,
        board: Board,
        action: Direction,
        reward: float,
        done: bool,
        step: int,
        max_steps: int,
    ) -> None:
        if len(board.snake.body) > 0:
            head_x, head_y = board.snake.head
        else:
            head_x, head_y = 0, 0
        lines = [
            "Learn2Slither - agent view",
            f"Step: {step}/{max_steps}",
            f"Action: {action.name}",
            f"Head: ({head_x}, {head_y})",
            f"Length: {len(board.snake)} | Reward: {reward:.1f}",
            "",
            "Legend: H=head S=snake G=green R=red W=wall 0=empty",
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
        sys.stdout.write("\033[H\033[J" + "\n".join(lines) + "\n")
        sys.stdout.flush()

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
            return "\033[30;47mW\033[0m"
        if len(board.snake.body) > 0 and position == board.snake.head:
            return "\033[94mH\033[0m"
        if len(board.snake.body) > 0 and position in board.snake.body:
            return "\033[96mS\033[0m"
        if position in board.green_apples:
            return "\033[92mG\033[0m"
        if position in board.red_apple:
            return "\033[91mR\033[0m"
        return "0"
