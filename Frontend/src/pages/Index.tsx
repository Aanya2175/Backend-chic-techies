import { useState, useEffect } from "react";
import { QuestionSidebar, QuestionDetail } from "@/features/questions";
import { CodeEditor, TestResults } from "@/features/coding-session";
import { Chatbot } from "@/features/chat";
import { toast } from "sonner";
import { submitAnswer, logActivity } from "@/services/firestore.service";
import { runCode, runTests, submitSolution } from "@/services/backend.service";

// Mock data - Replace with Flask API calls
const mockQuestions = [
  {
    id: 1,
    title: "isPrime",
    difficulty: "Easy" as const,
    completed: true,
    description: `Complete the 'isPrime' function below.

The function is expected to return an INTEGER.
The function accepts LONG_INTEGER n as parameter.

Given an integer, n, determine whether it is prime. If it is prime, return 1; otherwise return its smallest divisor greater than 1.`,
    examples: [
      {
        input: "n = 24",
        output: "2",
        explanation: "The number 24 is not prime; its divisors are [1, 2, 3, 4, 6, 8, 12, 24]. The smallest divisor greater than 1 is 2."
      }
    ],
    constraints: [
      "2 ≤ n ≤ 10¹²"
    ]
  },
  {
    id: 2,
    title: "Two Sum",
    difficulty: "Easy" as const,
    completed: false,
    description: `Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
    examples: [
      {
        input: "nums = [2,7,11,15], target = 9",
        output: "[0,1]",
        explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]."
      },
      {
        input: "nums = [3,2,4], target = 6",
        output: "[1,2]"
      }
    ],
    constraints: [
      "2 ≤ nums.length ≤ 10⁴",
      "-10⁹ ≤ nums[i] ≤ 10⁹",
      "-10⁹ ≤ target ≤ 10⁹"
    ]
  },
  {
    id: 3,
    title: "Binary Search",
    difficulty: "Easy" as const,
    completed: false,
    description: `Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.

You must write an algorithm with O(log n) runtime complexity.`,
    examples: [
      {
        input: "nums = [-1,0,3,5,9,12], target = 9",
        output: "4",
        explanation: "9 exists in nums and its index is 4"
      }
    ],
    constraints: [
      "1 ≤ nums.length ≤ 10⁴",
      "-10⁴ < nums[i], target < 10⁴"
    ]
  },
  {
    id: 4,
    title: "Merge Two Sorted Lists",
    difficulty: "Medium" as const,
    completed: false,
    description: `You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.`,
    examples: [
      {
        input: "list1 = [1,2,4], list2 = [1,3,4]",
        output: "[1,1,2,3,4,4]"
      }
    ],
    constraints: [
      "The number of nodes in both lists is in the range [0, 50]",
      "-100 ≤ Node.val ≤ 100"
    ]
  },
  {
    id: 5,
    title: "Maximum Subarray",
    difficulty: "Hard" as const,
    completed: false,
    description: `Given an integer array nums, find the subarray with the largest sum, and return its sum.`,
    examples: [
      {
        input: "nums = [-2,1,-3,4,-1,2,1,-5,4]",
        output: "6",
        explanation: "The subarray [4,-1,2,1] has the largest sum 6."
      }
    ],
    constraints: [
      "1 ≤ nums.length ≤ 10⁵",
      "-10⁴ ≤ nums[i] ≤ 10⁴"
    ]
  }
];

const defaultCode = `def isPrime(n):
    flag=True
    for i in range(2,n):
        if n%i==0:
            flag=False
            break
    if flag==False:
        return 1
    else:
        return 1

if __name__ == '__main__':`;

const Index = () => {
  const [activeQuestionId, setActiveQuestionId] = useState(1);
  const [code, setCode] = useState(defaultCode);
  const [language, setLanguage] = useState("python3");
  const [isRunning, setIsRunning] = useState(false);
  const [customInput, setCustomInput] = useState("");
  const [customOutput, setCustomOutput] = useState("");
  
  const [testCases, setTestCases] = useState([
    { id: 6, status: "passed" as const, visible: false, locked: true },
    { id: 7, status: "passed" as const, visible: true, input: "1072843847", output: "16141", expected: "16141" },
    { id: 8, status: "passed" as const, visible: false, locked: true },
    { id: 9, status: "passed" as const, visible: false, locked: true },
    { id: 10, status: "passed" as const, visible: false, locked: true },
    { id: 11, status: "passed" as const, visible: false, locked: true }
  ]);

  const activeQuestion = mockQuestions.find(q => q.id === activeQuestionId)!;

  // Run code with custom input - calls FastAPI backend
  const handleRunCode = async () => {
    setIsRunning(true);
    toast.info("Running code...");
    
    try {
      // TODO: Replace with actual user ID from Firebase Auth
      const userId = "demo-user-id";
      
      const result = await runCode({
        code,
        language,
        input: customInput,
        userId
      });
      
      setCustomOutput(result.output || "Code executed successfully");
      toast.success("Code executed successfully");
      
      // Log activity to Firebase
      await logActivity(userId, 'run_code', { 
        questionId: activeQuestionId,
        language 
      });
    } catch (error) {
      toast.error("Failed to run code");
      setCustomOutput("Error: " + (error as Error).message);
    } finally {
      setIsRunning(false);
    }
  };

  // Run tests - Backend reads from Firebase (inputs) and writes to (evaluationResults)
  const handleRunTests = async () => {
    setIsRunning(true);
    toast.info("Running tests...");
    
    try {
      // TODO: Replace with actual user ID from Firebase Auth
      const userId = "demo-user-id";
      
      const result = await runTests({
        code,
        language,
        questionId: activeQuestionId.toString(),
        userId
      });
      
      // Update test cases with results from backend
      if (result.testCases) {
        setTestCases(result.testCases);
      }
      
      toast.success(`Tests completed! Score: ${result.score || 0}%`);
      
      // Log activity to Firebase
      await logActivity(userId, 'run_tests', { 
        questionId: activeQuestionId,
        score: result.score 
      });
    } catch (error) {
      toast.error("Failed to run tests");
    } finally {
      setIsRunning(false);
    }
  };

  // Submit solution - Backend evaluates and writes to Firebase
  // Backend flow: userAnswers → evaluation_engine.py → evaluationResults
  //               → fuzzy_logic_engine.py → metrics
  //               → summary_generator.py → aiAnalysis
  const handleSubmit = async () => {
    setIsRunning(true);
    toast.info("Submitting solution...");
    
    try {
      // TODO: Replace with actual user ID from Firebase Auth
      const userId = "demo-user-id";
      
      // First, save answer to Firebase userAnswers collection
      const answerId = await submitAnswer(
        userId,
        activeQuestionId.toString(),
        code,
        language
      );
      
      // Then trigger backend evaluation
      const result = await submitSolution({
        code,
        language,
        questionId: activeQuestionId.toString(),
        userId
      });
      
      toast.success("Solution submitted successfully!");
      
      // Log activity to Firebase
      await logActivity(userId, 'submit_solution', { 
        questionId: activeQuestionId,
        answerId,
        score: result.score 
      });
      
      // Backend will write to:
      // - evaluationResults (test results)
      // - metrics (fuzzy logic scores)
      // - aiAnalysis (GPT-generated summary)
      
    } catch (error) {
      toast.error("Failed to submit solution");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="h-14 border-b border-border bg-card flex items-center px-6">
        <h1 className="text-xl font-bold text-primary">CodeAssess</h1>
        <div className="ml-auto flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Time: 40m left</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Question Sidebar */}
        <QuestionSidebar
          questions={mockQuestions}
          activeQuestionId={activeQuestionId}
          onQuestionSelect={setActiveQuestionId}
        />

        {/* Middle Section - Question Detail */}
        <div className="w-96 border-r border-border bg-background">
          <QuestionDetail question={activeQuestion} />
        </div>

        {/* Right Section - Code Editor & Results */}
        <div className="flex-1 flex flex-col">
          {/* Code Editor - 60% height */}
          <div className="h-[60%] border-b border-border">
            <CodeEditor
              code={code}
              language={language}
              onCodeChange={setCode}
              onLanguageChange={setLanguage}
              onRunCode={handleRunCode}
              onRunTests={handleRunTests}
              onSubmit={handleSubmit}
              isRunning={isRunning}
            />
          </div>

          {/* Test Results - 40% height */}
          <div className="h-[40%]">
            <TestResults
              testCases={testCases}
              customInput={customInput}
              customOutput={customOutput}
              onCustomInputChange={setCustomInput}
            />
          </div>
        </div>
      </div>

      {/* Chatbot */}
      <Chatbot />
    </div>
  );
};

export default Index;
