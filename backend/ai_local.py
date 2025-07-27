import requests
import json
from typing import List, Dict, Any

class LocalAIService:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "llama3.1:8b"  # Default model
    
    def is_available(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def query_model(self, prompt: str, model: str = None) -> str:
        """Send query to local model"""
        if not model:
            model = self.model
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 300
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"Error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def analyze_football_data(self, query: str, plays_data: List[Dict]) -> str:
        """Analyze football data with local AI"""
        
        # Prepare data summary
        if not plays_data:
            return "No game data available to analyze."
        
        total_plays = len(plays_data)
        total_yards = sum(play.get('yards_gained', 0) for play in plays_data)
        avg_yards = total_yards / total_plays if total_plays > 0 else 0
        
        # Formation analysis
        formations = {}
        play_types = {}
        downs = {}
        
        for play in plays_data:
            formation = play.get('formation', 'Unknown')
            play_type = play.get('play_type', 'Unknown')
            down = play.get('down', 0)
            
            formations[formation] = formations.get(formation, 0) + 1
            play_types[play_type] = play_types.get(play_type, 0) + 1
            downs[f"Down {down}"] = downs.get(f"Down {down}", 0) + 1
        
        # Get top formations and play types
        top_formations = sorted(formations.items(), key=lambda x: x[1], reverse=True)[:3]
        top_play_types = sorted(play_types.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Create comprehensive prompt
        prompt = f"""You are an expert football analytics assistant. Analyze the following game data and answer the user's question with specific insights.

GAME DATA SUMMARY:
- Total Plays: {total_plays}
- Total Yards Gained: {total_yards}
- Average Yards per Play: {avg_yards:.2f}

TOP FORMATIONS:
{chr(10).join([f"- {name}: {count} plays" for name, count in top_formations])}

TOP PLAY TYPES:
{chr(10).join([f"- {name}: {count} plays" for name, count in top_play_types])}

DOWN DISTRIBUTION:
{chr(10).join([f"- {down}: {count} plays" for down, count in sorted(downs.items())])}

USER QUESTION: {query}

Provide a detailed analysis with specific numbers from the data. Include insights about trends, strengths, weaknesses, and recommendations. Keep your response focused and actionable."""

        return self.query_model(prompt)
    
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
            return []
        except:
            return []

# Initialize service
local_ai = LocalAIService()