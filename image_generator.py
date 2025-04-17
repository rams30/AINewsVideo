import os
import io
from dotenv import load_dotenv
import google.generativeai as genai
import logging
import requests
import json
from PIL import Image

# Load environment variables
load_dotenv()

# Configure APIs
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()

# Validate API keys
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is empty or not found in environment variables. Please check your .env file.")
if not PEXELS_API_KEY:
    raise ValueError("PEXELS_API_KEY is empty or not found in environment variables. Please check your .env file.")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Pexels API configuration
PEXELS_API_HEADERS = {
    "Authorization": PEXELS_API_KEY
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_image_prompts(script):
    """Generate image prompts for each sentence using Gemini"""
    model = genai.GenerativeModel('gemini-pro')
    
    # Split script into sentences
    sentences = [s.strip() for s in script.split('.') if s.strip()]
    image_prompts = []
    
    for sentence in sentences:
        prompt = f"""Create a detailed search query for finding a relevant news image for this sentence:
        "{sentence}"
        
        The search query should:
        - Be concise and specific (2-4 words)
        - Focus on the main subject or action
        - Use common search terms
        - Be in English
        - Not include any technical terms
        """
        
        try:
            response = model.generate_content(prompt)
            if response.parts:
                search_query = response.parts[0].text.strip()
                image_prompts.append(search_query)
                logger.info(f"Generated search query for: {sentence}")
                logger.info(f"Search query: {search_query}")
        except Exception as e:
            logger.error(f"Error generating search query: {str(e)}")
            # Fallback to using the sentence itself
            image_prompts.append(sentence)
    
    return image_prompts

def generate_images(image_prompts):
    """Generate images using Pexels API"""
    images = []
    
    for search_query in image_prompts:
        try:
            logger.info(f"Searching for image with query: {search_query}")
            
            # Search for images using Pexels API
            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers=PEXELS_API_HEADERS,
                params={
                    "query": search_query,
                    "per_page": 1,
                    "orientation": "landscape"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if "photos" in data and len(data["photos"]) > 0:
                    # Get the first photo's URL
                    photo_url = data["photos"][0]["src"]["large"]
                    
                    # Download the image
                    img_response = requests.get(photo_url)
                    if img_response.status_code == 200:
                        # Convert to bytes
                        image_bytes = img_response.content
                        images.append(image_bytes)
                        logger.info(f"Successfully downloaded image for query: {search_query}")
                    else:
                        logger.error(f"Failed to download image: {img_response.status_code}")
                        images.append(None)
                else:
                    logger.error("No photos found")
                    images.append(None)
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                images.append(None)
                
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            images.append(None)
    
    return images 