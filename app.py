from flask import Flask, jsonify, request
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime

app = Flask(__name__)

# Function to fetch NBA games for a specific date
def get_nba_games(game_date=None):
    if game_date is None:
        game_date = datetime.today().strftime('%Y-%m-%d')
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()
        # Check if the response contains dataframes and handle empty lists
        if len(games) > 0 and not games[0].empty:
            return games[0].to_dict(orient='records')  # Convert to list of dictionaries
        else:
            return {"error": f"No games found for {game_date}"}
    except Exception as e:
        return {"error": str(e)}

# Flask route to get games for a specific date
@app.route('/nba-games', methods=['GET'])
def nba_games():
    game_date = request.args.get('date')  # Get the date from query parameters
    games = get_nba_games(game_date)
    return jsonify(games)  # Return the data as JSON

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
