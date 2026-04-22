import pandas as pd
import requests
import time

API_KEY = "8d0dd7c97774d0c8c654a1716b07847c"

df = pd.read_csv("backend/data/binge_dataset_final.csv")

runtime_col = []
episodes_col = []
total_watch_col = []

for _, row in df.iterrows():
    title = row['title']
    content_type = row['type']

    try:
        search_url = f"https://api.themoviedb.org/3/search/{content_type}?api_key={API_KEY}&query={title}"
        res = requests.get(search_url).json()

        if res['results']:
            tmdb_id = res['results'][0]['id']

            details_url = f"https://api.themoviedb.org/3/{content_type}/{tmdb_id}?api_key={API_KEY}"
            details = requests.get(details_url).json()

            if content_type == "movie":
                runtime = details.get("runtime", 120)
                episodes = 1
            else:
                ep_runtime = details.get("episode_run_time", [45])
                runtime = ep_runtime[0] if ep_runtime else 45
                episodes = details.get("number_of_episodes", 10)
        else:
            runtime = 120 if content_type == "movie" else 45
            episodes = 1 if content_type == "movie" else 10

    except:
        runtime = 120 if content_type == "movie" else 45
        episodes = 1 if content_type == "movie" else 10

    total_watch = round((runtime * episodes) / 60, 2)

    runtime_col.append(runtime)
    episodes_col.append(episodes)
    total_watch_col.append(total_watch)

    print("Done:", title)
    time.sleep(0.2)

df["runtime"] = runtime_col
df["episodes"] = episodes_col
df["total_watch_time"] = total_watch_col

df.to_csv("backend/data/binge_dataset_updated.csv", index=False)

print("✅ New dataset created!")