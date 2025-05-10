import pygame
import os
import re
from chessMove import isLegalMove

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
            image = piece_images.get(piece)
            if image:
                screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    if dragging_piece and dragging_pos:
        row, col = dragging_piece
        piece = board[row][col]
        image = piece_images.get(piece)
        if image:
            rect = image.get_rect(center=dragging_pos)
            screen.blit(image, rect)

def print_board(board):
    print("\nCurrent Board State:")
    for row in board:
        print(["{:>11}".format(cell if cell else "") for cell in row])
    print("-" * 100)

def index_to_pos(row, col):
    return f"{chr(col + ord('a'))}{8 - row}"

def run_chess_gui(board):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess with Legal Move Check")
    piece_images = load_piece_images()

    dragging = False
    dragging_piece = None
    mouse_x, mouse_y = 0, 0

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
                    piece_type = piece.split('-')[1].capitalize()
                    move_str = f"{piece_type}-{index_to_pos(from_row, from_col)}-{index_to_pos(row, col)}"
                    if isLegalMove(board, move_str):
                        board[row][col] = piece
                        board[from_row][from_col] = ""
                        print_board(board)
                    else:
                        print(f"Illegal move: {move_str}")
                dragging = False
                dragging_piece = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos

    pygame.quit()

# Sample board using "color-piece" format
sample_board = [
    ["black-rook", "black-knight", "black-bishop", "black-queen", "black-king", "black-bishop", "black-knight", "black-rook"],
    ["black-pawn"] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    [""] * 8,
    ["white-pawn"] * 8,
    ["white-rook", "white-knight", "white-bishop", "white-queen", "white-king", "white-bishop", "white-knight", "white-rook"]
]

if __name__ == "__main__":
    run_chess_gui(sample_board)