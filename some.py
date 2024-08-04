from google_auth_oauthlib.flow import Flow
from flask import session
import os
# Create the flow using the client secrets file from the Google API
# Console.

base_dir = os.path.abspath(os.path.dirname(__file__))
secret_file = os.path.join(base_dir, "Karman.apps.googleusercontent.com.json")

flow = Flow.from_client_secrets_file(
        secret_file,
        scopes=['https://www.googleapis.com/auth/youtube.readonly'],
    )
authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

session['state'] = state
