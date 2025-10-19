# compute_similarity.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.spatial.distance import cdist
import seaborn as sns

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv('backend/combined_normalized_data.csv')

print(f"Loaded {len(df)} frames")
print(f"Unique IDs: {df['id'].unique()}")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_sequence(df, shot_id):
    """Extract keypoint sequence for a given shot."""
    shot_df = df[df['id'].astype(str) == str(shot_id)].sort_values('frame_count').reset_index(drop=True)
    if shot_df.empty:
        available = ','.join(map(str, sorted(df['id'].unique(), key=lambda x: str(x))))
        raise ValueError(f"No frames found for id={shot_id}. Available ids: {available}")
    kpt_cols = [col for col in df.columns if col.startswith('kpt_')]
    return shot_df[kpt_cols].values


def calculate_angle(p1, p2, p3):
    """Calculate angle at p2 formed by p1-p2-p3."""
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
    v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0
    
    cos_angle = np.dot(v1, v2) / (norm1 * norm2)
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    return np.degrees(angle)


def analyze_key_poses(df, shot_id):
    """Analyze critical angles and positions during the smash."""
    shot_df = df[df['id'].astype(str) == str(shot_id)].sort_values('frame_count').reset_index(drop=True)
    if shot_df.empty:
        available = ','.join(map(str, sorted(df['id'].unique(), key=lambda x: str(x))))
        raise ValueError(f"No frames found for id={shot_id}. Available ids: {available}")
    
    analysis = []
    for idx, row in shot_df.iterrows():
        left_shoulder = (row.get('kpt_11_x', np.nan), row.get('kpt_11_y', np.nan))
        right_shoulder = (row.get('kpt_12_x', np.nan), row.get('kpt_12_y', np.nan))
        left_elbow = (row.get('kpt_13_x', np.nan), row.get('kpt_13_y', np.nan))
        right_elbow = (row.get('kpt_14_x', np.nan), row.get('kpt_14_y', np.nan))
        left_wrist = (row.get('kpt_15_x', np.nan), row.get('kpt_15_y', np.nan))
        right_wrist = (row.get('kpt_16_x', np.nan), row.get('kpt_16_y', np.nan))
        left_hip = (row.get('kpt_23_x', np.nan), row.get('kpt_23_y', np.nan))
        right_hip = (row.get('kpt_24_x', np.nan), row.get('kpt_24_y', np.nan))
        
        right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)
        right_shoulder_angle = calculate_angle(right_hip, right_shoulder, right_elbow)
        wrist_height = right_shoulder[1] - right_wrist[1]
        shoulder_width = abs(right_shoulder[0] - left_shoulder[0])
        hip_width = abs(right_hip[0] - left_hip[0])
        arm_extension = np.sqrt((right_wrist[0] - right_shoulder[0])**2 + (right_wrist[1] - right_shoulder[1])**2)
        
        analysis.append({
            'frame': row['frame_count'],
            'elbow_angle': right_elbow_angle,
            'shoulder_angle': right_shoulder_angle,
            'wrist_height': wrist_height,
            'shoulder_width': shoulder_width,
            'hip_width': hip_width,
            'arm_extension': arm_extension
        })
    
    return pd.DataFrame(analysis)


