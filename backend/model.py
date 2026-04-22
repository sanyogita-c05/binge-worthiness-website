import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_updated.csv")
df = pd.read_csv(data_path)

# ---------------- PREPROCESS ---------------- #

df['genres'] = df['genres'].fillna('')

# Convert genres → numeric feature
df['genre_count'] = df['genres'].apply(lambda x: len(x.split(',')))

# Handle missing values
df['runtime'] = df['runtime'].fillna(df['runtime'].mean())
df['episodes'] = df['episodes'].fillna(1)

# ---------------- FEATURES ---------------- #

X = df[['runtime', 'episodes', 'genre_count']]
y = df['binge_score']

# ---------------- TRAIN MODEL ---------------- #

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

print("✅ ML Model Loaded Successfully")

# ---------------- PREDICTION FUNCTION ---------------- #

def predict_binge_ml(runtime, episodes, genres):
    genre_count = len(genres.split(','))

    prediction = model.predict([[runtime, episodes, genre_count]])

    return float(prediction[0])