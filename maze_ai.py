import pygame
import random
import heapq
import time
import sys

# ============================================================
# AI ROBOT MAZE NAVIGATION GAME
# ============================================================

pygame.init()

# ---------------- WINDOW ----------------
WIDTH = 1100
HEIGHT = 760

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Robot Maze Navigation Game")

clock = pygame.time.Clock()
FPS = 60

# ---------------- COLORS ----------------
BLACK = (15, 15, 20)
WHITE = (245, 245, 245)
GRAY = (100, 100, 110)
LIGHT_GRAY = (180, 180, 190)

BLUE = (50, 150, 255)
GREEN = (50, 220, 100)
RED = (240, 70, 70)
YELLOW = (255, 210, 50)
PURPLE = (180, 80, 240)
ORANGE = (255, 150, 50)
CYAN = (50, 220, 220)

# ---------------- FONTS ----------------
font_title = pygame.font.SysFont("arial", 42, bold=True)
font_big = pygame.font.SysFont("arial", 32, bold=True)
font_medium = pygame.font.SysFont("arial", 24, bold=True)
font_small = pygame.font.SysFont("arial", 19)
font_tiny = pygame.font.SysFont("arial", 16)

# ============================================================
# SETTINGS
# ============================================================

CELL_SIZE = 28

MAZE_ROWS = 19
MAZE_COLS = 25

MAZE_X = 30
MAZE_Y = 125

# Game modes
HUMAN = 1
AI = 2
HUMAN_AI = 3
AI_AI = 4

# Difficulty
EASY = 1
MEDIUM = 2
HARD = 3

difficulty_name = {
    EASY: "EASY",
    MEDIUM: "MEDIUM",
    HARD: "HARD"
}

difficulty_settings = {
    EASY: {
        "obstacles": 3,
        "ai_delay": 12
    },
    MEDIUM: {
        "obstacles": 5,
        "ai_delay": 8
    },
    HARD: {
        "obstacles": 8,
        "ai_delay": 5
    }
}

# ============================================================
# GLOBAL GAME VARIABLES
# ============================================================

game_mode = HUMAN
difficulty = EASY

maze = []

player_pos = (1, 1)
ai_pos = (1, 1)
ai2_pos = (17, 1)

goal_pos = (17, 23)

moving_obstacles = []

game_state = "menu"

start_time = 0
finish_time = 0

ai_timer = 0
ai2_timer = 0
obstacle_timer = 0

player_moves = 0
ai_moves = 0
ai2_moves = 0

winner = ""
score = 0


# ============================================================
# TEXT
# ============================================================

def draw_text(text, font, color, x, y, center=False):

    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


# ============================================================
# CELL TO SCREEN
# ============================================================

def cell_to_pixel(row, col):

    x = MAZE_X + col * CELL_SIZE
    y = MAZE_Y + row * CELL_SIZE

    return x, y


# ============================================================
# DRAW ROBOT
# ============================================================

def draw_robot(position, color, label):

    row, col = position

    x, y = cell_to_pixel(row, col)

    cx = x + CELL_SIZE // 2
    cy = y + CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        color,
        (cx, cy),
        CELL_SIZE // 2 - 3
    )

    # Eyes
    pygame.draw.circle(
        screen,
        WHITE,
        (cx - 5, cy - 4),
        3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (cx + 5, cy - 4),
        3
    )

    # Mouth
    pygame.draw.line(
        screen,
        BLACK,
        (cx - 5, cy + 6),
        (cx + 5, cy + 6),
        2
    )

    text = font_tiny.render(label, True, WHITE)

    screen.blit(
        text,
        (
            cx - text.get_width() // 2,
            cy + 8
        )
    )


# ============================================================
# GENERATE MAZE
# ============================================================

