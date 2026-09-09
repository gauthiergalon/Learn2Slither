from dataclasses import dataclass

from display.terminal import TerminalObserver
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
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.board = Board(map_size)
        self.agent = agent
        self.max_steps = max_steps
        self.log_actions = log_actions
        self.gui = None
        self.terminal_observer = None
        if render_enabled:
            from display.gui import GUI

            self.gui = GUI(map_size)
            self.terminal_observer = TerminalObserver()

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
            if self.gui is not None and self.terminal_observer is not None:
                if not self.gui.running:
                    break
                self.gui.render(self.board)
                self.gui.tick()
                self.terminal_observer.render(
                    self.board,
                    action,
                    reward,
                    done,
                    step,
                    self.max_steps,
                )
            if done:
                break

        self.agent.end_episode()
        return EpisodeStats(total_reward, best_length)

    def close(self) -> None:
        if self.gui is not None:
            self.gui.close()
