from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

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
    print(f"Processing video: {path}")
