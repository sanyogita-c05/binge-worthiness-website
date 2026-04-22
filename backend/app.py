from flask import Flask, render_template, request
import pandas as pd
import os
import random
import numpy as np

from mood_engine import get_mood_recommendations
from model import predict_binge_ml, get_model_metrics
from scipy.stats import f_oneway

# Correct paths based on your new structure
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_updated.csv")
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


@app.route('/time_result', methods=['POST'])
def time_result():
    time_available = float(request.form['time'])
    results = []

    for _, row in df.iterrows():

        total_time = row['total_watch_time']
        runtime = row['runtime']
        episodes = row['episodes']

        # Skip invalid zero/negative times
        if total_time <= 0 or runtime <= 0:
           continue

        # Recommendation logic
        if total_time <= time_available:
            status = "✅ Can Finish Completely"
        elif total_time <= time_available * 2:
            status = "⏳ Good to Start"
        else:
            continue

        results.append({
            'title': row['title'],
            'type': row['type'],
            'runtime': runtime,
            'episodes': episodes,
            'total_time': round(total_time, 2),
            'score': round(row['binge_score'], 2),
            'status': status
        })

    # Sort by highest binge score
    results = sorted(results, key=lambda x: x['score'], reverse=True)

    # Top 50 results
    results = results[:50]

    return render_template(
        'time_result.html',
        results=results,
        time=time_available
    )

@app.route('/recommend')
def recommend():
    return render_template('recommend.html')


@app.route('/navbar')
def navbar():
    return render_template('navbar.html')

@app.route('/pipeline')
def pipeline():
    return render_template('pipeline.html')

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

@app.route('/ai_binge')
def ai_binge():
    return render_template('ai_binge.html')
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
    # Tableau handles all analytics, so no data processing needed
    return render_template("analytics.html")





# -------------------- PERSONALIZED FEATURE -------------------- #

@app.route('/personalized')
def personalized():
    return render_template('personalized.html')


@app.route('/personalized_result', methods=['POST'])
def personalized_result():

    user_input = request.form['movie'].lower()
    selected_genres = request.form.getlist('genres')
    mood = request.form['mood']
    time_available = float(request.form['time'])

    result = df[df['title'].str.lower().str.contains(user_input)]

    if not result.empty:
        movie = result.iloc[0]

        base_score = movie['binge_score']

        # ---------------------------
        # 🎭 CLEAN GENRE LIST (VERY IMPORTANT FIX)
        # ---------------------------
        movie_genres_raw = str(movie['genres'])
        movie_genre_list = [g.strip().lower() for g in movie_genres_raw.split(',')]

        # ---------------------------
        # 🎭 Genre Matching (SMART)
        # ---------------------------
        match_count = sum(1 for g in selected_genres if g.lower() in movie_genre_list)

        if selected_genres:
            genre_score = (match_count / len(selected_genres)) * 20
        else:
            genre_score = 0

        # ---------------------------
        # 😊 Mood Mapping (CRITICAL FIX)
        # ---------------------------
        mood_map = {
            "thriller": ["thriller", "mystery", "crime", "action"],
            "romance": ["romance", "drama"],
            "comedy": ["comedy"],
            "dark": ["crime", "mystery", "drama"],
            "feel-good": ["comedy", "family", "romance"]
        }

        mapped_genres = mood_map.get(mood.lower(), [])

        if any(g in movie_genre_list for g in mapped_genres):
            mood_score = 10
        else:
            mood_score = -5   # softer penalty

        # ---------------------------
        # ⏱ Time Logic (REALISTIC)
        # ---------------------------
        duration = movie.get('runtime', 120)  # minutes
        duration_hours = duration / 60

        ratio = time_available / duration_hours

        if ratio >= 1:
            time_score = 10
        elif ratio >= 0.5:
            time_score = 0
        else:
            time_score = -10

        # ---------------------------
        # 🧠 FINAL SCORE (BALANCED)
        # ---------------------------
        personalized_score = (
            (0.6 * base_score) +   # weight base score
            genre_score +
            mood_score +
            time_score
        )

        personalized_score = max(0, min(100, personalized_score))

        # ---------------------------
        # 📊 Confidence (BETTER)
        # ---------------------------
        confidence = round(
            max(30, min(100, 50 + genre_score + mood_score)),
            2
        )

        # ---------------------------
        # 💬 SMART MESSAGE
        # ---------------------------
        if personalized_score > 75:
            message = f"🔥 Perfect match! '{movie['title']}' will hook you."
        elif personalized_score > 50:
            message = f"👍 Decent choice, but may not fully match your mood/time."
        else:
            message = f"⚠️ Not ideal right now based on your mood or time."

        return render_template(
            'personalized_result.html',
            title=movie['title'],
            score=round(personalized_score, 2),
            confidence=confidence,
            genres=", ".join(selected_genres),
            mood=mood,
            time=time_available,
            message=message
        )

    else:
        return render_template(
            'personalized_result.html',
            title="Not Found",
            score="N/A",
            confidence="N/A",
            message="Try another movie"
        )


