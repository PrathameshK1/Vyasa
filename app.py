import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import json
import csv
import io

load_dotenv()  # load all the environment variables
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are an expert content creator specializing in transforming YouTube videos into high-quality blog posts for training Large Language Models. Your task is to:

1. Analyze the video transcript thoroughly.
2. Extract key insights, main topics, and supporting details.
3. Restructure the content into a well-organized blog post format.
4. Expand on important concepts with additional context or explanations.
5. Ensure the blog post is engaging, informative, and reflective of the video's core message.
6. Include relevant headings, subheadings, and bullet points for better readability.
7. Aim for a comprehensive blog post of about 1000-1500 words.

Please transform the following transcript into a high-quality blog post:"""

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

def generate_blog_post(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.title("YouTube Video to Blog Post Converter")

if 'blog_post' not in st.session_state:
    st.session_state.blog_post = None

if 'youtube_link' not in st.session_state:
    st.session_state.youtube_link = ""

youtube_link = st.text_input("Enter YouTube Video Link:", value=st.session_state.youtube_link)

if youtube_link and youtube_link != st.session_state.youtube_link:
    st.session_state.youtube_link = youtube_link
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Generate Blog Post") and youtube_link:
    with st.spinner("Generating blog post... This may take a few minutes."):
        transcript_text = extract_transcript_details(youtube_link)
        if transcript_text:
            st.session_state.blog_post = generate_blog_post(transcript_text, prompt)

if st.session_state.blog_post:
    st.markdown("## Generated Blog Post:")
    st.markdown(st.session_state.blog_post)
    
    # Options to download the blog post in different formats
    st.download_button(
        label="Download as Text",
        data=st.session_state.blog_post,
        file_name="blog_post.txt",
        mime="text/plain"
    )
    
    json_data = json.dumps({"blog_post": st.session_state.blog_post})
    st.download_button(
        label="Download as JSON",
        data=json_data,
        file_name="blog_post.json",
        mime="application/json"
    )
    
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["Blog Post"])
    csv_writer.writerow([st.session_state.blog_post])
    st.download_button(
        label="Download as CSV",
        data=csv_buffer.getvalue(),
        file_name="blog_post.csv",
        mime="text/csv"
    )

    if st.session_state.blog_post:
        if st.button("Start New Query"):
            st.session_state.blog_post = None
            st.session_state.youtube_link = ""
            st.experimental_rerun()
