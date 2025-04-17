import streamlit as st
import os
from news_scraper import get_trending_news
from script_generator import generate_script
from image_generator import generate_image_prompts, generate_images
from text_to_speech import generate_audio
from video_creator import create_video

st.title("📰 AI-Powered News Video Generator")

if st.button("Generate Video"):
    with st.spinner("Fetching news..."):
        news_data = get_trending_news()
        title, desc, image_url = news_data[0]  # Get first news item

    st.write("**News Title:**", title)
    st.write("**Description:**", desc)

    with st.spinner("Generating script..."):
        script = generate_script(title, desc)
    st.write("**Script:**", script)

    with st.spinner("Generating image prompts..."):
        image_prompts = generate_image_prompts(script)
        st.write("**Generated Image Prompts:**")
        for i, prompt in enumerate(image_prompts):
            st.write(f"Scene {i+1}: {prompt}")

    with st.spinner("Generating images..."):
        images = generate_images(image_prompts)
        valid_images = [img for img in images if img is not None]
        st.write(f"Generated {len(valid_images)} valid images out of {len(images)} attempts")
        
        if not valid_images:
            st.error("No valid images were generated. Please try again.")
            st.stop()
        
        for i, image_bytes in enumerate(valid_images):
            st.image(image_bytes, caption=f"Scene {i+1}", use_container_width=True)

    with st.spinner("Generating audio..."):
        audio_path = generate_audio(script)

    with st.spinner("Creating video..."):
        video_path = create_video(script, valid_images, audio_path)

    st.success("Video generated successfully!")
    st.video(video_path)
