# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from matching_engine import MatchingEngine
import pandas as pd

app = FastAPI(title="AI Powered Matching API", description="APIs for the hobby matching demo")

# This is crucial for your frontend to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for demo. Change for production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the matching engine when the app starts
engine = MatchingEngine()

@app.get("/")
def read_root():
    return {"message": "AI Powered Matching API is running!"}

# API 1: Cluster users and get matches
@app.get("/match/users/{user_id}")
def get_user_matches(user_id: int, top_n: int = 10):
    """Get top user matches for a given user ID."""
    try:
        matches = engine.get_user_matches(user_id, top_n)
        return {"user_id": user_id, "matches": matches}
    except Exception as e:
        return {"error": str(e)}

# API 2: Get event matches for a user
@app.get("/match/events/{user_id}")
def get_event_matches(user_id: int, top_n: int = 5):
    """Get top event matches for a given user ID."""
    try:
        matches = engine.get_event_matches(user_id, top_n)
        return {"user_id": user_id, "events": matches}
    except Exception as e:
        return {"error": str(e)}

@app.get("/users/")
def get_all_users():
    """Get all users. For the demo UI to display."""
    return engine.users_df.to_dict(orient='records')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)