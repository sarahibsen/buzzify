# using streamlit as the frontend
# utilizing spotify's web API to retrieve user information <3 
# fuck ai (?) 
# Resources: 
# https://medium.com/@alex.ginsberg/beginners-guide-to-the-spotify-web-api-bade6aa2d47c
# https://github.com/Alex-Ginsberg/Spot-Me
import streamlit as st
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# TODO: make a web URI so spotify doesn't scream
load_dotenv()
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI') 

if 'SPOTIPY_CLIENT_ID' in st.secrets:
    CLIENT_ID = st.secrets['SPOTIPY_CLIENT_ID']
    CLIENT_SECRET = st.secrets['SPOTIPY_CLIENT_SECRET']
    REDIRECT_URI = st.secrets['SPOTIPY_REDIRECT_URI']
else:
    # Fallback for local testing with .env
    load_dotenv()
    CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

#--- global variables 
SCOPE = "user-top-read"
LIMIT = 20
TIME_RANGE = 'medium_term' # short / medium / long


st.set_page_config(
    page_title="Buzzify",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Buzzify")

#------ functions 
def get_oauth_manager():
    """Initializes and returns the SpotifyOAuth manager."""
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=None # We are managing the state with Streamlit, not a file
    )


def get_top_tracks(sp):
    """Fetches the user's top tracks."""
    try:
        results = sp.current_user_top_tracks(
            limit=LIMIT, 
            time_range=TIME_RANGE
        )
        return results['items']
    except Exception as e:
        st.error(f"Error fetching top tracks: {e}")
        return []

def get_top_artists(sp):
    """Fetches the user's top artists."""
    try:
        # Use current_user_top_artists instead of tracks
        results = sp.current_user_top_artists(
            limit=LIMIT, 
            time_range=TIME_RANGE
        )
        return results['items']
    except Exception as e:
        st.error(f"Error fetching top artists: {e}")
        return []


if 'spotify_client' not in st.session_state:
    st.session_state['spotify_client'] = None

sp_oauth = get_oauth_manager()

# --- AUTHENTICATION FLOW ---
if st.query_params and 'code' in st.query_params:
    try:
        token_info = sp_oauth.get_access_token(st.query_params['code'], as_dict=True)
        access_token = token_info['access_token']
        st.session_state['spotify_client'] = spotipy.Spotify(auth=access_token)
        #    st.experimental_rerun() is replaced with the modern st.rerun()
        st.rerun() 
        
    except Exception as e:
        st.error(f"Failed to authenticate with Spotify. Error: {e}")
        st.session_state['spotify_client'] = None
        st.query_params.clear() 

if st.session_state['spotify_client'] is None:
    if CLIENT_ID == "YOUR_CLIENT_ID":
        st.error("Please set your Spotify Client ID and Secret in your .env file.")
        st.stop()
        
    auth_url = sp_oauth.get_authorize_url()
    
    st.markdown("---")
    st.markdown(
        f'<a href="{auth_url}" target="_self"><button style="background-color:#1db954; color:white; padding: 10px 20px; border: none; border-radius: 25px; cursor: pointer; font-size: 16px;">🔗 Login to Spotify</button></a>',
        unsafe_allow_html=True
    )
    st.info("You will be redirected to Spotify to log in and grant permissions.")


else:
    # --- DASHBOARD DISPLAY ---
    sp = st.session_state['spotify_client']
    
    # Debug message to confirm this block is reached
    st.success("Successfully logged into Spotify! Fetching your data...")
    
    # Fetch Data
    top_artists = get_top_artists(sp)
    top_tracks = get_top_tracks(sp)

    # Display Top Artists
    if top_artists:
        st.subheader(f"Your Top {LIMIT} Artists ({TIME_RANGE.replace('_', ' ').title()})")
        
        artist_list = []
        for i, artist in enumerate(top_artists):
            artist_list.append(f"{i+1}. **{artist['name']}**")
        
        st.markdown("\n".join(artist_list))

    st.markdown("---")
        
    # Display Top Tracks
    if top_tracks:
        st.subheader(f"Your Top {LIMIT} Tracks ({TIME_RANGE.replace('_', ' ').title()})")
        
        track_list = []
        for i, track in enumerate(top_tracks):
            artists = ", ".join([artist['name'] for artist in track['artists']])
            track_list.append(f"{i+1}. **{track['name']}** by {artists}")
        
        st.markdown("\n".join(track_list))
        
    # Logout Button
    if st.button("Logout"):
        st.session_state['spotify_client'] = None
        # Use the modern Streamlit rerun command
        st.rerun()
