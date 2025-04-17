import os
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip
from moviepy.config import change_settings
from PIL import Image
import io
import logging
import shutil


IMAGEMAGICK_BINARY = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_video(script, images, audio_path):
    try:
        os.makedirs("output", exist_ok=True)
        
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        
        sentences = [s.strip() for s in script.split('.') if s.strip()]
        
        logger.info(f"Number of sentences: {len(sentences)}")
        logger.info(f"Number of images: {len(images)}")
        logger.info(f"Audio duration: {total_duration} seconds")
        
        if not sentences or not images:
            raise ValueError("No sentences or images provided")
        
        duration_per_scene = total_duration / len(sentences)
        logger.info(f"Duration per scene: {duration_per_scene} seconds")
        
        clips = []
        for i, (sentence, image_bytes) in enumerate(zip(sentences, images)):
            try:
                if not image_bytes:
                    logger.warning(f"No image bytes for sentence {i+1}")
                    continue
                    
                try:
                    img = Image.open(io.BytesIO(image_bytes))
                    logger.info(f"Successfully opened image {i+1} with size {img.size}")
                except Exception as e:
                    logger.error(f"Error opening image {i+1}: {str(e)}")
                    continue
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    logger.info(f"Converted image {i+1} to RGB mode")
                
                img_path = f"output/temp_{i}.jpg"
                try:
                    img.save(img_path)
                    logger.info(f"Saved temporary image {i+1} to {img_path}")
                except Exception as e:
                    logger.error(f"Error saving image {i+1}: {str(e)}")
                    continue
                
                try:
                    img_clip = ImageClip(img_path).set_duration(duration_per_scene)
                    img_clip.fps = 24
                    logger.info(f"Created image clip {i+1}")
                except Exception as e:
                    logger.error(f"Error creating image clip {i+1}: {str(e)}")
                    continue
                
                try:
                    text_width = int(img.width * 0.9)  
                    font_size = int(img.height * 0.05)  
                    
                    text_clip = TextClip(
                        sentence,
                        fontsize=font_size,
                        color='white',
                        bg_color='rgba(0,0,0,0.7)',  
                        font='Arial-Bold',
                        size=(text_width, None),
                        method='caption',
                        align='center',
                        stroke_color='black',
                        stroke_width=2
                    ).set_duration(duration_per_scene)
                    
                    text_clip = text_clip.set_position(('center', 'bottom'))
                    text_clip.fps = 24
                    logger.info(f"Created text clip {i+1}")
                except Exception as e:
                    logger.error(f"Error creating text clip {i+1}: {str(e)}")
                    continue
                
                try:
                    video_clip = CompositeVideoClip([
                        img_clip,
                        text_clip
                    ])
                    video_clip.fps = 24
                    clips.append(video_clip)
                    logger.info(f"Successfully created composite clip {i+1}")
                except Exception as e:
                    logger.error(f"Error creating composite clip {i+1}: {str(e)}")
                    continue
                
            except Exception as e:
                logger.error(f"Error processing sentence {i}: {str(e)}")
                continue
        
        if not clips:
            raise ValueError("No valid clips were created. Check the logs for details.")
        
        final_video = concatenate_videoclips(clips)
        final_video.fps = 24
        
        final_video = final_video.set_audio(audio)
        
        output_path = "output/final_video.mp4"
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            fps=24,
            bitrate="5000k",
            threads=4,
            preset='medium'
        )
        
        for i in range(len(sentences)):
            try:
                os.remove(f"output/temp_{i}.jpg")
            except:
                pass
        
        final_video.close()
        audio.close()
        for clip in clips:
            clip.close()
        
        # Copy the video to the downloads folder for easy access
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads", "ai_news_video.mp4")
        shutil.copy2(output_path, downloads_path)
        logger.info(f"Video copied to Downloads folder: {downloads_path}")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error creating video: {str(e)}")
        raise
