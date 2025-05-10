import pygame
import os
import re
from chessMove import isLegalMove, Piece

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE_COLOR = (240, 217, 181)
BLACK_COLOR = (181, 136, 99)
ASSET_DIR = "assets/images"

def draw_board(screen):
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE_COLOR if (row + col) % 2 == 0 else BLACK_COLOR
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
    pygame.display.set_caption("Chess with Class-Based Pieces")
    piece_images = load_piece_images()

    dragging = False
    dragging_piece = None
    mouse_x, mouse_y = 0, 0
    turn_count = 1
    game_state = {
        "lastMove": None
    }

    running = True
    while running:
        draw_board(screen)
        draw_pieces(screen, board, piece_images, dragging_piece, (mouse_x, mouse_y) if dragging else None)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                if board[row][col]:
                    dragging = True
                    dragging_piece = (row, col)
                    mouse_x, mouse_y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                from_row, from_col = dragging_piece
                piece = board[from_row][from_col]
                if piece:
                    move_str = f"{piece.kind.capitalize()}-{index_to_pos(from_row, from_col)}-{index_to_pos(row, col)}"
                    if isLegalMove(board, move_str, game_state):
                        # Castling rook move
                        if piece.kind == "king" and abs(col - from_col) == 2:
                            rook_from = 0 if col < from_col else 7
                            rook_to = from_col - 1 if col < from_col else from_col + 1
                            board[from_row][rook_to] = board[from_row][rook_from]
                            board[from_row][rook_from] = None
                            board[from_row][rook_to].has_moved = True

                        # En passant capture
                        if piece.kind == "pawn" and col != from_col and board[row][col] is None:
                            board[from_row][col] = None

                        board[row][col] = piece
                        board[from_row][from_col] = None

                        # Update piece state
                        if piece.kind in ["king", "rook"]:
                            piece.has_moved = True
                        if piece.kind == "pawn" and abs(row - from_row) == 2:
                            piece.double_move_turn = turn_count

                        game_state["lastMove"] = move_str
                        print_board(board)
                        turn_count += 1
                    else:
                        print(f"Illegal move: {move_str}")
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