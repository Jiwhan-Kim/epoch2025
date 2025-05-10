from model.ollama import get_ai_answer

import pygame
import os
import re
import copy
from chessMove import isLegalMove, Piece, getAttackPoses
import time

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
BUTTON_RESTART = pygame.Rect(640, 130, 80, 30)
BUTTON_AI = pygame.Rect(640, 250, 80, 30)
PIECE_VALUES = {
    "king": 0,       # 체크메이트는 따로 처리
    "queen": 9,
    "rook": 5,
    "bishop": 3,
    "knight": 3,
    "pawn": 1,
}


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

def is_king_in_check(board, color):
    king_pos = None
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece and piece.color == color and piece.kind == "king":
                king_pos = (row, col)
                break
    if not king_pos:
        return True  # King not found, technically in check

    attack_board = get_attack_board(board, "black" if color == "white" else "white")
    return attack_board[king_pos[0]][king_pos[1]]

def is_king_in_check_after_move(board, from_pos, to_pos):
    temp_board = copy.deepcopy(board)
    r1 = 8 - int(from_pos[1])
    c1 = ord(from_pos[0].lower()) - ord('a')
    r2 = 8 - int(to_pos[1])
    c2 = ord(to_pos[0].lower()) - ord('a')

    piece = temp_board[r1][c1]
    temp_board[r2][c2] = piece
    temp_board[r1][c1] = None

    if not piece:
        return False

    return is_king_in_check(temp_board, piece.color)

def show_check_text(screen, font, board, turn):
    pygame.draw.rect(screen, (0, 0, 0), (630, 140, 90, 20))  # clear area
    if is_king_in_check(board, turn):
        text = font.render("Check!", True, (255, 0, 0))
        screen.blit(text, (645, 140))

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

def is_king_checkmate(board, attacker_color):
    """
    Return True if the given color's king is in checkmate.
    """
    if not is_king_in_check(board, attacker_color):
        return False

    # check all possible moves of all own pieces
    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if not piece or piece.color != attacker_color:
                continue
            from_pos = f"{chr(c1 + ord('a'))}{8 - r1}"
            for r2 in range(8):
                for c2 in range(8):
                    if r1 == r2 and c1 == c2:
                        continue
                    to_pos = f"{chr(c2 + ord('a'))}{8 - r2}"
                    move_str = f"{piece.kind.capitalize()}-{from_pos}-{to_pos}"
                    if isLegalMove(board, move_str):
                        temp_board = copy.deepcopy(board)
                        temp_board[r2][c2] = temp_board[r1][c1]
                        temp_board[r1][c1] = None
                        if not is_king_in_check(temp_board, attacker_color):
                            return False  # at least one valid move that escapes check
    return True  # no valid move escapes check


    from_row, from_col = king_pos
    from_pos = f"{chr(from_col + ord('a'))}{8 - from_row}"

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            to_row = from_row + dr
            to_col = from_col + dc
            if 0 <= to_row < 8 and 0 <= to_col < 8:
                to_pos = f"{chr(to_col + ord('a'))}{8 - to_row}"
                move_str = f"King-{from_pos}-{to_pos}"
                if isLegalMove(board, move_str) and not is_king_in_check_after_move(board, from_pos, to_pos):
                    # simulate move
                    temp_board = copy.deepcopy(board)
                    temp_board[to_row][to_col] = temp_board[from_row][from_col]
                    temp_board[from_row][from_col] = None
                    if not is_king_in_check(temp_board, attacker_color):
                        return False  # has a safe move
    return True  # no safe move

def is_stalemate(board, color):
    """
    Return True if the player of 'color' has no legal moves and is NOT in check (stalemate).
    """
    # 1. 킹이 체크 상태이면 스테일메이트 아님
    if is_king_in_check(board, color):
        return False

    # 2. 자신의 모든 말에 대해 가능한 이동이 1개라도 있는지 확인
    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if not piece or piece.color != color:
                continue
            from_pos = f"{chr(c1 + ord('a'))}{8 - r1}"
            for r2 in range(8):
                for c2 in range(8):
                    if r1 == r2 and c1 == c2:
                        continue
                    to_pos = f"{chr(c2 + ord('a'))}{8 - r2}"
                    move_str = f"{piece.kind.capitalize()}-{from_pos}-{to_pos}"
                    if isLegalMove(board, move_str):
                        temp_board = copy.deepcopy(board)
                        temp_board[r2][c2] = temp_board[r1][c1]
                        temp_board[r1][c1] = None
                        if not is_king_in_check(temp_board, color):
                            return False  # valid move exists
    return True  # no valid moves and not in check → stalemate

def is_game_ended(board, color):
    return is_king_checkmate(board, color) or is_stalemate(board, color)

def evaluate_board(board, color):
    """Return material score from the perspective of `color`."""
    score = 0
    for row in board:
        for piece in row:
            if piece:
                value = PIECE_VALUES.get(piece.kind, 0)
                if piece.color == color:
                    score += value
                else:
                    score -= value
    return score

