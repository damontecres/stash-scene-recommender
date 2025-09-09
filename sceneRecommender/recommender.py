import math
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

batch_size = 10000


def fetch(stash, query):
    result = []
    offset = 0
    while True:
        batch = stash.sql_query(query, [offset])["rows"]
        if not batch:
            break
        result.extend(batch)
        offset += batch_size
    return result


def get_recommendations(stash, scene_id, ignored_tags, num=25):
    scenes_df = pd.DataFrame(
        fetch(
            stash,
            f"SELECT id, title, rating, studio_id, director from scenes LIMIT {batch_size} OFFSET ?",
        ),
        columns=["scene_id", "title", "rating", "studio_id", "director"],
    )
    scenes_tags_df = pd.DataFrame(
        fetch(
            stash,
            f"SELECT scene_id, tag_id FROM scenes_tags LIMIT {batch_size} OFFSET ?",
        ),
        columns=["scene_id", "tag_id"],
    )
    scenes_performers_df = pd.DataFrame(
        fetch(
            stash,
            f"SELECT scene_id, performer_id FROM performers_scenes LIMIT {batch_size} OFFSET ?",
        ),
        columns=["scene_id", "performer_id"],
    )

    if ignored_tags:
        scenes_tags_df = scenes_tags_df[~scenes_tags_df["tag_id"].isin(ignored_tags)]

    scenes_tags_df["tag_id"] = scenes_tags_df["tag_id"].apply(lambda x: "tag_" + str(x))
    scene_tags = (
        scenes_tags_df.groupby("scene_id")["tag_id"].apply(", ".join).reset_index()
    )

    scenes_performers_df["performer_id"] = scenes_performers_df["performer_id"].apply(
        lambda x: "per_" + str(x)
    )
    scenes_performers_df = (
        scenes_performers_df.groupby("scene_id")["performer_id"]
        .apply(", ".join)
        .reset_index()
    )

    scenes_df = pd.merge(scenes_df, scene_tags, on="scene_id", how="left")
    scenes_df = pd.merge(scenes_df, scenes_performers_df, on="scene_id", how="left")

    # Clean data
    scenes_df["director"] = (
        scenes_df["director"].fillna("").apply(lambda x: x.replace(" ", "_"))
    )
    # scenes_df = scenes_df.fillna("")
    scenes_df["studio_id"] = scenes_df["studio_id"].apply(
        lambda x: "studio_" + str(int(x)) if not math.isnan(x) else ""
    )
    # scenes = scenes[scenes["title"] != '']
    # scenes_df = scenes_df[scenes_df["tag_id"] != '']
    # scenes_df = scenes_df[scenes_df["performer_id"] != '']
    scenes_df["content"] = (
        scenes_df["director"].astype(str)
        + " "
        + scenes_df["studio_id"]
        + " "
        + scenes_df["tag_id"]
        + " "
        + scenes_df["performer_id"]
    )
    scenes_df.dropna(subset=["content"], inplace=True)
    scenes_df = scenes_df.reset_index()

    vectorizer = TfidfVectorizer(max_df=0.66)
    tfidf = vectorizer.fit_transform(scenes_df["content"])
    n_components = min(100, tfidf.shape[1] - 1)
    lsa = TruncatedSVD(n_components=n_components, algorithm="arpack")
    lsa.fit(tfidf)

    index = scenes_df[scenes_df["scene_id"] == scene_id].index[0]

    similarity_scores = cosine_similarity(tfidf[index], tfidf)
    similar_scenes = list(enumerate(similarity_scores[0]))
    sorted_similar_scenes = sorted(similar_scenes, key=lambda x: x[1], reverse=True)[
        1 : num + 1
    ]

    results = []
    for i, score in sorted_similar_scenes:
        title = scenes_df.loc[i, "title"]
        scene_id = scenes_df.loc[i, "scene_id"]
        if score > 0:
            results.append(
                {"scene_id": int(scene_id), "title": title, "score": float(score)}
            )
    return results
