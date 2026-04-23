import requests
import pandas as pd

API_KEY = "YOUR_API_KEY"

data_list = []

# -------- MOVIES -------- #
for page in range(1, 21):
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page={page}"
    response = requests.get(url)
    data = response.json()

    for movie in data['results']:
        data_list.append({
            "id": movie['id'],
            "title": movie['title'],
            "type": "movie",
            "rating": movie['vote_average'],
            "votes": movie['vote_count'],
            "popularity": movie['popularity'],
            "release_date": movie['release_date'],
            "genre_ids": movie['genre_ids'],
            "overview": movie['overview']
        })

# -------- TV SHOWS -------- #
for page in range(1, 21):
    url = f"https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&page={page}"
    response = requests.get(url)
    data = response.json()

    for show in data['results']:
        data_list.append({
            "id": show['id'],
            "title": show['name'],
            "type": "tv",
            "rating": show['vote_average'],
            "votes": show['vote_count'],
            "popularity": show['popularity'],
            "release_date": show['first_air_date'],
            "genre_ids": show['genre_ids'],
            "overview": show['overview']
        })

df = pd.DataFrame(data_list)
df.to_csv("binge_dataset_fast.csv", index=False)

print("✅ Fast dataset created!")
print(df.head())