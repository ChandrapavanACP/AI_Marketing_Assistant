# BUSINESS SCIENCE UNIVERSITY
# PYTHON FOR GENERATIVE AI COURSE
# RETRIEVAL-AUGMENTED GENERATION (RAG)
# ***

# Goal: Collect Expertise on a Topic that's relevant to your business application

# YOUTUBE API SETUP ------------------------------------------------
# 1. Go to https://console.developers.google.com/
# 2. Create a new project
# 3. Enable the YouTube Data API v3
# 4. Create credentials
# 5. Place the credentials in a file called credentials.yml formatted as follows:
# youtube: 'YOUR_API_KEY'

# 1.0 IMPORTS 

# * FIX: pytube is currently broken. This patch requires pytubefix
# !pip install pytubefix

# from langchain_community.document_loaders import YoutubeLoader
from langchain_pytubefix import YoutubeLoaderFix

from googleapiclient.discovery import build

import yaml
import os

import pandas as pd
from tqdm import tqdm
from pprint import pprint


# 2.0 YOUTUBE API KEY SETUP 

PATH_CREDENTIALS = '../credentials.yml'

os.environ['YOUTUBE_API_KEY'] = yaml.safe_load(open(PATH_CREDENTIALS))['youtube'] 

# 3.0 VIDEO TRANSCRIPT SCRAPING FUNCTIONS

def search_videos(topic, api_key, max_results=20):
    """
    Search for videos on a topic using the YouTube API
    
    Parameters
    ----------
    topic : str
        The topic to search for
    api_key : str
        The YouTube API key
    max_results : int
        The maximum number of videos to return
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    request = youtube.search().list(
        q=topic,
        part='id,snippet',
        maxResults=max_results,
        type='video'
    )
    response = request.execute()
    video_ids = [item['id']['videoId'] for item in response['items']]
    return video_ids

def load_video(video_id, add_video_info=False,):
    """
    Load a video transcript from YouTube
    
    Parameters
    ----------
    video_id : str
        The YouTube video ID
    add_video_info : bool
        Whether to add video metadata to the output. Requires `pytubefix` to be installed.
    """
    url = f'https://www.youtube.com/watch?v={video_id}'
    loader = YoutubeLoaderFix.from_youtube_url(
        url, 
        # * CHANGE THIS TO TRUE ONCE YOUTUBE'S API IS FIXED
        add_video_info=add_video_info,
    )
    doc = loader.load()[0]
    doc_df = pd.DataFrame([doc.metadata])
    doc_df['video_url'] = url
    doc_df['page_content'] = doc.page_content
    return doc_df


# 4.0 SCRAPE YOUTUBE VIDEOS TRANSCRIPTS

# TOPIC = "Formula 1 Racing Cars and How They Work"
TOPIC = "Social Media Brand Strategy Tips"

video_ids = search_videos(
    topic=TOPIC, 
    api_key=os.environ['YOUTUBE_API_KEY'], 
    max_results=5
)
video_ids

video_ids[0]

video = load_video(video_ids[3], add_video_info=False)

pprint(video['page_content'][0])

# 5.0 PROCESS ALL VIDEOS

# * Scrape the video metadata and page content
videos = []
for video_id in tqdm(video_ids, desc="Processing videos"):
    try:
        video = load_video(video_id, add_video_info=True)
        videos.append(video)
    except Exception as e:
        print(f"Skipping video {video_id} due to error: {e}")


videos_df = pd.concat(videos, ignore_index=True)

videos_df.head()

# * Store the video transcripts in a CSV File
# videos_df.to_csv('data/youtube_videos.csv', index=False)



# 6.0 SAVE VIDEOS TO CSV

videos_df = pd.read_csv('data/youtube_videos.csv')
pprint(videos_df['page_content'][0])
videos_df['video_url'][0]

videos_df.head()


