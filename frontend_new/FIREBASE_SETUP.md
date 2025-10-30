# Firebase Setup Guide

## Architecture Overview

This application uses Firebase/Firestore for data storage and FastAPI (Python) for backend processing.

### Firestore Collections Structure

```
├── users
│   ├── id (auto)
│   ├── email
│   ├── displayName
│   ├── role (candidate/recruiter)
│   └── createdAt
│
├── questions
│   ├── id (auto)
│   ├── title
│   ├── difficulty
│   ├── description
│   ├── examples[]
│   ├── constraints[]
│   └── languages (subcollection)
│       ├── name
│       ├── version
│       └── starterCode
│
├── inputs
│   ├── id (auto)
│   ├── questionId
│   ├── input
│   ├── expectedOutput
│   ├── isVisible
│   └── isLocked
│
├── userAnswers
│   ├── id (auto)
│   ├── userId
│   ├── questionId
│   ├── code
│   ├── language
│   ├── submittedAt
│   └── status
│
├── evaluationResults
│   ├── id (auto)
│   ├── answerId
│   ├── userId
│   ├── questionId
│   ├── testCases[]
│   ├── overallScore
│   └── completedAt
│
├── metrics
│   ├── id (auto)
│   ├── userId
│   ├── questionId
│   ├── metric_type
│   ├── value
│   └── calculatedAt
│
├── aiAnalysis
│   ├── id (auto)
│   ├── userId
│   ├── summary
│   ├── strengths[]
│   ├── weaknesses[]
│   ├── suggestions[]
│   └── generatedAt
│
├── gptPrompts
│   ├── id (auto)
│   ├── promptType
│   ├── prompt
│   ├── response
│   └── tokens
│
└── activityLogs
    ├── id (auto)
    ├── userId
    ├── action
    ├── details
    └── timestamp
```

## Setup Steps

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add Project"
3. Follow the setup wizard
4. Enable Firestore Database in "Build" > "Firestore Database"

### 2. Get Firebase Configuration

1. In Firebase Console, go to Project Settings
2. Scroll down to "Your apps"
3. Click the web icon (</>)
4. Copy the configuration object
5. Update `src/config/firebase.ts` with your values

### 3. Set Environment Variables

1. Copy `.env.example` to `.env`
2. Fill in your Firebase configuration values
3. Set your FastAPI backend URL

```bash
cp .env.example .env
```

### 4. Create Firestore Indexes

For optimal performance, create these composite indexes:

```
Collection: userAnswers
Fields: userId (Ascending), submittedAt (Descending)

Collection: evaluationResults
Fields: userId (Ascending), completedAt (Descending)

Collection: activityLogs
Fields: userId (Ascending), timestamp (Descending)
```

### 5. Set Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Everyone can read questions
    match /questions/{questionId} {
      allow read: if request.auth != null;
      allow write: if false; // Only through admin SDK
      
      match /languages/{languageId} {
        allow read: if request.auth != null;
      }
    }
    
    // Users can read test inputs for questions
    match /inputs/{inputId} {
      allow read: if request.auth != null;
      allow write: if false; // Only through admin SDK
    }
    
    // Users can write their own answers
    match /userAnswers/{answerId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
    
    // Users can read their own evaluation results
    match /evaluationResults/{resultId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow write: if false; // Only backend can write
    }
    
    // Users can read their own metrics
    match /metrics/{metricId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow write: if false; // Only backend can write
    }
    
    // Users can read their own AI analysis
    match /aiAnalysis/{analysisId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow write: if false; // Only backend can write
    }
    
    // Activity logs - read own, write own
    match /activityLogs/{logId} {
      allow read: if request.auth != null && resource.data.userId == request.auth.uid;
      allow create: if request.auth != null && request.resource.data.userId == request.auth.uid;
    }
  }
}
```

## Backend Integration (FastAPI)

### Backend Endpoints

Your FastAPI backend should implement these endpoints:

#### 1. POST /api/run-code
Executes code with custom input and returns output.

**Request:**
```json
{
  "code": "string",
  "language": "string",
  "input": "string",
  "userId": "string"
}
```

**Response:**
```json
{
  "output": "string",
  "executionTime": "number",
  "error": "string?"
}
```

#### 2. POST /api/run-tests
Runs all test cases for a question.

**Request:**
```json
{
  "code": "string",
  "language": "string",
  "questionId": "string",
  "userId": "string"
}
```

**Backend Flow:**
1. Read from `inputs` collection (test cases)
2. Execute code against each test
3. Write results to `evaluationResults` collection

**Response:**
```json
{
  "testCases": [...],
  "score": "number"
}
```

#### 3. POST /api/submit
Submits solution for final evaluation.

**Request:**
```json
{
  "code": "string",
  "language": "string",
  "questionId": "string",
  "userId": "string"
}
```

**Backend Flow:**
1. Read from `userAnswers` and `inputs` collections
2. Run `evaluation_engine.py` → Write to `evaluationResults`
3. Run `fuzzy_logic_engine.py` → Write to `metrics`
4. Run `summary_generator.py` → Write to `aiAnalysis`
5. Store GPT interactions in `gptPrompts`

**Response:**
```json
{
  "evaluationId": "string",
  "score": "number",
  "status": "string"
}
```

### Backend Firebase Admin Setup

In your FastAPI backend, use Firebase Admin SDK:

```python
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin
cred = credentials.Certificate("path/to/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Get Firestore client
db = firestore.client()

# Example: Read user answer
def get_user_answer(answer_id):
    doc_ref = db.collection('userAnswers').document(answer_id)
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

# Example: Write evaluation results
def save_evaluation_result(data):
    doc_ref = db.collection('evaluationResults').document()
    doc_ref.set(data)
    return doc_ref.id
```

## Frontend Usage

### Authentication

```typescript
import { useFirebaseAuth } from '@/hooks/useFirebaseAuth';

const { user, login, logout } = useFirebaseAuth();

// Login
await login('user@example.com', 'password');

// Logout
await logout();
```

### Fetching Questions

```typescript
import { getQuestions, getQuestionById } from '@/services/firestore.service';

// Get all questions
const questions = await getQuestions();

// Get specific question with languages
const question = await getQuestionById('question-id');
```

### Submitting Code

```typescript
import { submitAnswer } from '@/services/firestore.service';
import { submitSolution } from '@/services/backend.service';

// Save to Firebase
const answerId = await submitAnswer(userId, questionId, code, language);

// Trigger backend evaluation
const result = await submitSolution({
  code,
  language,
  questionId,
  userId
});
```

## Data Flow

1. **User submits code** → Frontend saves to `userAnswers` collection
2. **Frontend calls backend API** → `/api/submit`
3. **Backend reads** from `userAnswers` and `inputs` collections
4. **Backend processes:**
   - `evaluation_engine.py` evaluates code
   - `fuzzy_logic_engine.py` calculates metrics
   - `summary_generator.py` generates AI analysis
5. **Backend writes** to:
   - `evaluationResults`
   - `metrics`
   - `aiAnalysis`
   - `gptPrompts`
6. **Frontend fetches** results from Firestore and displays to user

## Testing

1. Start your FastAPI backend: `uvicorn main:app --reload`
2. Start the React frontend: `npm run dev`
3. Configure Firebase in `.env`
4. Test the complete flow: Run Code → Run Tests → Submit