def generate_maze():

    global maze

    maze = [
        [1 for _ in range(MAZE_COLS)]
        for _ in range(MAZE_ROWS)
    ]

    maze[1][1] = 0

    stack = [(1, 1)]

    directions = [
        (-2, 0),
        (2, 0),
        (0, -2),
        (0, 2)
    ]

    while stack:

        row, col = stack[-1]

        neighbors = []

        dirs = directions[:]
        random.shuffle(dirs)

        for dr, dc in dirs:

            nr = row + dr
            nc = col + dc

            if (
                1 <= nr < MAZE_ROWS - 1
                and 1 <= nc < MAZE_COLS - 1
                and maze[nr][nc] == 1
            ):
                neighbors.append((nr, nc))

        if neighbors:

            nr, nc = random.choice(neighbors)

            wall_r = (row + nr) // 2
            wall_c = (col + nc) // 2

            maze[wall_r][wall_c] = 0
            maze[nr][nc] = 0

            stack.append((nr, nc))

        else:

            stack.pop()

    # Ensure starting areas are open

    maze[1][1] = 0
    maze[1][2] = 0
    maze[2][1] = 0

    maze[MAZE_ROWS - 2][1] = 0
    maze[MAZE_ROWS - 3][1] = 0
    maze[MAZE_ROWS - 2][2] = 0

    # Ensure goal area is open

    maze[MAZE_ROWS - 2][MAZE_COLS - 2] = 0
    maze[MAZE_ROWS - 3][MAZE_COLS - 2] = 0
    maze[MAZE_ROWS - 2][MAZE_COLS - 3] = 0


# ============================================================
# DRAW MAZE
# ============================================================

def draw_maze():

    for row in range(MAZE_ROWS):

        for col in range(MAZE_COLS):

            x, y = cell_to_pixel(row, col)

            rect = pygame.Rect(
                x,
                y,
                CELL_SIZE,
                CELL_SIZE
            )

            if maze[row][col] == 1:

                pygame.draw.rect(
                    screen,
                    (35, 40, 55),
                    rect
                )

                pygame.draw.rect(
                    screen,
                    (60, 65, 80),
                    rect,
                    1
                )

            else:

                pygame.draw.rect(
                    screen,
                    (225, 230, 235),
                    rect
                )


# ============================================================
# DRAW GOAL
# ============================================================

def draw_goal():

    row, col = goal_pos

    x, y = cell_to_pixel(row, col)

    cx = x + CELL_SIZE // 2
    cy = y + CELL_SIZE // 2

    pygame.draw.circle(
        screen,
        GREEN,
        (cx, cy),
        CELL_SIZE // 2 - 3
    )

    pygame.draw.circle(
        screen,
        WHITE,
        (cx, cy),
        CELL_SIZE // 2 - 8,
        2
    )

    draw_text(
        "G",
        font_small,
        WHITE,
        cx,
        cy,
        True
    )


# ============================================================
# A* HEURISTIC
# ============================================================

def heuristic(a, b):

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ============================================================
# GET NEIGHBORS
# ============================================================

def get_neighbors(position):

    row, col = position

    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1)
    ]

    result = []

    for dr, dc in directions:

        nr = row + dr
        nc = col + dc

        if (
            0 <= nr < MAZE_ROWS
            and 0 <= nc < MAZE_COLS
            and maze[nr][nc] == 0
        ):
            result.append((nr, nc))

    return result


# ============================================================
# A* PATHFINDING
# ============================================================

def astar(start, goal, blocked=None):

    if blocked is None:
        blocked = set()

    if start in blocked:
        blocked = set(blocked)
        blocked.discard(start)

    if goal in blocked:
        blocked = set(blocked)
        blocked.discard(goal)

    open_list = []

    heapq.heappush(
        open_list,
        (0, start)
    )

    came_from = {}

    g_score = {
        start: 0
    }

    while open_list:

        _, current = heapq.heappop(open_list)

        if current == goal:

            path = []

            while current in came_from:

                path.append(current)

                current = came_from[current]

            path.append(start)

            path.reverse()

            return path

        for neighbor in get_neighbors(current):

            if neighbor in blocked:
                continue

            new_cost = g_score[current] + 1

            if (
                neighbor not in g_score
                or new_cost < g_score[neighbor]
            ):

                g_score[neighbor] = new_cost

                priority = (
                    new_cost
                    + heuristic(neighbor, goal)
                )

                came_from[neighbor] = current

                heapq.heappush(
                    open_list,
                    (priority, neighbor)
                )

    return []


