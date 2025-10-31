from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
from services import firebase_service

router = APIRouter()


class RunCodeRequest(BaseModel):
    code: str
    language: str
    input: Optional[str] = ""


class RunTestsRequest(BaseModel):
    code: str
    language: str
    questionId: str
    userId: str


class SubmitSolutionRequest(BaseModel):
    code: str
    language: str
    questionId: str
    userId: str


@router.post("/run-code")
def run_code(req: RunCodeRequest):
    """Mock code runner for local development. Replace with a secure sandbox for production."""
    start = time.time()
    if req.language.startswith("py"):
        output = f"Mock run: received {len(req.code)} bytes of code. Input: {req.input}"
        exec_time = round(time.time() - start, 4)
        return {"output": output, "executionTime": exec_time, "error": None}
    return {"output": "Language runner not implemented (mock).", "executionTime": 0.0, "error": None}


@router.post("/run-tests")
def run_tests(req: RunTestsRequest):
    # fetch test cases from firestore (mock-safe)
    inputs = firebase_service.list_test_cases_for_question(req.questionId)
    test_cases = []
    passed = 0
    for i, inp in enumerate(inputs, start=1):
        visible = inp.get("visible", True)
        expected = inp.get("expectedOutput") or inp.get("expected") or ""
        # mock check: pass if code length is odd (placeholder logic)
        ok = len(req.code) % 2 == 1
        status = "passed" if ok else "failed"
        if ok:
            passed += 1
        test_cases.append({
            "testId": inp.get("id", f"t{i}"),
            "passed": ok,
            "actualOutput": "mock-output",
            "expectedOutput": expected,
            "executionTime": 0.001,
            "visible": visible,
        })

    score = int((passed / max(1, len(inputs))) * 100) if inputs else 0

    # persist an evaluation result for frontend listeners
    firebase_service.save_evaluation_result({
        "userId": req.userId,
        "questionId": req.questionId,
        "testCases": test_cases,
        "overallScore": score,
        "completedAt": time.time(),
    })

    return {"testCases": test_cases, "score": score}


@router.post("/submit")
def submit_solution(req: SubmitSolutionRequest):
    # run tests and persist metrics/ai analysis (mock)
    tests_res = run_tests(RunTestsRequest(code=req.code, language=req.language, questionId=req.questionId, userId=req.userId))
    score = tests_res.get("score", 0)
    firebase_service.save_metric({
        "userId": req.userId,
        "questionId": req.questionId,
        "metric_type": "overall",
        "value": score,
        "details": {},
    })
    firebase_service.save_ai_analysis({
        "userId": req.userId,
        "questionId": req.questionId,
        "summary": "Mock summary - replace with LLM output",
        "overallRating": score,
    })
    return {"evaluationId": None, "score": score, "status": "completed"}


@router.post("/chatbot")
def chatbot(body: Dict[str, Any]):
    prompt = body.get("prompt", "")
    response = {"response": f"Mock response for prompt: {prompt}"}
    firebase_service.save_gpt_prompt({
        "prompt": prompt,
        "response": response["response"],
        "tokens": 0,
    })
    return response
