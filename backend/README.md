# Backend (Hackathon)

How to run (local):
1. Create virtualenv:
   python -m venv venv
   source venv/bin/activate   # windows: venv\Scripts\activate

2. Install deps:
   pip install -r requirements.txt

3. Optional env:
   - Create .env with (if using OpenAI):
       OPENAI_API_KEY=sk-...
   - For Firebase:
       FIREBASE_CRED_JSON=path/to/serviceAccount.json
       FIREBASE_DB_URL=https://<project>.firebaseio.com

4. Start server:
   uvicorn main:app --reload --port 8000

5. API docs:
   http://127.0.0.1:8000/docs

Notes:
- If you don't provide Firebase or OPENAI keys, the backend runs in mock mode for development.
- Use tests/sample_candidate.json to simulate candidate submissions.