# ============================================================
# CREATE OBSTACLES
# ============================================================

def create_obstacles():

    global moving_obstacles

    moving_obstacles = []

    count = difficulty_settings[difficulty]["obstacles"]

    attempts = 0

    forbidden = {
        (1, 1),
        (MAZE_ROWS - 2, 1),
        goal_pos
    }

    while len(moving_obstacles) < count and attempts < 1000:

        attempts += 1

        row = random.randint(1, MAZE_ROWS - 2)
        col = random.randint(1, MAZE_COLS - 2)

        position = (row, col)

        if maze[row][col] != 0:
            continue

        if position in forbidden:
            continue

        if position in moving_obstacles:
            continue

        moving_obstacles.append(position)


# ============================================================
# MOVE OBSTACLES
# ============================================================

def move_obstacles():

    global moving_obstacles

    new_positions = []

    occupied = {
        player_pos,
        ai_pos,
        ai2_pos,
        goal_pos
    }

    for position in moving_obstacles:

        possible = get_neighbors(position)

        random.shuffle(possible)

        new_position = position

        for candidate in possible:

            if candidate not in occupied:
                new_position = candidate
                break

        new_positions.append(new_position)

        occupied.add(new_position)

    moving_obstacles = new_positions


# ============================================================
# DRAW OBSTACLES
# ============================================================

def draw_obstacles():

    for row, col in moving_obstacles:

        x, y = cell_to_pixel(row, col)

        rect = pygame.Rect(
            x + 5,
            y + 5,
            CELL_SIZE - 10,
            CELL_SIZE - 10
        )

        pygame.draw.rect(
            screen,
            RED,
            rect,
            border_radius=5
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (
                x + CELL_SIZE // 2,
                y + CELL_SIZE // 2
            ),
            4
        )


# ============================================================
# AI DECISION
# ============================================================

def ai_choose_next(current_position, other_positions=None):

    if other_positions is None:
        other_positions = []

    blocked = set(moving_obstacles)

    for position in other_positions:
        blocked.add(position)

    blocked.discard(current_position)
    blocked.discard(goal_pos)

    path = astar(
        current_position,
        goal_pos,
        blocked
    )

    if len(path) >= 2:

        return path[1]

    # Backup path
    path = astar(
        current_position,
        goal_pos
    )

    if len(path) >= 2:
        return path[1]

    return current_position


# ============================================================
# HUMAN MOVEMENT
# ============================================================

def move_player(dr, dc):

    global player_pos
    global player_moves

    row, col = player_pos

    new_row = row + dr
    new_col = col + dc

    if not (
        0 <= new_row < MAZE_ROWS
        and 0 <= new_col < MAZE_COLS
    ):
        return

    new_position = (new_row, new_col)

    if maze[new_row][new_col] == 1:
        return

    if new_position in moving_obstacles:
        return

    player_pos = new_position

    player_moves += 1


# ============================================================
# START GAME
# ============================================================

def start_game():

    global player_pos
    global ai_pos
    global ai2_pos
    global moving_obstacles

    global start_time
    global finish_time

    global ai_timer
    global ai2_timer
    global obstacle_timer

    global player_moves
    global ai_moves
    global ai2_moves

    global winner
    global score
    global game_state

    # Create new maze
    generate_maze()

    # Create obstacles
    create_obstacles()

    # Set positions
    player_pos = (1, 1)
    ai_pos = (1, 1)
    ai2_pos = (MAZE_ROWS - 2, 1)

    # Remove obstacles from starting positions
    moving_obstacles = [
        position
        for position in moving_obstacles
        if position not in {
            player_pos,
            ai_pos,
            ai2_pos,
            goal_pos
        }
    ]

    # Reset values
    start_time = time.time()
    finish_time = 0

    ai_timer = 0
    ai2_timer = 0
    obstacle_timer = 0

    player_moves = 0
    ai_moves = 0
    ai2_moves = 0

    winner = ""
    score = 0

    game_state = "playing"


