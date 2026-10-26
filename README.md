# Maze Maker

A small interactive maze generator and solver written in Python with Pygame. Choose who creates the maze and who solves it, then select the number of rows and columns (from 5 to 30).

## Modes

- **Generate + solve for me** — create a random maze and watch the computer find a shortest route.
- **Generate + let me play** — navigate a random maze yourself.
- **Let me draw + solve for me** — open passages by clicking interior walls, then watch the computer solve your maze.
- **Let me draw + then play** — draw passages, then navigate your maze.

The green circle marks the start and the orange circle marks the goal. For manual play, use the arrow keys or WASD. In a drawn maze, click a wall between neighboring cells to open or close it. A drawn maze must have an open route between start and goal before the computer can solve it.

## Run

Install the dependency and start the app:

```text
python -m pip install -r requirements.txt
python main.py
```

Use **Escape** to return to the main menu, **R** to create/reset the current maze, and **Enter** to confirm the size screen. In draw-and-solve mode, **Space** starts the solver.

## Tests

Run the maze model tests with:

```text
python -m unittest
```
