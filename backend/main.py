from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import compute_similarity
import extract_input_data
import kronos_ai
import normalize_data
import smash_classifier
import pandas as pd

app = FastAPI()

# Allow frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use your domain in production
    allow_methods=["*"],
    allow_headers=["*"]
)

UPLOAD_FOLDER = "backend/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Home route serving HTML (optional, mainly for testing)
@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """
    <html>
        <body>
            <h2>Upload a Video</h2>
            <form action="/upload" enctype="multipart/form-data" method="post">
                <input type="file" name="video" accept="video/*" required>
                <input type="submit" value="Upload">
            </form>
        </body>
    </html>
    """
    return html_content

# Upload endpoint
@app.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    # Save uploaded video as hello.mp4 (preserve extension)
    ext = os.path.splitext(video.filename)[1] or ".mp4"
    filename = f"smash_video_example{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    # Call your processing function
    process_video(save_path)

    return {"message": f"Video uploaded and saved as {filename}"}

def process_video(path):
    # Placeholder for your MediaPipe/OpenPose logic
    extract_input_data.main()
    normalize_data.main()
    smash_classifier.main()
    compute_similarity.main()
    kronos_ai.main()
    
    '''
    

    #Extract keypoints and create CSV and gif
    extract_input_data.create_gif(extract_input_data.extract_keypoints(path))

    # Normalize data
    
    TEST_PATH = "backend\user_keypoints_selected.csv"
    TRAIN_PATH = "backend\clean_smash_dataset.csv"

    normalize_data.process_datasets(TRAIN_PATH, TEST_PATH)

    # Compute similarity scores

    compute_similarity.get_sequence('backend/combined_normalized_data.csv', 'user_video')

    values = 'backend/combined_normalized_data.csv'.loc[2:4, 'backend/combined_normalized_data.csv'.columns[0]].values

    ref_114_seq = compute_similarity.get_sequence('backend/combined_normalized_data.csv', values[0])
    ref_135_seq = compute_similarity.get_sequence('backend/combined_normalized_data.csv', values[1])
    ref_148_seq = compute_similarity.get_sequence('backend/combined_normalized_data.csv', values[2])

    dist_114, path_114 = compare_motion_sequences(user_seq, ref_114_seq)
    dist_135, path_135 = compare_motion_sequences(user_seq, ref_135_seq)
    dist_148, path_148 = compare_motion_sequences(user_seq, ref_148_seq)
    '''