# ============================================================
# FINISH GAME
# ============================================================

def finish_game(result):

    global game_state
    global winner
    global finish_time
    global score

    winner = result

    finish_time = time.time()

    elapsed = finish_time - start_time

    score = max(
        100,
        int(10000 / max(1, elapsed))
    )

    game_state = "game_over"


# ============================================================
# CHECK WINNER
# ============================================================

def check_winner():

    if game_mode == HUMAN:

        if player_pos == goal_pos:
            finish_game("PLAYER WINS")

    elif game_mode == AI:

        if ai_pos == goal_pos:
            finish_game("AI WINS")

    elif game_mode == HUMAN_AI:

        if player_pos == goal_pos:
            finish_game("PLAYER WINS")

        elif ai_pos == goal_pos:
            finish_game("AI WINS")

    elif game_mode == AI_AI:

        if ai_pos == goal_pos:
            finish_game("AI 1 WINS")

        elif ai2_pos == goal_pos:
            finish_game("AI 2 WINS")


# ============================================================
# MODE NAME
# ============================================================

def get_mode_name():

    if game_mode == HUMAN:
        return "HUMAN"

    if game_mode == AI:
        return "AI"

    if game_mode == HUMAN_AI:
        return "HUMAN VS AI"

    return "AI VS AI"


# ============================================================
# GAME INFORMATION
# ============================================================

def draw_game_info():

    pygame.draw.rect(
        screen,
        (25, 28, 40),
        (0, 0, WIDTH, 105)
    )

    draw_text(
        "AI ROBOT MAZE",
        font_big,
        CYAN,
        30,
        18
    )

    draw_text(
        "Mode: " + get_mode_name(),
        font_small,
        WHITE,
        30,
        60
    )

    draw_text(
        "Difficulty: " + difficulty_name[difficulty],
        font_small,
        WHITE,
        230,
        60
    )

    elapsed = time.time() - start_time

    draw_text(
        "Time: " + str(int(elapsed)) + "s",
        font_small,
        YELLOW,
        500,
        60
    )

    draw_text(
        "Moves: " + str(player_moves),
        font_small,
        WHITE,
        700,
        60
    )

    draw_text(
        "ESC = Menu",
        font_tiny,
        LIGHT_GRAY,
        920,
        25
    )


# ============================================================
# DRAW PATH
# ============================================================

def draw_path(path, color):

    if len(path) < 2:
        return

    points = []

    for row, col in path:

        x, y = cell_to_pixel(row, col)

        points.append(
            (
                x + CELL_SIZE // 2,
                y + CELL_SIZE // 2
            )
        )

    pygame.draw.lines(
        screen,
        color,
        False,
        points,
        3
    )


def draw_ai_paths():

    if game_mode == HUMAN:
        return

    if game_mode == AI_AI:

        path1 = astar(
            ai_pos,
            goal_pos,
            set(moving_obstacles)
        )

        path2 = astar(
            ai2_pos,
            goal_pos,
            set(moving_obstacles)
        )

        draw_path(path1, PURPLE)
        draw_path(path2, ORANGE)

    else:

        path = astar(
            ai_pos,
            goal_pos,
            set(moving_obstacles)
        )

        draw_path(path, PURPLE)


# ============================================================
# BUTTON
# ============================================================

def draw_button(text, x, y, width, height, selected=False):

    if selected:
        color = BLUE
    else:
        color = (45, 50, 65)

    rect = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=10
    )

    pygame.draw.rect(
        screen,
        LIGHT_GRAY,
        rect,
        2,
        border_radius=10
    )

    draw_text(
        text,
        font_medium,
        WHITE,
        x + width // 2,
        y + height // 2,
        True
    )


# ============================================================
# MAIN MENU
# ============================================================

