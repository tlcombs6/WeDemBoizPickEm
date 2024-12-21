from flask import Flask, render_template_string
from nba_api.stats.endpoints import leaguestandings
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def leaderboard():
    # Define players and their chosen teams by IDs in draft order
    draft_order = [
        "Frankie",
        "Eric",
        "Kyle",
        "Jake",
        "Casey"
    ]

    players = {
        "Frankie": [1610612738, 1610612756, 1610612753, 1610612746, 1610612759, 1610612764],
        "Eric": [1610612760, 1610612739, 1610612763, 1610612745, 1610612761, 1610612757],
        "Kyle": [1610612743, 1610612749, 1610612754, 1610612747, 1610612737, 1610612751],
        "Jake": [1610612752, 1610612742, 1610612758, 1610612744, 1610612762, 1610612765],
        "Casey": [1610612755, 1610612750, 1610612748, 1610612740, 1610612741, 1610612766]
    }

    # Fetch current team standings data
    standings = leaguestandings.LeagueStandings(season='2024-25', season_type='Regular Season')
    standings_df = standings.get_data_frames()[0]
    teams_stats = standings_df[['TeamID', 'TeamName', 'WINS', 'LOSSES']].copy()
    teams_stats['WIN_PERCENTAGE'] = teams_stats['WINS'] / (teams_stats['WINS'] + teams_stats['LOSSES'])
    team_stats_dict = teams_stats.set_index('TeamID').to_dict('index')

    results = []
    for player in draft_order:
        team_ids = players[player]
        ordered_teams = [team_stats_dict[team_id] for team_id in team_ids if team_id in team_stats_dict]
        total_wins = sum(team['WINS'] for team in ordered_teams)
        results.append({
            "Player": player,
            "Total Wins": total_wins,
            "Teams": ordered_teams
        })

    # Calculate season progress
    season_start = datetime(2024, 10, 24)
    season_end = datetime(2025, 5, 1)
    today = datetime.now()
    elapsed_days = (today - season_start).days
    total_days = (season_end - season_start).days
    season_progress = (elapsed_days / total_days) * 100 if elapsed_days > 0 else 0

    # HTML template with a direct static path for the image
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pick 'Em Leaderboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; }
            header { text-align: center; }
            header img { width: 100%; height: auto; display: block; }
            h1 { color: #444; margin: 20px; text-align: center; }
            .content { margin: 20px; }
            .progress-container {
                width: 60%;
                background-color: #f3f3f3;
                border-radius: 5px;
                margin: 20px auto;
                text-align: left;
            }
            .progress-bar {
                height: 20px;
                background-color: #4caf50;
                border-radius: 5px;
                text-align: center;
                color: white;
                line-height: 20px;
            }
            .player { font-weight: bold; font-size: 1.2em; margin-top: 20px; }
            .team { margin-left: 20px; }
            .blue { color: blue; }
            .green { color: green; }
            .yellow { color: goldenrod; }
            .red { color: red; }
        </style>
    </head>
    <body>
        <header>
            <img src="static/StephDray.webp" alt="Header Image">
        </header>
        <div class="content">
            <h1>🏀 PICK 'EM LEADERBOARD 🏀</h1>
            <div class="progress-container">
                <div class="progress-bar" style="width: {{ "%.2f"|format(season_progress) }}%;">
                    {{ "%.2f"|format(season_progress) }}% through NBA season
                </div>
            </div>
            {% for result in results %}
                <div class="player">{{ result['Player'] }}: {{ result['Total Wins'] }} wins</div>
                <ul>
                    {% for team in result['Teams'] %}
                        <li class="team">
                            {{ team['TeamName'] }} - {{ team['WINS'] }} wins
                            <span class="{% if team['WIN_PERCENTAGE'] > 0.75 %}blue
                                          {% elif team['WIN_PERCENTAGE'] > 0.55 %}green
                                          {% elif team['WIN_PERCENTAGE'] > 0.35 %}yellow
                                          {% else %}red{% endif %}">
                                ({{ "%.2f"|format(team['WIN_PERCENTAGE'] * 100) }}%)
                            </span>
                        </li>
                    {% endfor %}
                </ul>
            {% endfor %}
        </div>
    </body>
    </html>
    """

    rendered_html = render_template_string(html_template, results=results, season_progress=season_progress)
    with open("leaderboard.html", "w") as f:
        f.write(rendered_html)
    print("Static leaderboard saved as 'leaderboard.html'")

if __name__ == "__main__":
    with app.app_context():
        leaderboard()
