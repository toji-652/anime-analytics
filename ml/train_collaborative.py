import logging
import os
import pickle

import implicit
import mlflow
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TrainCollaborative")

def train_als_model(
    ratings_df: pd.DataFrame | None = None,
    factors: int = 64,
    regularization: float = 0.05,
    iterations: int = 15,
    artifacts_dir: str = "ml/artifacts"
) -> tuple[implicit.als.AlternatingLeastSquares, dict]:

    os.makedirs(artifacts_dir, exist_ok=True)

    if ratings_df is None:
        logger.info("No ratings_df provided, generating mock interaction data for training pipeline.")
        ratings_df = pd.DataFrame({
            "user_id": np.random.randint(1, 100, 500),
            "anime_id": np.random.randint(1, 50, 500),
            "score": np.random.randint(1, 11, 500)
        })

    # Encode IDs to contiguous indices
    user_ids = ratings_df["user_id"].unique()
    anime_ids = ratings_df["anime_id"].unique()

    user2idx = {uid: i for i, uid in enumerate(user_ids)}
    anime2idx = {aid: i for i, aid in enumerate(anime_ids)}
    idx2anime = {i: aid for aid, i in anime2idx.items()}

    rows = ratings_df["user_id"].map(user2idx).values
    cols = ratings_df["anime_id"].map(anime2idx).values
    data = ratings_df["score"].values.astype(np.float32)

    user_anime_matrix = csr_matrix((data, (rows, cols)), shape=(len(user_ids), len(anime_ids)))

    # Start MLflow run if configured
    try:
        mlflow.start_run(run_name="als_collaborative_filtering")
        mlflow.log_params({
            "factors": factors,
            "regularization": regularization,
            "iterations": iterations,
            "num_users": len(user_ids),
            "num_items": len(anime_ids)
        })
    except Exception as e:
        logger.warning(f"MLflow logging bypassed ({e})")

    # Fit ALS model
    model = implicit.als.AlternatingLeastSquares(
        factors=factors,
        regularization=regularization,
        iterations=iterations,
        random_state=42
    )
    # implicit expects item x user matrix for training
    model.fit(user_anime_matrix.T)

    mappings = {
        "user2idx": user2idx,
        "anime2idx": anime2idx,
        "idx2anime": idx2anime
    }

    # Save artifacts
    model_path = os.path.join(artifacts_dir, "als_model.pkl")
    mappings_path = os.path.join(artifacts_dir, "als_mappings.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(mappings_path, "wb") as f:
        pickle.dump(mappings, f)

    try:
        mlflow.log_artifact(model_path)
        mlflow.end_run()
    except Exception:
        pass

    logger.info(f"ALS collaborative model trained and saved to {model_path}")
    return model, mappings

if __name__ == "__main__":
    train_als_model()
