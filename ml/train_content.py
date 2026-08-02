import logging
import os
import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrainContent")

def train_content_model(
    anime_df: pd.DataFrame | None = None,
    max_features: int = 5000,
    artifacts_dir: str = "ml/artifacts"
) -> tuple[TfidfVectorizer, np.ndarray, dict]:

    os.makedirs(artifacts_dir, exist_ok=True)

    if anime_df is None:
        logger.info("No anime_df provided, generating mock anime metadata for content model.")
        anime_df = pd.DataFrame({
            "mal_id": [1, 2, 3, 4, 5],
            "title": ["Cowboy Bebop", "Trigun", "Evangelion", "Naruto", "One Piece"],
            "type": ["TV", "TV", "TV", "TV", "TV"],
            "source": ["Original", "Manga", "Original", "Manga", "Manga"],
            "synopsis": [
                "Bounty hunters in space chasing criminals in a futuristic noir setting.",
                "Vash the Stampede is a legendary gunman with a huge bounty on his head.",
                "Teenage pilots command giant bio-mecha units against mysterious alien Angels.",
                "A young ninja seeks recognition from his village and dreams of becoming the Hokage.",
                "Monkey D. Luffy searches for the ultimate treasure to become King of the Pirates."
            ],
            "genres": ["Action Sci-Fi Space", "Action Sci-Fi Comedy", "Action Sci-Fi Mecha Psychological", "Action Martial Arts Comedy", "Action Adventure Fantasy Comedy"],
            "studios": ["Sunrise", "Madhouse", "Gainax", "Studio Pierrot", "Toei Animation"]
        })

    # Construct combined content feature text
    anime_df["content_text"] = (
        anime_df["synopsis"].fillna("") + " " +
        anime_df["genres"].fillna("") + " " +
        anime_df["studios"].fillna("") + " " +
        anime_df["type"].fillna("") + " " +
        anime_df["source"].fillna("")
    )

    tfidf = TfidfVectorizer(max_features=max_features, stop_words="english")
    tfidf_matrix = tfidf.fit_transform(anime_df["content_text"])

    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    anime_ids = anime_df["mal_id"].values
    anime2idx = {aid: i for i, aid in enumerate(anime_ids)}
    idx2anime = {i: aid for aid, i in anime2idx.items()}

    content_artifacts = {
        "tfidf": tfidf,
        "cosine_sim": cosine_sim,
        "anime2idx": anime2idx,
        "idx2anime": idx2anime,
        "anime_df": anime_df[["mal_id", "title", "genres", "studios"]]
    }

    artifact_path = os.path.join(artifacts_dir, "content_model.pkl")
    with open(artifact_path, "wb") as f:
        pickle.dump(content_artifacts, f)

    logger.info(f"TF-IDF content model trained on {len(anime_ids)} items and saved to {artifact_path}")
    return tfidf, cosine_sim, content_artifacts

if __name__ == "__main__":
    train_content_model()
