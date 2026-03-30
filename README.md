# Local AI Document Quiz Generator

A full-stack, privacy-first web application that allows users to upload PDF documents and automatically generates a multiple-choice quiz using a local Large Language Model (LLM). It also features an AI-powered grading system that provides custom, objective feedback for the user's answers.

Because this application utilizes [Ollama](https://ollama.com/), the entire AI pipeline runs 100% locally on your machine. No data is sent to external APIs like OpenAI or Google, ensuring complete document privacy.

## What is this project?
This is a full-stack, local AI-powered web application that transforms static reading materials into interactive assessments. Users can upload a PDF document, and the application will instantly generate a custom multiple-choice quiz based strictly on the document's content, auto-grade the user's answers, and log the results into a database.

## Overview
Built as an internship project, this application bridges the gap between modern frontend design and backend AI engineering. It utilizes a Python/FastAPI backend to parse PDF text and communicate with a locally hosted Large Language Model (Llama 3 via Ollama). This ensures 100% data privacy and zero API costs. The frontend is built with vanilla HTML/CSS/JS, featuring a modern, responsive UI that provides users with a clean "Report Card" and detailed AI tutor feedback.

## Main Features
* **📄 Automated Document Ingestion:** Extracts text directly from user-uploaded PDFs using `PyPDF2`.
* **🎯 Dynamic Generation:** Users can scale the assessment length (1-10 questions) on the fly.
* **🤖 AI Tutor Feedback:** Provides custom, objective explanations for why an answer was correct or incorrect.
* **📊 Deterministic Scoring:** Utilizes Python-based math to ensure 100% accurate fraction-based grading (e.g., 8/10), bypassing common LLM counting hallucinations.
* **💾 Persistent CSV Logging:** Automatically tracks timestamps, user inputs, and scores into a queryable backend database (`quiz_results.csv`).
* **✨ Modern SaaS UI:** Features a sleek, responsive interface with custom CSS, interactive hover states, and clear data visualization.
* **📥 Offline Export:** Allows users to download their generated quiz as a `.txt` file for offline study.

## Challenges Faced & Fixes
1. **LLM Math Hallucinations:** * *Challenge:* The AI was accurately grading individual questions but failing to count the final score accurately. 
   * *Fix:* Offloaded the mathematical counting logic from the LLM prompt to deterministic Python code on the backend (`correct_count = sum(...)`).
2. **Handling Empty Inputs / Skipped Questions:** * *Challenge:* When users skipped a question, the AI panicked and hallucinated feedback. 
   * *Fix:* Implemented strict rule-based prompt engineering, explicitly commanding the AI to recognize "No answer provided" and output a specific, formatted response.
3. **Mismatched String Grading:** * *Challenge:* The AI generated correct answers like "A) Option" but the user selected "Option", causing the grader to mark it wrong. 
   * *Fix:* Overhauled the generation prompt to make exact string matching between the `options` array and the `correct_answer` field non-negotiable.

## Project Structure
```text
AI-Quiz-App/
│
├── main.py                # FastAPI backend and LLM routing
├── index.html             # Frontend UI and JavaScript logic
├── requirements.txt       # Python dependencies
├── quiz_results.csv       # Automatically generated database of user scores
└── README.md              # Project documentation
```text

##  Tech Stack
* **Backend:** Python, FastAPI, Uvicorn
* **Frontend:** Vanilla HTML, CSS, JavaScript
* **AI Engine:** Ollama (`llama3` model)
* **Document Processing:** PyPDF2

##  How to Run Locally

### Prerequisites
1. Install [Python 3.10+](https://www.python.org/downloads/).
2. Install [Ollama](https://ollama.com/) and download the model: `ollama pull llama3`

### Installation Steps
1. Clone this repository to your local machine:
   `git clone https://github.com/ADITYAMIRAJKAR/AI-Quiz-App.git`
2. Navigate to the folder and install dependencies:
   `pip install -r requirements.txt`
3. Start the FastAPI backend server:
   `uvicorn main:app --reload`
4. Open the `index.html` file in your web browser.
5. Upload a PDF and generate your quiz!

---
## How To Use
* **Launch the UI: Open the index.html file in any modern web browser (Chrome, Edge, Safari).

* **Upload Material: Click "Choose File" and upload a PDF document containing educational text, lecture notes, or an article.

* **Set Constraints: Enter the number of questions you want the AI to generate (between 1 and 10).

* **Generate: Click "Generate Assessment". The UI will display a loading state while the backend extracts the text and the LLM formulates the JSON question data.

* **Take the Assessment: Read the generated questions and select your answers. (Tip: Try intentionally skipping a question or getting one wrong to test the AI's dynamic feedback logic).

* **Evaluate: Click "Submit for Evaluation". The app will calculate your final fraction score and display detailed, question-by-question tutor feedback.

* **Review Logs: Open the automatically generated quiz_results.csv file in your code editor or a spreadsheet program (like Excel) to view the backend database logging in action.

## Development Journal

### Day 2: Prompt Engineering & Feature Expansion
* **Strict JSON Enforcement:** Overhauled the system prompts to eliminate LLM hallucinations, ensuring the AI strictly outputs clean JSON instead of conversational text.
* **Grading Logic Fix:** Corrected an issue where the AI was validating "Option A" instead of the literal text, ensuring 100% accurate grading.
* **Offline Export Feature:** Added a JavaScript function to dynamically generate a downloadable `.txt` file containing the quiz questions, user choices, and AI feedback.

### Day 3: Dynamic Scaling, Pro UI, and Database Logging
* **Dynamic Question Scaling:** Upgraded the FastAPI backend to accept dynamic user form data, allowing the application to scale the generated quiz length (1-10 questions) on the fly without breaking the AI's context window.
* **Pro UI Overhaul:** Completely redesigned the frontend architecture with a modern, responsive CSS framework. Implemented clean typography, interactive hover states, and intuitive visual feedback for a SaaS-quality user experience.
* **Persistent Database Logging (CSV):** Engineered a persistent backend data logging system using Python's `csv` and `os` modules. The server now automatically captures and formats timestamps, user submissions, correct answers, and AI evaluations into a clean, queryable spreadsheet (`quiz_results.csv`) for administrative review.

### Continuation of Day 3: Edge-Case Handling & Material Design Overhaul
* **Advanced Prompt Engineering (Bug Fixes):** Resolved critical grading bugs by implementing strict, rule-based LLM instructions. Forced exact-string matching for options and explicitly handled edge cases like skipped questions ("No answer provided") to prevent AI hallucinations and guarantee 100% grading accuracy.
* **Google Forms UI/UX:** Completely redesigned the frontend architecture to mirror the classic, trusted Google Forms Material Design aesthetic. Implemented custom CSS variables, intuitive question cards, and interactive visual feedback for a highly polished, production-ready user experience.

### Day 4: Custom SaaS UI, Deterministic Scoring & Report Cards
* **Modern Tech Aesthetic Overhaul:** Pivoted from a standard Google Forms clone to a custom, premium AI SaaS interface. Implemented the 'Inter' font, subtle CSS background gradients, and modern hover states (floating cards with soft shadows) for a highly polished, professional look.
* **Deterministic Python Scoring:** Discovered and resolved a common LLM limitation (hallucinating math/counting). Offloaded the final score calculation from the AI prompt to the Python backend to guarantee 100% mathematical accuracy on every submission.
* **Dynamic Report Card UI:** Engineered a custom data-grid "Report Card" feature at the bottom of the assessment. It uses frontend JavaScript to instantly calculate and visualize the user's Total Questions, Correct Answers, Wrong Answers, and Final Fraction Score (e.g., 8/10).
* **Edge-Case Prompt Engineering:** Bulletproofed the AI generation and grading prompts. Forced exact-string matching for multiple-choice options and added strict fallback rules for unanswered questions ("No answer provided") to eliminate AI guesswork and app crashes.