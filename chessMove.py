from piece import *
def pos_to_index(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    return row, col

def is_clear_path(board, r1, c1, r2, c2):
    dr = (r2 - r1) and (1 if r2 > r1 else -1)
    dc = (c2 - c1) and (1 if c2 > c1 else -1)

    cur_r, cur_c = r1 + dr, c1 + dc
    while (cur_r, cur_c) != (r2, c2):
        if board[cur_r][cur_c] is not None:
            return False
        cur_r += dr
        cur_c += dc
    return True

def isLegalMove(board, move_str, state=None):
    import re
    match = re.match(r"([a-zA-Z]+)-([a-h][1-8])-([a-h][1-8])", move_str)
    if not match:
        return False

    piece_type, from_pos, to_pos = match.groups()
    piece_type = piece_type.lower()
    from_row, from_col = pos_to_index(from_pos)
    to_row, to_col = pos_to_index(to_pos)

    piece = board[from_row][from_col]
    if not piece or piece.kind != piece_type:
        return False

    target = board[to_row][to_col]
    if target and target.color == piece.color:
        return False

    dr, dc = to_row - from_row, to_col - from_col
    abs_dr, abs_dc = abs(dr), abs(dc)

    # Castling logic
    if piece.kind == "king" and abs_dc == 2 and dr == 0:
        if piece.has_moved:
            return False
        rook_col = 0 if dc == -2 else 7
        rook = board[from_row][rook_col]
        if not rook or rook.kind != "rook" or rook.color != piece.color or rook.has_moved:
            return False
        return is_clear_path(board, from_row, from_col, from_row, rook_col)

    if piece.kind == "king":
        return max(abs_dr, abs_dc) == 1

    elif piece.kind == "queen":
        if abs_dr == abs_dc or dr == 0 or dc == 0:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece.kind == "rook":
        if dr == 0 or dc == 0:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece.kind == "bishop":
        if abs_dr == abs_dc:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece.kind == "knight":
        return (abs_dr, abs_dc) in [(2, 1), (1, 2)]

    elif piece.kind == "pawn":
        direction = -1 if piece.color == "white" else 1
        start_row = 6 if piece.color == "white" else 1
        if dc == 0:
            if dr == direction and board[to_row][to_col] is None:
                return True
            if from_row == start_row and dr == 2 * direction and board[from_row + direction][from_col] is None and board[to_row][to_col] is None:
                return True
        elif abs_dc == 1 and dr == direction:
            if board[to_row][to_col] and board[to_row][to_col].color != piece.color:
                return True
            # En passant
            if state:
                last_move = state.get("lastMove")
                if last_move:
                    last_piece_type, last_from, last_to = re.match(r"([a-zA-Z]+)-([a-h][1-8])-([a-h][1-8])", last_move).groups()
                    last_from_row, last_from_col = pos_to_index(last_from)
                    last_to_row, last_to_col = pos_to_index(last_to)
                    last_piece = board[last_to_row][last_to_col]
                    if last_piece and last_piece.kind == "pawn" and abs(last_to_row - last_from_row) == 2:
                        if last_to_row == from_row and last_to_col == to_col:
                            return True
        return False

    return False

def getPawnAttackSquares(board, position):
    """
    Return list of squares that the pawn at 'position' can attack (not move to).
    Only diagonal capture squares, regardless of whether a piece is there.
    """
    r = 8 - int(position[1])
    c = ord(position[0].lower()) - ord('a')

    if not (0 <= r < 8 and 0 <= c < 8):
        return []

    piece = board[r][c]
    if not piece or piece.kind != 'pawn':
        return []

    direction = -1 if piece.color == 'white' else 1
    attack_squares = []

    for dc in [-1, 1]:
        new_r = r + direction
        new_c = c + dc
        if 0 <= new_r < 8 and 0 <= new_c < 8:
            attack_squares.append((new_r, new_c))

    return attack_squares


def getAttackPoses(board, piece_type, position):
    """
    Return a list of positions the given piece type can attack from the given position.
    e.g., getAttackPoses(board, "KING", "e4")
    """
    poses = []
    r1 = 8 - int(position[1])
    c1 = ord(position[0].lower()) - ord('a')
    piece_type = piece_type.lower()

    piece = board[r1][c1]
    if not piece or piece.kind != piece_type:
        return []

    if piece_type == "pawn":
        return getPawnAttackSquares(board, position)

    for r2 in range(8):
        for c2 in range(8):
            if r1 == r2 and c1 == c2:
                continue
            move_str = f"{piece_type.capitalize()}-{position}-{chr(c2 + 97)}{8 - r2}"
            if isLegalMove(board, move_str):
                poses.append((r2, c2))

    return poses

