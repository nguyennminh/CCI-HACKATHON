from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import backend.extract_input_data as extract_input_data
import backend.compute_similarity as compute_similarity
import backend.kronos_ai as kronos_ai
import backend.normalize_data as normalize_data
import backend.generate_pro_gif as generate_pro_gif
import backend.smash_classifier as smash_classifier
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
    generate_pro_gif.main()
    kronos_ai.main()