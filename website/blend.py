from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import isodate
import requests
import random
import os
from google.oauth2.credentials import Credentials

rapidapi_key = "886084b336mshafae2d96e57bab9p152a02jsn585a728172e3"
MAX_VIDEOS = 600
RAPID_ID = 'videoId'
YT_ID = 'id'
NUM_BASE_VIDEOS = 20
NUM_RECOMMENDED_VIDEOS = 40



def authenticate_user(client_secrets_file):
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Create the flow using the client secrets file
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)

    # Run the local server to handle the OAuth 2.0 redirect
    credentials = flow.run_local_server(port=8080)
    
    print(type(credentials))

    return credentials

def get_video_by_id(credentials, video_id):
    youtube = build('youtube', 'v3', credentials=credentials)
    
    request = youtube.videos().list(
        part='snippet,contentDetails,statistics',
        id=video_id
    )
    
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]
    else:
        return None
    
def is_short_video(video):
    duration = video['contentDetails']['duration']
    duration_seconds = isodate.parse_duration(duration).total_seconds()
    
    return duration_seconds < 120

def get_video_details(credentials, video_id):
    youtube = build('youtube', 'v3', credentials=credentials)
    
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    
    response = request.execute()
    if response['items']:
        return response['items'][0]
    return None

def get_liked_videos(credentials):
    youtube = build('youtube', 'v3', credentials=credentials)

    next_page_token = None
    liked_videos = []

    while len(liked_videos) < MAX_VIDEOS:
        request = youtube.videos().list(
            part=["snippet", "contentDetails"],
            maxResults=50,
            myRating = 'like',
            pageToken = next_page_token
            
        )
        response = request.execute()

        # Add fetched videos to list
        liked_videos.extend(response.get("items", []))

        # Check if there's another page of results
        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break
    # Removing shorts  
    liked_videos = [video for video in liked_videos if not is_short_video(video)]
    
    return liked_videos
            
def get_base_videos(credentials):
    liked_videos = get_liked_videos(credentials)
    if len(liked_videos) < 50: 
        return liked_videos
    # Randomnly select elements from the liked_videos list
    select_videos = random.sample(liked_videos, NUM_BASE_VIDEOS)
    
    return select_videos

def get_related_videos(rapidapi_key, video_id):
    url = "https://yt-api.p.rapidapi.com/related"
    querystring = {"id": video_id}
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "yt-api.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    
    # Check for rate limit errors
    if response.status_code == 429:
        print("Rate limit exceeded. Try again later.")
        return []
    # Handle unexpected response structure
    if 'data' not in response.json():
        print("Unexpected response structure:", response.json())
        return []
    
    return response.json()['data']
   
def get_recommended_videos(credentials):
    
    recommended_videos = []
    base_videos = get_base_videos(credentials)
    unique_ids = set()
    count = 0
    
    for video in base_videos:
        count += 1
        print(count)
        
        related_videos = get_related_videos(rapidapi_key, video[YT_ID])
        
        for related_video in related_videos:
            if related_video['videoId'] not in unique_ids:
                unique_ids.add(related_video['videoId'])
                recommended_videos.append(related_video)
    
    if len(recommended_videos) <= NUM_RECOMMENDED_VIDEOS:
        return recommended_videos    
    return random.sample(recommended_videos, NUM_RECOMMENDED_VIDEOS)
        

base_dir = os.path.abspath(os.path.dirname(__file__))
secret_file = os.path.join(base_dir, "Karman.apps.googleusercontent.com.json")


credentials = authenticate_user(secret_file)


get_liked_videos(credentials)



