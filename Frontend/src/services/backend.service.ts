// Backend API service for FastAPI integration
// This connects to your Python backend that processes code evaluation

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface RunCodeRequest {
  code: string;
  language: string;
  input: string;
  userId: string;
}

export interface RunTestsRequest {
  code: string;
  language: string;
  questionId: string;
  userId: string;
}

export interface SubmitSolutionRequest {
  code: string;
  language: string;
  questionId: string;
  userId: string;
}

// Run code with custom input
export const runCode = async (request: RunCodeRequest) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/run-code`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error('Failed to run code');
    }

    return await response.json();
  } catch (error) {
    console.error('Error running code:', error);
    throw error;
  }
};

// Run test cases
// Backend will read from Firebase: userAnswers, inputs
// Backend will write to Firebase: evaluationResults
export const runTests = async (request: RunTestsRequest) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/run-tests`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error('Failed to run tests');
    }

    return await response.json();
  } catch (error) {
    console.error('Error running tests:', error);
    throw error;
  }
};

// Submit solution for evaluation
// Backend will:
// 1. Read userAnswers and inputs from Firebase
// 2. Run evaluation_engine.py
// 3. Write to evaluationResults
// 4. Run fuzzy_logic_engine.py and write to metrics
// 5. Run summary_generator.py and write to aiAnalysis
export const submitSolution = async (request: SubmitSolutionRequest) => {
  try {
    const response = await fetch(`${BACKEND_URL}/api/submit`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error('Failed to submit solution');
    }

    return await response.json();
  } catch (error) {
    console.error('Error submitting solution:', error);
    throw error;
  }
};
