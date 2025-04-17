import os
from dotenv import load_dotenv
import requests
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_trending_news():
    """Fetch trending news articles from News API"""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "").strip()
    
    if not NEWS_API_KEY:
        raise ValueError("NEWS_API_KEY is empty or not found in environment variables. Please check your .env file.")
    
    try:
        # Make request to News API
        response = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={
                "country": "us",
                "apiKey": NEWS_API_KEY,
                "pageSize": 5  # Limit to 5 articles
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            
            if not articles:
                logger.warning("No articles found in the response")
                return []
            
            # Extract relevant information from articles
            news_data = []
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "") or ""
                image_url = article.get("urlToImage", "") or ""
                
                if title:  # Only include articles with titles
                    news_data.append((title, description, image_url))
                    logger.info(f"Added article: {title}")
            
            return news_data
            
        else:
            logger.error(f"News API request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return []
