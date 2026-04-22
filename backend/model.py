import pandas as pd
from sklearn.linear_model import LinearRegression

# -------------------------
# Load dataset
# -------------------------
df = pd.read_csv("data/binge_dataset_updated.csv")

# -------------------------
# Feature Engineering
# -------------------------

# Total watch time (in hours)
df['total_watch_time'] = (df['runtime'] * df['episodes']) / 60

# Smart time transformation (VERY IMPORTANT FIX)
df['time_score'] = 1 / (1 + df['total_watch_time'])

# Optional but powerful feature
df['engagement'] = df['rating_norm'] * df['votes_norm']

# -------------------------
# Features & Target
# -------------------------
features = [
    'rating_norm',
    'votes_norm',
    'popularity_norm',
    'recency_norm',
    'time_score',
    'engagement'
]

target = 'binge_score'

X = df[features]
y = df[target]

# -------------------------
# Train Model
# -------------------------
model = LinearRegression()
model.fit(X, y)

# -------------------------
# Prediction Function
# -------------------------
def predict_binge_ml(movie_row):

    # Calculate watch time
    total_watch_time = (movie_row['runtime'] * movie_row['episodes']) / 60

    # Same transformation as training
    time_score = 1 / (1 + total_watch_time)

    # Engagement feature
    engagement = movie_row['rating_norm'] * movie_row['votes_norm']

    # Input for prediction
    input_data = [[
        movie_row['rating_norm'],
        movie_row['votes_norm'],
        movie_row['popularity_norm'],
        movie_row['recency_norm'],
        time_score,
        engagement
    ]]

    # Predict
    prediction = model.predict(input_data)[0]

    # Clamp score between 0–100
    prediction = max(0, min(100, prediction))

    return round(prediction, 2)