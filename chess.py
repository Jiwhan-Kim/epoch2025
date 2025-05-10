from dataclasses import dataclass, replace
from enum import Enum, auto
from typing import Optional, Tuple, List

# ─── Low–level helpers ──────────────────────────────────────────────────────────

FILE_TO_IDX = {c: i for i, c in enumerate("ABCDEFGH")}
IDX_TO_FILE = {i: c for c, i in FILE_TO_IDX.items()}


def square_to_coords(square: str) -> Tuple[int, int]:
    """'A1' → (0,0)  |  'H8' → (7,7)"""
    file, rank = square[0].upper(), int(
        square[1])            # assumes legal input
    return rank - 1, FILE_TO_IDX[file]


def coords_to_square(rank: int, file: int) -> str:
    return f"{IDX_TO_FILE[file]}{rank + 1}"

# ─── Core chess data types (trimmed) ────────────────────────────────────────────


class Color(Enum):
    WHITE = auto()
    BLACK = auto()


class Piece(Enum):
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = range(6)


@dataclass
class Figure:
    kind: Piece
    color: Color
    has_moved: bool = False              # castling / pawn logic helper


Board = List[List[Optional[Figure]]]     # 8 × 8 grid


@dataclass
class GameState:
    board: Board
    side_to_move: Color                  # Color.WHITE / Color.BLACK
    castling_rights: str                 # e.g. "KQkq"
    en_passant_target: Optional[str]     # algebraic square like 'E6'
    halfmove_clock: int                  # for 50-move rule
    fullmove_number: int

# ─── Move-application routine ───────────────────────────────────────────────────


PIECE_TOKEN = {
    "K": Piece.KING,   "Q": Piece.QUEEN, "R": Piece.ROOK,
    "B": Piece.BISHOP, "N": Piece.KNIGHT, "P": Piece.PAWN,
}


def apply_move(tokens: list[str], state: GameState) -> GameState:
    """
    tokens: [<piece letter>, <from square>, <to square>]
            e.g. ["N", "G1", "F3"]   or ["P", "E2", "E4"]
    Returns a *new* GameState; original stays intact.
    Assumes the move is *already known* to be legal.
    """
    piece_tok, from_sq, to_sq = tokens
    kind = PIECE_TOKEN[piece_tok.upper()]

    r_from, c_from = square_to_coords(from_sq)
    r_to,   c_to = square_to_coords(to_sq)

    piece = state.board[r_from][c_from]
    if piece is None:
        raise ValueError(f"No piece on {from_sq}")
    if piece.kind != kind or piece.color != state.side_to_move:
        raise ValueError("Piece mismatch or not your turn")

    # --- clone board (shallow copy rows to keep it cheap) ---
    new_board = [row[:] for row in state.board]
    new_board[r_from][c_from] = None
    new_board[r_to][c_to] = replace(piece, has_moved=True)

    # --- update castling rights when king or rook moves ---
    rights = state.castling_rights
    if piece.kind is Piece.KING:
        rights = rights.replace("K", "").replace(
            "Q", "") if piece.color is Color.WHITE else rights
        rights = rights.replace("k", "").replace(
            "q", "") if piece.color is Color.BLACK else rights
    elif piece.kind is Piece.ROOK:
        if from_sq == "A1":
            rights = rights.replace("Q", "")
        if from_sq == "H1":
            rights = rights.replace("K", "")
        if from_sq == "A8":
            rights = rights.replace("q", "")
        if from_sq == "H8":
            rights = rights.replace("k", "")

    # --- en passant bookkeeping ---
    ep = None
    if piece.kind is Piece.PAWN and abs(r_to - r_from) == 2:
        # square *behind* the pawn becomes target (rank between start and dest)
        mid_rank = (r_to + r_from) // 2
        ep = coords_to_square(mid_rank, c_from)

    # reset half-move clock on any pawn move or capture
    is_capture = state.board[r_to][c_to] is not None
    halfclock = 0 if (
        piece.kind is Piece.PAWN or is_capture) else state.halfmove_clock + 1

    # fullmove number advances after Black’s move
    fullmove = state.fullmove_number + \
        (1 if state.side_to_move is Color.BLACK else 0)

    return GameState(
        board=new_board,
        side_to_move=Color.BLACK if state.side_to_move is Color.WHITE else Color.WHITE,
        castling_rights=rights,
        en_passant_target=ep,
        halfmove_clock=halfclock,
        fullmove_number=fullmove,
    )

# ─── Example usage ──────────────────────────────────────────────────────────────


if __name__ == "__main__":
    # build a *very* tiny start position: just kings
    empty = [[None]*8 for _ in range(8)]
    empty[0][4] = Figure(Piece.KING, Color.WHITE)
    empty[7][4] = Figure(Piece.KING, Color.BLACK)
    gs = GameState(empty, Color.WHITE, "KQkq", None, 0, 1)

    gs2 = apply_move(["K", "E1", "E2"], gs)
    print(gs2.board[1][4].kind, gs2.side_to_move)
