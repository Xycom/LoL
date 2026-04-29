from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
from riot_api import get_puuid, get_match_ids, get_match_data
from analysis import analyze_player_data

app = FastAPI(
    title="League of Legends Self Review Tool",
    description="Analyze your League of Legends performance with Diamond baseline comparisons",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisRequest(BaseModel):
    summoner_name: str
    num_matches: int = 5


class PlayerStats(BaseModel):
    summoner: str
    role: str
    avg_cspm: float
    avg_vs_diamond: float
    gold_baseline: float
    diamond_baseline: float


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>League of Legends Self Review Tool</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 800px;
                width: 100%;
                padding: 40px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            h1 {
                color: #333;
                font-size: 28px;
                margin-bottom: 10px;
            }
            
            .subtitle {
                color: #666;
                font-size: 16px;
            }
            
            .form-group {
                margin-bottom: 20px;
            }
            
            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            
            input, select {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            
            input:focus, select:focus {
                outline: none;
                border-color: #667eea;
            }
            
            button {
                width: 100%;
                padding: 12px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            button:active {
                transform: translateY(0);
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            
            .spinner {
                border: 4px solid #ddd;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .results {
                display: none;
                margin-top: 40px;
            }
            
            .metrics {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .metric-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }
            
            .metric-label {
                color: #666;
                font-size: 14px;
                margin-bottom: 8px;
            }
            
            .metric-value {
                color: #333;
                font-size: 28px;
                font-weight: 700;
            }
            
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            
            th {
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                color: #333;
                font-weight: 600;
                border-bottom: 2px solid #ddd;
            }
            
            td {
                padding: 12px;
                border-bottom: 1px solid #ddd;
                color: #666;
            }
            
            tr:hover {
                background: #f8f9fa;
            }
            
            .error {
                display: none;
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                border-left: 4px solid #c33;
            }
            
            .success {
                display: none;
                background: #efe;
                color: #3c3;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                border-left: 4px solid #3c3;
            }
            
            .insight {
                padding: 12px;
                border-radius: 6px;
                margin-bottom: 10px;
                border-left: 4px solid;
            }
            
            .insight.warning {
                background: #fef3cd;
                border-left-color: #ffc107;
                color: #856404;
            }
            
            .insight.success {
                background: #d4edda;
                border-left-color: #28a745;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚔️ League Self Review Tool</h1>
                <p class="subtitle">Analyze your performance with Diamond baseline comparisons</p>
            </div>
            
            <div class="error" id="error"></div>
            <div class="success" id="success"></div>
            
            <form id="analysisForm">
                <div class="form-group">
                    <label for="summonerName">Summoner Name</label>
                    <input 
                        type="text" 
                        id="summonerName" 
                        placeholder="e.g., Faker"
                        required
                    >
                </div>
                
                <div class="form-group">
                    <label for="numMatches">Number of Matches</label>
                    <select id="numMatches">
                        <option value="5">Last 5 Matches</option>
                        <option value="10">Last 10 Matches</option>
                        <option value="15">Last 15 Matches</option>
                        <option value="20">Last 20 Matches</option>
                    </select>
                </div>
                
                <button type="submit">Analyze</button>
            </form>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Fetching match data...</p>
            </div>
            
            <div class="results" id="results">
                <h2>📊 Performance Summary</h2>
                <div class="metrics" id="metrics"></div>
                
                <h3>Detailed Results by Role</h3>
                <table id="resultsTable">
                    <thead>
                        <tr>
                            <th>Role</th>
                            <th>Avg CSPM</th>
                            <th>Avg vs Diamond</th>
                            <th>Gold Baseline</th>
                            <th>Diamond Baseline</th>
                        </tr>
                    </thead>
                    <tbody id="tableBody"></tbody>
                </table>
                
                <h3 style="margin-top: 30px;">💡 Coaching Insights</h3>
                <div id="insights"></div>
            </div>
        </div>
        
        <script>
            document.getElementById('analysisForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const summonerName = document.getElementById('summonerName').value;
                const numMatches = parseInt(document.getElementById('numMatches').value);
                
                document.getElementById('error').style.display = 'none';
                document.getElementById('success').style.display = 'none';
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            summoner_name: summonerName,
                            num_matches: numMatches
                        })
                    });
                    
                    if (!response.ok) {
                        const error = await response.json();
                        throw new Error(error.detail || 'Analysis failed');
                    }
                    
                    const data = await response.json();
                    displayResults(data, summonerName);
                    
                    document.getElementById('success').textContent = `✅ Analysis complete for ${summonerName}`;
                    document.getElementById('success').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('error').textContent = `❌ Error: ${error.message}`;
                    document.getElementById('error').style.display = 'block';
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            });
            
            function displayResults(data, summonerName) {
                const stats = data.stats;
                
                if (stats.length === 0) {
                    document.getElementById('error').textContent = `No data found for ${summonerName}`;
                    document.getElementById('error').style.display = 'block';
                    return;
                }
                
                // Display metrics
                const avgCspm = (stats.reduce((sum, s) => sum + s.avg_cspm, 0) / stats.length).toFixed(2);
                const avgVsDiamond = (stats.reduce((sum, s) => sum + s.avg_vs_diamond, 0) / stats.length).toFixed(2);
                
                document.getElementById('metrics').innerHTML = `
                    <div class="metric-card">
                        <div class="metric-label">Average CSPM</div>
                        <div class="metric-value">${avgCspm}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Avg vs Diamond</div>
                        <div class="metric-value">${avgVsDiamond}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Roles Played</div>
                        <div class="metric-value">${stats.length}</div>
                    </div>
                `;
                
                // Display table
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = stats.map(stat => `
                    <tr>
                        <td>${stat.role}</td>
                        <td>${stat.avg_cspm.toFixed(2)}</td>
                        <td>${stat.avg_vs_diamond.toFixed(2)}</td>
                        <td>${stat.gold_baseline.toFixed(2)}</td>
                        <td>${stat.diamond_baseline.toFixed(2)}</td>
                    </tr>
                `).join('');
                
                // Display insights
                const insights = document.getElementById('insights');
                insights.innerHTML = stats.map(stat => {
                    const isBelowDiamond = stat.avg_vs_diamond < 0;
                    const className = isBelowDiamond ? 'warning' : 'success';
                    const sign = stat.avg_vs_diamond >= 0 ? '+' : '';
                    return `
                        <div class="insight ${className}">
                            <strong>${stat.role}:</strong> ${stat.avg_cspm.toFixed(2)} CSPM (${sign}${stat.avg_vs_diamond.toFixed(2)} vs Diamond)
                        </div>
                    `;
                }).join('');
                
                document.getElementById('results').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """


@app.post("/api/analyze")
async def analyze(request: AnalysisRequest):
    """API endpoint for analyzing player data"""
    try:
        if not request.summoner_name:
            raise HTTPException(status_code=400, detail="Summoner name is required")
        
        if request.num_matches not in [5, 10, 15, 20]:
            raise HTTPException(status_code=400, detail="Number of matches must be 5, 10, 15, or 20")
        
        # Get PUUID
        puuid = get_puuid(request.summoner_name)
        
        # Get match IDs
        match_ids = get_match_ids(puuid, count=request.num_matches)
        
        # Get match data
        match_data_list = []
        for match_id in match_ids:
            match_data = get_match_data(match_id)
            match_data_list.append(match_data)
        
        # Analyze data
        results_df = analyze_player_data(match_data_list, puuid)
        
        # Filter to only the target player
        target_results = results_df[results_df["Summoner"] == request.summoner_name]
        
        if target_results.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {request.summoner_name} in recent matches"
            )
        
        # Convert to list of dicts
        stats = []
        for _, row in target_results.iterrows():
            stats.append({
                "summoner": row["Summoner"],
                "role": row["Role"],
                "avg_cspm": float(row["Avg CSPM"]),
                "avg_vs_diamond": float(row["Avg vs Diamond"]),
                "gold_baseline": float(row["Gold Baseline"]),
                "diamond_baseline": float(row["Diamond Baseline"]),
            })
        
        return {"stats": stats}
    
    except ValueError:
        raise HTTPException(status_code=404, detail="Summoner not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
