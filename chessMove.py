# sde
import re

def pos_to_index(pos):
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    return row, col

def is_clear_path(board, r1, c1, r2, c2):
    dr = (r2 - r1) and (1 if r2 > r1 else -1)
    dc = (c2 - c1) and (1 if c2 > c1 else -1)

    cur_r, cur_c = r1 + dr, c1 + dc
    while (cur_r, cur_c) != (r2, c2):
        if board[cur_r][cur_c] != "":
            return False
        cur_r += dr
        cur_c += dc
    return True

def isLegalMove(board, move_str):
    match = re.match(r"([a-zA-Z]+)-([a-h][1-8])-([a-h][1-8])", move_str)
    if not match:
        return False

    piece_type, from_pos, to_pos = match.groups()
    piece_type = piece_type.lower()
    from_row, from_col = pos_to_index(from_pos)
    to_row, to_col = pos_to_index(to_pos)

    piece = board[from_row][from_col]
    if not piece:
        return False

    color, actual_type = piece.split('-')
    if actual_type != piece_type:
        return False

    target = board[to_row][to_col]
    if target and target.startswith(color):
        return False  # can't capture own piece

    dr, dc = to_row - from_row, to_col - from_col
    abs_dr, abs_dc = abs(dr), abs(dc)

    if piece_type == "king":
        return max(abs_dr, abs_dc) == 1

    elif piece_type == "queen":
        if abs_dr == abs_dc or dr == 0 or dc == 0:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece_type == "rook":
        if dr == 0 or dc == 0:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece_type == "bishop":
        if abs_dr == abs_dc:
            return is_clear_path(board, from_row, from_col, to_row, to_col)
        return False

    elif piece_type == "knight":
        return (abs_dr, abs_dc) in [(2, 1), (1, 2)]

    elif piece_type == "pawn":
        direction = -1 if color == "white" else 1
        start_row = 6 if color == "white" else 1
        if dc == 0:
            if dr == direction and board[to_row][to_col] == "":
                return True
            if from_row == start_row and dr == 2 * direction and board[from_row + direction][from_col] == "" and board[to_row][to_col] == "":
                return True
        elif abs_dc == 1 and dr == direction and board[to_row][to_col] and not board[to_row][to_col].startswith(color):
            return True
        return False

    return False
