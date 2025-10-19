# pose_backend.py
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Indices for right shoulder, left shoulder, etc.
KEYPOINT_INDICES = [12, 11, 14, 13, 16, 15, 24, 23]

def extract_keypoints(video_path='uploads/smash_video_example.mp4', output_csv='user_keypoints_selected.csv'):
    print(f"Opening video: {video_path}")
    
    # Check if video file exists
    import os
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found at {video_path}")
        return None
    
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    
    # LOWER the confidence thresholds to detect more poses
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # Try different complexities: 0, 1, or 2
        min_detection_confidence=0.3,  # Lowered from 0.5
        min_tracking_confidence=0.3    # Lowered from 0.5
    )
    
    cap = cv2.VideoCapture(video_path)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print(f"ERROR: Could not open video {video_path}")
        return None
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    print(f"Video properties:")
    print(f"  Total frames: {total_frames}")
    print(f"  FPS: {fps}")
    print(f"  Resolution: {width}x{height}")
    
    keypoints_data = []
    frame_count = 0
    frames_processed = 0
    frames_with_pose = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        frames_processed += 1
        
        # Convert to RGB (MediaPipe requires RGB)
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Set image to writeable false to improve performance
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        
        if results.pose_landmarks:
            frames_with_pose += 1
            landmarks = results.pose_landmarks.landmark
            keypoints = []
            
            # Check if all required keypoints are visible
            all_visible = True
            for idx in KEYPOINT_INDICES:
                lm = landmarks[idx]
                # Check visibility score
                if hasattr(lm, 'visibility') and lm.visibility < 0.5:
                    all_visible = False
                    break
                keypoints.extend([lm.x, lm.y])
            
            # Only add if all keypoints are reasonably visible
            if all_visible:
                keypoints_data.append([frame_count] + keypoints)
            
            # Draw landmarks on frame
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            mp_drawing.draw_landmarks(
                image_bgr, 
                results.pose_landmarks, 
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
            
            # Show detection status
            cv2.putText(image_bgr, f"Pose Detected: Frame {frame_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Pose Detection', image_bgr)
        else:
            # Show no detection
            cv2.putText(frame, f"No Pose Detected: Frame {frame_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Pose Detection', frame)
        
        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            print("Interrupted by user")
            break
        
        frame_count += 1
        
        # Print progress every 30 frames
        if frame_count % 30 == 0:
            print(f"Processed {frame_count}/{total_frames} frames, detected pose in {frames_with_pose} frames")
    
    cap.release()
    cv2.destroyAllWindows()
    pose.close()
    
    print(f"\n=== EXTRACTION SUMMARY ===")
    print(f"Total frames processed: {frames_processed}")
    print(f"Frames with pose detected: {frames_with_pose}")
    print(f"Frames with all keypoints visible: {len(keypoints_data)}")
    
    if len(keypoints_data) == 0:
        print("\nERROR: No valid pose data extracted!")
        print("Possible issues:")
        print("  1. Person not fully visible in frame")
        print("  2. Video quality too low")
        print("  3. Lighting conditions poor")
        print("  4. Person too far from camera")
        print("  5. Video format/codec issues")
        return None
    
    # Build DataFrame and save CSV
    columns = ['frame_count'] + [f'kpt_{i}_{axis}' for i in KEYPOINT_INDICES for axis in ['x', 'y']]
    df_user = pd.DataFrame(keypoints_data, columns=columns)
    df_user.insert(0, 'id', 'user_video')
    df_user.insert(1, 'type_of_shot', 'smash')
    
    df_user.to_csv(output_csv, index=False)
    print(f"\n✅ Saved keypoints to {output_csv} with {len(df_user)} frames")
    print(f"First few rows:")
    print(df_user.head())
    return output_csv


def create_gif(csv_path='backend/user_keypoints_selected.csv'):
    df = pd.read_csv(csv_path)
    
    print(f"\nLoaded CSV with {len(df)} rows")
    print(f"Columns: {list(df.columns)}")
    
    if 'type_of_shot' in df.columns:
        df = df.drop('type_of_shot', axis=1)
    
    shot_id = 'user_video'
    shot_df = df[df['id'] == shot_id].reset_index(drop=True)
    
    # Check if we have any data
    if len(shot_df) == 0:
        print(f"ERROR: No frames found for shot_id '{shot_id}'")
        print(f"Available IDs: {df['id'].unique()}")
        return None
    
    print(f"Creating GIF with {len(shot_df)} frames...")
    
    # Skeleton connections
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
    
    fig, ax = plt.subplots(figsize=(6, 8))
    lines = []
    for _ in skeleton:
        line, = ax.plot([], [], 'ro-', markersize=5, linewidth=2)
        lines.append(line)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.invert_yaxis()
    ax.set_title(f"Skeleton Animation - Shot {shot_id}")
    ax.set_aspect('equal')
    
    def update(frame):
        row = shot_df.iloc[frame]
        keypoints = {}
        for kpt in KEYPOINT_INDICES:
            # Transform coordinates: rotate 90° counterclockwise
            keypoints[kpt] = (1 - row[f'kpt_{kpt}_y'], row[f'kpt_{kpt}_x'])
        
        for idx, (a,b) in enumerate(skeleton):
            if keypoints[a][0] != 0 and keypoints[a][1] != 0 and keypoints[b][0] != 0 and keypoints[b][1] != 0:
                lines[idx].set_data([keypoints[a][0], keypoints[b][0]],
                                    [keypoints[a][1], keypoints[b][1]])
            else:
                lines[idx].set_data([], [])
        return lines
    
    anim = FuncAnimation(fig, update, frames=len(shot_df), interval=100, blit=False)
    os.makedirs('static', exist_ok=True)
    gif_filename = f'static/badminton_shot_{shot_id}.gif'
    
    try:
        print("Saving animation...")
        anim.save(gif_filename, writer='pillow', fps=15)
        print(f"✅ Saved animation to {gif_filename}")
        plt.close()
        return gif_filename
    except Exception as e:
        print(f"ERROR saving GIF: {e}")
        import traceback
        traceback.print_exc()
        plt.close()
        return None


if __name__ == "__main__":
    # OPTION 1: Use absolute path
    video_path = r'C:\Users\kotha\Downloads\CCI-HACKATHON\backend\uploads\smash_video_example.mp4'
    
    # OPTION 2: Or use relative path from where you're running the script
    # video_path = '../smash_video_example.mp4'  # if video is one folder up
    # video_path = './videos/smash_video_example.mp4'  # if video is in a 'videos' subfolder
    
    # Check if file exists before processing
    import os
    if not os.path.exists(video_path):
        print(f"ERROR: Cannot find video at: {video_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in current directory: {os.listdir('.')}")
        
        # Try to find the video file
        print("\nSearching for .mp4 files...")
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.mp4'):
                    print(f"Found: {os.path.join(root, file)}")
    else:
        csv_file = extract_keypoints(video_path)
        
        if csv_file:
            print(f"\n✅ CSV file created: {csv_file}")
            gif_file = create_gif(csv_file)
            if gif_file:
                print(f"\n✅ GIF created successfully: {gif_file}")
            else:
                print("\n❌ Failed to create GIF")
        else:
            print("\n❌ Failed to extract keypoints")