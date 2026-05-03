import pandas as pd
import numpy as np

# ==============================
# 1. LOAD DATASET
# ==============================
df = pd.read_csv("binge_dataset_updated.csv")

print("Original Shape:", df.shape)


# ==============================
# 2. INITIAL DATA CHECK
# ==============================
print("\nMissing Values:\n", df.isnull().sum())
print("\nDuplicate Rows:", df.duplicated().sum())


# ==============================
# 3. HANDLE MISSING VALUES
# ==============================
# Drop rows where genres are missing
df = df.dropna(subset=['genres'])

# Remove 'Unknown' genres if they exist
df = df[df['genres'] != 'Unknown']

# Drop rows where critical columns are missing
df = df.dropna(subset=['year', 'release_date'])


# ==============================
# 4. FIX ZERO VALUES (IMPORTANT)
# ==============================

# Replace invalid zeros with NaN
df['rating'] = df['rating'].replace(0, np.nan)
df['votes'] = df['votes'].replace(0, np.nan)
df['runtime'] = df['runtime'].replace(0, np.nan)
df['total_watch_time'] = df['total_watch_time'].replace(0, np.nan)

# Drop rows where essential values are missing
df = df.dropna(subset=['rating', 'votes', 'runtime'])


# ==============================
# 5. REMOVE DUPLICATES
# ==============================
df = df.drop_duplicates(subset=['title'])


# ==============================
# 6. FIX DATA TYPES
# ==============================
df['year'] = df['year'].astype(int)


# ==============================
# 7. REMOVE OUTLIERS
# ==============================

# Remove unrealistic values
df = df[df['episodes'] < 1000]
df = df[df['total_watch_time'] < 1000]


# ==============================
# 8. NORMALIZE FEATURES
# ==============================

df['rating_norm'] = (df['rating'] - df['rating'].min()) / (df['rating'].max() - df['rating'].min())
df['votes_norm'] = (df['votes'] - df['votes'].min()) / (df['votes'].max() - df['votes'].min())
df['recency_norm'] = (df['year'] - df['year'].min()) / (df['year'].max() - df['year'].min())


# ==============================
# 9. CALCULATE BINGE SCORE
# ==============================

df['binge_score'] = (
    0.4 * df['rating_norm'] +
    0.3 * df['votes_norm'] +
    0.3 * df['recency_norm']
)


# ==============================
# 10. CREATE BINGE CATEGORY
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
# 11. FINAL CHECK
# ==============================

print("\nCleaned Shape:", df.shape)
print("\nRemaining Missing Values:\n", df.isnull().sum())


# ==============================
# 12. SAVE CLEAN DATASET
# ==============================

df.to_csv("cleaned_binge_dataset.csv", index=False)

print("\n✅ Cleaned dataset saved as 'cleaned_binge_dataset.csv'")