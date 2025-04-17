import os
import requests
import base64
from dotenv import load_dotenv
import logging
from PIL import Image
import io

load_dotenv()

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")
if not RUNWAY_API_KEY:
    raise ValueError("RUNWAY_API_KEY not found in environment variables")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_animated_video(image_bytes, prompt, duration=3):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        image_base64 = base64.b64encode(img_byte_arr).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {RUNWAY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "image": image_base64,
            "prompt": prompt,
            "duration": duration,
            "motion": 0.5,
            "style": "cinematic"
        }
        
        logger.info(f"Making request to Runway API with prompt: {prompt[:50]}...")
        
        response = requests.post(
            "https://api.runwayml.com/v1/image-to-video",
            headers=headers,
            json=payload
        )
        
        logger.info(f"Runway API response status code: {response.status_code}")
        logger.info(f"Response content: {response.text[:500]}...")
        
        if response.status_code == 200:
            try:
                video_data = response.json()
                logger.info("Successfully parsed JSON response")
                
                if "video" in video_data:
                    logger.info("Found video data in response")
                    video_bytes = base64.b64decode(video_data["video"])
                    logger.info(f"Successfully decoded video bytes (size: {len(video_bytes)} bytes)")
                    return video_bytes
                else:
                    logger.error("No video data in response. Response keys: %s", video_data.keys())
                    return None
            except Exception as e:
                logger.error(f"Error processing API response: {str(e)}")
                logger.error(f"Response content: {response.text[:500]}...")
                return None
        else:
            logger.error(f"API request failed with status {response.status_code}")
            logger.error(f"Response content: {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"Error in video generation: {str(e)}")
        return None 