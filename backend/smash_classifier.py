# smash_classifier.py
"""
Badminton Smash Classifier using DTW Similarity
-----------------------------------------------
This module compares badminton form sequences using Dynamic Time Warping (DTW)
to identify how closely a player's motion matches the ideal smash reference.

Outputs:
- form_scores.csv: List of videos ranked by similarity score (0-1)
"""

import os
import pandas as pd
import numpy as np
from dtaidistance import dtw


def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """
    Load normalized data and preprocess it by handling missing values.

    Args:
        csv_path (str): Path to combined normalized dataset.

    Returns:
        pd.DataFrame: Cleaned and interpolated dataset.
    """
    print(f"📂 Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path)

    if 'type_of_shot' in df.columns:
        df = df.drop('type_of_shot', axis=1)
        print("🔹 Removed 'type_of_shot' column (not needed for classification).")

    # Identify coordinate columns
    coords = [col for col in df.columns if "kpt" in col]

    # Replace zeros with NaN (missing points)
    df[coords] = df[coords].replace(0.0, np.nan)

    # Interpolate missing coordinates frame-by-frame within each video ID
    df[coords] = df.groupby('id')[coords].transform(lambda g: g.interpolate(limit_direction='both'))

    print("✅ Data cleaned and interpolated successfully.")
    return df


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract statistical features (mean, std) per keypoint per shot.

    Args:
        df (pd.DataFrame): Cleaned keypoint data.

    Returns:
        pd.DataFrame: Feature summary per shot.
    """
    print("📊 Extracting features for each shot...")
    coords = [col for col in df.columns if "kpt" in col]
    features = []

    for shot_id, group in df.groupby('id'):
        f = {f"{col}_mean": group[col].mean() for col in coords}
        f.update({f"{col}_std": group[col].std() for col in coords})
        f["shot_id"] = shot_id
        features.append(f)

    features_df = pd.DataFrame(features)
    print(f"✅ Extracted features for {len(features_df)} shots.")
    return features_df


def get_sequence(group: pd.DataFrame, joints=None) -> np.ndarray:
    """
    Convert a group of frames into a flattened sequence of x,y coordinates.

    Args:
        group (pd.DataFrame): Data for one shot/video.
        joints (list[int]): Joint indices to include (default: upper body).

    Returns:
        np.ndarray: Flattened sequence of coordinates.
    """
    if joints is None:
        joints = [12, 11, 14, 13, 16, 15, 24, 23]  # Default upper-body joints

    data = []
    for j in joints:
        data.append(group[f'kpt_{j}_x'].values)
        data.append(group[f'kpt_{j}_y'].values)
    return np.array(data).flatten()


def compute_form_scores(df: pd.DataFrame, ideal_id: str) -> pd.DataFrame:
    """
    Compute DTW-based similarity scores for each shot vs. an ideal reference.

    Args:
        df (pd.DataFrame): Cleaned dataset with keypoints.
        ideal_id (str): The ID of the reference (ideal) shot.

    Returns:
        pd.DataFrame: DataFrame with IDs and similarity scores.
    """
    print(f"⚙️ Computing form similarity scores using DTW...")
    ideal = df[df["id"] == ideal_id]
    ideal_seq = get_sequence(ideal)

    sequences = {shot_id: get_sequence(g) for shot_id, g in df.groupby("id")}

    scores = {}
    for shot_id, seq in sequences.items():
        dist = dtw.distance(seq, ideal_seq)
        scores[shot_id] = 1 / (1 + dist)  # Higher = better match

    score_df = pd.DataFrame(list(scores.items()), columns=["id", "form_score"])
    score_df = score_df.sort_values("form_score", ascending=False)
    print("✅ DTW scoring complete.")
    return score_df


def save_scores(score_df: pd.DataFrame, filename: str = "form_scores.csv"):
    """
    Save similarity scores to a CSV file.

    Args:
        score_df (pd.DataFrame): DataFrame containing shot IDs and scores.
        filename (str): Output CSV filename.
    """
    score_df.to_csv(filename, index=False)
    print(f"📁 Scores saved to {filename}")
    print(score_df.head())


def classify_smash(csv_path: str, ideal_id: str = "user_video") -> pd.DataFrame:
    """
    Full end-to-end process: load data, clean, extract features, compute DTW scores.

    Args:
        csv_path (str): Path to normalized dataset (e.g., combined_normalized_data.csv).
        ideal_id (str): Reference video ID for ideal form.

    Returns:
        pd.DataFrame: Final DataFrame with form similarity scores.
    """
    df = load_and_clean_data(csv_path)
    features_df = extract_features(df)
    score_df = compute_form_scores(df, ideal_id)
    save_scores(score_df)
    return score_df


# Run module directly for testing or pipeline execution
if __name__ == "__main__":
    DATA_PATH = "backend\combined_normalized_data.csv"
    IDEAL_ID = "user_video"  # Replace with your ideal reference ID

    print("🏸 Running Badminton Smash Classifier...\n")
    score_df = classify_smash(DATA_PATH, IDEAL_ID)

    print("\n=== TOP MATCHES ===")
    print(score_df.head())