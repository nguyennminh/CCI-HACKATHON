import pandas as pd
import numpy as np

# Load training data
df_train = pd.read_csv('clean_smash_dataset.csv')

# Step 1: Normalize pixel coordinates to 0-1 range for training data
# First, we need to find the video dimensions or use the max values
def normalize_coordinates(df):
    """Normalize pixel coordinates to 0-1 range"""
    df_normalized = df.copy()
    
    # Get all x and y columns
    x_cols = [col for col in df.columns if col.endswith('_x') and col.startswith('kpt_')]
    y_cols = [col for col in df.columns if col.endswith('_y') and col.startswith('kpt_')]
    
    # Find max values for normalization (per video if needed)
    for video_id in df['id'].unique():
        mask = df_normalized['id'] == video_id
        
        # Get non-zero values to find actual frame dimensions
        x_values = df_normalized.loc[mask, x_cols].values.flatten()
        y_values = df_normalized.loc[mask, y_cols].values.flatten()
        
        x_values = x_values[x_values > 0]
        y_values = y_values[y_values > 0]
        
        if len(x_values) > 0 and len(y_values) > 0:
            max_x = x_values.max()
            max_y = y_values.max()
            
            # Normalize
            for col in x_cols:
                df_normalized.loc[mask, col] = df_normalized.loc[mask, col] / max_x
            for col in y_cols:
                df_normalized.loc[mask, col] = df_normalized.loc[mask, col] / max_y
    
    return df_normalized

# Normalize training data
df_train_normalized = normalize_coordinates(df_train)

# Step 2: Remap keypoint indices to match testing data format
# Training uses: 5,6,7,8,9,10,11,12 -> Testing uses: 11,12,13,14,15,16,23,24
keypoint_mapping = {
    5: 11,   # left_shoulder
    6: 12,   # right_shoulder
    7: 13,   # left_elbow
    8: 14,   # right_elbow
    9: 15,   # left_wrist
    10: 16,  # right_wrist
    11: 23,  # left_hip
    12: 24   # right_hip
}

def remap_keypoints(df, mapping):
    """Remap keypoint column names to match testing data format"""
    df_remapped = pd.DataFrame()
    
    # Keep id and frame_count
    df_remapped['id'] = df['id']
    df_remapped['frame_count'] = df['frame_count']
    
    # Remap keypoints
    for old_idx, new_idx in sorted(mapping.items(), key=lambda x: x[1]):
        old_x_col = f'kpt_{old_idx}_x'
        old_y_col = f'kpt_{old_idx}_y'
        new_x_col = f'kpt_{new_idx}_x'
        new_y_col = f'kpt_{new_idx}_y'
        
        if old_x_col in df.columns and old_y_col in df.columns:
            df_remapped[new_x_col] = df[old_x_col]
            df_remapped[new_y_col] = df[old_y_col]
    
    return df_remapped

# Remap training data to match testing format
df_train_final = remap_keypoints(df_train_normalized, keypoint_mapping)

# Save normalized and remapped training data
df_train_final.to_csv('training_data_normalized.csv', index=False)

print("Training data normalized and remapped!")
print("\nTraining data sample:")
print(df_train_final.head())
print(f"\nTraining data shape: {df_train_final.shape}")
print(f"Columns: {list(df_train_final.columns)}")

# Load and verify testing data format
df_test = pd.read_csv('user_keypoints_selected.csv')
print("\n" + "="*50)
print("Testing data sample:")
print(df_test.head())
print(f"\nTesting data shape: {df_test.shape}")
print(f"Columns: {list(df_test.columns)}")

# Verify value ranges
print("\n" + "="*50)
print("Training data value ranges:")
for col in df_train_final.columns:
    if col.startswith('kpt_'):
        print(f"{col}: {df_train_final[col].min():.4f} to {df_train_final[col].max():.4f}")

print("\nTesting data value ranges:")
for col in df_test.columns:
    if col.startswith('kpt_'):
        print(f"{col}: {df_test[col].min():.4f} to {df_test[col].max():.4f}")

# Optional: Combine datasets for ML training
# Make sure both have the same columns
df_train_ml = df_train_final.copy()
df_train_ml['type_of_shot'] = 'smash'  # Add if you have this info

df_test_ml = df_test.copy()

# Reorder columns to match
common_cols = ['id', 'type_of_shot', 'frame_count'] + [col for col in df_train_ml.columns if col.startswith('kpt_')]
df_train_ml = df_train_ml[common_cols]
df_test_ml = df_test_ml[common_cols]

# Combine
df_combined = pd.concat([df_train_ml, df_test_ml], ignore_index=True)
df_combined.to_csv('combined_normalized_data.csv', index=False)

print("\n" + "="*50)
print(f"Combined dataset saved with {len(df_combined)} frames")
print(f"Training frames: {len(df_train_ml)}")
print(f"Testing frames: {len(df_test_ml)}")