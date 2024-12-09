from flask import Flask, render_template_string, jsonify
import json
from nba_api.stats.endpoints import leaguestandings
import os

app = Flask(__name__)

@app.route("/")
def leaderboard():
    # Load cached standings from the JSON file
    with open("standings.json", "r") as f:
        standings_data = json.load(f)

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
        player_teams = [team for team in standings_data if team["TeamID"] in team_ids]
        total_wins = sum(team["WINS"] for team in player_teams)
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
                    {{ team['TeamName'] }} - {{ team['WINS'] }} wins ({{ "%.2f" | format(team['WIN_PERCENTAGE'] * 100) }}% win rate)
                </li>
            {% endfor %}
        </ul>
        <hr>
    {% endfor %}
    """
    return render_template_string(html, results=results)

@app.route("/update-standings")
def update_standings():
    try:
        # Fetch standings from the NBA API
        standings = leaguestandings.LeagueStandings(season='2024-25', season_type='Regular Season')
        data = standings.get_data_frames()[0].to_dict(orient='records')

        # Save the data to a local JSON file
        with open("standings.json", "w") as f:
            json.dump(data, f)

        return jsonify({"status": "success", "message": "Standings updated successfully!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
