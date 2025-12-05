import requests
from bs4 import BeautifulSoup
import json


response = requests.get('https://everynoise.com/everynoise1d.html')
soup = BeautifulSoup(response.content, 'html.parser')

# Find all td elements with class="note"
genres = []
for td in soup.find_all('td', class_='note'):
    link = td.find('a')
    if link and link.text:
        genre_name = link.text.strip()
        genres.append({'name': genre_name})

with open('data/genres.jl', 'w', encoding='utf-8') as f:
    for genre in genres:
        f.write(json.dumps(genre) + '\n')

print(f"✅ Saved {len(genres)} genres to data/genres.jl")

print("\nFirst 10 genres:")
for genre in genres[:10]:
    print(f"  - {genre['name']}")
