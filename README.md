# Local AI Document Quiz Generator

A full-stack, privacy-first web application that allows users to upload PDF documents and automatically generates a multiple-choice quiz using a local Large Language Model (LLM). It also features an AI-powered grading system that provides custom, objective feedback for the user's answers.

Because this application utilizes [Ollama](https://ollama.com/), the entire AI pipeline runs 100% locally on your machine. No data is sent to external APIs like OpenAI or Google, ensuring complete document privacy.

## Features
* **PDF Text Extraction:** Parses and extracts text from user-uploaded PDF files.
* **Dynamic Quiz Generation:** Uses a local LLM to read the document context and generate a 3-question multiple-choice quiz formatted in strict JSON.
* **Automated AI Tutor:** Evaluates user submissions against the generated answer key.
* **Prompt Engineering:** Implements strict system prompts to prevent LLM hallucination and ensure objective grading.
* **Responsive UI:** Clean, vanilla frontend for seamless document uploading and quiz-taking.

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

## Development Journal

### Day 2: Prompt Engineering & Feature Expansion
* **Strict JSON Enforcement:** Overhauled the system prompts to eliminate LLM hallucinations, ensuring the AI strictly outputs clean JSON instead of conversational text.
* **Grading Logic Fix:** Corrected an issue where the AI was validating "Option A" instead of the literal text, ensuring 100% accurate grading.
* **Offline Export Feature:** Added a JavaScript function to dynamically generate a downloadable `.txt` file containing the quiz questions, user choices, and AI feedback.

### Day 3: Dynamic Scaling, Pro UI, and Database Logging
* **Dynamic Question Scaling:** Upgraded the FastAPI backend to accept dynamic user form data, allowing the application to scale the generated quiz length (1-10 questions) on the fly without breaking the AI's context window.
* **Pro UI Overhaul:** Completely redesigned the frontend architecture with a modern, responsive CSS framework. Implemented clean typography, interactive hover states, and intuitive visual feedback for a SaaS-quality user experience.
* **Persistent Database Logging (CSV):** Engineered a persistent backend data logging system using Python's `csv` and `os` modules. The server now automatically captures and formats timestamps, user submissions, correct answers, and AI evaluations into a clean, queryable spreadsheet (`quiz_results.csv`) for administrative review.
