import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in environment variables")
genai.configure(api_key=GOOGLE_API_KEY)

def generate_script(title, description):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""Create a concise, engaging 30-second news narration script based on this news:
    Title: {title}
    Description: {description}
    
    The script should be:
    - Pure narration text only
    - No scene markers or formatting
    - Engaging and informative
    - Suitable for a news voiceover
    - Approximately 30 seconds when read aloud
    - Focus on the key points of the news story
    """
    
    try:
        print("Generating narration script...")
        response = model.generate_content(prompt)
        
        if not response.parts:
            print("No content parts in response")
            raise Exception("Empty response from Gemini")
            
        script = response.parts[0].text.strip()
        print("Generated narration:", script)
        return script
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        # Fallback to simple narration
        return f"{title}. {description} Stay tuned for more updates on this developing story."
