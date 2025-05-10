from enum import Enum


class Piece(Enum):
    KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN = range(6)


class Figure:
    kind: Piece
    color: bool  # True for White, False for Black
    has_moved: bool = False


if __name__ == "__main__":
    pass
