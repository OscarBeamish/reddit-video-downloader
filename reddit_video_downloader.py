# import config.py
from config import reddit
import praw
import yt_dlp as youtube_dl
import os
import shutil
from moviepy.editor import concatenate_videoclips, VideoFileClip
from datetime import datetime

# Reddit API Credentials
reddit_credentials = reddit

# Initialize Reddit API
reddit_instance = praw.Reddit(client_id=reddit_credentials['client_id'],
                              client_secret=reddit_credentials['client_secret'],
                              user_agent=reddit_credentials['user_agent'],
                              username=reddit_credentials['username'],
                              password=reddit_credentials['password'])

def download_videos(subreddit_name, limit=20):
    try:
        subreddit = reddit_instance.subreddit(subreddit_name)
        all_videos = subreddit.top(time_filter='all')
    except Exception as e:
        print(f"Error accessing subreddit '{subreddit_name}': {e}")
        return []

    video_urls = []
    for submission in all_videos:
        if len(video_urls) >= limit:
            break
        if hasattr(submission, 'url') and submission.media and 'reddit_video' in submission.media:
            video_duration = submission.media['reddit_video']['duration']
            if video_duration <= 45:
                video_urls.append(submission.url)

    if not video_urls:
        print(f"No suitable videos found in the subreddit '{subreddit_name}'.")
    return video_urls[:limit]

def download_video(url, index, folder):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{folder}/{index}.mp4',
        'quiet': False,
        'verbose': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Failed to download video from {url}. Error: {e}")

def create_video_sequence(videos, folder):
    clips = [VideoFileClip(video) for video in videos if os.path.exists(video)]
    if clips:
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(f"{folder}/final_video.mp4")
    else:
        print("No videos were downloaded successfully. Cannot create final video sequence.")

# Main Script
if __name__ == "__main__":
    subreddit_name = 'cringe'
    date_folder = datetime.now().strftime('%y%m%d')
    video_folder = f'videos/{date_folder}'

    # Create video folder if it doesn't exist and clear existing files
    if os.path.exists(video_folder):
        shutil.rmtree(video_folder)
    os.makedirs(video_folder)

    print(f"Attempting to access the subreddit: {subreddit_name}")
    video_urls = download_videos(subreddit_name)
    
    if not video_urls:
        print(f"Failed to retrieve videos from subreddit: {subreddit_name}")
    else:
        downloaded_videos = []
        for i, url in enumerate(video_urls):
            print(f"Attempting to download video from {url}")
            download_video(url, i, video_folder)
            if os.path.exists(f'{video_folder}/{i}.mp4'):
                downloaded_videos.append(f'{video_folder}/{i}.mp4')
        create_video_sequence(downloaded_videos, video_folder)
