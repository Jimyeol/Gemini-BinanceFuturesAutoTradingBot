import requests
import json

def get_fear_and_greed_index():
    url = "https://api.alternative.me/fng/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # This will raise an error for bad status codes
        data = response.json()
        return json.dumps(data, indent=4)
    except requests.RequestException as e:
        print(f"Error fetching data from Fear & Greed Index API: {e}")
        return None