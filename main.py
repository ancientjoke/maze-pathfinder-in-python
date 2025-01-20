import pygame
import math
import random
import heapq
from timeit import default_timer as timer

# Window dimensions
WIDTH = 600
HEIGHT = 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Maze Solver ( Using A* Algorithm )")

# Updated Colors
BACKGROUND = (255, 255, 255)  
PATH_CLOSE = (204, 204, 0) 
PATH_OPEN = (255, 255, 0)  
GRID = (255, 255, 255)
WALL = (0, 0, 0)
START = (255, 215, 0)
END = (255, 69, 0)
PATH = (0, 255, 127)

class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = BACKGROUND
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def reset(self):
        self.color = BACKGROUND

    def make_close(self):
        self.color = PATH_CLOSE

    def make_open(self):
        self.color = PATH_OPEN

    def make_wall(self):
        self.color = WALL
    
    def make_start(self):
        self.color = START

    def make_end(self):
        self.color = END

    def make_path(self):
        self.color = PATH

    def is_closed(self):
        return self.color == PATH_CLOSE

    def is_opened(self):
        return self.color == PATH_OPEN

    def is_wall(self):
        return self.color == WALL
    
    def is_start(self):
        return self.color == START

    def is_end(self):
        return self.color == END

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        """
        Populate the neighbours list with valid adjacent nodes.
        Only needs to be called after walls are established or changed.
        """
        self.neighbours = []
        # Down
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall():
            self.neighbours.append(grid[self.row + 1][self.col])
        # Up
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
            self.neighbours.append(grid[self.row - 1][self.col])
        # Right
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall():
            self.neighbours.append(grid[self.row][self.col + 1])
        # Left
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
            self.neighbours.append(grid[self.row][self.col - 1])

def __lt__(self, other):
    return False

def h(p1, p2):
    """
    Heuristic function:
    Computes the Manhattan distance between two points.
    """
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(node_path, current, draw, counter_start):
    """
    Backtrack through node_path to color the final solution.
    """
    pygame.display.set_caption("Maze Solver ( Constructing Path... )")
    path_count = 0
    while current in node_path:
        current = node_path[current]
        current.make_path()
        path_count += 1
        draw()

    counter_end = timer()
    time_elapsed = counter_end - counter_start
    pygame.display.set_caption(
        f"Time Elapsed: {format(time_elapsed, '.2f')}s | "
        f"Cells Visited: {len(node_path) + 1} | Shortest Path: {path_count + 1} Cells"
    )

