from flask import Flask, request

import os

STASH_SCHEME = os.getenv("STASH_SCHEME", "http")
STASH_HOST = os.getenv("STASH_HOST", "localhost")
STASH_PORT = int(os.getenv("STASH_PORT", 9999))
STASH_API_KEY = os.getenv("STASH_API_KEY", None)
IGNORED_TAGS = [
    int(x.strip())
    for x in os.getenv("IGNORED_TAGS", "").split(",")
    if x.strip().isdigit()
]

app = Flask(__name__)


@app.route("/recommend/<int:scene_id>")
def recommend(scene_id):
    num = int(request.args.get("num", 25))
    print(f"Getting {num} recommendations for scene {scene_id}")

    from sceneRecommender.recommender import get_recommendations
    from stashapi.stashapp import StashInterface

    conn = {
        "scheme": STASH_SCHEME,
        "host": STASH_HOST,
        "Port": STASH_PORT,
        "apiKey": STASH_API_KEY,
    }
    stash = StashInterface(conn)
    results = get_recommendations(stash, scene_id, IGNORED_TAGS, num)
    return {"recommendations": results}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