def draw_menu():

    screen.fill(BLACK)

    draw_text(
        "AI ROBOT MAZE",
        font_title,
        CYAN,
        WIDTH // 2,
        75,
        True
    )

    draw_text(
        "AI-Based Robot Maze Navigation Game",
        font_medium,
        WHITE,
        WIDTH // 2,
        125,
        True
    )

    draw_text(
        "Choose Game Mode",
        font_big,
        YELLOW,
        WIDTH // 2,
        190,
        True
    )

    draw_button(
        "1. HUMAN",
        350,
        240,
        400,
        50
    )

    draw_button(
        "2. AI",
        350,
        300,
        400,
        50
    )

    draw_button(
        "3. HUMAN VS AI",
        350,
        360,
        400,
        50
    )

    draw_button(
        "4. AI VS AI",
        350,
        420,
        400,
        50
    )

    draw_text(
        "Press 1 - 4 to select",
        font_small,
        LIGHT_GRAY,
        WIDTH // 2,
        510,
        True
    )

    draw_text(
        "ENTER = Continue",
        font_medium,
        GREEN,
        WIDTH // 2,
        550,
        True
    )

    draw_text(
        "H = How to Play",
        font_small,
        WHITE,
        WIDTH // 2,
        595,
        True
    )

    draw_text(
        "ESC = Exit",
        font_small,
        GRAY,
        WIDTH // 2,
        635,
        True
    )


# ============================================================
# DIFFICULTY MENU
# ============================================================

def draw_difficulty():

    screen.fill(BLACK)

    draw_text(
        "SELECT DIFFICULTY",
        font_title,
        CYAN,
        WIDTH // 2,
        90,
        True
    )

    draw_button(
        "1. EASY",
        350,
        220,
        400,
        60,
        difficulty == EASY
    )

    draw_button(
        "2. MEDIUM",
        350,
        300,
        400,
        60,
        difficulty == MEDIUM
    )

    draw_button(
        "3. HARD",
        350,
        380,
        400,
        60,
        difficulty == HARD
    )

    draw_text(
        "1 / 2 / 3 = Select Difficulty",
        font_small,
        LIGHT_GRAY,
        WIDTH // 2,
        490,
        True
    )

    draw_text(
        "ENTER = Start",
        font_medium,
        GREEN,
        WIDTH // 2,
        535,
        True
    )

    draw_text(
        "BACKSPACE = Back",
        font_small,
        GRAY,
        WIDTH // 2,
        580,
        True
    )


# ============================================================
# HELP SCREEN
# ============================================================

def draw_help():

    screen.fill(BLACK)

    draw_text(
        "HOW TO PLAY",
        font_title,
        CYAN,
        WIDTH // 2,
        75,
        True
    )

    instructions = [
        ("Reach the green G to finish the maze.", WHITE),
        ("", WHITE),
        ("HUMAN MODE", YELLOW),
        ("Arrow Keys = Move", WHITE),
        ("", WHITE),
        ("AI MODE", YELLOW),
        ("AI uses A* pathfinding.", WHITE),
        ("", WHITE),
        ("HUMAN VS AI", YELLOW),
        ("Human competes against AI.", WHITE),
        ("", WHITE),
        ("AI VS AI", YELLOW),
        ("AI 1 and AI 2 race each other.", WHITE),
        ("", WHITE),
        ("Red blocks = Moving obstacles", RED),
        ("", WHITE),
        ("ESC = Return to Menu", LIGHT_GRAY)
    ]

    y = 145

    for text, color in instructions:

        draw_text(
            text,
            font_small,
            color,
            WIDTH // 2,
            y,
            True
        )

        y += 29


# ============================================================
# GAME OVER
# ============================================================

