import requests

prompts = [
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
    "black-rook black-knight black-bishop black-queen black-king black-bishop black-knight black-rook",
    "black-pawn black-pawn black-pawn black-pawn black-pawn black-pawn black-pawn pawn",
    "none none none none none none none none",
    "none none none none none none none none",
    "none none none none none none none none",
    "none none none none none none none none",
    "white-rook white-knight white-bishop white-queen white-king white-bishop white-knight white-rook",
    "white-pawn white-pawn white-pawn white-pawn white-pawn white-pawn white-pawn white-pawn",
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

response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": "\n".join(prompts_log),
        "stream": False
    }
)

print(response)
print(response.json()["response"])
