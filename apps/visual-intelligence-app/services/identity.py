import os
import cv2
import numpy as np
from typing import List

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False

DB_PATH = "authorized_faces"

def init_identity_db():
    if not os.path.exists(DB_PATH):
        os.makedirs(DB_PATH)
        # Create a dummy README so git doesn't ignore the directory
        with open(os.path.join(DB_PATH, "README.md"), "w") as f:
            f.write("Drop images of authorized personnel in this directory to seed the Authorized Users DB for DeepFace.")

def analyze_identities(frame_np) -> List[str]:
    """
    Analyzes an OpenCV frame using DeepFace.
    Returns a list of identified tags: 'Authorized User' or 'Unknown Person'.
    """
    identities = []
    if not DEEPFACE_AVAILABLE:
        return identities
    
    try:
        # DeepFace find() returns a list of pandas dataframes for each face detected
        dfs = DeepFace.find(img_path=frame_np, db_path=DB_PATH, enforce_detection=True, silent=True)
        
        # We must decipher the dataframes
        for df in dfs:
            if not df.empty:
                identities.append("Authorized User")
            else:
                identities.append("Unknown Person")
                
    except ValueError:
        # Thrown when enforce_detection is True but no faces are present in the image
        pass 
    except Exception as e:
        print(f"[DeepFace] Identity Pipeline Error: {e}")
        
    return identities
