import pandas as pd
from sklearn.linear_model import LinearRegression

# Load dataset
df = pd.read_csv("data/binge_dataset_updated.csv")

# -------------------------
# Feature Engineering
# -------------------------
df['total_time'] = (df['runtime'] * df['episodes']) / 60

features = ['rating_norm', 'votes_norm', 'popularity_norm', 'recency_norm', 'total_time']
target = 'binge_score'

X = df[features]
y = df[target]

# Train model
model = LinearRegression()
model.fit(X, y)


# -------------------------
# Prediction Function
# -------------------------
def predict_binge_ml(movie_row):
    total_time = (movie_row['runtime'] * movie_row['episodes']) / 60

    input_data = [[
        movie_row['rating_norm'],
        movie_row['votes_norm'],
        movie_row['popularity_norm'],
        movie_row['recency_norm'],
        total_time
    ]]

    prediction = model.predict(input_data)[0]

    # Clamp score
    prediction = max(0, min(100, prediction))

    return prediction