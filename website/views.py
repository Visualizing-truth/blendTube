from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_required, current_user
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from . import db
from .models import Room, Video, User
from .blend import get_recommended_videos
import os
import random

views = Blueprint('views', __name__)

base_dir = os.path.abspath(os.path.dirname(__file__))
secret_file = os.path.join(base_dir, "blendTube.json")

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    room_id = current_user.room_id
    room = Room.query.filter_by(id=room_id).first()
    return render_template("home.html", user=current_user, room=room)

@views.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        secret_file,
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
        redirect_uri=url_for('views.callback', _external=True, _scheme='https')
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state

    return redirect(authorization_url)

@views.route('/callback')
def callback():
    state = session.get('state')
    flow = Flow.from_client_secrets_file(
        secret_file,
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
        state=state
    )
    flow.redirect_uri = url_for('views.callback', _external=True, _scheme='https')

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    print(credentials)
    print(type(credentials))
    session['credentials'] = credentials_to_dict(credentials)
    

    return redirect(url_for('views.home'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def dict_to_credentials(credentials_dict):
    return Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict.get('refresh_token'),
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes']
    )


@views.route('/blend', methods=['GET', 'POST'])
def blend():
    if not current_user.is_authenticated:
        flash("Please log in to access this page.", category='error')
        return redirect(url_for('auth.enterRoom'))
    
    blended = False
    
    room_id = current_user.room_id
    room = Room.query.filter_by(id=room_id).first()
        
    if len(current_user.videos) > 0:
        blended = True
        
    if not blended:  
        if 'credentials' not in session:
            flash("Please authenticate first.", category='error')
            return redirect(url_for('views.oauth2callback'))

        credentials_dict = session['credentials']
        credentials = dict_to_credentials(credentials_dict)
        
        recommended_videos = get_recommended_videos(credentials)
        
        for video in recommended_videos:
            videoTitle = video['title']       
            new_video = Video(video_id=video['videoId'], videoname=videoTitle, user_id=current_user.id)
            db.session.add(new_video)
            db.session.commit()
    
    videos = set()
    for user in room.users:
        for video in user.videos:
            videos.add(video)
    
    videos = list(videos)
    
    random.shuffle(videos)
    
    ordered_videos = {}
    for video in videos:
        user_id = video.user_id
        user = User.query.filter_by(id=user_id).first()
        ordered_videos[video.video_id]=[user, video.videoname]
        
    return render_template("blend.html", user=current_user, room=room, ordered_videos=ordered_videos)
