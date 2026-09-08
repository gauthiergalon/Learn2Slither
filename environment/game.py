# Episode loop with terminal/GUI rendering
# Wires agent and board; renders only visible cross by default

from dataclasses import dataclass
import sys

from environment.board import Board


@dataclass(frozen=True)
class EpisodeStats:
    reward: float
    best_length: int


class Game:
    def __init__(
        self,
        map_size: int,
        agent,
        max_steps: int = 100,
        render_enabled: bool = True,
        log_actions: bool = False,
    ):
        self.board = Board(map_size)
        self.agent = agent
        self.max_steps = max_steps
        self.log_actions = log_actions
        self.gui = None
        if render_enabled:
            from display.gui import GUI

            self.gui = GUI(map_size)

    def run_episode(self) -> EpisodeStats:
        self.board.reset()
        total_reward = 0.0
        best_length = len(self.board.snake)

        for step in range(1, self.max_steps + 1):
            action = self.agent.choose_action(self.board)

            reward, done = self.board.step(action)
            self.agent.observe(self.board, reward, done)
            total_reward += reward
            best_length = max(best_length, len(self.board.snake))

            if self.gui is not None:
                self.gui.render(self.board)
                self.gui.tick()
                self._render_terminal(action, reward, done, step)
            if done:
                break

        self.agent.end_episode()
        return EpisodeStats(total_reward, best_length)

    def close(self) -> None:
        if self.gui is not None:
            self.gui.close()

    def _render_terminal(
        self,
        action,
        reward: float,
        done: bool,
        step: int,
    ) -> None:
        head_x, head_y = self.board.snake.head
        lines = [
            "Learn2Slither - vue de l'agent",
            f"Etape : {step}/{self.max_steps}",
            f"Action choisie : {action.name}",
            f"Position de la tete : ({head_x}, {head_y})",
            f"Taille : {len(self.board.snake)} | Reward : {reward:.1f}",
            "",
            "Legende : H=tete S=serpent G=verte R=rouge W=mur .=vide",
            "",
        ]
        visible_positions = self._visible_positions()

        for y in range(-1, self.board.size + 1):
            row = []
            for x in range(-1, self.board.size + 1):
                position = (x, y)
                if position in visible_positions:
                    row.append(self._cell_symbol(position))
                else:
                    row.append(" ")
            lines.append(" ".join(row))

        if done:
            lines.extend(["", "Partie terminee."])

        sys.stdout.write("\033[H\033[J" + "\n".join(lines) + "\n")
        sys.stdout.flush()

    def _visible_positions(self) -> set[tuple[int, int]]:
        head_x, head_y = self.board.snake.head
        positions = {(head_x, head_y)}
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            x, y = head_x, head_y
            while True:
                positions.add((x, y))
                if not 0 <= x < self.board.size or not 0 <= y < self.board.size:
                    break
                x += dx
                y += dy
        return positions

    def _cell_symbol(self, position: tuple[int, int]) -> str:
        x, y = position
        if not 0 <= x < self.board.size or not 0 <= y < self.board.size:
            return "\033[30;47mW\033[0m"
        if position == self.board.snake.head:
            return "\033[94mH\033[0m"
        if position in self.board.snake.body:
            return "\033[96mS\033[0m"
        if position in self.board.green_apples:
            return "\033[92mG\033[0m"
        if position in self.board.red_apple:
            return "\033[91mR\033[0m"
        return "."