def compare_motion_sequences(user_seq, reference_seq):
    """Compare two motion sequences using Dynamic Time Warping (DTW)."""
    n, m = len(user_seq), len(reference_seq)
    dtw_matrix = np.full((n + 1, m + 1), np.inf)
    dtw_matrix[0, 0] = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = euclidean(user_seq[i-1], reference_seq[j-1])
            dtw_matrix[i, j] = cost + min(
                dtw_matrix[i-1, j],    
                dtw_matrix[i, j-1],    
                dtw_matrix[i-1, j-1]   
            )
    
    distance = dtw_matrix[n, m]
    
    path = []
    i, j = n, m
    while i > 0 and j > 0:
        path.append((i-1, j-1))
        candidates = [
            (dtw_matrix[i-1, j], i-1, j),
            (dtw_matrix[i, j-1], i, j-1),
            (dtw_matrix[i-1, j-1], i-1, j-1)
        ]
        _, i, j = min(candidates)
    
    path.reverse()
    return distance, path


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    # Extract sequences
    user_seq = get_sequence(df, 'user_video')

    # Read the CSV
    df = pd.read_csv("backend/form_scores.csv")

    # Get the first column name (if you don’t know it)
    first_col = df.columns[0]

    # Get rows 3, 4, 5 (remember: Python is 0-indexed, so these are index 2, 3, 4)
    values = df.loc[2:4, first_col].values
    print(values)

    df = pd.read_csv('backend/combined_normalized_data.csv')

    ref_114_seq = get_sequence(df, values[0])
    ref_135_seq = get_sequence(df, values[1])
    ref_148_seq = get_sequence(df, values[2])

    dist_114, path_114 = compare_motion_sequences(user_seq, ref_114_seq)
    dist_135, path_135 = compare_motion_sequences(user_seq, ref_135_seq)
    dist_148, path_148 = compare_motion_sequences(user_seq, ref_148_seq)

    print("DTW DISTANCE ANALYSIS")
    print("=" * 60)
    print(f"Distance to Shot {values[0]}: {dist_114:.4f}")
    print(f"Distance to Shot {values[1]}: {dist_135:.4f}")
    print(f"Distance to Shot {values[2]}: {dist_148:.4f}")

    best_ref_id = min([(dist_114, values[0]), (dist_135, values[1]), (dist_148, values[2])])[1]
    print(f"\nBest matching reference: Shot {best_ref_id}")

    # Key pose analysis
    user_analysis = analyze_key_poses(df, 'user_video')
    ref_114_analysis = analyze_key_poses(df, values[0])
    ref_135_analysis = analyze_key_poses(df, values[1])
    ref_148_analysis = analyze_key_poses(df, values[2])

    best_ref_analysis = {values[0]: ref_114_analysis, values[1]: ref_135_analysis, values[2]: ref_148_analysis}[best_ref_id]

    # Identify impact frames
    user_impact_idx = user_analysis['wrist_height'].idxmin()
    ref_impact_idx = best_ref_analysis['wrist_height'].idxmin()
    user_impact = user_analysis.iloc[user_impact_idx]
    ref_impact = best_ref_analysis.iloc[ref_impact_idx]

    print("IMPACT POINT ANALYSIS")
    print("=" * 60)
    print(f"User impact at frame: {user_impact['frame']}")
    print(f"Reference impact at frame: {ref_impact['frame']}")

    # Feedback generation
    def generate_detailed_feedback(user_analysis, ref_analysis, user_impact, ref_impact, threshold=15):
        feedback = []
        feedback.append("\n" + "="*60)
        feedback.append("BADMINTON SMASH FORM ANALYSIS")
        feedback.append("="*60)
        
        # Elbow angle
        elbow_diff = user_impact['elbow_angle'] - ref_impact['elbow_angle']
        feedback.append(f"\n📐 ELBOW ANGLE AT IMPACT:")
        feedback.append(f"   Your angle: {user_impact['elbow_angle']:.1f}°")
        feedback.append(f"   Reference: {ref_impact['elbow_angle']:.1f}°")
        feedback.append(f"   Difference: {elbow_diff:+.1f}°")
        
        if abs(elbow_diff) > threshold:
            if elbow_diff > 0:
                feedback.append("   ⚠️  Your elbow is too straight. Bend your elbow more for power.")
            else:
                feedback.append("   ⚠️  Your elbow is too bent. Extend more at contact for reach.")
        else:
            feedback.append("   ✅ Excellent elbow angle!")
        
        # Shoulder angle
        shoulder_diff = user_impact['shoulder_angle'] - ref_impact['shoulder_angle']
        feedback.append(f"\n💪 SHOULDER ANGLE AT IMPACT:")
        feedback.append(f"   Your angle: {user_impact['shoulder_angle']:.1f}°")
        feedback.append(f"   Reference: {ref_impact['shoulder_angle']:.1f}°")
        feedback.append(f"   Difference: {shoulder_diff:+.1f}°")
        
        if abs(shoulder_diff) > threshold:
            if shoulder_diff > 0:
                feedback.append("   ⚠️  Over-rotation detected.")
            else:
                feedback.append("   ⚠️  Rotate your torso more into the shot for core power.")
        else:
            feedback.append("   ✅ Good shoulder rotation!")
        
        # Contact point height
        height_diff = user_impact['wrist_height'] - ref_impact['wrist_height']
        feedback.append(f"\n🎯 CONTACT POINT HEIGHT:")
        feedback.append(f"   Your height: {user_impact['wrist_height']:.3f}")
        feedback.append(f"   Reference: {ref_impact['wrist_height']:.3f}")
        feedback.append(f"   Difference: {height_diff:+.3f}")
        
        if abs(height_diff) > 0.05:
            if height_diff > 0:
                feedback.append("   ⚠️  Contact too low — jump higher or time earlier.")
            else:
                feedback.append("   ⚠️  Contact too high — ensure optimal height for power.")
        else:
            feedback.append("   ✅ Excellent contact height!")
        
        # Arm extension
        extension_diff = user_impact['arm_extension'] - ref_impact['arm_extension']
        feedback.append(f"\n🏹 ARM EXTENSION AT IMPACT:")
        feedback.append(f"   Your extension: {user_impact['arm_extension']:.3f}")
        feedback.append(f"   Reference: {ref_impact['arm_extension']:.3f}")
        feedback.append(f"   Difference: {extension_diff:+.3f}")
        
        if abs(extension_diff) > 0.05:
            if extension_diff < 0:
                feedback.append("   ⚠️  Reach higher for full extension.")
            else:
                feedback.append("   ⚠️  Over-extension detected — maintain control.")
        else:
            feedback.append("   ✅ Good arm extension!")
        
        # Overall score
        score = 100
        if abs(elbow_diff) > threshold: score -= 20
        if abs(shoulder_diff) > threshold: score -= 20
        if abs(height_diff) > 0.05: score -= 20
        if abs(extension_diff) > 0.05: score -= 15
        
        feedback.append(f"\n⭐ OVERALL FORM SCORE: {score}/100")
        
        if score >= 90:
            feedback.append("   🏆 Excellent form!")
        elif score >= 70:
            feedback.append("   👍 Good form with minor improvements needed.")
        elif score >= 50:
            feedback.append("   📈 Decent form but multiple areas need work.")
        else:
            feedback.append("   💪 Keep practicing!")
        
        with open('backend/output.txt', 'w', encoding='utf-8') as f:
            f.write("\n".join(feedback))
        return "\n".join(feedback)

    feedback = generate_detailed_feedback(user_analysis, best_ref_analysis, user_impact, ref_impact)
    print(feedback)

if __name__ == "__main__":
    main()