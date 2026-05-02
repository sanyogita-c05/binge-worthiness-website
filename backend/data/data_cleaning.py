import pandas as pd

# Load dataset
df = pd.read_csv("binge_dataset_fast.csv")

# ---------------- CLEAN BASIC ---------------- #
df.drop_duplicates(inplace=True)
df.dropna(subset=['title', 'rating'], inplace=True)

# ---------------- HANDLE GENRES ---------------- #
# TMDb Genre Mapping
genre_map = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
    80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
    14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
    9648: "Mystery", 10749: "Romance", 878: "Sci-Fi",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}

def convert_genres(genre_ids):
    if pd.isna(genre_ids):
        return ""
    
    # Convert string "[28, 12]" → list
    genre_ids = eval(genre_ids)
    
    names = [genre_map.get(g, "") for g in genre_ids]
    return ", ".join([n for n in names if n])

df['genres'] = df['genre_ids'].apply(convert_genres)

# ---------------- DATE PROCESSING ---------------- #
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['year'] = df['release_date'].dt.year

# ---------------- HANDLE MISSING ---------------- #
df['overview'] = df['overview'].fillna("No description")

# ---------------- DROP UNUSED ---------------- #
df.drop(columns=['genre_ids'], inplace=True)

# ---------------- SAVE CLEAN DATA ---------------- #
df.to_csv("binge_dataset_cleaned.csv", index=False)

print("✅ Cleaned dataset ready!")
print(df.head())