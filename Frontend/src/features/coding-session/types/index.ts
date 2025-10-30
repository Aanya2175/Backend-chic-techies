export interface TestCase {
  id: number;
  status: "passed" | "failed" | "locked";
  input?: string;
  output?: string;
  expected?: string;
  visible: boolean;
}

export interface CodeExecutionRequest {
  code: string;
  language: string;
  input: string;
  userId: string;
}

export interface TestExecutionRequest {
  code: string;
  language: string;
  questionId: string;
  userId: string;
}

export interface SubmissionRequest {
  code: string;
  language: string;
  questionId: string;
  userId: string;
}