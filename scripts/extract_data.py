import requests
import chess.pgn
import pandas as pd
import io
import re

class ChessdbConfig:
    def __init__(self):
        self.base_url = "https://lichess.org/api/games/user/"
        self.user = "uguray"
        self.params = {
            "rated": "true",
            "analysed": "true",
            "tags": "true",
            "clocks": "true",
            "evals": "true",
            "opening": "false",
            "since": "1614546000000",  # Timestamp for the start date
            "until": "1721163600000",  # Timestamp for the end date
            "perfType": "rapid,classical,standard"
        }


class ChessdbExtract(ChessdbConfig):
    def __init__(self):
        super().__init__()

    def construct_api_call(self):
        # Construct the base URL
        api_url = f"{self.base_url}{self.user}"

        # Add query parameters
        query_params = "&".join([f"{key}={value}" for key, value in self.params.items()])

        # Complete API URL
        full_api_url = f"{api_url}?{query_params}"

        return full_api_url

    def get_data(self):
        # Make the request
        response = requests.get(self.construct_api_call())

        # Check if worked
        if response.status_code == 200:
            return response.text
        else:
            response.raise_for_status()


class ChessdbTransform(ChessdbExtract):
    def __init__(self):
        super().__init__()
        self.pgn_file_path = "C:/Users/vorfreu/PycharmProjects/ChessDB/data/lichess_uguray_2024-07-16.pgn"
        with open(self.pgn_file_path, encoding="utf-8") as pgn_file:
            self.pgn_data = pgn_file.read()
    def transform_to_dataframe(self):
        games = []

        # Parse the PGN data using chess.pgn
        # TODO: Change this later on to get from get_data()
        pgn = io.StringIO(self.pgn_data)

        while True:
            game = chess.pgn.read_game(pgn)
            if game is None:
                break

            game_info = {
                'Event': game.headers.get('Event'),
                'Site': game.headers.get('Site'),
                'Date': game.headers.get('Date'),
                'White': game.headers.get('White'),
                'Black': game.headers.get('Black'),
                'Result': game.headers.get('Result'),
                'WhiteElo': game.headers.get('WhiteElo'),
                'BlackElo': game.headers.get('BlackElo'),
                'Variant': game.headers.get('Variant'),
                'TimeControl': game.headers.get('TimeControl'),
                'ECO': game.headers.get('ECO'),
                'Termination': game.headers.get('Termination')
            }

            # Extract moves and evaluations from the game
            move_number = 1
            node = game
            while node.variations:
                next_node = node.variations[0]
                for move in node.board().move_stack:
                    move_str = move.uci()
                    eval_annotation = node.eval()
                    remaining_clock = node.clock()

                    # Create a row for each move
                    row = {
                        'site': game_info['Site'],
                        'date': game_info['Date'],
                        'white': game_info['White'],
                        'black': game_info['Black'],
                        'result': game_info['Result'],
                        'whiteElo': game_info['WhiteElo'],
                        'blackElo': game_info['BlackElo'],
                        'variant': game_info['Variant'],
                        'timeControl': game_info['TimeControl'],
                        'ECO': game_info['ECO'],
                        'termination': game_info['Termination'],
                        'moveNumber': move_number,
                        'move': move_str,
                        'eval': eval_annotation,
                        'remainingClock': remaining_clock
                    }
                    games.append(row)
                    move_number += 1

                node = next_node

        # Convert games list to DataFrame
        df = pd.DataFrame(games)

        return df






if __name__ == "__main__":
    transformer = ChessdbTransform()
    transformed_data = transformer.transform_to_dataframe()
    print(transformed_data)
    transformed_data.to_csv("C:/Users/vorfreu/PycharmProjects/ChessDB/data/example_data.csv")