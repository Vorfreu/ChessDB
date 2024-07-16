import chess.pgn
import pandas as pd

# Open the PGN file
pgn = open("C:/Users/vorfreu/Documents/Projects/lichess_uguray_2024-07-06.pgn")

# List to store the parsed data
data = []


# Define a function to parse each game
def parse_game(game, player_name):
    game_id = game.headers.get("Event", "Unknown")
    result = game.headers.get("Result")
    white = game.headers.get("White")
    black = game.headers.get("Black")
    white_elo = game.headers.get("WhiteElo")
    black_elo = game.headers.get("BlackElo")

    my_color = "white" if white == player_name else "black"
    my_elo = white_elo if my_color == "white" else black_elo
    result_value = 1 if (result == "1-0" and my_color == "white") or (result == "0-1" and my_color == "black") else 0

    node = game
    move_number = 1

    while not node.is_end():
        next_node = node.variation(0)
        move = node.board().san(next_node.move)
        eval_value = next_node.eval() if next_node.eval() else 0
        clock_time = node.clock() if node.clock() else "Unknown"

        # Only include moves by the player
        if (my_color == "white" and move_number % 2 != 0) or (my_color == "black" and move_number % 2 == 0):
            data.append({
                "game_id": game_id,
                "color": my_color,
                "result": result_value,
                "my_elo": my_elo,
                "move": move,
                "eval": eval_value,
                "clock": clock_time
            })

        node = next_node
        move_number += 1


# Loop through all games in the PGN file
while True:
    game = chess.pgn.read_game(pgn)
    if game is None:
        break
    parse_game(game, "uguray")

# Create a DataFrame
df = pd.DataFrame(data)

# Save to CSV or any other desired format
df.to_csv("parsed_moves.csv", index=False)

print(df.head(5))
