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


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


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

        return render_template(
            'result.html',
            title=movie['title'],
            score=round(movie['binge_score'], 2),
            category=movie['binge_category']
        )
    else:
        return render_template(
            'result.html',
            title="Not Found",
            score="N/A",
            category="Try another movie"
        )


# -------------------- RUN -------------------- #

if __name__ == '__main__':
    app.run(debug=True)