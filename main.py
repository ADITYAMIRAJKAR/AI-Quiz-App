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

# Allows your frontend to communicate with this backend
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

    # Cap the maximum questions to prevent the AI from timing out locally
    if num_questions > 10:
        num_questions = 10

    try:
        # Read the PDF
        pdf_reader = PyPDF2.PdfReader(file.file)
        document_text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                document_text += extracted + "\n"
        
        # Limit text length to avoid overflowing the AI's context window
        document_text = document_text[:5000] 

        if not document_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

        # STRICT PROMPT for generating questions
        system_prompt = f"""
        You are a strict, objective Quiz Generator API. Based ONLY on the provided document text, 
        generate a {num_questions}-question multiple-choice quiz. 
        
        Document Text:
        {document_text}

        Your ONLY job is to output valid JSON. Do not include introductory text, greetings, or formatting like markdown blocks.
        
        CRITICAL INSTRUCTION: For the "correct_answer" field, you MUST output the exact text of the correct option. Do NOT write "Option A", "Option B", etc.

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
        # STRICT PROMPT for grading
        system_prompt = f"""
        You are a strict, objective automated grading system. 
        You are receiving a JSON array containing quiz questions, the user's selected answer, and the objectively correct answer.
        
        Data: {json.dumps(data.submissions)}

        Your ONLY job is to compare the "user_answer" to the "correct_answer". 
        If they do not match exactly, the answer is wrong. 
        
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

        # Ask the AI to grade the quiz
        response = ollama.generate(model='llama3', prompt=system_prompt, format='json', stream=False)
        result_data = json.loads(response['response'])

        # --- CSV LOGGING LOGIC ---
        csv_file = "quiz_results.csv"
        file_exists = os.path.isfile(csv_file)

        # Open the CSV file in 'append' mode so we don't overwrite previous quizzes
        with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # If the file is brand new, write the header row first
            if not file_exists:
                writer.writerow(["Timestamp", "Question ID", "Question Text", "User Answer", "Correct Answer", "Is Correct", "Tutor Feedback"])

            # Get the exact time the user submitted the quiz
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Loop through the user's submissions and save them to the CSV
            for sub in data.submissions:
                # Match the submission with the AI's feedback
                feedback = next((item for item in result_data.get('feedback', []) if item.get("question_id") == sub.get("question_id")), None)

                is_correct = feedback["is_correct"] if feedback else False
                tutor_msg = feedback["tutor_message"] if feedback else "No feedback provided"

                # Write the row of data into the spreadsheet!
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

        # Finally, send the grading results back to the frontend website
        return result_data

    except Exception as e:
        print(f"🔥 GRADING ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)