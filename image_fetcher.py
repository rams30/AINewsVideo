import requests
import os
from dotenv import load_dotenv

load_dotenv()

def download_images(news_data):
    images = []
    for title, description, image_url in news_data:
        try:
            if image_url:  # Check if image URL exists
                response = requests.get(image_url)
                if response.status_code == 200:
                    images.append(response.content)
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
    return images
