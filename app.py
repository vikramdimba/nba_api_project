import os
from flask import Flask, jsonify, request
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime
import json

app = Flask(__name__)

# Simple in-memory cache
cache = {}

def get_nba_games(game_date=None):
    if game_date is None:
        game_date = datetime.today().strftime('%Y-%m-%d')
    
    # Check if data is in cache
    if game_date in cache:
        return cache[game_date]
    
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()
        if len(games) > 0 and not games[0].empty:
            result = games[0].to_dict(orient='records')
            # Store in cache
            cache[game_date] = result
            return result
        else:
            return {"error": f"No games found for {game_date}"}
    except Exception as e:
        return {"error": str(e)}

@app.route('/nba-games', methods=['GET'])
def nba_games():
    game_date = request.args.get('date')
    games = get_nba_games(game_date)
    return jsonify(games)

if __name__ == "__main__":
    app.run(debug=True)