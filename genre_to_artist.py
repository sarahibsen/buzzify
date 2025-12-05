import json


# Load genres from genres.jl
def load_genres(filepath='data/genres.jl'):
    """Load the genre list from JSON Lines file."""
    genres = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            genre_data = json.loads(line)
            genres.append(genre_data['name'])
    return genres

available_genres = load_genres()
print(f"Loaded {len(available_genres)} genres")

def load_artists(): 
    """ load in the artist lists """
    pass 
