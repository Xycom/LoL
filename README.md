# Collegiate League Self Review Tool

A local analytics dashboard for analyzing League of Legends match data and coaching insights using Riot API.

## Features

- ⚔️ **Recent Match Analysis**: Pulls and analyzes your last 5 matches
- 📊 **CS Per Minute Metrics**: Calculates CSPM and compares against rank-based baselines
- 🎯 **Role Detection**: Automatically assigns roles to each champion
- 💎 **Diamond Baseline Comparison**: See how your farming efficiency stacks up
- 👥 **Per-Player Aggregation**: Aggregated performance metrics across multiple matches
- 💡 **Coaching Insights**: Quick visual feedback on performance

## Quick Start

### 1. Get a Riot API Key

1. Go to [Riot Developer Portal](https://developer.riotgames.com/)
2. Sign in or create an account
3. Create a new API key
4. Copy your API key

### 2. Setup

```bash
cd league_self_review

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure

Edit `.env` and add your API key:

```
RIOT_API_KEY=your_api_key_here
```

### 4. Run

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Usage

1. Enter your summoner name in the sidebar
2. Click "Analyze Last 5 Matches"
3. Review your performance metrics:
   - **Avg CSPM**: Your average creep score per minute
   - **Avg vs Diamond**: How far above/below Diamond baseline
   - **Role Summary**: Breakdown by role played

## CSPM Baselines

Reference thresholds by role and rank:

| Role     | Gold | Diamond |
|----------|------|---------|
| Top      | 6.5  | 7.5     |
| Jungle   | 5.5  | 6.5     |
| Mid      | 6.5  | 8.5     |
| ADC      | 7.0  | 9.0     |
| Support  | 1.5  | 2.2     |

## Project Structure

```
league_self_review/
├── app.py              # Streamlit dashboard UI
├── riot_api.py         # Riot API integration
├── analysis.py         # Analytics and calculations
├── .env                # Configuration (your API key)
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints Used

- **Summoner V4**: `/lol/summoner/v4/summoners/by-name/{summonerName}`
- **Match V5**: `/lol/match/v5/matches/by-puuid/{puuid}/ids`
- **Match V5**: `/lol/match/v5/matches/{matchId}`

## Region Configuration

- **Platform Region**: `na1` (North America)
- **Match Routing Region**: `americas`

*Easily customizable in `riot_api.py` for other regions*

## Future Enhancements

The MVP is designed to be easily expandable:

- 📈 Early game metrics (CS at 10 minutes)
- 💰 Gold per minute trends
- 🎯 Objective participation tracking
- 💀 Death clustering analysis
- 👥 Team-wide dashboards
- 📊 Historical trends over time

## Troubleshooting

### "Summoner not found"
- Check spelling of summoner name (case-insensitive)
- Ensure the account is on NA region

### "API Key Error"
- Verify API key in `.env` file
- Check that the key hasn't expired
- Generate a new key from [Riot Developer Portal](https://developer.riotgames.com/)

### Import Errors
- Run `pip install -r requirements.txt`
- Verify you're in the correct virtual environment

## Notes

- This tool is for **self-review and coaching purposes only**
- Respect Riot's [API Terms of Service](https://developer.riotgames.com/terms)
- Development API keys have rate limits
- Suitable for local analysis, not production dashboards

## License

Personal use only. Created for League of Legends analytics.
