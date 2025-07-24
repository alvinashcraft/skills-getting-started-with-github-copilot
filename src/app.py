"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Update the Activity class to include participants
class Activity:
    def __init__(self, id, name, date, location, description):
        self.id = id
        self.name = name
        self.date = date
        self.location = location
        self.description = description
        self.participants = []  # Add a list to store participants


# In-memory activity database
activities = [
    Activity(1, "Hiking at Mountain Trail", "2023-10-15", "Mountain Park",
             "A beginner-friendly hiking trip with beautiful views."),
    Activity(2, "Community Cleanup", "2023-10-22", "City Beach",
             "Help keep our beach clean! Supplies will be provided."),
    Activity(3, "Charity Run", "2023-11-05", "Downtown",
             "5k run to raise funds for the local animal shelter.")
]


# Add function to add a participant to an activity
def add_participant_to_activity(activity_id, participant_name):
    for activity in activities:
        if activity.id == int(activity_id):
            if participant_name not in activity.participants:
                activity.participants.append(participant_name)
                return True
    return False


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(status_code=400, detail="Student is already signed up")

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


# Add route to handle participant registration
@app.route('/register', methods=['POST'])
def register():
    activity_id = request.form.get('activity_id')
    participant_name = request.form.get('participant_name')

    if not activity_id or not participant_name:
        return redirect(url_for('index', error="Please fill in all fields"))

    success = add_participant_to_activity(activity_id, participant_name)

    if success:
        return redirect(url_for('index', message="Successfully registered for the activity!"))
    else:
        return redirect(url_for('index', error="Activity not found or registration failed"))


# Update the index route to pass error/success messages
@app.route('/')
def index():
    error = request.args.get('error')
    message = request.args.get('message')
    return render_template('index.html', activities=activities, error=error, message=message)
