"""Interactive maze generator and solver built with Pygame."""

from __future__ import annotations

import random
from collections import deque

import pygame


WIDTH = 1120
HEIGHT = 820
GRID_AREA = pygame.Rect(80, 135, 960, 560)
MIN_SIZE = 5
MAX_SIZE = 30

BACKGROUND = (18, 25, 38)
PANEL = (28, 38, 55)
WALL = (222, 231, 245)
TEXT = (242, 246, 252)
MUTED = (163, 178, 199)
ACCENT = (80, 190, 255)
GREEN = (68, 211, 145)
ORANGE = (255, 177, 82)


class Maze:
    """A grid maze whose cell walls are stored in N, E, S, W order."""

    DIRECTIONS = ((-1, 0, 0, 2), (0, 1, 1, 3), (1, 0, 2, 0), (0, -1, 3, 1))

    def __init__(self, rows: int, columns: int, generated: bool = False) -> None:
        self.rows = rows
        self.columns = columns
        self.walls = [[[True, True, True, True] for _ in range(columns)] for _ in range(rows)]
        if generated:
            self.generate()

    def generate(self) -> None:
        """Carve a connected maze using randomized depth-first search."""
        visited = {(0, 0)}
        stack = [(0, 0)]
        while stack:
            row, column = stack[-1]
            options = [
                (row + dr, column + dc, wall, opposite)
                for dr, dc, wall, opposite in self.DIRECTIONS
                if 0 <= row + dr < self.rows
                and 0 <= column + dc < self.columns
                and (row + dr, column + dc) not in visited
            ]
            if not options:
                stack.pop()
                continue
            next_row, next_column, wall, opposite = random.choice(options)
            self.walls[row][column][wall] = False
            self.walls[next_row][next_column][opposite] = False
            visited.add((next_row, next_column))
            stack.append((next_row, next_column))

    def toggle_wall(self, row: int, column: int, wall: int) -> bool:
        """Toggle an internal wall and its matching neighbor wall."""
        dr, dc, _, opposite = self.DIRECTIONS[wall]
        next_row, next_column = row + dr, column + dc
        if not (0 <= next_row < self.rows and 0 <= next_column < self.columns):
            return False
        is_opening = self.walls[row][column][wall]
        self.walls[row][column][wall] = not is_opening
        self.walls[next_row][next_column][opposite] = not is_opening
        return True

    def neighbors(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        row, column = cell
        result = []
        for dr, dc, wall, _ in self.DIRECTIONS:
            next_row, next_column = row + dr, column + dc
            if (
                not self.walls[row][column][wall]
                and 0 <= next_row < self.rows
                and 0 <= next_column < self.columns
            ):
                result.append((next_row, next_column))
        return result

    def solve(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> tuple[list[tuple[int, int]], list[tuple[int, int]] | None]:
        """Return BFS exploration order and a shortest path, if one exists."""
        queue = deque([start])
        previous: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        explored = []
        while queue:
            cell = queue.popleft()
            explored.append(cell)
            if cell == goal:
                break
            for neighbor in self.neighbors(cell):
                if neighbor not in previous:
                    previous[neighbor] = cell
                    queue.append(neighbor)
        if goal not in previous:
            return explored, None
        path = []
        cell: tuple[int, int] | None = goal
        while cell is not None:
            path.append(cell)
            cell = previous[cell]
        path.reverse()
        return explored, path


def centered_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    center: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    font: pygame.font.Font,
    mouse: tuple[int, int],
    enabled: bool = True,
) -> None:
    hovered = rect.collidepoint(mouse) and enabled
    color = (56, 89, 121) if hovered else (39, 59, 82)
    if not enabled:
        color = (38, 45, 57)
    pygame.draw.rect(surface, color, rect, border_radius=10)
    pygame.draw.rect(surface, (78, 104, 132), rect, 1, border_radius=10)
    centered_text(surface, font, label, rect.center, TEXT if enabled else MUTED)


def grid_geometry(maze: Maze) -> tuple[int, int, int]:
    cell_size = max(12, min(38, GRID_AREA.width // maze.columns, GRID_AREA.height // maze.rows))
    grid_width = cell_size * maze.columns
    grid_height = cell_size * maze.rows
    left = GRID_AREA.centerx - grid_width // 2
    top = GRID_AREA.centery - grid_height // 2
    return left, top, cell_size


def cell_center(maze: Maze, cell: tuple[int, int]) -> tuple[int, int]:
    left, top, size = grid_geometry(maze)
    row, column = cell
    return left + column * size + size // 2, top + row * size + size // 2


def wall_at_position(
    maze: Maze, position: tuple[int, int]
) -> tuple[int, int, int] | None:
    """Find the closest editable wall segment under the mouse."""
    left, top, size = grid_geometry(maze)
    x, y = position
    best: tuple[int, int] | None = None
    best_distance = 9
    for row in range(maze.rows):
        for column in range(maze.columns):
            x0, y0 = left + column * size, top + row * size
            segments = (
                (0, (x0, y0), (x0 + size, y0)),
                (1, (x0 + size, y0), (x0 + size, y0 + size)),
                (2, (x0, y0 + size), (x0 + size, y0 + size)),
                (3, (x0, y0), (x0, y0 + size)),
            )
            for wall, start, end in segments:
                dr, dc, _, _ = Maze.DIRECTIONS[wall]
                if not (0 <= row + dr < maze.rows and 0 <= column + dc < maze.columns):
                    continue
                if not maze.walls[row][column][wall]:
                    continue
                sx, sy = start
                ex, ey = end
                distance = abs(y - sy) if sy == ey else abs(x - sx)
                within_segment = sx - 2 <= x <= ex + 2 if sy == ey else sy - 2 <= y <= ey + 2
                if within_segment and distance < best_distance:
                    best_distance = distance
                    best = row * maze.columns + column, wall
    if best is None:
        return None
    return best[0] // maze.columns, best[0] % maze.columns, best[1]


def draw_maze(
    surface: pygame.Surface,
    maze: Maze,
    player: tuple[int, int],
    editing: bool,
    explored: set[tuple[int, int]],
    path: list[tuple[int, int]] | None,
) -> None:
    left, top, size = grid_geometry(maze)
    for row in range(maze.rows):
        for column in range(maze.columns):
            rect = pygame.Rect(left + column * size, top + row * size, size, size)
            fill = (35, 49, 68)
            if (row, column) in explored:
                fill = (67, 105, 136)
            if path and (row, column) in path:
                fill = (48, 135, 112)
            pygame.draw.rect(surface, fill, rect)
            if editing:
                pygame.draw.rect(surface, (44, 60, 80), rect, 1)
            x, y = rect.x, rect.y
            if maze.walls[row][column][0]:
                pygame.draw.line(surface, WALL, (x, y), (x + size, y), 3)
            if maze.walls[row][column][1]:
                pygame.draw.line(surface, WALL, (x + size, y), (x + size, y + size), 3)
            if maze.walls[row][column][2]:
                pygame.draw.line(surface, WALL, (x, y + size), (x + size, y + size), 3)
            if maze.walls[row][column][3]:
                pygame.draw.line(surface, WALL, (x, y), (x, y + size), 3)

    start = cell_center(maze, (0, 0))
    goal = cell_center(maze, (maze.rows - 1, maze.columns - 1))
    pygame.draw.circle(surface, GREEN, start, max(5, size // 4))
    pygame.draw.circle(surface, ORANGE, goal, max(5, size // 4))
    if not editing:
        pygame.draw.circle(surface, ACCENT, cell_center(maze, player), max(5, size // 5))


def main() -> None:
    pygame.init()
    pygame.display.set_caption("Maze Maker")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    title_font = pygame.font.SysFont("arial", 46, bold=True)
    heading_font = pygame.font.SysFont("arial", 28, bold=True)
    body_font = pygame.font.SysFont("arial", 21)
    small_font = pygame.font.SysFont("arial", 17)

    state = "menu"
    mode = "generated_auto"
    rows, columns = 15, 20
    maze: Maze | None = None
    player = (0, 0)
    editing = False
    explored_order: list[tuple[int, int]] = []
    solution: list[tuple[int, int]] | None = None
    animation_index = 0
    last_animation = 0
    status = ""
    running = True

    while running:
        mouse = pygame.mouse.get_pos()
        screen.fill(BACKGROUND)
        clicked = None

        if state == "menu":
            centered_text(screen, title_font, "MAZE MAKER", (WIDTH // 2, 145), TEXT)
            centered_text(screen, body_font, "Build a maze, find a path, or do both yourself.", (WIDTH // 2, 195), MUTED)
            menu_buttons = [
                ("generated_auto", "Generate + solve for me"),
                ("generated_manual", "Generate + let me play"),
                ("draw_auto", "Let me draw + solve for me"),
                ("draw_manual", "Let me draw + then play"),
            ]
            for index, (key, label) in enumerate(menu_buttons):
                rect = pygame.Rect(WIDTH // 2 - 210, 250 + index * 76, 420, 58)
                button(screen, rect, label, body_font, mouse)
            centered_text(screen, small_font, "Choose a mode to set your maze size.", (WIDTH // 2, 590), MUTED)

        elif state == "settings":
            centered_text(screen, title_font, "MAZE SIZE", (WIDTH // 2, 130), TEXT)
            mode_labels = {
                "generated_auto": "Computer-generated maze · automatic solve",
                "generated_manual": "Computer-generated maze · you play",
                "draw_auto": "Your maze · automatic solve",
                "draw_manual": "Your maze · you play",
            }
            centered_text(screen, body_font, mode_labels[mode], (WIDTH // 2, 190), MUTED)
            centered_text(screen, heading_font, f"Columns     {columns}     Rows     {rows}", (WIDTH // 2, 310), TEXT)
            controls = [
                (pygame.Rect(330, 365, 70, 52), "C-"),
                (pygame.Rect(410, 365, 70, 52), "C+"),
                (pygame.Rect(640, 365, 70, 52), "R-"),
                (pygame.Rect(720, 365, 70, 52), "R+"),
            ]
            for rect, label in controls:
                button(screen, rect, label, body_font, mouse)
            start_rect = pygame.Rect(WIDTH // 2 - 120, 480, 240, 58)
            back_rect = pygame.Rect(WIDTH // 2 - 120, 555, 240, 48)
            button(screen, start_rect, "Create maze", body_font, mouse)
            button(screen, back_rect, "Back to menu", body_font, mouse)
            centered_text(screen, small_font, f"Choose between {MIN_SIZE} and {MAX_SIZE} cells per side.", (WIDTH // 2, 640), MUTED)

        elif state == "maze" and maze is not None:
            is_auto = mode.endswith("auto")
            centered_text(screen, heading_font, "YOUR MAZE" if mode.startswith("draw") else "GENERATED MAZE", (WIDTH // 2, 45), TEXT)
            subtitle = "Click an interior wall to open or close it." if editing else "Move with arrow keys or WASD."
            if is_auto and not editing:
                subtitle = "The computer is searching for the shortest route."
            centered_text(screen, small_font, f"{columns} columns × {rows} rows  ·  {subtitle}", (WIDTH // 2, 82), MUTED)

            pygame.draw.rect(screen, PANEL, GRID_AREA.inflate(16, 16), border_radius=12)
            current_explored = set(explored_order[:animation_index]) if is_auto and not editing else set()
            visible_path = solution if is_auto and not editing and animation_index >= len(explored_order) else None
            draw_maze(screen, maze, player, editing, current_explored, visible_path)

            action_label = "Solve maze" if mode == "draw_auto" and editing else (
                "Start playing" if mode == "draw_manual" and editing else "Edit maze" if mode.startswith("draw") else "New maze"
            )
            action_rect = pygame.Rect(390, 724, 190, 45)
            menu_rect = pygame.Rect(600, 724, 150, 45)
            button(screen, action_rect, action_label, body_font, mouse, enabled=not (is_auto and not editing and mode.startswith("generated")))
            button(screen, menu_rect, "Main menu", body_font, mouse)
            message = status or ("Click walls to create passages." if editing else "")
            if not message and not editing and not is_auto:
                message = "Reach the orange goal."
            if not message and is_auto and not editing and visible_path:
                message = f"Route found in {len(solution) - 1} steps."
            if not message and is_auto and not editing and solution is None and animation_index >= len(explored_order):
                message = "No route to the goal. Return to edit the maze."
            centered_text(screen, small_font, message, (WIDTH // 2, 697), GREEN if "found" in message or "steps" in message else MUTED)

            if is_auto and not editing and animation_index < len(explored_order):
                now = pygame.time.get_ticks()
                if now - last_animation >= 18:
                    animation_index += 1
                    last_animation = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "menu"
                    status = ""
                elif event.key == pygame.K_RETURN and state == "settings":
                    clicked = "start"
                elif event.key == pygame.K_SPACE and state == "maze" and mode == "draw_auto" and editing:
                    clicked = "action"
                elif state == "maze" and maze is not None and not editing and not mode.endswith("auto"):
                    moves = {
                        pygame.K_UP: (-1, 0, 0),
                        pygame.K_w: (-1, 0, 0),
                        pygame.K_RIGHT: (0, 1, 1),
                        pygame.K_d: (0, 1, 1),
                        pygame.K_DOWN: (1, 0, 2),
                        pygame.K_s: (1, 0, 2),
                        pygame.K_LEFT: (0, -1, 3),
                        pygame.K_a: (0, -1, 3),
                    }
                    if event.key in moves:
                        dr, dc, wall = moves[event.key]
                        row, column = player
                        next_cell = row + dr, column + dc
                        if 0 <= next_cell[0] < rows and 0 <= next_cell[1] < columns and not maze.walls[row][column][wall]:
                            player = next_cell
                            if player == (rows - 1, columns - 1):
                                status = "You solved it! Nice work."
                elif event.key == pygame.K_r and state == "maze":
                    clicked = "reset"
                elif event.key == pygame.K_BACKSPACE and state == "settings":
                    state = "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "menu":
                    for index, (key, _) in enumerate(menu_buttons):
                        rect = pygame.Rect(WIDTH // 2 - 210, 250 + index * 76, 420, 58)
                        if rect.collidepoint(event.pos):
                            clicked = key
                            break
                elif state == "settings":
                    controls = [
                        (pygame.Rect(330, 365, 70, 52), "C-"),
                        (pygame.Rect(410, 365, 70, 52), "C+"),
                        (pygame.Rect(640, 365, 70, 52), "R-"),
                        (pygame.Rect(720, 365, 70, 52), "R+"),
                    ]
                    for rect, label in controls:
                        if rect.collidepoint(event.pos):
                            clicked = label
                            break
                    if pygame.Rect(WIDTH // 2 - 120, 480, 240, 58).collidepoint(event.pos):
                        clicked = "start"
                    elif pygame.Rect(WIDTH // 2 - 120, 555, 240, 48).collidepoint(event.pos):
                        clicked = "back"
                elif state == "maze" and maze is not None:
                    if pygame.Rect(390, 724, 190, 45).collidepoint(event.pos):
                        clicked = "action"
                    elif pygame.Rect(600, 724, 150, 45).collidepoint(event.pos):
                        clicked = "menu"
                    elif editing:
                        wall = wall_at_position(maze, event.pos)
                        if wall:
                            maze.toggle_wall(*wall)
                            status = ""

        if clicked in ("generated_auto", "generated_manual", "draw_auto", "draw_manual"):
            mode = clicked
            state = "settings"
        elif state == "settings" and clicked in ("C-", "C+", "R-", "R+"):
            columns += -1 if clicked == "C-" else 1 if clicked == "C+" else 0
            rows += -1 if clicked == "R-" else 1 if clicked == "R+" else 0
            columns = max(MIN_SIZE, min(MAX_SIZE, columns))
            rows = max(MIN_SIZE, min(MAX_SIZE, rows))
        elif state == "settings" and clicked == "back":
            state = "menu"
        elif state == "settings" and clicked == "start":
            maze = Maze(rows, columns, generated=mode.startswith("generated"))
            player = (0, 0)
            editing = mode.startswith("draw")
            status = ""
            explored_order = []
            solution = None
            animation_index = 0
            if mode == "generated_auto":
                explored_order, solution = maze.solve(player, (rows - 1, columns - 1))
                last_animation = pygame.time.get_ticks()
            state = "maze"
        elif state == "maze" and clicked == "menu":
            state = "menu"
            status = ""
        elif state == "maze" and clicked == "action" and maze is not None:
            if mode == "draw_auto" and editing:
                explored_order, solution = maze.solve((0, 0), (rows - 1, columns - 1))
                if solution is None:
                    status = "No route yet. Open more walls, then try again."
                else:
                    editing = False
                    animation_index = 0
                    last_animation = pygame.time.get_ticks()
                    status = ""
            elif mode == "draw_manual" and editing:
                editing = False
                player = (0, 0)
                status = ""
            elif mode.startswith("draw") and not editing:
                editing = True
                status = ""
        elif state == "maze" and clicked == "reset":
            maze = Maze(rows, columns, generated=mode.startswith("generated"))
            player = (0, 0)
            editing = mode.startswith("draw")
            status = ""
            explored_order = []
            solution = None
            animation_index = 0
            if mode == "generated_auto":
                explored_order, solution = maze.solve(player, (rows - 1, columns - 1))
                last_animation = pygame.time.get_ticks()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