def draw_game_over():

    screen.fill(BLACK)

    draw_text(
        "RACE FINISHED",
        font_title,
        CYAN,
        WIDTH // 2,
        90,
        True
    )

    if winner == "PLAYER WINS":
        color = GREEN

    elif winner == "AI WINS":
        color = PURPLE

    elif winner == "AI 1 WINS":
        color = PURPLE

    else:
        color = ORANGE

    draw_text(
        winner,
        font_title,
        color,
        WIDTH // 2,
        180,
        True
    )

    elapsed = finish_time - start_time

    draw_text(
        "Time: " + str(round(elapsed, 2)) + " seconds",
        font_medium,
        WHITE,
        WIDTH // 2,
        260,
        True
    )

    draw_text(
        "Score: " + str(score),
        font_medium,
        YELLOW,
        WIDTH // 2,
        305,
        True
    )

    draw_text(
        "Player Moves: " + str(player_moves),
        font_small,
        WHITE,
        WIDTH // 2,
        355,
        True
    )

    draw_text(
        "AI 1 Moves: " + str(ai_moves),
        font_small,
        PURPLE,
        WIDTH // 2,
        390,
        True
    )

    draw_text(
        "AI 2 Moves: " + str(ai2_moves),
        font_small,
        ORANGE,
        WIDTH // 2,
        425,
        True
    )

    draw_text(
        "ENTER = Play Again",
        font_medium,
        GREEN,
        WIDTH // 2,
        510,
        True
    )

    draw_text(
        "M = Main Menu",
        font_small,
        WHITE,
        WIDTH // 2,
        555,
        True
    )

    draw_text(
        "ESC = Exit",
        font_small,
        GRAY,
        WIDTH // 2,
        600,
        True
    )


# ============================================================
# DRAW GAME
# ============================================================

def draw_game():

    screen.fill((18, 20, 28))

    draw_game_info()

    draw_maze()

    draw_ai_paths()

    draw_goal()

    draw_obstacles()

    if game_mode == HUMAN:

        draw_robot(
            player_pos,
            BLUE,
            "P"
        )

    elif game_mode == AI:

        draw_robot(
            ai_pos,
            PURPLE,
            "AI"
        )

    elif game_mode == HUMAN_AI:

        draw_robot(
            player_pos,
            BLUE,
            "P"
        )

        draw_robot(
            ai_pos,
            PURPLE,
            "AI"
        )

    elif game_mode == AI_AI:

        draw_robot(
            ai_pos,
            PURPLE,
            "1"
        )

        draw_robot(
            ai2_pos,
            ORANGE,
            "2"
        )

    # Bottom legend

    y = HEIGHT - 35

    if game_mode in [HUMAN, HUMAN_AI]:

        pygame.draw.circle(
            screen,
            BLUE,
            (35, y),
            8
        )

        draw_text(
            "Player",
            font_tiny,
            WHITE,
            50,
            y - 9
        )

    if game_mode in [AI, HUMAN_AI, AI_AI]:

        pygame.draw.circle(
            screen,
            PURPLE,
            (150, y),
            8
        )

        draw_text(
            "AI 1",
            font_tiny,
            WHITE,
            165,
            y - 9
        )

    if game_mode == AI_AI:

        pygame.draw.circle(
            screen,
            ORANGE,
            (240, y),
            8
        )

        draw_text(
            "AI 2",
            font_tiny,
            WHITE,
            255,
            y - 9
        )

    pygame.draw.circle(
        screen,
        RED,
        (335, y),
        8
    )

    draw_text(
        "Obstacle",
        font_tiny,
        WHITE,
        350,
        y - 9
    )


# ============================================================
# UPDATE GAME
# ============================================================

