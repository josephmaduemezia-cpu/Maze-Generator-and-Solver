import unittest
from collections import deque

from main import Maze, grid_geometry, wall_at_position


class MazeTests(unittest.TestCase):
    def test_generated_maze_connects_every_cell(self):
        for rows, columns in ((5, 5), (8, 12), (20, 9)):
            with self.subTest(rows=rows, columns=columns):
                maze = Maze(rows, columns, generated=True)
                explored, path = maze.solve((0, 0), (rows - 1, columns - 1))
                reachable = {(0, 0)}
                queue = deque([(0, 0)])
                while queue:
                    for neighbor in maze.neighbors(queue.popleft()):
                        if neighbor not in reachable:
                            reachable.add(neighbor)
                            queue.append(neighbor)
                self.assertEqual(len(reachable), rows * columns)
                self.assertIsNotNone(path)
                self.assertIn((rows - 1, columns - 1), explored)
                self.assertEqual(path[0], (0, 0))
                self.assertEqual(path[-1], (rows - 1, columns - 1))

    def test_toggle_wall_keeps_neighbor_walls_symmetric(self):
        maze = Maze(3, 4)
        self.assertTrue(maze.toggle_wall(1, 1, 1))
        self.assertFalse(maze.walls[1][1][1])
        self.assertFalse(maze.walls[1][2][3])
        self.assertTrue(maze.toggle_wall(1, 2, 3))
        self.assertTrue(maze.walls[1][1][1])
        self.assertTrue(maze.walls[1][2][3])

    def test_boundary_walls_cannot_be_toggled(self):
        maze = Maze(3, 3)
        self.assertFalse(maze.toggle_wall(0, 0, 0))
        self.assertTrue(maze.walls[0][0][0])
        self.assertFalse(maze.toggle_wall(2, 2, 1))
        self.assertTrue(maze.walls[2][2][1])

    def test_mouse_position_selects_an_interior_wall(self):
        maze = Maze(5, 5)
        left, top, size = grid_geometry(maze)
        wall_position = left + size, top + size // 2
        self.assertEqual(wall_at_position(maze, wall_position), (0, 0, 1))

    def test_solver_finds_path_in_user_drawn_maze(self):
        maze = Maze(3, 3)
        _, path = maze.solve((0, 0), (2, 2))
        self.assertIsNone(path)
        for row, column, wall in ((0, 0, 1), (0, 1, 2), (1, 1, 1), (1, 2, 2)):
            maze.toggle_wall(row, column, wall)
        _, path = maze.solve((0, 0), (2, 2))
        self.assertEqual(path, [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)])


if __name__ == "__main__":
    unittest.main()
