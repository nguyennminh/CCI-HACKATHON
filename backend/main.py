from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import subprocess
import json
import logging

# Configure logging to see the progress in your terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Middleware ---
# This allows your React frontend (running on localhost:3000) to communicate with this backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
# Create the necessary directories if they don't already exist.
os.makedirs("uploads", exist_ok=True)
os.makedirs("static", exist_ok=True)

# This makes the 'static' folder publicly accessible at the /static URL.
# This is how the frontend will be able to fetch and display the generated GIF.
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Main Upload & Analysis Endpoint ---
@app.post("/upload")
async def analyze_smash_video(video: UploadFile = File(...)):
    """
    This single endpoint handles the entire process:
    1. Saves the uploaded video.
    2. Runs the full sequence of analysis scripts.
    3. Returns the final feedback JSON and the URL to the animated GIF.
    """
    
    # 1. Save the uploaded video to a consistent path that our scripts expect.
    video_path = os.path.join("uploads", "user_smash_video.mp4")
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        logger.info(f"Video saved successfully to {video_path}")
    except Exception as e:
        logger.error(f"Error saving video file: {e}")
        raise HTTPException(status_code=500, detail=f"Could not save video file: {e}")

    # 2. Define the sequence of scripts to run for the analysis pipeline.
    #    The order is critical for the process to work correctly.
    scripts = [
        "extract_input_data.py",
        "normalize_data.py",
        "compute_similarity.py",
        "kronos_ai.py",
    ]
    
    try:
        for script in scripts:
            logger.info(f"--- Running script: {script} ---")
            
            # We use subprocess.run to execute each Python script.
            # `check=True` is very important: if a script fails (returns a non-zero exit code),
            # it will raise an exception, stopping the pipeline immediately.
            process = subprocess.run(
                ["python", script],
                capture_output=True,
                text=True,
                check=True 
            )
            # Log the standard output from the script for debugging purposes.
            logger.info(f"Output from {script}:\n{process.stdout}")
            if process.stderr:
                logger.warning(f"Stderr from {script}:\n{process.stderr}")

    except subprocess.CalledProcessError as e:
        # This block catches errors if any of the scripts fail.
        logger.error(f"--- SCRIPT FAILED: {e.cmd[-1]} ---")
        logger.error(f"Return code: {e.returncode}")
        logger.error(f"Stdout:\n{e.stdout}")
        logger.error(f"Stderr:\n{e.stderr}")
        # Send a user-friendly error back to the frontend.
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during the analysis pipeline in script: {os.path.basename(e.cmd[-1])}."
        )
    except FileNotFoundError:
        logger.error("A script was not found. Ensure all analysis scripts are in the backend directory.")
        raise HTTPException(status_code=500, detail="A required analysis script was not found on the server.")


    # 3. If all scripts ran successfully, read the final results.
    feedback_json_path = "badminton_feedback.json"
    
    # The GIF path should now be consistent thanks to our changes in extract_input_data.py
    gif_url = "/static/badminton_shot_user_video.gif" 

    if not os.path.exists(feedback_json_path):
        raise HTTPException(status_code=500, detail="Analysis completed, but the feedback.json file was not generated.")

    with open(feedback_json_path, "r") as f:
        feedback_data = json.load(f)

    # 4. Construct the final response object to send back to the React frontend.
    response_data = {
        "feedback": feedback_data,
        "gifUrl": gif_url
    }

    logger.info("✅ Successfully completed analysis. Sending results to frontend.")
    return JSONResponse(content=response_data)


# --- Root Endpoint for API Health Check ---
@app.get("/")
def read_root():
    """ A simple endpoint to check if the API server is running. """
    return {"message": "Welcome to the Badminton AI Coach API. Ready to analyze!"}