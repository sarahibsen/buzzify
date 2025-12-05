import musicbrainzngs
import time

musicbrainzngs.set_useragent("Buzzify", "1.0", "your@email.com")

def get_musicbrainz_genres(artist_name):
    """Search MusicBrainz for artist genres."""
    try:
        result = musicbrainzngs.search_artists(artist=artist_name, limit=1)
        if result['artist-list']:
            artist_id = result['artist-list'][0]['id']
            artist_detail = musicbrainzngs.get_artist_by_id(artist_id, includes=['tags'])
            tags = artist_detail['artist'].get('tag-list', [])
            return [tag['name'] for tag in tags[:5]]  # Top 5 tags
    except:
        return []
    time.sleep(1)  # Rate limiting
    return []