def get_best_move(board, color, game_state):
    """Return best move_str for the given color based on simple evaluation."""
    best_score = float('-inf')
    best_move = None

    for r1 in range(8):
        for c1 in range(8):
            piece = board[r1][c1]
            if not piece or piece.color != color:
                continue

            from_pos = f"{chr(c1 + ord('a'))}{8 - r1}"
            for r2 in range(8):
                for c2 in range(8):
                    if r1 == r2 and c1 == c2:
                        continue
                    to_pos = f"{chr(c2 + ord('a'))}{8 - r2}"
                    move_str = f"{piece.kind.capitalize()}-{from_pos}-{to_pos}"

                    if isLegalMove(board, move_str, game_state):
                        # simulate move
                        temp_board = copy.deepcopy(board)
                        temp_board[r2][c2] = temp_board[r1][c1]
                        temp_board[r1][c1] = None

                        score = evaluate_board(temp_board, color)
                        if score > best_score:
                            best_score = score
                            best_move = move_str

    return best_move

def run_chess_gui(board):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess with Beginner Mode")
    piece_images = load_piece_images()
    font = pygame.font.SysFont(None, 24)

    white_time = 600  # seconds (10 minutes)
    black_time = 600
    last_time = time.time()

    dragging = False
    dragging_piece = None
    mouse_x, mouse_y = 0, 0
    turn_count = 1
    current_turn = "white"
    move_history = []
    board_history = [copy.deepcopy(board)]
    current_state_index = 0
    game_state = {
        "lastMove": None,
        "turnCount": turn_count  # now storing numeric turn
    }
    beginner_mode = False

    running = True
    game_over = False
    result_message = ""
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

        pygame.draw.rect(screen, (200, 200, 255), BUTTON_AI)
        screen.blit(font.render("AI move", True, (0, 0, 0)), (650, 255))
        pygame.draw.rect(screen, (255, 255, 255), (630, 300, 90, 50))  # clear time display background
        screen.blit(font.render(result_message, True, (255, 0, 0)), (635, 205))

        show_check_text(screen, font, board, current_turn)

        # 시간 표시
        elapsed = time.time() - last_time
        if not game_over:
            if current_turn == "white":
                white_time -= elapsed
            else:
                black_time -= elapsed
        last_time = time.time()

        screen.blit(font.render(f"W: {int(white_time//60):02}:{int(white_time%60):02}", True, (0,0,0)), (640, 300))
        screen.blit(font.render(f"B: {int(black_time//60):02}:{int(black_time%60):02}", True, (0,0,0)), (640, 320))

        if white_time <= 0:
            result_message = "Black wins on time"
            game_over = True
        elif black_time <= 0:
            result_message = "White wins on time"
            game_over = True
        if not game_over:
            if is_king_in_check(board, current_turn):
                if is_king_checkmate(board, current_turn):
                    result_message = f"{('White' if current_turn == 'black' else 'Black')} wins by checkmate"
                    game_over = True
            elif is_stalemate(board, current_turn):
                result_message = "Stalemate"
                game_over = True

        if game_over:
            pygame.draw.rect(screen, (255, 200, 200), (640, 170, 80, 30))
            pygame.draw.rect(screen, (0, 0, 0), (630, 200, 90, 30))
            screen.blit(font.render("Restart", True, (0, 0, 0)), (645, 175))

        show_check_text(screen, font, board, current_turn)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if BUTTON_AI.collidepoint(event.pos):
                    if not game_over and current_turn == "black":
                        while True:
                            move_str = get_best_move(board, current_turn, game_state)
                            print(move_str)
                            try:
                                _, from_pos, to_pos = move_str.split("-")
                                from_row = 8 - int(from_pos[1])
                                from_col = ord(from_pos[0]) - ord('a')
                                to_row = 8 - int(to_pos[1])
                                to_col = ord(to_pos[0]) - ord('a')
                                piece = board[from_row][from_col]
                                if piece and isLegalMove(board, move_str, game_state):
                                    break
                            except:
                                print("ERROR")
                                continue
                        try:
                            _, from_pos, to_pos = move_str.split("-")
                            from_row = 8 - int(from_pos[1])
                            from_col = ord(from_pos[0]) - ord('a')
                            to_row = 8 - int(to_pos[1])
                            to_col = ord(to_pos[0]) - ord('a')
                            piece = board[from_row][from_col]
                            if piece:
                                if isLegalMove(board, move_str, game_state):
                                    board[to_row][to_col] = piece
                                    board[from_row][from_col] = None
                                    game_state["turnCount"] = turn_count  # Removed lastMove usage
                                    move_history.append(move_str)
                                    board_history = board_history[:current_state_index + 1]
                                    board_history.append(copy.deepcopy(board))
                                    current_state_index += 1

                                    print_board(board)

                                    turn_count += 1
                            current_turn = "black" if current_turn == "white" else "white"
                            last_time = time.time()
                        except Exception as e:
                            print("AI move error:", e)

                print(board)
                if game_over and pygame.Rect(640, 170, 80, 30).collidepoint(event.pos):
                    board = create_initial_board()
                    piece_images = load_piece_images()
                    dragging = False
                    dragging_piece = None
                    mouse_x, mouse_y = 0, 0
                    turn_count = 1
                    current_turn = "white"
                    move_history.clear()
                    board_history = [copy.deepcopy(board)]
                    current_state_index = 0
                    # Removed lastMove reference
                    game_state["turnCount"] = turn_count
                    game_state["turnCount"] = turn_count
                    game_over = False
                    result_message = ""
                    continue
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
                    if game_over:
                        continue
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
                        if isLegalMove(board, move_str, game_state) and current_state_index == len(board_history) - 1 and not is_king_in_check_after_move(board, index_to_pos(from_row, from_col), index_to_pos(row, col)):
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

                            game_state["turnCount"] = turn_count  # Removed lastMove usage
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
