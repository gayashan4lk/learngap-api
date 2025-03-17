from crewai.tools import BaseTool
import requests
import json
import os
from dotenv import load_dotenv
import time
from urllib.parse import urlparse

load_dotenv()

class OnlineCourseTool(BaseTool):
    name: str = "Online Course Search Tool"
    description: str = "Search the internet for real, accessible online courses"

    def _run(self, query: str) -> str:
        """
        Search the internet for online courses and validate the URLs
        """
        course_platforms = [
            "coursera.org", "udemy.com", "edx.org", "linkedin.com/learning",
            "pluralsight.com", "skillshare.com", "codecademy.com"
        ]
        
        # Create platform-specific searches
        all_results = []
        
        # General search
        enhanced_query = f"online course {query}"
        general_results = self._search_with_serper(enhanced_query)
        all_results.extend(general_results)
        
        # Platform specific searches
        for platform in course_platforms:
            platform_query = f"{query} course site:{platform}"
            platform_results = self._search_with_serper(platform_query)
            all_results.extend(platform_results)
            time.sleep(0.5)  # Avoid rate limiting
        
        # Filter and validate results
        validated_results = []
        for result in all_results:
            url = result.get('link')
            if url and self._is_likely_course_url(url) and self._validate_url(url):
                validated_results.append(result)
                if len(validated_results) >= 10:  # Limit to 10 validated results
                    break
        
        return json.dumps(validated_results, indent=2)
    
    def _search_with_serper(self, query: str) -> list:
        """
        Perform a search using Serper API
        """
        url = "https://google.serper.dev/search"
        
        payload = json.dumps({
            "q": query,
            "num": 10,
            "autocorrect": True
        })
        
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response_data = response.json()
            
            # Extract organic search results
            results = response_data.get('organic', [])
            return results
        except Exception as e:
            print(f"Error searching with Serper: {e}")
            return []
    
    def _is_likely_course_url(self, url: str) -> bool:
        """
        Check if the URL is likely to be a course based on the domain and path
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()
        
        # Check if URL is from a known course platform
        course_platforms = [
            "coursera.org", "udemy.com", "edx.org", "linkedin.com/learning",
            "pluralsight.com", "skillshare.com", "codecademy.com", "khanacademy.org",
            "futurelearn.com", "masterclass.com", "brilliant.org", "datacamp.com"
        ]
        
        if any(platform in domain for platform in course_platforms):
            return True
        
        # Check for course-related keywords in the path
        course_keywords = ["course", "learn", "class", "training", "tutorial", "specialization"]
        if any(keyword in path for keyword in course_keywords):
            return True
            
        return False
    
    def _validate_url(self, url: str) -> bool:
        """
        Check if the URL is accessible (returns a 200 status code)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except Exception:
            return False