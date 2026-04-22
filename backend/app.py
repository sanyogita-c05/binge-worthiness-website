from flask import Flask, render_template, request
import pandas as pd
import os
import random

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

# -------------------- RUN -------------------- #

if __name__ == '__main__':
    app.run(debug=True)