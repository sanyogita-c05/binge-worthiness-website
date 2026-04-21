import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_final.csv")
df = pd.read_csv(data_path)

# ---------------- PREPROCESS ---------------- #
df['overview'] = df['overview'].fillna('')
df['genres'] = df['genres'].fillna('')
df['content'] = df['genres'] + " " + df['overview']

# ---------------- TF-IDF ---------------- #
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['content'])

# ---------------- MOOD MAPPING ---------------- #
mood_dict = {
    "sad": "emotional sad loss tragedy heartbreak crying depression",
    "happy": "fun joy happiness feel good comedy light family",
    "romantic": "love romance relationship emotional couple",
    "comedy": "funny humor light happy comedy laughter",
    "thriller": "suspense thriller mystery crime action intense",
    "dark": "crime violence revenge psychological thriller mystery",
    "mind-blowing": "twist psychological sci-fi mystery thriller",
    "motivational": "inspiring success struggle biography sports",
    "scary": "horror fear ghost supernatural thriller"
}

# ---------------- MAIN FUNCTION ---------------- #
def get_mood_recommendations(user_mood):
    mood = user_mood.lower().strip()

    # ❌ If mood not found
    if mood not in mood_dict:
        return []

    # Convert mood to vector
    mood_vector = tfidf.transform([mood_dict[mood]])

    # Compute similarity
    similarity_scores = cosine_similarity(mood_vector, tfidf_matrix).flatten()

    # ---------------- 🔥 THRESHOLD FILTER ---------------- #
    threshold = 0.1

    filtered_indices = [
        i for i, score in enumerate(similarity_scores)
        if score > threshold
    ]

    # Sort filtered movies by similarity
    top_indices = sorted(
        filtered_indices,
        key=lambda i: similarity_scores[i],
        reverse=True
    )[:20]

    # ---------------- RESULTS ---------------- #
    results = []

    for idx in top_indices:
        movie = df.iloc[idx]

        results.append({
            "title": movie['title'],
            "score": round(float(movie['binge_score']), 2),
            "overview": movie['overview'] if movie['overview'] else "No description available"
        })

    return results