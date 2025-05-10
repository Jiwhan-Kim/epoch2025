import pygame
import os

# Constants
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS
WHITE_COLOR = (240, 217, 181)
BLACK_COLOR = (181, 136, 99)
ASSET_DIR = "assets/images"

def algebraic_to_index(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    return row, col

def index_to_algebraic(row, col):
    return f"{chr(col + ord('a'))}{8 - row}"

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
                piece_images[(color, piece_type)] = image
            except pygame.error:
                print(f"Could not load image: {full_path}")
    return piece_images

def draw_pieces(screen, board_data, piece_images, dragging_piece=None, dragging_pos=None):
    for color, pieces in board_data.items():
        for piece, pos in pieces.items():
            if dragging_piece and dragging_piece == (color, piece):
                continue  # Skip drawing dragged piece (drawn later)
            row, col = algebraic_to_index(pos)
            piece_type = ''.join([c for c in piece if not c.isdigit()])
            image = piece_images.get((color, piece_type))
            if image:
                screen.blit(image, (col * SQUARE_SIZE, row * SQUARE_SIZE))

    if dragging_piece and dragging_pos:
        color, piece = dragging_piece
        piece_type = ''.join([c for c in piece if not c.isdigit()])
        image = piece_images.get((color, piece_type))
        if image:
            rect = image.get_rect(center=dragging_pos)
            screen.blit(image, rect)

def find_piece_at(board_data, row, col):
    target_pos = index_to_algebraic(row, col)
    for color, pieces in board_data.items():
        for piece, pos in pieces.items():
            if pos == target_pos:
                return color, piece
    return None, None

def run_chess_gui(board_data):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess Drag-and-Drop")
    piece_images = load_piece_images()

    dragging = False
    dragging_piece = None
    mouse_x, mouse_y = 0, 0

    running = True
    while running:
        draw_board(screen)
        draw_pieces(screen, board_data, piece_images, dragging_piece, (mouse_x, mouse_y) if dragging else None)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                color, piece = find_piece_at(board_data, row, col)
                if piece:
                    dragging = True
                    dragging_piece = (color, piece)
                    mouse_x, mouse_y = event.pos

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                col, row = event.pos[0] // SQUARE_SIZE, event.pos[1] // SQUARE_SIZE
                new_pos = index_to_algebraic(row, col)
                color, piece = dragging_piece
                board_data[color][piece] = new_pos
                dragging = False
                dragging_piece = None

            elif event.type == pygame.MOUSEMOTION and dragging:
                mouse_x, mouse_y = event.pos

    pygame.quit()

# Sample board input
sample_board = {
    "white": {"king": "e1", "queen": "d1", "rook1": "a1", "rook2": "h1", "bishop1": "c1", "bishop2": "f1",
              "knight1": "b1", "knight2": "g1", "pawn1": "a2", "pawn2": "b2", "pawn3": "c2", "pawn4": "d2",
              "pawn5": "e2", "pawn6": "f2", "pawn7": "g2", "pawn8": "h2"},
    "black": {"king": "e8", "queen": "d8", "rook1": "a8", "rook2": "h8", "bishop1": "c8", "bishop2": "f8",
              "knight1": "b8", "knight2": "g8", "pawn1": "a7", "pawn2": "b7", "pawn3": "c7", "pawn4": "d7",
              "pawn5": "e7", "pawn6": "f7", "pawn7": "g7", "pawn8": "h7"}
}

if __name__ == "__main__":
    run_chess_gui(sample_board)
