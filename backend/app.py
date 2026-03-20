from flask import Flask, render_template, request
import pandas as pd
import os

# Tell Flask where frontend files are
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)

# Load dataset
data_path = os.path.join(os.path.dirname(__file__), "data", "binge_dataset_final.csv")
df = pd.read_csv(data_path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.form['movie'].lower()
    mood = request.form['mood']
    time_available = float(request.form['time'])

    result = df[df['title'].str.lower().str.contains(user_input)]

    if not result.empty:
        movie = result.iloc[0]

        base_score = movie['binge_score']

        # ---------------- PERSONALIZATION ---------------- #

        # Mood boost
        genre = str(movie['genres'])

        mood_bonus = 0
        if mood.lower() in genre.lower():
            mood_bonus = 10

        # Time adjustment
        time_bonus = 0
        if time_available >= 3:
            time_bonus = 5
        elif time_available < 2:
            time_bonus = -5

        personalized_score = base_score + mood_bonus + time_bonus

        # Clamp score between 0–100
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
            category
            ="Try another movie"
        )

@app.route('/binge')
def binge():
    return render_template('binge.html')

@app.route('/personalized')
def personalized():
    return render_template('personalized.html')

@app.route('/time')
def time_calc():
    return render_template('time.html')

@app.route('/mood')
def mood():
    return render_template('mood.html')

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/trending')
def trending():
    return render_template('trending.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')


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

if __name__ == '__main__':
    app.run(debug=True)