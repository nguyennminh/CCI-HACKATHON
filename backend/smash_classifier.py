import pandas as pd
import numpy as np
from dtaidistance import dtw


df = pd.read_csv('combined_normalized_data.csv')

# Removing type_of_shot (they're all the same)
df = df.drop('type_of_shot', axis = 1)

df.head()

# Replace zeros with NaN (missing points)
coords = [col for col in df.columns if "kpt" in col]
df[coords] = df[coords].replace(0.0, np.nan)

# Optionally interpolate missing values frame-by-frame
df[coords] = df.groupby('id')[coords].transform(lambda group: group.interpolate(limit_direction='both'))

features = []

for shot_id, group in df.groupby('id'):
    f = {}
    for col in coords:
        f[f'{col}_mean'] = group[col].mean()
        f[f'{col}_std'] = group[col].std()
    f['shot_id'] = shot_id  # Keep track of which shot this is
    features.append(f)

features_df = pd.DataFrame(features)
features_df.head()

ideal_id = 'user_video'  # choose one good sequence
ideal = df[df['id'] == ideal_id]

def get_sequence(group, joints=[12, 11, 14, 13, 16, 15, 24, 23]):  # upper-body joints for smash
    data = []
    for i in joints:
        data.append(group[f'kpt_{i}_x'].values)
        data.append(group[f'kpt_{i}_y'].values)
    return np.array(data).flatten()

sequences = {shot_id: get_sequence(g) for shot_id, g in df.groupby('id')}

ideal_seq = get_sequence(ideal)
scores = {}

for shot_id, seq in sequences.items():
    dist = dtw.distance(seq, ideal_seq)
    scores[shot_id] = 1 / (1 + dist) 

score_df = pd.DataFrame(list(scores.items()), columns=['id', 'form_score'])
score_df = score_df.sort_values('form_score', ascending=False)
print(score_df.head())