import pygame
import os
import re
import copy
from chessMove import isLegalMove, Piece, getAttackPoses

# Constants
WIDTH, HEIGHT = 720, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = 640 // COLS
WHITE_COLOR = (240, 217, 181)
BLACK_COLOR = (181, 136, 99)
DANGER_COLOR = (255, 100, 100)
ASSET_DIR = "assets/images"
BUTTON_HISTORY = pygame.Rect(640, 10, 70, 30)
BUTTON_BACK = pygame.Rect(640, 50, 30, 30)
BUTTON_FORWARD = pygame.Rect(680, 50, 30, 30)
BUTTON_BEGINNER = pygame.Rect(640, 90, 80, 30)

def get_attack_board(board, attacker_color):
    attack_board = [[False for _ in range(8)] for _ in range(8)]
    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if not piece or piece.color != attacker_color:
                continue
            for r2 in range(8):
                for c2 in range(8):
                    if r1 == r2 and c1 == c2:
                        continue
                    move_str = f"{piece.kind.capitalize()}-{chr(c1+97)}{8-r1}-{chr(c2+97)}{8-r2}"
                    attack_poses = getAttackPoses(board, piece.kind.capitalize(), f"{chr(c1+97)}{8-r1}")

                    for attackPos in attack_poses:
                        x, y = attackPos
                        attack_board[x][y] = True
    return attack_board

def draw_board(screen, attack_board=None):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE_COLOR if (row + col) % 2 == 0 else BLACK_COLOR
            if attack_board and attack_board[row][col]:
                color = DANGER_COLOR
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))



def load_piece_images():
    piece_images = {}
    for color in ['white', 'black']:
        for piece_type in ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']:
            filename = f"{color}-{piece_type}.png"
            full_path = os.path.join(ASSET_DIR, filename)
            try:
                image = pygame.image.load(full_path)
                image = pygame.transform.smoothscale(image, (SQUARE_SIZE, SQUARE_SIZE))
                piece_images[f"{color}-{piece_type}"] = image
            except pygame.error:
                print(f"Could not load image: {full_path}")
    return piece_images

def draw_pieces(screen, board, piece_images, dragging_piece=None, dragging_pos=None):
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if not piece:
                continue
            if dragging_piece and dragging_piece == (row, col):
                continue
            key = f"{piece.color}-{piece.kind}"
            image = piece_images.get(key)
            if image:
                screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    if dragging_piece and dragging_pos:
        row, col = dragging_piece
        piece = board[row][col]
        key = f"{piece.color}-{piece.kind}"
        image = piece_images.get(key)
        if image:
            rect = image.get_rect(center=dragging_pos)
            screen.blit(image, rect)

def print_board(board):
    print("\nCurrent Board State:")
    for row in board:
        print([str(cell) if cell else "" for cell in row])
    print("-" * 100)

def index_to_pos(row, col):
    return f"{chr(col + ord('a'))}{8 - row}"

def run_chess_gui(board):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess with Beginner Mode")
    piece_images = load_piece_images()
    font = pygame.font.SysFont(None, 24)

    dragging = False
    dragging_piece = None
    mouse_x, mouse_y = 0, 0
    turn_count = 1
    current_turn = "white"
    move_history = []
    board_history = [copy.deepcopy(board)]
    current_state_index = 0
    game_state = {
        "lastMove": None
    }
    beginner_mode = False

    running = True
    while running:
        attack_board = get_attack_board(board, 'black' if current_turn == 'white' else 'white') if beginner_mode else None

        draw_board(screen, attack_board)
        draw_pieces(screen, board, piece_images, dragging_piece, (mouse_x, mouse_y) if dragging else None)

        pygame.draw.rect(screen, (200, 200, 200), BUTTON_HISTORY)
        pygame.draw.rect(screen, (180, 180, 180), BUTTON_BACK)
        pygame.draw.rect(screen, (180, 180, 180), BUTTON_FORWARD)
        pygame.draw.rect(screen, (180, 255, 180), BUTTON_BEGINNER)
        screen.blit(font.render("History", True, (0, 0, 0)), (BUTTON_HISTORY.x + 5, BUTTON_HISTORY.y + 5))
        screen.blit(font.render("<", True, (0, 0, 0)), (BUTTON_BACK.x + 8, BUTTON_BACK.y + 5))
        screen.blit(font.render(">", True, (0, 0, 0)), (BUTTON_FORWARD.x + 8, BUTTON_FORWARD.y + 5))
        screen.blit(font.render("Beginner", True, (0, 0, 0)), (BUTTON_BEGINNER.x + 2, BUTTON_BEGINNER.y + 5))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if BUTTON_HISTORY.collidepoint(event.pos):
                    print("\nMove History:")
                    for move in move_history:
                        print(move)
                    continue
                elif BUTTON_BACK.collidepoint(event.pos):
                    if current_state_index > 0:
                        current_state_index -= 1
                        board = copy.deepcopy(board_history[current_state_index])
                        current_turn = "white" if current_state_index % 2 == 0 else "black"
                    continue
                elif BUTTON_FORWARD.collidepoint(event.pos):
                    if current_state_index < len(board_history) - 1:
                        current_state_index += 1
                        board = copy.deepcopy(board_history[current_state_index])
                        current_turn = "white" if current_state_index % 2 == 0 else "black"
                    continue
                elif BUTTON_BEGINNER.collidepoint(event.pos):
                    beginner_mode = not beginner_mode
                    continue

                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if 0 <= row < 8 and 0 <= col < 8:
                    if board[row][col] and board[row][col].color == current_turn:
                        dragging = True
                        dragging_piece = (row, col)
                        mouse_x, mouse_y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if 0 <= row < 8 and 0 <= col < 8:
                    from_row, from_col = dragging_piece
                    piece = board[from_row][from_col]
                    if piece:
                        move_str = f"{piece.kind.capitalize()}-{index_to_pos(from_row, from_col)}-{index_to_pos(row, col)}"
                        if isLegalMove(board, move_str, game_state) and current_state_index == len(board_history) - 1:
                            if piece.kind == "king" and abs(col - from_col) == 2:
                                rook_from = 0 if col < from_col else 7
                                rook_to = from_col - 1 if col < from_col else from_col + 1
                                board[from_row][rook_to] = board[from_row][rook_from]
                                board[from_row][rook_from] = None
                                board[from_row][rook_to].has_moved = True

                            if piece.kind == "pawn" and col != from_col and board[row][col] is None:
                                board[from_row][col] = None

                            board[row][col] = piece
                            board[from_row][from_col] = None

                            if piece.kind in ["king", "rook"]:
                                piece.has_moved = True
                            if piece.kind == "pawn" and abs(row - from_row) == 2:
                                piece.double_move_turn = turn_count

                            game_state["lastMove"] = move_str
                            move_history.append(move_str)
                            board_history = board_history[:current_state_index + 1]
                            board_history.append(copy.deepcopy(board))
                            current_state_index += 1

                            print_board(board)
                            turn_count += 1
                            current_turn = "black" if current_turn == "white" else "white"
                        else:
                            print(f"Illegal move or not at latest state: {move_str}")
                dragging = False
                dragging_piece = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos

    pygame.quit()


def create_initial_board():
    board = [[None for _ in range(8)] for _ in range(8)]
    order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    for i in range(8):
        board[0][i] = Piece("black", order[i])
        board[1][i] = Piece("black", "pawn")
        board[6][i] = Piece("white", "pawn")
        board[7][i] = Piece("white", order[i])
    return board

if __name__ == "__main__":
    run_chess_gui(create_initial_board())
