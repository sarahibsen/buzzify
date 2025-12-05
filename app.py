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
@st.cache_data
def load_artist_genres():
    """Load the artist-genre mapping from CSV."""
    try:
        df = pd.read_csv('data/artist_genres.csv')
        # Create a dictionary for faster lookup
        artist_dict = {}
        for _, row in df.iterrows():
            artist_name = row['artist_name']
            genres = row['artist_genre'].split(', ') if pd.notna(row['artist_genre']) else []
            artist_dict[artist_name.lower()] = genres
        return artist_dict
    except FileNotFoundError:
        st.error("Could not find data/artist_genres.csv file!")
        return {}

def get_artist_genres(artist_name, artist_dict):
    """Get genres for an artist from the CSV lookup."""
    return artist_dict.get(artist_name.lower(), [])

def generate_genre_report(top_artists, artist_dict):
    """Generate a genre distribution report from top artists."""
    all_genres = []
    matched_artists = []
    unmatched_artists = []
    
    for artist in top_artists:
        artist_name = artist['name']
        genres = get_artist_genres(artist_name, artist_dict)
        
        if genres:
            matched_artists.append({
                'name': artist_name,
                'genres': genres
            })
            all_genres.extend(genres)
        else:
            # Fallback to Spotify's genres if not in CSV
            spotify_genres = artist.get('genres', [])
            if spotify_genres:
                matched_artists.append({
                    'name': artist_name,
                    'genres': spotify_genres
                })
                all_genres.extend(spotify_genres)
            else:
                unmatched_artists.append(artist_name)
    
    # Count genre frequencies
    genre_counts = Counter(all_genres)
    
    return {
        'genre_counts': genre_counts,
        'matched_artists': matched_artists,
        'unmatched_artists': unmatched_artists,
        'total_artists': len(top_artists),
        'matched_count': len(matched_artists)
    }

def get_oauth_manager():
    """Initializes and returns the SpotifyOAuth manager."""
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=None
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

if st.query_params and 'code' in st.query_params:
    try:
        token_info = sp_oauth.get_access_token(st.query_params['code'])
        if isinstance(token_info, dict):
            access_token = token_info['access_token']
        else:
            access_token = token_info
        
        st.session_state['spotify_client'] = spotipy.Spotify(auth=access_token)
        st.query_params.clear()
        st.rerun() 
        
    except Exception as e:
        st.error(f"Failed to authenticate with Spotify. Error: {e}")
        st.session_state['spotify_client'] = None
        st.query_params.clear() 

if st.session_state['spotify_client'] is None:
    # --- LOGIN DISPLAY ---
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
    
    st.success("✅ Successfully logged into Spotify!")
    
    # Fetch Data
    top_artists = get_top_artists(sp)
    top_tracks = get_top_tracks(sp)
    
    # Load genre mapping
    artist_dict = load_artist_genres()

    # Display Top Artists
    if top_artists:
        st.subheader(f"Your Top {LIMIT} Artists ({TIME_RANGE.replace('_', ' ').title()})")
        
        artist_list = []
        for i, artist in enumerate(top_artists):
            genres = get_artist_genres(artist['name'], artist_dict)
            genre_display = ", ".join(genres[:3]) if genres else "No genre data"
            artist_list.append(f"{i+1}. **{artist['name']}** — *{genre_display}*")
        
        st.markdown("\n".join(artist_list))

        st.markdown("---")
        
        # Generate Report Button
        if st.button("📊 Generate Genre Report", type="primary", use_container_width=True):
            with st.spinner("Analyzing your music taste..."):
                report = generate_genre_report(top_artists, artist_dict)
                
                st.subheader("🎸 Your Genre Distribution")
                
                # Display top genres
                if report['genre_counts']:
                    st.write(f"Based on your top {report['matched_count']} artists:")
                    
                    # Get top 10 genres
                    top_genres = report['genre_counts'].most_common(10)
                    
                    # Create a bar chart
                    genre_df = pd.DataFrame(top_genres, columns=['Genre', 'Count'])
                    st.bar_chart(genre_df.set_index('Genre'))
                    
                    # Show percentage breakdown
                    st.write("**Top Genres:**")
                    total_mentions = sum(report['genre_counts'].values())
                    for genre, count in top_genres:
                        percentage = (count / total_mentions) * 100
                        st.write(f"• **{genre}**: {count} mentions ({percentage:.1f}%)")
                    
                    # Determine dominant genre
                    dominant_genre = top_genres[0][0]
                    st.success(f"🎯 Your dominant genre is: **{dominant_genre}**")
                    
                    # Show unmatched artists if any
                    if report['unmatched_artists']:
                        with st.expander("⚠️ Artists without genre data"):
                            st.write(", ".join(report['unmatched_artists']))
                else:
                    st.warning("No genre data found for your artists.")

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
    st.markdown("---")
    if st.button("Logout"):
        st.session_state['spotify_client'] = None
        st.rerun()
