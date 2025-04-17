from gtts import gTTS
import os

def generate_audio(script, output_path="output/audio.mp3"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    tts = gTTS(text=script, lang='en', slow=False)
    tts.save(output_path)
    return output_path 