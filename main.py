from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import PyPDF2
import ollama
import json

app = FastAPI(title="Local AI Quiz Generator & Grader")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-quiz")
async def generate_quiz(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

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

        system_prompt = f"""
        You are an expert educational assistant. Based ONLY on the provided document text, 
        generate a 3-question multiple-choice quiz. 
        
        Document Text:
        {document_text}

        Respond ONLY with a valid JSON object strictly matching this schema:
        {{
            "quiz_title": "A relevant title",
            "questions": [
                {{
                    "id": 1,
                    "question_text": "The actual question here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option B"
                }}
            ]
        }}
        """

        response = ollama.generate(model='llama3', prompt=system_prompt, format='json', stream=False)
        return json.loads(response['response'])

    except Exception as e:
        print(f"🔥 THE EXACT ERROR IS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class QuizSubmission(BaseModel):
    submissions: List[Dict[str, Any]]

@app.post("/evaluate-answers")
async def evaluate_answers(data: QuizSubmission):
    try:
        system_prompt = f"""
        You are an encouraging tutor. Evaluate the user's answers to these quiz questions.
        
        Data: {json.dumps(data.submissions)}

        Respond ONLY with a valid JSON object strictly matching this schema:
        {{
            "score_summary": "You got X out of Y correct!",
            "feedback": [
                {{
                    "question_id": 1,
                    "is_correct": true,
                    "tutor_message": "A 1-sentence explanation of why they were right or wrong."
                }}
            ]
        }}
        """

        response = ollama.generate(model='llama3', prompt=system_prompt, format='json', stream=False)
        return json.loads(response['response'])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)