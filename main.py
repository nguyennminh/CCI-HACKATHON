from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import traceback
import backend.extract_input_data as extract_input_data
import backend.compute_similarity as compute_similarity
import backend.kronos_ai as kronos_ai
import backend.normalize_data as normalize_data
import backend.generate_pro_gif as generate_pro_gif
import backend.smash_classifier as smash_classifier
import pandas as pd
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from enum import Enum

app = FastAPI()

# Allow frontend to call the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

UPLOAD_FOLDER = "backend/uploads"
OUTPUT_FOLDER = "backend"
GIFS_FOLDER = "static"

for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER, GIFS_FOLDER]:
    os.makedirs(folder, exist_ok=True)

class ProcessingStatus(str, Enum):
    IDLE = "idle"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Initialize the global processing state
processing_state = {
    "status": ProcessingStatus.IDLE,
    "error": None
}

app.mount("/gifs", StaticFiles(directory=GIFS_FOLDER), name="gifs")

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

def process_video(path):
    """Process video in background"""
    global processing_state
    
    try:
        print("=" * 50)
        print("STARTING VIDEO PROCESSING")
        print("=" * 50)
        
        processing_state["status"] = ProcessingStatus.PROCESSING
        processing_state["error"] = None
        
        extract_input_data.main()
        print("✓ extract_input_data completed")
        
        normalize_data.main()
        print("✓ normalize_data completed")
        
        smash_classifier.main()
        print("✓ smash_classifier completed")
        
        compute_similarity.main()
        print("✓ compute_similarity completed")
        
        generate_pro_gif.main()
        print("✓ generate_pro_gif completed")
        
        kronos_ai.main()
        print("✓ kronos_ai completed")
        
        processing_state["status"] = ProcessingStatus.COMPLETED
        print("=" * 50)
        print("PROCESSING COMPLETED SUCCESSFULLY")
        print("=" * 50)
        
    except Exception as e:
        processing_state["status"] = ProcessingStatus.FAILED
        processing_state["error"] = str(e)
        print("=" * 50)
        print("PROCESSING FAILED:")
        print(str(e))
        traceback.print_exc()
        print("=" * 50)

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    global processing_state
    
    print("\n" + "=" * 50)
    print("UPLOAD REQUEST RECEIVED")
    print("=" * 50)
    
    try:
        print(f"Filename: {video.filename}")
        print(f"Content-Type: {video.content_type}")
        
        # Save uploaded video
        ext = os.path.splitext(video.filename)[1] or ".mp4"
        filename = f"smash_video_example{ext}"
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"Saving to: {save_path}")
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        file_size = os.path.getsize(save_path)
        print(f"✓ File saved successfully ({file_size} bytes)")
        
        # Reset state and start background processing
        processing_state["status"] = ProcessingStatus.UPLOADING
        background_tasks.add_task(process_video, save_path)
        
        print("✓ Background task queued")
        print("=" * 50 + "\n")
        
        return {
            "message": f"Video uploaded successfully. Processing started.",
            "filename": filename,
            "status": "processing"
        }
        
    except Exception as e:
        print("✗ UPLOAD FAILED:")
        print(str(e))
        traceback.print_exc()
        print("=" * 50 + "\n")
        
        processing_state["status"] = ProcessingStatus.FAILED
        processing_state["error"] = str(e)
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload failed: {str(e)}"}
        )

@app.get("/status")
async def get_status():
    """Get current processing status"""
    return {
        "status": processing_state["status"],
        "error": processing_state["error"]
    }

@app.get("/results")
async def get_results():
    """Return the processed results"""
    global processing_state
    
    if processing_state["status"] != ProcessingStatus.COMPLETED:
        return JSONResponse(
            status_code=202,
            content={
                "status": processing_state["status"],
                "message": "Processing not complete yet"
            }
        )
    
    try:
        tips_path = os.path.join(OUTPUT_FOLDER, "badminton_feedback.txt")
        
        if not os.path.exists(tips_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"Tips file not found at {tips_path}"}
            )
        
        with open(tips_path, 'r', encoding='utf-8') as f:
            tips = f.read()
        
        pro_gif_path = os.path.join(GIFS_FOLDER, "proshot.gif")
        user_gif_path = os.path.join(GIFS_FOLDER, "badminton_shot_user_video.gif")
        
        if not os.path.exists(pro_gif_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"Pro GIF not found at {pro_gif_path}"}
            )
        
        if not os.path.exists(user_gif_path):
            return JSONResponse(
                status_code=404,
                content={"error": f"User GIF not found at {user_gif_path}"}
            )
        
        return {
            "proGif": "/gifs/proshot.gif",
            "userGif": "/gifs/badminton_shot_user_video.gif",
            "tips": tips,
            "status": "completed"
        }
        
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": f"Error retrieving results: {str(e)}"}
        )

@app.post("/reset")
async def reset_state():
    """Reset processing state"""
    global processing_state
    processing_state["status"] = ProcessingStatus.IDLE
    processing_state["error"] = None
    return {"message": "State reset successfully"}