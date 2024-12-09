from flask import Flask, render_template_string
import pandas as pd
from nba_api.stats.endpoints import leaguestandings

app = Flask(__name__)

@app.route("/")
def leaderboard():
    # Define players and their chosen teams
    players = {
        "Frankie": [1610612738, 1610612756, 1610612753, 1610612746, 1610612759, 1610612764],
        "Eric": [1610612760, 1610612739, 1610612763, 1610612745, 1610612761, 1610612757],
        "Kyle": [1610612743, 1610612749, 1610612754, 1610612747, 1610612737, 1610612751],
        "Jake": [1610612752, 1610612742, 1610612758, 1610612744, 1610612762, 1610612765],
        "Casey": [1610612755, 1610612750, 1610612748, 1610612740, 1610612741, 1610612766]
    }

    # Fetch standings from the NBA API
    standings = leaguestandings.LeagueStandings(season='2024-25', season_type='Regular Season')
    standings_df = standings.get_data_frames()[0]
    teams_stats = standings_df[['TeamID', 'TeamName', 'WINS', 'LOSSES']].copy()
    teams_stats['WIN_PERCENTAGE'] = teams_stats['WINS'] / (teams_stats['WINS'] + teams_stats['LOSSES'])

    # Calculate player results
    results = []
    for player, team_ids in players.items():
        player_teams = teams_stats[teams_stats['TeamID'].isin(team_ids)]
        total_wins = player_teams['WINS'].sum()
        results.append({"Player": player, "Total Wins": total_wins, "Teams": player_teams.to_dict('records')})
    results = sorted(results, key=lambda x: x['Total Wins'], reverse=True)

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

if __name__ == "__main__":
    app.run(debug=True)


