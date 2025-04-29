import numpy as np  # Import numpy as np for arrays and math operations
import pygame       # Import pygame for game development (graphics and sounds)
import sys          # Import sys to handle system-specific functions like exiting
import math         # Import math for mathematical operations and functions
import random       # Import random to generate random numbers or choices
import os           # Import os to interact with the operating system (files, folders)

# Colors
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game Settings
ROW_COUNT = 6
COLUMN_COUNT = 7
WINDOW_LENGTH = 4

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

def create_board():     # Create a new game board filled with zeros (empty cells)
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):     # Drop a piece into the board at the given row and column
    board[row][col] = piece

def is_valid_location(board, col):      # Check if the top row in the selected column is still empty
    return board[ROW_COUNT - 1][col] == 0

def get_next_open_row(board, col):     # Find the next available row in the selected column
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board):     # Print the board flipped vertically to match game view
    print(np.flip(board, 0))

def winning_move(board, piece): # Check for 4 in a row horizontally
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all([board[r][c+i] == piece for i in range(4)]):
                return True
    for c in range(COLUMN_COUNT):    # Check for 4 in a row vertically
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c] == piece for i in range(4)]):
                return True
    for c in range(COLUMN_COUNT - 3):   # Check for 4 in a row diagonally (down-right)
        for r in range(ROW_COUNT - 3):
            if all([board[r+i][c+i] == piece for i in range(4)]):
                return True
    for c in range(COLUMN_COUNT - 3):      # Check for 4 in a row diagonally (up-right)

        for r in range(3, ROW_COUNT):
            if all([board[r-i][c+i] == piece for i in range(4)]):
                return True

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 10
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        if score > 0:
            score -= 4
        else:
            score = 0
    return score

def score_position(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, math.inf)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -math.inf)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))

    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            print(f"AI evaluating move at column {col} with score {new_score}")
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE + SQUARESIZE/2), int(r*SQUARESIZE + SQUARESIZE + SQUARESIZE/2)), RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE + SQUARESIZE/2), height - int(r*SQUARESIZE + SQUARESIZE/2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE + SQUARESIZE/2), height - int(r*SQUARESIZE + SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def ask_restart():
    print("\nDo you want to restart the game?")
    choice = input("Enter 'y' to restart or anything else to exit: ")
    if choice.lower() == 'y':
        global board, game_over, turn
        board = create_board()
        draw_board(board)
        game_over = False
        # Optionally, you can ask again who starts if you want
    else:
        pygame.quit()
        sys.exit()


# Initialize Pygame
pygame.init()

SQUARESIZE = 100
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE/2 - 5)

screen = pygame.display.set_mode(size)
myfont = pygame.font.SysFont("monospace", 75)

board = create_board()
print_board(board)
draw_board(board)

# Difficulty setting
print("Select difficulty level:")
print("1. Easy")
print("2. Medium")
print("3. Hard")

difficulty = int(input("Enter choice (1-3): "))
if difficulty == 1:
    depth = 2
elif difficulty == 2:
    depth = 4
elif difficulty == 3:
    depth = 6
else:
    print("Defaulting to Medium difficulty.")
    depth = 4

# Game Mode setting
print("\nChoose game mode:")
print("1. Player vs Player")
print("2. Player vs AI")
print("3. AI vs AI")

mode = int(input("Enter choice (1-3): "))

if mode == 1:
    turn = PLAYER
elif mode == 2:
    start_player = int(input("Who should start the game? (1. Player / 2. AI): "))
    turn = PLAYER if start_player == 1 else AI
elif mode == 3:
    turn = AI
else:
    print("Invalid mode. Defaulting to Player vs AI.")
    turn = PLAYER

game_over = False

# Main Game Loop
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if mode == 1:
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                color = RED if turn == PLAYER else YELLOW
                pygame.draw.circle(screen, color, (posx, int(SQUARESIZE/2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    piece = PLAYER_PIECE if turn == PLAYER else AI_PIECE
                    drop_piece(board, row, col, piece)

                    score = score_position(board, piece)
                    print(f"Score for Player {piece}: {score}")

                    if winning_move(board, piece):
                        label_text = "Player 1 wins!!" if turn == PLAYER else "Player 2 wins!!"
                        label_color = RED if turn == PLAYER else YELLOW
                        label = myfont.render(label_text, 1, label_color)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn = AI if turn == PLAYER else PLAYER

                    if game_over:
                        pygame.time.wait(2000)
                        ask_restart()

        elif mode == 2:
            if turn == PLAYER:
                if event.type == pygame.MOUSEMOTION:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                    pygame.display.update()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        score = score_position(board, PLAYER_PIECE)
                        print(f"Score for Player: {score}")

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player wins!!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True

                        print_board(board)
                        draw_board(board)

                        turn = AI

                        if game_over:
                            pygame.time.wait(2000)
                            ask_restart()

            elif turn == AI and not game_over:
                col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)
                if is_valid_location(board, col):
                    pygame.time.wait(500)
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, AI_PIECE)

                    score = score_position(board, AI_PIECE)
                    print(f"Score for AI: {score}")

                    if winning_move(board, AI_PIECE):
                        label = myfont.render("AI wins!!", 1, YELLOW)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn = PLAYER

                    if game_over:
                        pygame.time.wait(2000)
                        ask_restart()

        elif mode == 3:
            if not game_over:
                pygame.time.wait(500)
                col, minimax_score = minimax(board, depth, -math.inf, math.inf, True)
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    piece = AI_PIECE if turn == AI else PLAYER_PIECE
                    drop_piece(board, row, col, piece)

                    score = score_position(board, piece)
                    print(f"Score for {'AI 1' if turn == AI else 'AI 2'}: {score}")

                    if winning_move(board, piece):
                        label_text = "AI 1 wins!!" if turn == AI else "AI 2 wins!!"
                        label_color = YELLOW if turn == AI else RED
                        label = myfont.render(label_text, 1, label_color)
                        screen.blit(label, (40, 10))
                        game_over = True

                    print_board(board)
                    draw_board(board)

                    turn = AI if turn == PLAYER else PLAYER

                    if game_over:
                        pygame.time.wait(2000)
                        ask_restart()