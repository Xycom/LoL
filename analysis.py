import pandas as pd
from typing import List, Dict


# CSPM Baselines by role and rank
CSPM_BASELINES = {
    "Top": {"Gold": 6.5, "Diamond": 7.5},
    "Jungle": {"Gold": 5.5, "Diamond": 6.5},
    "Mid": {"Gold": 6.5, "Diamond": 8.5},
    "ADC": {"Gold": 7.0, "Diamond": 9.0},
    "Support": {"Gold": 1.5, "Diamond": 2.2},
}


def map_role(team_position: str) -> str:
    """
    Map team position to role.
    
    Args:
        team_position: Raw team position value from API
        
    Returns:
        Mapped role name
    """
    role_map = {
        "TOP": "Top",
        "JUNGLE": "Jungle",
        "MIDDLE": "Mid",
        "BOTTOM": "ADC",
        "UTILITY": "Support",
    }
    return role_map.get(team_position, "Unknown")


def calculate_cspm(total_minions: int, neutral_minions: int, game_duration_seconds: int) -> float:
    """
    Calculate CS per minute.
    
    Args:
        total_minions: Total lane minions killed
        neutral_minions: Neutral minions (jungle) killed
        game_duration_seconds: Game duration in seconds
        
    Returns:
        CS per minute
    """
    total_cs = total_minions + neutral_minions
    game_duration_minutes = game_duration_seconds / 60
    return total_cs / game_duration_minutes if game_duration_minutes > 0 else 0


def process_match_data(match_data: dict, target_puuid: str) -> List[Dict]:
    """
    Extract player stats from a match.
    
    Args:
        match_data: Match data from Riot API
        target_puuid: PUUID of the target player
        
    Returns:
        List of dictionaries with player stats
    """
    participants = match_data["info"]["participants"]
    game_duration = match_data["info"]["gameDuration"]
    
    player_stats = []
    
    for participant in participants:
        stats = {
            "summonerName": participant["summonerName"],
            "champion": participant["championName"],
            "role": map_role(participant["teamPosition"]),
            "cspm": calculate_cspm(
                participant["totalMinionsKilled"],
                participant["neutralMinionsKilled"],
                game_duration,
            ),
            "puuid": participant["puuid"],
        }
        player_stats.append(stats)
    
    return player_stats


def add_baselines(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add baseline columns to DataFrame.
    
    Args:
        df: DataFrame with player stats
        
    Returns:
        DataFrame with baseline columns added
    """
    df["Gold_Baseline"] = df["role"].map(
        lambda role: CSPM_BASELINES.get(role, {}).get("Gold", None)
    )
    df["Diamond_Baseline"] = df["role"].map(
        lambda role: CSPM_BASELINES.get(role, {}).get("Diamond", None)
    )
    df["vs_Diamond"] = df["cspm"] - df["Diamond_Baseline"]
    
    return df


def analyze_player_data(match_data_list: List[dict], target_puuid: str) -> pd.DataFrame:
    """
    Analyze player performance across multiple matches.
    
    Args:
        match_data_list: List of match data dictionaries
        target_puuid: PUUID of the target player
        
    Returns:
        DataFrame with aggregated player stats grouped by summoner and role
    """
    all_stats = []
    
    # Collect stats from all matches
    for match_data in match_data_list:
        stats = process_match_data(match_data, target_puuid)
        all_stats.extend(stats)
    
    # Create DataFrame
    df = pd.DataFrame(all_stats)
    
    if df.empty:
        return df
    
    # Add baselines
    df = add_baselines(df)
    
    # Aggregate by summoner and role
    aggregated = (
        df.groupby(["summonerName", "role"])
        .agg({
            "cspm": "mean",
            "vs_Diamond": "mean",
            "Gold_Baseline": "first",
            "Diamond_Baseline": "first",
        })
        .reset_index()
        .round(2)
    )
    
    # Rename columns for display
    aggregated.columns = [
        "Summoner",
        "Role",
        "Avg CSPM",
        "Avg vs Diamond",
        "Gold Baseline",
        "Diamond Baseline",
    ]
    
    return aggregated
