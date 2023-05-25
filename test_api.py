import requests

def print_board(board):
    for row in board:
        print(" ".join(row))

def start_game(bot_rating):
    api_url = "https://online-go.com/api/v1"

    # Get a bot opponent with the desired rating
    response = requests.get(api_url + "/bots?disable_custom_ais=true")
    bots = response.json()
    selected_bot = None
    for bot in bots:
        if bot["rating"] == bot_rating:
            selected_bot = bot
            break

    if not selected_bot:
        print("No bot found with the desired rating.")
        return

    bot_id = selected_bot["id"]
    bot_rating = selected_bot["rating"]

    # Start a new game with the bot
    response = requests.post(api_url + "/challenges", json={"opponent": bot_id})
    game_id = response.json()["id"]
    print("New game started against Bot (Rating: {})".format(bot_rating))

    # Play the game
    while True:
        # Get game state
        response = requests.get(api_url + "/games/{}".format(game_id))
        game_data = response.json()["game"]

        # Print current board state
        print("Current board state:")
        print_board(game_data["initial_state"])

        # Check if it's the player's turn or the bot's turn
        if game_data["game_system"]["white"]["username"] == "Bot":
            print("Bot's turn...")
        else:
            move = input("Enter your move (e.g., 'B2'): ")
            data = {
                "move": move
            }
            response = requests.post(api_url + "/games/{}/move".format(game_id), json=data)
            result = response.json()["game"]["status"]
            if result == "play":
                print("Move successful.")
            elif result == "finished":
                game_result = response.json()["game"]["outcome"]
                print("The game has ended. Result: {}".format(game_result))
                break

            # Print opponent's move
            response = requests.get(api_url + "/games/{}".format(game_id))
            game_data = response.json()["game"]
            opponent_move = game_data["moves"][-1]["vertex"]
            print("Opponent's move: {}".format(opponent_move))

board_size = 9  # Change the board size as desired
bot_rating = 1000  # Change the desired bot rating
start_game(bot_rating)
