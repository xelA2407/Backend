from fastapi import FastAPI, UploadFile, Form
import openai
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = FastAPI()

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize OpenAI
openai.api_key = "YOUR_OPENAI_API_KEY_HERE"

@app.get("/")
def read_root():
    return {"message": "AI Learning Backend is Live!"}

@app.post("/generate_course/")
async def generate_course(name: str = Form(...), topic: str = Form(...), skill_level: str = Form(...)):
    prompt = f"Create a learning path for {name}, who wants to learn {topic}. Skill level: {skill_level}. Make it personalized."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a professional learning assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    learning_path = response.choices[0].message['content']

    # Save to Firebase
    user_ref = db.collection("Users").document(name)
    user_ref.set({
        "selectedTopics": [topic],
        "skillLevelPerTopic": {topic: skill_level},
        "learningPath": learning_path
    }, merge=True)

    return {"learning_path": learning_path}

@app.post("/upload_problem/")
async def upload_problem(name: str = Form(...), file: UploadFile = None):
    content = await file.read()
    user_problem_text = content.decode('utf-8')

    ai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert tutor in Excel, SQL, Power BI and Tableau."},
            {"role": "user", "content": f"Here is a problem:\n{user_problem_text}\nPlease help me solve it."}
        ]
    )

    ai_answer = ai_response.choices[0].message['content']

    # Save problem and AI answer to Firebase
    problems_ref = db.collection("Problems").document()
    problems_ref.set({
        "userId": name,
        "userQuestion": user_problem_text,
        "aiAnswer": ai_answer
    })

    return {"ai_answer": ai_answer}