# -------------------- MOOD RECOMMENDATION (ML FEATURE) -------------------- #

@app.route('/mood_recommend', methods=['POST'])
def mood_recommend():
    mood = request.form['mood']

    recommendations = get_mood_recommendations(mood)

    return render_template(
        'recommend.html',
        recommendations=recommendations,
        mood=mood
    )

@app.route('/ai_predict', methods=['POST'])
def ai_predict():
    user_input = request.form['movie'].lower()

    result = df[df['title'].str.lower().str.contains(user_input)]

    if not result.empty:
        movie = result.iloc[0]

        # ML Prediction
        score = predict_binge_ml(movie)

        runtime = movie['runtime']
        episodes = movie['episodes']
        total_time = (runtime * episodes) / 60

        return render_template(
            'ai_result.html',
            title=movie['title'],
            score=round(score, 2),
            runtime=runtime,
            episodes=episodes,
            total_time=round(total_time, 2),
            genres=movie['genres']
        )

    else:
        return render_template(
            'ai_result.html',
            title="Not Found",
            score="N/A"
        )


@app.route('/stage5')
def stage5():
    results = []

    for _, row in df.iterrows():
        try:
            score = predict_binge_ml(row)
            results.append({
                "title": row["title"],
                "score": round(score, 2)
            })
        except:
            pass

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return render_template("stage5.html", movies=results[:20])

@app.route('/ai_predictions', methods=['GET', 'POST'])
def ai_predictions():
    top_n = request.args.get('top_n', '20')

    results = []

    for _, row in df.iterrows():
        try:
            score = predict_binge_ml(row)
            results.append({
                "title": row["title"],
                "score": round(score, 2)
            })
        except:
            pass

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    if top_n != "all":
        results = results[:int(top_n)]

    return render_template(
        "ai_predictions.html",
        movies=results,
        selected=top_n
    )

@app.route('/evaluation_metrics')
def evaluation_metrics():
    metrics = get_model_metrics()
    return render_template(
        "evaluation_metrics.html",
        metrics=metrics
    )

@app.route('/algorithms_used')
def algorithms_used():
    return render_template("algorithms_used.html")

# -------------------- EDA / ANALYSIS -------------------- #

# -------------------- EDA / ANALYSIS -------------------- #

