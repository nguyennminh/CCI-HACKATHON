# normalize_data.py
"""
Badminton Keypoint Normalization and Remapping
----------------------------------------------
This script normalizes training data (keypoint coordinates) and remaps indices
to match the testing data format for AI model consistency.

Outputs:
- training_data_normalized.csv
- combined_normalized_data.csv
"""

import os
import pandas as pd
import numpy as np


def normalize_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize pixel coordinates to the 0-1 range for each video.

    Args:
        df (pd.DataFrame): Input DataFrame with keypoint coordinates.

    Returns:
        pd.DataFrame: Normalized DataFrame.
    """
    df_normalized = df.copy()
    
    # Identify x and y coordinate columns
    x_cols = [col for col in df.columns if col.startswith('kpt_') and col.endswith('_x')]
    y_cols = [col for col in df.columns if col.startswith('kpt_') and col.endswith('_y')]
    
    for video_id in df['id'].unique():
        mask = df_normalized['id'] == video_id
        
        # Extract non-zero coordinate values
        x_values = df_normalized.loc[mask, x_cols].values.flatten()
        y_values = df_normalized.loc[mask, y_cols].values.flatten()
        
        x_values = x_values[x_values > 0]
        y_values = y_values[y_values > 0]
        
        if len(x_values) > 0 and len(y_values) > 0:
            max_x = x_values.max()
            max_y = y_values.max()
            
            # Normalize all keypoint columns
            for col in x_cols:
                df_normalized.loc[mask, col] /= max_x
            for col in y_cols:
                df_normalized.loc[mask, col] /= max_y
    
    return df_normalized


def remap_keypoints(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Remap keypoint indices from training format to testing format.

    Args:
        df (pd.DataFrame): Normalized DataFrame.
        mapping (dict): Dictionary mapping old keypoint indices to new ones.

    Returns:
        pd.DataFrame: Remapped DataFrame.
    """
    df_remapped = pd.DataFrame({
        'id': df['id'],
        'frame_count': df['frame_count']
    })
    
    for old_idx, new_idx in sorted(mapping.items(), key=lambda x: x[1]):
        old_x_col = f'kpt_{old_idx}_x'
        old_y_col = f'kpt_{old_idx}_y'
        new_x_col = f'kpt_{new_idx}_x'
        new_y_col = f'kpt_{new_idx}_y'
        
        if old_x_col in df.columns and old_y_col in df.columns:
            df_remapped[new_x_col] = df[old_x_col]
            df_remapped[new_y_col] = df[old_y_col]
    
    return df_remapped


def verify_data_ranges(df: pd.DataFrame, label: str):
    """
    Print summary of value ranges for all keypoints.
    """
    print("\n" + "=" * 50)
    print(f"{label} VALUE RANGES")
    for col in df.columns:
        if col.startswith('kpt_'):
            print(f"{col}: {df[col].min():.4f} to {df[col].max():.4f}")


def process_datasets(train_path: str, test_path: str):
    """
    Normalize and remap training data, then align with testing data format.
    Save outputs to CSV for model training.

    Args:
        train_path (str): Path to training dataset CSV.
        test_path (str): Path to testing dataset CSV.
    """
    print("Loading training data...")
    df_train = pd.read_csv(train_path)

    print("Normalizing coordinates...")
    df_train_normalized = normalize_coordinates(df_train)

    keypoint_mapping = {
        5: 11,  # left_shoulder
        6: 12,  # right_shoulder
        7: 13,  # left_elbow
        8: 14,  # right_elbow
        9: 15,  # left_wrist
        10: 16, # right_wrist
        11: 23, # left_hip
        12: 24  # right_hip
    }

    print("Remapping keypoints to match testing data format...")
    df_train_final = remap_keypoints(df_train_normalized, keypoint_mapping)
    df_train_final.to_csv('backend/training_data_normalized.csv', index=False)
    print("✅ Saved normalized training data to 'training_data_normalized.csv'")

    print("Loading testing data...")
    df_test = pd.read_csv(test_path)

    # Display verification info
    print("\nTraining Data Preview:")
    print(df_train_final.head())
    print(f"Shape: {df_train_final.shape}")

    print("\nTesting Data Preview:")
    print(df_test.head())
    print(f"Shape: {df_test.shape}")

    verify_data_ranges(df_train_final, "TRAINING")
    verify_data_ranges(df_test, "TESTING")

    # Optional: Combine datasets for ML
    df_train_final['type_of_shot'] = 'smash'
    df_test['type_of_shot'] = 'user_input'

    common_cols = ['id', 'type_of_shot', 'frame_count'] + [col for col in df_train_final.columns if col.startswith('kpt_')]
    df_train_final = df_train_final[common_cols]
    df_test = df_test[common_cols]

    df_combined = pd.concat([df_train_final, df_test], ignore_index=True)
    df_combined.to_csv('backend/combined_normalized_data.csv', index=False)

    print("\n" + "="*50)
    print(f"✅ Combined dataset saved to 'combined_normalized_data.csv'")
    print(f"Training frames: {len(df_train_final)}")
    print(f"Testing frames: {len(df_test)}")
    print(f"Total frames: {len(df_combined)}")


if __name__ == "__main__":
    # Example file paths (edit as needed)
    TRAIN_PATH = "backend\clean_smash_dataset.csv"
    TEST_PATH = "backend\user_keypoints_selected.csv"
    process_datasets(TRAIN_PATH, TEST_PATH)
