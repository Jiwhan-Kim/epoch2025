import re
from copy import deepcopy
from typing import List, Tuple

# --------------------------------------------------------------------
# Coordinate helpers
# --------------------------------------------------------------------
FILES = "abcdefghijklmnopqrstuvwxyz"               # extendable
BOARD_SIZE = 8                                     # classic chess


def square_to_coords(square: str) -> Tuple[int, int]:
    """
    "a4" -> (row, col) where row 0 is black's back rank (rank 8)
    Supports multi-letter files ("aa1") and multi-digit ranks ("a12").
    """
    m = re.fullmatch(r"([a-zA-Z]+)(\d+)", square.strip())
    if not m:
        raise ValueError(f"Bad square: {square}")
    file_part, rank_part = m.groups()

    # calculate 0-based file index (a=0, b=1 …, z=25, aa=26, ab=27, …)
    col = 0
    for ch in file_part.lower():
        col = col * 26 + (ord(ch) - ord("a") + 1)
    col -= 1

    # rank 1 is white back rank → row 7
    row = BOARD_SIZE - int(rank_part)
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        raise ValueError(f"Square {square} is off the board")
    return row, col


# --------------------------------------------------------------------
# Rule helpers
# --------------------------------------------------------------------
DIR_WHITE, DIR_BLACK = -1, +1                      # “forward” for each colour


def path_clear(board: List[List[str]],
               r0: int, c0: int, r1: int, c1: int) -> bool:
    """True if every intermediate square on a rook/bishop/queen ray is empty."""
    dr = (r1 - r0) and (1 if r1 > r0 else -1)
    dc = (c1 - c0) and (1 if c1 > c0 else -1)
    r, c = r0 + dr, c0 + dc
    while (r, c) != (r1, c1):
        if board[r][c]:
            return False
        r, c = r + dr, c + dc
    return True


# --------------------------------------------------------------------
# Piece-specific legality checks
# --------------------------------------------------------------------
def legal_king(board, colour, r0, c0, r1, c1):
    return max(abs(r1 - r0), abs(c1 - c0)) == 1


def legal_knight(board, colour, r0, c0, r1, c1):
    return sorted((abs(r1 - r0), abs(c1 - c0))) == [1, 2]


def legal_rook(board, colour, r0, c0, r1, c1):
    return (r0 == r1 or c0 == c1) and path_clear(board, r0, c0, r1, c1)


def legal_bishop(board, colour, r0, c0, r1, c1):
    return abs(r1 - r0) == abs(c1 - c0) and path_clear(board, r0, c0, r1, c1)


def legal_queen(board, colour, r0, c0, r1, c1):
    return (legal_rook(board, colour, r0, c0, r1, c1) or
            legal_bishop(board, colour, r0, c0, r1, c1))


def legal_pawn(board, colour, r0, c0, r1, c1):
    direction = DIR_WHITE if colour == "white" else DIR_BLACK
    start_rank = 6 if colour == "white" else 1

    # Simple one-square push
    if c0 == c1 and r1 - r0 == direction and not board[r1][c1]:
        return True
    # Two squares from starting rank
    if (c0 == c1 and r0 == start_rank and
        r1 - r0 == 2 * direction and
        not board[r0 + direction][c0] and
            not board[r1][c1]):
        return True
    # Captures
    if abs(c1 - c0) == 1 and r1 - r0 == direction and board[r1][c1]:
        target_colour, _ = board[r1][c1].split("-")
        return target_colour != colour
    return False


LEGALITY_DISPATCH = {
    "king":   legal_king,
    "queen":  legal_queen,
    "rook":   legal_rook,
    "bishop": legal_bishop,
    "knight": legal_knight,
    "pawn":   legal_pawn,
}

# --------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------


def move_piece(board: List[List[str]], move: List[str]) -> None:
    """
    `move` is like ["king", "a4", "a5"].
    Mutates `board` if the move is legal; raises ValueError otherwise.
    """
    if len(move) != 3:
        raise ValueError("Move must be [piece, from_sq, to_sq]")

    piece_name, from_sq, to_sq = (s.strip().lower() for s in move)
    r0, c0 = square_to_coords(from_sq)
    r1, c1 = square_to_coords(to_sq)

    piece_str = board[r0][c0]
    if not piece_str:
        raise ValueError(f"No piece on {from_sq}")
    colour, real_piece = piece_str.split("-")
    if real_piece != piece_name:
        raise ValueError(f"{from_sq} contains a {
                         real_piece}, not a {piece_name}")

    # Target square must not hold a friendly piece
    if board[r1][c1]:
        tgt_colour, _ = board[r1][c1].split("-")
        if tgt_colour == colour:
            raise ValueError("Cannot capture your own piece")

    # Pseudo-legal move according to the piece’s movement pattern
    try:
        ok = LEGALITY_DISPATCH[real_piece](board, colour, r0, c0, r1, c1)
    except KeyError:
        raise ValueError(f"Unknown piece type: {real_piece!r}")
    if not ok:
        raise ValueError(f"Illegal move for {
                         colour}-{real_piece}: {from_sq} → {to_sq}")

    # All checks passed – perform the move
    board[r1][c1], board[r0][c0] = board[r0][c0], ""
    # (At this level we ignore check, check-mate, castling, en-passant, promotion.)


# --------------------------------------------------------------------
# Example
# --------------------------------------------------------------------
if __name__ == "__main__":
    sample_board = [
        ["black-rook", "black-knight", "black-bishop", "black-queen",
            "black-king", "black-bishop", "black-knight", "black-rook"],
        ["black-pawn"] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        [""] * 8,
        ["white-pawn"] * 8,
        ["white-rook", "white-knight", "white-bishop", "white-queen",
            "white-king", "white-bishop", "white-knight", "white-rook"]
    ]

    # Advance the white king one square up from e1 → e2 (r7c4 -> r6c4)
    move_piece(sample_board, ["king", "e1", "e2"])
    print(*sample_board, sep="\n")
