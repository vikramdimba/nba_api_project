import os
import redis
from urllib.parse import urlparse
from flask import Flask, jsonify, request
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime
import json

app = Flask(__name__)

# Get the Redis URL from the environment
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')

# Parse the Redis URL
url = urlparse(redis_url)

# Create the Redis client
redis_client = redis.Redis(host=url.hostname, port=url.port, password=url.password)

# ... rest of your app.py code ...

from flask import Flask, jsonify, request
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime
import redis
import json
import os
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup Redis connection
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

# Function to fetch NBA games for a specific date
def get_nba_games(game_date=None):
    if game_date is None:
        game_date = datetime.today().strftime('%Y-%m-%d')
    
    # Check if data is in cache
    cached_data = redis_client.get(f"nba_games:{game_date}")
    if cached_data:
        logging.info(f"Returning cached data for {game_date}")
        return json.loads(cached_data)
    
    logging.info(f"Fetching new data for {game_date}")
    try:
        scoreboard = scoreboardv2.ScoreboardV2(game_date=game_date)
        games = scoreboard.get_data_frames()
        if len(games) > 0 and not games[0].empty:
            result = games[0].to_dict(orient='records')
            # Cache the result for 1 hour
            redis_client.setex(f"nba_games:{game_date}", 3600, json.dumps(result))
            return result
        else:
            logging.warning(f"No games found for {game_date}")
            return {"error": f"No games found for {game_date}"}
    except Exception as e:
        logging.error(f"Error fetching data for {game_date}: {str(e)}")
        return {"error": str(e)}

# Flask route to get games for a specific date
@app.route('/nba-games', methods=['GET'])
def nba_games():
    game_date = request.args.get('date')
    logging.info(f"Received request for date: {game_date}")
    games = get_nba_games(game_date)
    return jsonify(games)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)