def update_game():

    global ai_timer
    global ai2_timer
    global obstacle_timer

    global ai_pos
    global ai2_pos

    global ai_moves
    global ai2_moves

    # ---------------- OBSTACLES ----------------

    obstacle_timer += 1

    if obstacle_timer >= 40:

        move_obstacles()

        obstacle_timer = 0

    # ---------------- AI ----------------

    ai_timer += 1
    ai2_timer += 1

    delay = difficulty_settings[difficulty]["ai_delay"]

    # AI mode
    if game_mode == AI:

        if ai_timer >= delay:

            new_position = ai_choose_next(
                ai_pos
            )

            if new_position != ai_pos:

                ai_pos = new_position
                ai_moves += 1

            ai_timer = 0

    # Human vs AI
    elif game_mode == HUMAN_AI:

        if ai_timer >= delay:

            new_position = ai_choose_next(
                ai_pos,
                [player_pos]
            )

            if new_position != ai_pos:

                ai_pos = new_position
                ai_moves += 1

            ai_timer = 0

    # AI vs AI
    elif game_mode == AI_AI:

        if ai_timer >= delay:

            new_position = ai_choose_next(
                ai_pos,
                [ai2_pos]
            )

            if new_position != ai_pos:

                ai_pos = new_position
                ai_moves += 1

            ai_timer = 0

        if ai2_timer >= delay + 2:

            new_position = ai_choose_next(
                ai2_pos,
                [ai_pos]
            )

            if new_position != ai2_pos:

                ai2_pos = new_position
                ai2_moves += 1

            ai2_timer = 0

    # ---------------- COLLISION ----------------

    if game_mode in [HUMAN, HUMAN_AI]:

        if player_pos in moving_obstacles:

            if game_mode == HUMAN:

                ai_pos_reset = (1, 1)

                # Reset player
                globals()["player_pos"] = (
                    MAZE_ROWS - 2,
                    1
                )

    if game_mode in [AI, HUMAN_AI, AI_AI]:

        if ai_pos in moving_obstacles:

            ai_pos = (1, 1)

    if game_mode == AI_AI:

        if ai2_pos in moving_obstacles:

            ai2_pos = (
                MAZE_ROWS - 2,
                1
            )

    check_winner()


# ============================================================
# KEYBOARD
# ============================================================

def handle_playing_key(event):

    global game_state

    if event.key == pygame.K_ESCAPE:

        game_state = "menu"
        return

    if game_mode not in [HUMAN, HUMAN_AI]:

        return

    if event.key == pygame.K_UP:

        move_player(-1, 0)

    elif event.key == pygame.K_DOWN:

        move_player(1, 0)

    elif event.key == pygame.K_LEFT:

        move_player(0, -1)

    elif event.key == pygame.K_RIGHT:

        move_player(0, 1)


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    clock.tick(FPS)

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ---------------- MENU ----------------

            if game_state == "menu":

                if event.key == pygame.K_1:

                    game_mode = HUMAN

                elif event.key == pygame.K_2:

                    game_mode = AI

                elif event.key == pygame.K_3:

                    game_mode = HUMAN_AI

                elif event.key == pygame.K_4:

                    game_mode = AI_AI

                elif event.key == pygame.K_RETURN:

                    game_state = "difficulty"

                elif event.key == pygame.K_h:

                    game_state = "help"

                elif event.key == pygame.K_ESCAPE:

                    running = False

            # ---------------- DIFFICULTY ----------------

            elif game_state == "difficulty":

                if event.key == pygame.K_1:

                    difficulty = EASY

                elif event.key == pygame.K_2:

                    difficulty = MEDIUM

                elif event.key == pygame.K_3:

                    difficulty = HARD

                elif event.key == pygame.K_RETURN:

                    start_game()

                elif event.key == pygame.K_BACKSPACE:

                    game_state = "menu"

                elif event.key == pygame.K_ESCAPE:

                    game_state = "menu"

            # ---------------- HELP ----------------

            elif game_state == "help":

                if event.key in [
                    pygame.K_ESCAPE,
                    pygame.K_BACKSPACE
                ]:

                    game_state = "menu"

            # ---------------- PLAYING ----------------

            elif game_state == "playing":

                handle_playing_key(event)

            # ---------------- GAME OVER ----------------

            elif game_state == "game_over":

                if event.key == pygame.K_RETURN:

                    start_game()

                elif event.key == pygame.K_m:

                    game_state = "menu"

                elif event.key == pygame.K_ESCAPE:

                    running = False

    # ========================================================
    # UPDATE
    # ========================================================

    if game_state == "playing":

        update_game()

    # ========================================================
    # DRAW
    # ========================================================

    if game_state == "menu":

        draw_menu()

    elif game_state == "difficulty":

        draw_difficulty()

    elif game_state == "help":

        draw_help()

    elif game_state == "playing":

        draw_game()

    elif game_state == "game_over":

        draw_game_over()

    pygame.display.flip()


# ============================================================
# EXIT
# ============================================================

pygame.quit()
sys.exit()