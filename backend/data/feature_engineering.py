import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# Load cleaned data
df = pd.read_csv("binge_dataset_cleaned.csv")

# ---------------- NORMALIZATION ---------------- #
scaler = MinMaxScaler()

df[['rating_norm']] = scaler.fit_transform(df[['rating']])
df[['votes_norm']] = scaler.fit_transform(df[['votes']])
df[['popularity_norm']] = scaler.fit_transform(df[['popularity']])

# Recency score (newer = higher)
df['recency'] = df['year'].fillna(2000)
df[['recency_norm']] = scaler.fit_transform(df[['recency']])

# ---------------- BINGE SCORE ---------------- #
df['binge_score'] = (
    df['rating_norm'] * 0.4 +
    df['popularity_norm'] * 0.2 +
    df['votes_norm'] * 0.2 +
    df['recency_norm'] * 0.2
) * 100

# ---------------- CATEGORY ---------------- #
def categorize(score):
    if score < 40:
        return "Low"
    elif score < 70:
        return "Medium"
    else:
        return "High"

df['binge_category'] = df['binge_score'].apply(categorize)

# ---------------- SAVE ---------------- #
df.to_csv("binge_dataset_final.csv", index=False)

print("✅ Binge score added!")
print(df[['title', 'binge_score', 'binge_category']].head())