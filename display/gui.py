# GUI rendering observer for snake game board
import pygame

from environment.board import Board

WINDOW_SIZE = 800
COLOR_GRID_LINE = (200, 200, 200)
COLOR_BG = (0, 0, 0)
COLOR_SNAKE = (0, 0, 255)
COLOR_GREEN_APPLE = (0, 255, 0)
COLOR_RED_APPLE = (255, 0, 0)
Color = tuple[int, int, int]


class GUI:
    def __init__(self, map_size: int):
        pygame.init()
        self.map_size = map_size
        self.cell_size = WINDOW_SIZE / map_size
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Learn2Slither")
        self.clock = pygame.time.Clock()
        self.running = True

    def draw_grid_lines(self) -> None:
        for index in range(1, self.map_size):
            position = round(index * self.cell_size)
            pygame.draw.line(
                self.screen,
                COLOR_GRID_LINE,
                (position, 0),
                (position, WINDOW_SIZE),
            )
            pygame.draw.line(
                self.screen,
                COLOR_GRID_LINE,
                (0, position),
                (WINDOW_SIZE, position),
            )

    def draw_cell(self, x: int, y: int, color: Color) -> None:
        left = round(x * self.cell_size)
        top = round(y * self.cell_size)
        right = round((x + 1) * self.cell_size)
        bottom = round((y + 1) * self.cell_size)
        rect = pygame.Rect(
            left, top, right - left, bottom - top
        )
        pygame.draw.rect(self.screen, color, rect)

    def render(self, board: Board) -> None:
        self.screen.fill(COLOR_BG)

        for (x, y) in board.green_apples:
            self.draw_cell(x, y, COLOR_GREEN_APPLE)

        for (x, y) in board.red_apple:
            self.draw_cell(x, y, COLOR_RED_APPLE)

        for (x, y) in board.snake.body:
            self.draw_cell(x, y, COLOR_SNAKE)

        self.draw_grid_lines()
        pygame.display.flip()

    def tick(self, fps: int = 10):
        self.clock.tick(fps)

    def close(self) -> None:
        pygame.quit()
