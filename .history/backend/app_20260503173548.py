from flask import Flask, render_template, request
import pandas as pd
import os
import random
import numpy as np
from statsmodels.tsa.arima.model import ARIMA

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
data_path = os.path.join(os.path.dirname(__file__), "data", "cleaned_binge_dataset.csv")
df = pd.read_csv(data_path)

df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year

def forecast_trend(series):
    if len(series) < 5:
        return []

    model = ARIMA(series, order=(2,0,2))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=3)
    return forecast.tolist()

# -------------------- ROUTES -------------------- #

@app.route('/genre_trend', methods=['GET', 'POST'])
def genre_trend():
    if request.method == 'POST':
        genre = request.form['genre']

        series = get_genre_time_series(genre)

        years = series.index.tolist()
        scores = series.values.tolist()

        # 🔮 Forecast
        forecast = forecast_trend(series)

        # Create future years
        if len(years) > 0:
            last_year = years[-1]
            future_years = [last_year + i for i in range(1, len(forecast)+1)]
        else:
            future_years = []

        return render_template(
            'genre_trend.html',
            genre=genre,
            years=years,
            scores=scores,
            forecast=forecast,
            future_years=future_years
        )

    return render_template('genre_trend.html')

def get_genre_time_series(selected_genre):
    # Expand genres
    genre_df = df.assign(genres=df['genres'].str.split(',')).explode('genres')
    genre_df['genres'] = genre_df['genres'].str.strip().str.lower()

    # Filter selected genre
    genre_df = genre_df[genre_df['genres'] == selected_genre.lower()]

    # Group by year
    yearly = genre_df.groupby('year')['binge_score'].mean().dropna()

    return yearly

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


@app.route('/stage6')
def stage6():
    return render_template('stage6.html')

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

    # ===============================
    # LOAD CLEANED + UNCLEANED DATA
    # ===============================
    cleaned_df = df.copy()

    raw_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_updated.csv")
    raw_df = pd.read_csv(raw_path)

    # ---- BASIC INFO ----
    total_rows, total_cols = cleaned_df.shape
    columns = cleaned_df.columns.tolist()
    sample_data = cleaned_df.head(5).to_dict(orient='records')

    # ===============================
    # 🔴 BEFORE CLEANING
    # ===============================
    missing_before = raw_df.isnull().sum()

    # ===============================
    # 🟢 AFTER CLEANING
    # ===============================
    missing = cleaned_df.isnull().sum()
    duplicates = cleaned_df.duplicated().sum()

    # ---- CLEANING NOTES ----
    cleaning_notes = [
        "Missing values handled using median",
        "Duplicates removed",
        "Genres standardized",
        "Feature normalization applied"
    ]

    # ===============================
    # UNIVARIATE
    # ===============================
    genre_expanded = cleaned_df.assign(
        genres=cleaned_df['genres'].str.split(',')
    ).explode('genres')

    genre_expanded['genres'] = genre_expanded['genres'].str.strip()

    genre_counts = genre_expanded['genres'].value_counts().head(10)

    # Rating bins
    bins = [0, 2, 4, 6, 8, 10]
    hist, bin_edges = np.histogram(cleaned_df['rating'].dropna(), bins=bins)

    rating_bins = [
        f"{int(bin_edges[i])}-{int(bin_edges[i+1])}"
        for i in range(len(bin_edges)-1)
    ]
    rating_counts = hist.tolist()

    # ===============================
    # CORRELATION
    # ===============================
    corr_df = cleaned_df[
        ['rating', 'votes', 'popularity', 'runtime', '']
    ].dropna()

    corr_matrix = corr_df.corr().round(2)

    # ===============================
    # ANOVA
    # ===============================
    genre_groups = genre_expanded.groupby('genres')['binge_score'].apply(list)
    valid_groups = [g for g in genre_groups if len(g) > 5]

    if len(valid_groups) > 1:
        f_stat, p_value = f_oneway(*valid_groups)
    else:
        f_stat, p_value = 0, 1

    alpha = 0.05
    if p_value < alpha:
        hypothesis_result = "Reject Null Hypothesis"
    else:
        hypothesis_result = "Fail to Reject Null Hypothesis"

    # ===============================
    # INSIGHTS
    # ===============================
    insights = [
        f"Dataset contains {total_rows} rows",
        f"Average rating: {round(cleaned_df['rating'].mean(),2)}",
        f"Average binge score: {round(cleaned_df['binge_score'].mean(),2)}",
        f"Most common genre: {genre_counts.index[0]}"
    ]

    return render_template(
        "analysis.html",

        total_rows=total_rows,
        total_cols=total_cols,
        columns=columns,
        sample_data=sample_data,

        # 🔴 BEFORE CLEANING
        missing_before_labels=missing_before.index.tolist(),
        missing_before_values=missing_before.values.tolist(),

        # 🟢 AFTER CLEANING
        missing_labels=missing.index.tolist(),
        missing_values=missing.values.tolist(),
        duplicates=duplicates,
        cleaning_notes=cleaning_notes,

        genre_labels=genre_counts.index.tolist(),
        genre_counts=genre_counts.tolist(),

        corr_labels=corr_matrix.columns.tolist(),
        corr_values=corr_matrix.values.tolist(),

        rating_bins=rating_bins,
        rating_counts=rating_counts,

        insights=insights,

        f_stat=round(f_stat, 3),
        p_value=round(p_value, 5),
        hypothesis_result=hypothesis_result
    )

# -------------------- RUN -------------------- #

if __name__ == '__main__':
    app.run(debug=True)