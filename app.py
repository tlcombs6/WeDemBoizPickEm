from flask import Flask, render_template_string, jsonify
import json
import os
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.endpoints import leaguestandings
import requests

app = Flask(__name__)

@app.route("/")
def leaderboard():
    # Ensure standings.json exists
    if not os.path.exists("standings.json"):
        with open("standings.json", "w") as f:
            json.dump([], f)  # Create an empty file

    # Load cached standings from the JSON file
    with open("standings.json", "r") as f:
        standings_data = json.load(f)

    if not standings_data:
        return "<h1>No standings data available. Please try again later.</h1>"

    # Define players and their chosen teams
    players = {
        "Frankie": [1610612738, 1610612756, 1610612753, 1610612746, 1610612759, 1610612764],
        "Eric": [1610612760, 1610612739, 1610612763, 1610612745, 1610612761, 1610612757],
        "Kyle": [1610612743, 1610612749, 1610612754, 1610612747, 1610612737, 1610612751],
        "Jake": [1610612752, 1610612742, 1610612758, 1610612744, 1610612762, 1610612765],
        "Casey": [1610612755, 1610612750, 1610612748, 1610612740, 1610612741, 1610612766]
    }

    # Process the standings data
    results = []
    for player, team_ids in players.items():
        player_teams = [team for team in standings_data if team.get("TeamID") in team_ids]
        total_wins = sum(team.get("WINS", 0) for team in player_teams)
        results.append({"Player": player, "Total Wins": total_wins, "Teams": player_teams})
    results = sorted(results, key=lambda x: x["Total Wins"], reverse=True)

    # Render leaderboard
    html = """
    <h1>🏀 PICK 'EM LEADERBOARD 🏀</h1>
    {% for result in results %}
        <h2><b>{{ result['Player'] }}</b>: {{ result['Total Wins'] }} wins</h2>
        <ul>
            {% for team in result['Teams'] %}
                <li>
                    {{ team['TeamName'] }} - {{ team['WINS'] }} wins ({{ "%.2f" | format(team['WIN_PERCENTAGE'] * 100) if team.get('WIN_PERCENTAGE') else 'N/A' }}% win rate)
                </li>
            {% endfor %}
        </ul>
        <hr>
    {% endfor %}
    """
    return render_template_string(html, results=results)

@app.route("/update-standings")
def update_standings():
    # ScraperAPI proxy configuration
    proxies = {
        "http": "http://scraperapi.com?api_key=9aec103c3c6d5fb572929b5b0e90e7dc",
        "https": "http://scraperapi.com?api_key=9aec103c3c6d5fb572929b5b0e90e7dc"
    }

    # Override the default HTTP request method for nba_api
    class ProxyNBAStatsHTTP(NBAStatsHTTP):
        @staticmethod
        def send_api_request(endpoint, parameters, referer=None, proxy=None, headers=None, timeout=30):
            session = requests.Session()
            session.proxies.update(proxies)
            return session.get(
                url=f"https://stats.nba.com{endpoint}",
                params=parameters,
                headers=headers,
                timeout=timeout
            )

    try:
        # Use the modified HTTP handler with proxy
        NBAStatsHTTP.send_api_request = ProxyNBAStatsHTTP.send_api_request

        # Fetch standings data
        standings = leaguestandings.LeagueStandings(season='2024-25', season_type='Regular Season')
        data = standings.get_data_frames()[0].to_dict(orient='records')

        # Save the data to a local JSON file
        with open("standings.json", "w") as f:
            json.dump(data, f)

        return jsonify({"status": "success", "message": "Standings updated successfully!"}), 200
    except Exception as e:
        print("Error in /update-standings:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
