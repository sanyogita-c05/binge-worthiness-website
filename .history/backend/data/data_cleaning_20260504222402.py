import pandas as pd
import numpy as np

# ==============================
# 1. LOAD DATASET
# ==============================
df = pd.read_csv("binge_dataset_fast.csv")

print("Original Shape:", df.shape)

# ==============================
# 2. BASIC CLEANING
# ==============================
df.drop_duplicates(inplace=True)
df.dropna(subset=['title', 'rating'], inplace=True)

# ==============================
# 3. HANDLE GENRES (TMDb Mapping)
# ==============================
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
    try:
        genre_ids = eval(genre_ids)
        names = [genre_map.get(g, "") for g in genre_ids]
        return ", ".join([n for n in names if n])
    except:
        return ""

df['genres'] = df['genre_ids'].apply(convert_genres)

# Remove unknown/empty genres
df = df[df['genres'] != ""]
df = df[df['genres'] != "Unknown"]

# ==============================
# 4. DATE PROCESSING
# ==============================
df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
df['year'] = df['release_date'].dt.year

df = df.dropna(subset=['year', 'release_date'])

# ==============================
# 5. HANDLE MISSING VALUES
# ==============================
df['overview'] = df['overview'].fillna("No description")

# ==============================
# 6. REMOVE UNUSED COLUMNS
# ==============================
if 'genre_ids' in df.columns:
    df.drop(columns=['genre_ids'], inplace=True)

# ==============================
# 7. FIX ZERO VALUES
# ==============================
df['rating'] = df['rating'].replace(0, np.nan)
df['votes'] = df['votes'].replace(0, np.nan)
df['runtime'] = df['runtime'].replace(0, np.nan)
df['total_watch_time'] = df['total_watch_time'].replace(0, np.nan)

df = df.dropna(subset=['rating', 'votes', 'runtime'])

# ==============================
# 8. REMOVE DUPLICATES (BY TITLE)
# ==============================
df = df.drop_duplicates(subset=['title'])

# ==============================
# 9. FIX DATA TYPES
# ==============================
df['year'] = df['year'].astype(int)

# ==============================
# 10. REMOVE OUTLIERS
# ==============================
df = df[df['episodes'] < 1000]
df = df[df['total_watch_time'] < 1000]

# ==============================
# 11. NORMALIZATION
# ==============================
df['rating_norm'] = (df['rating'] - df['rating'].min()) / (df['rating'].max() - df['rating'].min())
df['votes_norm'] = (df['votes'] - df['votes'].min()) / (df['votes'].max() - df['votes'].min())
df['recency_norm'] = (df['year'] - df['year'].min()) / (df['year'].max() - df['year'].min())

# ==============================
# 12. BINGE SCORE CALCULATION
# ==============================
df['binge_score'] = (
    0.4 * df['rating_norm'] +
    0.3 * df['votes_norm'] +
    0.3 * df['recency_norm']
)

# ==============================
# 13. BINGE CATEGORY
# ==============================
def categorize(score):
    if score < 0.4:
        return "Low"
    elif score < 0.7:
        return "Medium"
    else:
        return "High"

df['binge_category'] = df['binge_score'].apply(categorize)

# ==============================
# 14. FINAL CHECK
# ==============================
print("\nCleaned Shape:", df.shape)
print("\nRemaining Missing Values:\n", df.isnull().sum())

# ==============================
# 15. SAVE CLEAN DATASET
# ==============================
df.to_csv("cleaned_binge_dataset.csv", index=False)

print("\n✅ Final cleaned dataset saved as 'cleaned_binge_dataset.csv'")
print(df.head())