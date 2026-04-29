import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")
PLATFORM_REGION = "na1"
ROUTING_REGION = "americas"

BASE_URL = f"https://{PLATFORM_REGION}.api.riotgames.com"
MATCH_BASE_URL = f"https://{ROUTING_REGION}.api.riotgames.com"


def get_puuid(summoner_name: str) -> str:
    """
    Get PUUID for a summoner using Summoner V4 API.
    
    Args:
        summoner_name: The summoner's name
        
    Returns:
        PUUID (Player Universally Unique Identifier)
        
    Raises:
        Exception: If the API request fails or summoner not found
    """
    url = f"{BASE_URL}/lol/summoner/v4/summoners/by-name/{summoner_name}"
    params = {"api_key": API_KEY}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    data = response.json()
    return data["puuid"]


def get_match_ids(puuid: str, count: int = 5) -> list:
    """
    Get match IDs for a player using Match V5 API.
    
    Args:
        puuid: Player's PUUID
        count: Number of recent matches to retrieve (default: 5)
        
    Returns:
        List of match IDs
        
    Raises:
        Exception: If the API request fails
    """
    url = f"{MATCH_BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    params = {
        "start": 0,
        "count": count,
        "api_key": API_KEY
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()


def get_match_data(match_id: str) -> dict:
    """
    Get detailed match data using Match V5 API.
    
    Args:
        match_id: The match ID
        
    Returns:
        Dictionary containing match data
        
    Raises:
        Exception: If the API request fails
    """
    url = f"{MATCH_BASE_URL}/lol/match/v5/matches/{match_id}"
    params = {"api_key": API_KEY}
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    return response.json()