@app.route('/analysis')
def analysis():

    # ---- BASIC INFO ----
    total_rows, total_cols = df.shape
    columns = df.columns.tolist()

    sample_data = df.head(5).to_dict(orient='records')

    # ---- MISSING VALUES ----
    missing = df.isnull().sum()
    duplicates = df.duplicated().sum()

    # ---- CLEANING NOTES ----
    cleaning_notes = [
        "Missing values in numeric columns were handled using median values.",
        "Duplicate records were identified and removed.",
        "Genres were standardized and cleaned for consistency.",
        "Normalized columns (rating_norm, votes_norm, etc.) were created for fair comparison."
    ]

    # ---- UNIVARIATE ----
    rating_data = df['rating'].dropna().tolist()

    genre_expanded = df.assign(genres=df['genres'].str.split(',')).explode('genres')
    genre_expanded['genres'] = genre_expanded['genres'].str.strip()

    genre_counts = genre_expanded['genres'].value_counts().head(10)
    runtime_data = df['runtime'].dropna().tolist()

    # ---- BIVARIATE ----
    rating_popularity = df[['rating', 'popularity']].dropna()

    genre_rating = genre_expanded.groupby('genres')['rating'].mean().sort_values(ascending=False).head(10)

    runtime_binge = df[['runtime', 'binge_score']].dropna()

    # ---- CORRELATION ----
    corr_df = df[['rating', 'votes', 'popularity', 'runtime', 'binge_score', 'total_watch_time']].dropna()
    corr_matrix = corr_df.corr().round(2)

    # ===========================
    # 🔥 HYPOTHESIS TEST (ANOVA)
    # ===========================

    # Prepare data: group binge scores by genre
    genre_groups = genre_expanded.groupby('genres')['binge_score'].apply(list)

    # Filter only genres with enough data
    valid_groups = [g for g in genre_groups if len(g) > 5]

    if len(valid_groups) > 1:
        f_stat, p_value = f_oneway(*valid_groups)
    else:
        f_stat, p_value = 0, 1  # fallback


    # Create bins
    bins = [0, 2, 4, 6, 8, 10]
    hist, bin_edges = np.histogram(df['rating'].dropna(), bins=bins)

    rating_bins = [f"{int(bin_edges[i])}-{int(bin_edges[i+1])}" for i in range(len(bin_edges)-1)]
    rating_counts = hist.tolist()

    # Decision
    alpha = 0.05
    if p_value < alpha:
        hypothesis_result = "Reject Null Hypothesis: Different genres have significantly different binge scores."
    else:
        hypothesis_result = "Fail to Reject Null Hypothesis: No significant difference in binge scores across genres."

    # ---- INSIGHTS ----
    top_genre = genre_counts.index[0]
    avg_rating = round(df['rating'].mean(), 2)
    avg_binge = round(df['binge_score'].mean(), 2)

    insights = [
        f"The dataset contains {total_rows} records with {total_cols} features describing content characteristics.",
        f"Average rating is {avg_rating}, indicating generally well-rated content.",
        f"Average binge score is {avg_binge}, reflecting user engagement trends.",
        f"Genre '{top_genre}' appears most frequently in the dataset.",
        "Higher ratings and popularity tend to increase binge-worthiness.",
        "Shorter runtime content often shows better engagement.",
        hypothesis_result
    ]

    return render_template(
        "analysis.html",

        total_rows=total_rows,
        total_cols=total_cols,
        columns=columns,
        sample_data=sample_data,

        missing_labels=missing.index.tolist(),
        missing_values=missing.values.tolist(),
        duplicates=duplicates,
        cleaning_notes=cleaning_notes,

        rating_data=rating_data,
        genre_labels=genre_counts.index.tolist(),
        genre_counts=genre_counts.tolist(),
        runtime_data=runtime_data,

        rating_list=rating_popularity['rating'].tolist(),
        popularity_list=rating_popularity['popularity'].tolist(),

        genre_rating_labels=genre_rating.index.tolist(),
        genre_rating_values=genre_rating.tolist(),

        runtime_list=runtime_binge['runtime'].tolist(),
        binge_list=runtime_binge['binge_score'].tolist(),

        corr_labels=corr_matrix.columns.tolist(),
        corr_values=corr_matrix.values.tolist(),

        rating_bins=rating_bins,
        rating_counts=rating_counts,

        insights=insights,

        # 🔥 NEW VARIABLES
        f_stat=round(f_stat, 3),
        p_value=round(p_value, 5),
        hypothesis_result=hypothesis_result
    )

# -------------------- RUN -------------------- #

if __name__ == '__main__':
    app.run(debug=True)