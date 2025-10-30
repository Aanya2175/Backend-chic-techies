from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import subprocess
import tempfile
import os
import json
from services.data_processing import evaluate_raw_session
from services.summary_generator import generate_summary

router = APIRouter()

class RunCodeRequest(BaseModel):
    code: str
    language: str
    input: str
    userId: str

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

def execute_code(code: str, language: str, input_data: str = "") -> Dict[str, Any]:
    """Execute code and return output"""
    try:
        if language == "python3":
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                result = subprocess.run(
                    ['python3', f.name],
                    input=input_data,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                os.unlink(f.name)
                
                return {
                    "output": result.stdout,
                    "error": result.stderr,
                    "returncode": result.returncode
                }
        else:
            return {"error": f"Language {language} not supported yet", "returncode": 1}
            
    except subprocess.TimeoutExpired:
        return {"error": "Code execution timed out", "returncode": 1}
    except Exception as e:
        return {"error": str(e), "returncode": 1}

@router.post("/api/run-code")
async def run_code(request: RunCodeRequest):
    """Execute code with custom input"""
    try:
        result = execute_code(request.code, request.language, request.input)
        
        # Log activity for evaluation
        activity_event = {
            "event_type": "run",
            "payload": {
                "result": "success" if result["returncode"] == 0 else "fail",
                "language": request.language
            },
            "timestamp": 1698000000  # Use current timestamp in production
        }
        
        return {
            "output": result["output"],
            "error": result["error"],
            "success": result["returncode"] == 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/run-tests")
async def run_tests(request: RunTestsRequest):
    """Run test cases against code"""
    try:
        # Mock test cases - replace with Firebase data in production
        test_cases = [
            {"id": 1, "input": "24", "expected": "2"},
            {"id": 2, "input": "17", "expected": "1"},
            {"id": 3, "input": "100", "expected": "2"}
        ]
        
        results = []
        passed = 0
        
        for test_case in test_cases:
            result = execute_code(request.code, request.language, test_case["input"])
            
            actual_output = result["output"].strip()
            expected_output = test_case["expected"].strip()
            test_passed = actual_output == expected_output and result["returncode"] == 0
            
            if test_passed:
                passed += 1
                
            results.append({
                "id": test_case["id"],
                "status": "passed" if test_passed else "failed",
                "input": test_case["input"],
                "output": actual_output,
                "expected": expected_output,
                "visible": True
            })
        
        score = (passed / len(test_cases)) * 100
        
        # Log activity for evaluation
        activity_event = {
            "event_type": "run_tests",
            "payload": {
                "score": score,
                "passed": passed,
                "total": len(test_cases)
            },
            "timestamp": 1698000000
        }
        
        return {
            "testCases": results,
            "score": score,
            "passed": passed,
            "total": len(test_cases)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/submit")
async def submit_solution(request: SubmitSolutionRequest):
    """Submit solution for full evaluation"""
    try:
        # First run tests
        test_result = await run_tests(RunTestsRequest(
            code=request.code,
            language=request.language,
            questionId=request.questionId,
            userId=request.userId
        ))
        
        # Create session events for evaluation
        session_events = [
            {
                "event_type": "edit",
                "payload": {"keystrokes": len(request.code)},
                "timestamp": 1698000000
            },
            {
                "event_type": "run_tests",
                "payload": {"score": test_result["score"]},
                "timestamp": 1698000030
            },
            {
                "event_type": "submit_solution",
                "payload": {"final_score": test_result["score"]},
                "timestamp": 1698000060
            }
        ]
        
        # Run full evaluation pipeline
        evaluation_result = evaluate_raw_session(session_events)
        
        if "error" in evaluation_result:
            return {"error": evaluation_result["error"]}
        
        # Generate summary
        summary = generate_summary(evaluation_result)
        
        return {
            "score": test_result["score"],
            "testResults": test_result["testCases"],
            "evaluation": evaluation_result,
            "summary": summary,
            "recommendations": evaluation_result.get("recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))