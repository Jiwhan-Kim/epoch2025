class Piece:
    def __init__(self, color, kind):
        self.color = color            # 'white' or 'black'
        self.kind = kind              # 'pawn', 'rook', etc.
        self.has_moved = False        # for king, rook, and castling
        self.double_move_turn = -1    # for pawn's en passant

    def __str__(self):
        return f"{self.color}-{self.kind}"

    def __repr__(self):
        return str(self)
