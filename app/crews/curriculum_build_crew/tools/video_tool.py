from crewai.tools import BaseTool
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class VideoTool(BaseTool):
    name: str = "Custom Serper Dev Tool"
    description: str = "Search the internet for youtube Videos."

    def _run(self, query: str) -> str:
        """
        Search the internet for youtube Videos.
        """

        url = "https://google.serper.dev/videos"

        payload = json.dumps({
            "q": query,
            "num": 20,
            "autocorrect": False,
            "tbs": "qdr:d"
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Parse the JSON response
        response_data = response.json()

        # Extract only the 'news' property
        video_data = response_data.get('videos', [])

        # Convert the news data back to a JSON string
        return json.dumps(video_data, indent=2)
