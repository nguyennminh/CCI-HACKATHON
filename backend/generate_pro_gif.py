import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def main():
    bf = pd.read_csv("backend/form_scores.csv")

    # Get the first column name (if you don’t know it)
    first_col = bf.columns[0]

    # Get rows 3, 4, 5 (remember: Python is 0-indexed, so these are index 2, 3, 4)
    values = bf.loc[2:4, first_col].values
    # Choose which shot id to visualize
    df = pd.read_csv('backend/combined_normalized_data.csv')


    shot_id = values[0]  # e.g., first shot id from the selected rows

    shot_df = df[df['id'] == shot_id].reset_index(drop=True)

    skeleton = [
            (11, 12),
            (11, 13),
            (13, 15),
            (12, 14),
            (14, 16),
            (11, 23),
            (12, 24),
            (23, 24)
        ]

    KEYPOINT_INDICES = [12, 11, 14, 13, 16, 15, 24, 23]

    # Set up the plot
    fig, ax = plt.subplots(figsize=(6,8))
    lines = []
    for _ in skeleton:
        line, = ax.plot([], [], 'ro-', markersize=5)
        lines.append(line)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.invert_yaxis()
    ax.set_title(f"Skeleton Animation - Shot {shot_id}")
    ax.set_aspect('equal')

    # Animation function
    def update(frame):
        row = shot_df.iloc[frame]
        keypoints = {}
        for kpt in KEYPOINT_INDICES:
            # Transform coordinates: rotate 90° counterclockwise
            keypoints[kpt] = (row[f'kpt_{kpt}_x'], row[f'kpt_{kpt}_y'])
        
        for idx, (a,b) in enumerate(skeleton):
            if keypoints[a][0] != 0 and keypoints[a][1] != 0 and keypoints[b][0] != 0 and keypoints[b][1] != 0:
                lines[idx].set_data([keypoints[a][0], keypoints[b][0]],
                                    [keypoints[a][1], keypoints[b][1]])
            else:
                lines[idx].set_data([], [])
        return lines

    # Create animation
    anim = FuncAnimation(fig, update, frames=len(shot_df), interval=200, blit=True)

    # plt.show()

    # Save animation 
    anim.save('static/proshot.gif', writer='pillow',fps=10)

if __name__ == "__main__":
    main()