def algorithm_heapq(draw, grid, start, end, counter_start):
    """
    Optimized A* Search using heapq instead of PriorityQueue.
    Also reduces screen updates to improve performance.
    """
    count = 0
    # open_set is our priority queue, each item is (f_score, count, node)
    open_set = []
    heapq.heappush(open_set, (0, count, start))

    node_path = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    f_score = {spot: float("inf") for row in grid for spot in row}

    g_score[start] = 0
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}
    iteration_count = 0

    while open_set:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

        current = heapq.heappop(open_set)[2]
        open_set_hash.remove(current)

        # If we've reached the goal
        if current == end:
            reconstruct_path(node_path, end, draw, counter_start)
            end.make_end()
            return True

        # Explore neighbors
        for neighbour in current.neighbours:
            temp_g_score = g_score[current] + 1
            # If we've found a cheaper path
            if temp_g_score < g_score[neighbour]:
                node_path[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] = temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    heapq.heappush(open_set, (f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()

        # Update colors - minimize frequency to improve speed
        iteration_count += 1
        if iteration_count % 10 == 0:  # Update screen every 10 iterations (tweak as needed)
            draw()

        if current != start:
            current.make_close()

    # If we exit the loop without finding a path
    pygame.display.set_caption("Maze Solver ( Unable To Find The Target Node! )")
    return False

def make_grid(rows, width):
    """
    Creates a 2D grid of Node objects.
    """
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)
    return grid

def draw_grid(window, rows, width):
    """
    Draws grid lines on the screen. 
    """
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(window, GRID, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(window, GRID, (j * gap, 0), (j * gap, width))

def draw_grid_wall(rows, grid):
    """
    Makes the boundary cells walls.
    """
    for i in range(rows):
        for j in range(rows):
            # If on the border, make it a wall
            if i in (0, rows - 1) or j in (0, rows - 1):
                spot = grid[i][j]
                spot.make_wall()

def draw(window, grid, rows, width):
    """
    Draws the entire grid (nodes + walls + lines) on the screen.
    """
    for row in grid:
        for spot in row:
            spot.draw(window)
    draw_grid(window, rows, width)
    draw_grid_wall(rows, grid)
    pygame.display.update()

def get_mouse_pos(pos, rows, width):
    """
    Gets the (row, col) in the grid from a (x, y) mouse position.
    """
    gap = width // rows
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col

def generate_dfs_maze(grid, rows, start, end):
    """
    Generates a maze using a randomized Depth-First Search (DFS) approach.
    Ensures there's always a path from start to end by carving walls along DFS.
    """

    # Mark all interior cells as walls (except Start & End)
    for i in range(rows):
        for j in range(rows):
            spot = grid[i][j]
            if (spot == start) or (spot == end):
                spot.reset()
            elif i in (0, rows - 1) or j in (0, rows - 1):
                # keep boundary as walls
                spot.make_wall()
            else:
                # set interior cells as walls initially
                spot.make_wall()
    
    # A helper function to get valid, non-wall neighbors
    def get_unvisited_neighbors(cell):
        valid_neighbors = []
        # We define moves for up/down/left/right
        moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in moves:
            nx, ny = cell.row + dx, cell.col + dy
            if 0 <= nx < rows and 0 <= ny < rows:
                neighbor = grid[nx][ny]
                # It's considered 'unvisited' if it's still a wall
                if neighbor.is_wall() and neighbor != start and neighbor != end:
                    valid_neighbors.append(neighbor)
        return valid_neighbors
    
    # Depth-First Search stack
    stack = [start]
    start.reset()  # carve the start so it's not a wall

    while stack:
        current_cell = stack[-1]
        # Get all possible unvisited (wall) neighbors
        unvisited_neighbors = get_unvisited_neighbors(current_cell)

        if unvisited_neighbors:
            # Pick a random neighbor, remove the wall, and move there
            next_cell = random.choice(unvisited_neighbors)
            next_cell.reset()  # carve path by resetting color from wall to blank
            stack.append(next_cell)
        else:
            # Backtrack if no unvisited neighbors
            stack.pop()

    # Optional: Ensure End is carved after DFS, in case it was left a wall
    end.reset()

def main(window, width):
    ROWS = 30
    grid = make_grid(ROWS, width)

    Start = None
    End = None
    Run = True

    while Run:
        draw(window, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Run = False

            # Left mouse button
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not Start and spot != End:
                    Start = spot
                    Start.make_start()
                elif not End and spot != Start:
                    End = spot
                    End.make_end()
                elif spot != Start and spot != End:
                    spot.make_wall()

            # Right mouse button
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_mouse_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == Start:
                    Start = None
                if spot == End:
                    End = None

            # Keyboard events
            if event.type == pygame.KEYDOWN:
                # Remind user to set start & end if they haven't
                if not Start and not End:
                    pygame.display.set_caption("Maze Solver ( Set Start & End Nodes! )")

                # Press SPACE to run the (optimized) search
                if event.key == pygame.K_SPACE and Start and End:
                    counter_start = timer()
                    pygame.display.set_caption("Maze Solver ( Searching... )")
                    # Update neighbours once before the algorithm
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    algorithm_heapq(lambda: draw(window, grid, ROWS, width), grid, Start, End, counter_start)

                # Press C to clear the grid
                if event.key == pygame.K_c:
                    Start = None
                    End = None
                    pygame.display.set_caption("Maze Solver ( Using A* Algorithm )")
                    grid = make_grid(ROWS, width)

                # Press R to generate a random maze
                if event.key == pygame.K_r and Start and End:
                    generate_dfs_maze(grid, ROWS, Start, End)
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    pygame.display.set_caption("Maze Solver ( Random Maze Generated )")

    pygame.quit()

if __name__ == "__main__":
    main(win, WIDTH)
