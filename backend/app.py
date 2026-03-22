from flask import Flask, render_template, request
import pandas as pd
import os

# Correct paths based on your new structure
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_final.csv")
df = pd.read_csv(data_path)


# -------------------- ROUTES -------------------- #

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/score')
def score():
    return render_template('score.html')


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/mood')
def mood_page():
    return render_template('mood.html')


@app.route('/time')
def time_page():
    return render_template('time.html')


@app.route('/recommend')
def recommend():
    return render_template('recommend.html')


@app.route('/navbar')
def navbar():
    return render_template('navbar.html')





@app.route('/trends')
def trends():
    return render_template('trends.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# -------------------- CORE FEATURE -------------------- #

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.form['movie'].lower()
    mood = request.form['mood']
    time_available = float(request.form['time'])

    result = df[df['title'].str.lower().str.contains(user_input)]

    if not result.empty:
        movie = result.iloc[0]

        base_score = movie['binge_score']

        # 🎯 Mood-based bonus
        genre = str(movie['genres'])
        mood_bonus = 10 if mood.lower() in genre.lower() else 0

        # ⏱ Time-based adjustment
        if time_available >= 3:
            time_bonus = 5
        elif time_available < 2:
            time_bonus = -5
        else:
            time_bonus = 0

        personalized_score = base_score + mood_bonus + time_bonus

        # Clamp score
        personalized_score = max(0, min(100, personalized_score))

        return render_template(
            'result.html',
            title=movie['title'],
            score=round(personalized_score, 2),
            category=movie['binge_category'],
            mood=mood,
            time=time_available
        )

    else:
        return render_template(
            'result.html',
            title="Not Found",
            score="N/A",
            category="Try another movie"
        )


# -------------------- SIMPLE BINGE SCORE -------------------- #

@app.route('/predict_binge', methods=['POST'])
def predict_binge():
    user_input = request.form['movie'].lower()

    result = df[df['title'].str.lower().str.contains(user_input)]

    if not result.empty:
        movie = result.iloc[0]

        score = round(movie['binge_score'], 2)

        # 🎯 Category Logic
        if score < 40:
            category = "🟢 Low"
        elif score < 70:
            category = "🟡 Medium"
        else:
            category = "🔴 Highly Bingeable"

        # 📊 Confidence (simple logic based on votes/reviews)
        if 'num_votes' in movie:
            votes = movie['num_votes']
            confidence = min(100, round((votes / 100000) * 100, 2))
        else:
            confidence = 85  # fallback

        return render_template(
            'result.html',
            title=movie['title'],
            score=score,
            category=category,
            confidence=confidence
        )

    else:
        return render_template(
            'result.html',
            title="Not Found",
            score="N/A",
            category="Try another movie",
            confidence="N/A"
        )










@app.route('/analytics')
def analytics():
    global df

    # -----------------------------
    # 1. Binge Score Distribution
    # -----------------------------
    binge_distribution = df['binge_score'].tolist()

    # -----------------------------
    # 2. Genre vs Binge Score (TOP 10 ONLY)
    # -----------------------------
    df['genres'] = df['genres'].fillna('')
    df_genre = df.assign(genres=df['genres'].str.split(',')).explode('genres')
    df_genre['genres'] = df_genre['genres'].str.strip()
    df_genre = df_genre[df_genre['genres'] != '']

    genre_score = (
        df_genre.groupby('genres')['binge_score']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # -----------------------------
    # 3. Sample data (IMPORTANT FIX)
    # -----------------------------
    sample_df = df.sample(n=min(200, len(df)))  # LIMIT POINTS

    episode_length = sample_df['recency_norm'].tolist()
    completion_prob = sample_df['popularity_norm'].tolist()

    imdb_rating = sample_df['rating'].tolist()
    imdb_binge = sample_df['binge_score'].tolist()

    reviews = sample_df['votes'].tolist()
    popularity = sample_df['popularity'].tolist()

    # -----------------------------
    # 4. Trend (sorted)
    # -----------------------------
    trend_data = df.groupby('year')['popularity'].mean().reset_index()
    trend_data = trend_data.sort_values('year')

    return render_template(
        "analytics.html",
        binge_distribution=binge_distribution,
        genre_labels=genre_score['genres'].tolist(),
        genre_scores=genre_score['binge_score'].tolist(),
        episode_length=episode_length,
        completion_prob=completion_prob,
        imdb_rating=imdb_rating,
        imdb_binge=imdb_binge,
        reviews=reviews,
        popularity=popularity,
        years=trend_data['year'].tolist(),
        trend_popularity=trend_data['popularity'].tolist()
    )

# -------------------- RUN -------------------- #

if __name__ == '__main__':
    app.run(debug=True)