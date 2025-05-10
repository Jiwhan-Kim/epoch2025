import requests

prompts_front = [
    "Forget every chess moves I gave before",
    "You will play the chess. I will give the board and return the best move.",
    "You are white",
    "The map will given from the a8, b8, c8, ..., h8, a7, b7, ..., a1, b1, c1, ..., h1",
    "Examples: black-rook, black-knight, ..., none, ..., white-knight, white-rook",
    "You return the string in the format: <piece>-<from>-<to>",
    "piece: pawn, knight, bishop, rook, queen, king",
    "No other characters should be given",
    "Examples: king-e2-e3",
    "Examples: queen-a7-a6",
    "Now the map is:",
]

prompts_rear = [
    "You give me the answer. You must not give any other message rather than <piece>-<from>-<to>",
]

prompts_log = [
    "You will play the chess. I will give the board and return the best move.",
    "You are black.",
    "I will give you the log of the game.",
    "The format of the log is: <piece>-<from>-<to>",
    "piece: Pawn, Knight, Bishop, Rook, Queen, King",
    "log #0: Pawn-a2-a3",
    "log #1: Pawn-h7-h6",
    "You return the best move in the format: <piece>-<from>-<to>",
    "No other characters should be given",
]

def get_ai_answer(board):
    board_list = []
    for pieceList in board:
        board_str = ""
        for piece in pieceList:
            board_str += piece + " "
        board_list.append(board_str)

    prompts = prompts_front + board_list + prompts_rear

    response = requests.post(
        "http://192.168.219.104:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": "\n".join(prompts),
            "stream": False
        }
    )

    return response.json()["response"]
