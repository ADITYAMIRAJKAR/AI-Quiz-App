from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import PyPDF2
import ollama
import json
import csv
import os
from datetime import datetime

app = FastAPI(title="Local AI Quiz Generator & Grader")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# ENDPOINT 1: GENERATE THE QUIZ
# ---------------------------------------------------------
@app.post("/generate-quiz")
async def generate_quiz(file: UploadFile = File(...), num_questions: int = Form(3)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if num_questions > 10:
        num_questions = 10

    try:
        pdf_reader = PyPDF2.PdfReader(file.file)
        document_text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                document_text += extracted + "\n"
        
        document_text = document_text[:5000] 

        if not document_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

        # FIX 1: Explicit rules added to ensure exact string matching
        system_prompt = f"""
        You are a strict, objective Quiz Generator API. Based ONLY on the provided document text, 
        generate a {num_questions}-question multiple-choice quiz. 
        
        Document Text:
        {document_text}

        Your ONLY job is to output valid JSON. Do not include introductory text, greetings, or formatting like markdown blocks.
        
        CRITICAL INSTRUCTIONS: 
        1. Every question MUST have exactly 4 options in the "options" array.
        2. The "correct_answer" MUST be an EXACT string match to one of the items inside the "options" array. This is non-negotiable. Do not write "Option A".

        Respond ONLY with a valid JSON object strictly matching this schema:
        {{
            "quiz_title": "A relevant title",
            "questions": [
                {{
                    "id": 1,
                    "question_text": "The actual question here?",
                    "options": ["Apple", "Banana", "Orange", "Grape"],
                    "correct_answer": "Banana"
                }}
            ]
        }}
        """

        response = ollama.generate(model='llama3', prompt=system_prompt, format='json', stream=False)
        return json.loads(response['response'])

    except Exception as e:
        print(f"🔥 GENERATION ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
# ENDPOINT 2: EVALUATE ANSWERS & SAVE TO CSV
# ---------------------------------------------------------
class QuizSubmission(BaseModel):
    submissions: List[Dict[str, Any]]

@app.post("/evaluate-answers")
async def evaluate_answers(data: QuizSubmission):
    try:
        # FIX 2: Explicit grading rules for "No answer provided" and strict matching
        system_prompt = f"""
        You are a strict automated grading system. 
        Here is the submitted data: {json.dumps(data.submissions)}

        CRITICAL GRADING RULES:
        1. Compare "user_answer" to "correct_answer".
        2. If "user_answer" is exactly "No answer provided", then "is_correct" MUST be false. Your "tutor_message" should say: "You skipped this question. The correct answer was: [correct_answer]."
        3. If "user_answer" exactly matches "correct_answer", then "is_correct" MUST be true. Your "tutor_message" should say: "Correct!"
        4. If "user_answer" does not match "correct_answer", then "is_correct" MUST be false. Your "tutor_message" should say: "Incorrect. You chose [user_answer], but the correct answer was [correct_answer]."
        
        You MUST return a feedback object for EVERY question ID in the provided data.
        
        Respond ONLY with a valid JSON object strictly matching this schema:
        {{
            "score_summary": "You got X out of Y correct.",
            "feedback": [
                {{
                    "question_id": 1,
                    "is_correct": false,
                    "tutor_message": "Correct! / Incorrect. The correct answer was [insert correct answer here]."
                }}
            ]
        }}
        """

        response = ollama.generate(model='llama3', prompt=system_prompt, format='json', stream=False)
        result_data = json.loads(response['response'])

        # --- CSV LOGGING LOGIC ---
        csv_file = "quiz_results.csv"
        file_exists = os.path.isfile(csv_file)

        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(["Timestamp", "Question ID", "Question Text", "User Answer", "Correct Answer", "Is Correct", "Tutor Feedback"])

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for sub in data.submissions:
                feedback = next((item for item in result_data.get('feedback', []) if item.get("question_id") == sub.get("question_id")), None)

                is_correct = feedback["is_correct"] if feedback else False
                tutor_msg = feedback["tutor_message"] if feedback else "No feedback provided by AI"

                writer.writerow([
                    timestamp,
                    sub.get("question_id", ""),
                    sub.get("question_text", ""),
                    sub.get("user_answer", ""),
                    sub.get("correct_answer", ""),
                    is_correct,
                    tutor_msg
                ])
        # ------------------------------

        return result_data

    except Exception as e:
        print(f"🔥 GRADING ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)