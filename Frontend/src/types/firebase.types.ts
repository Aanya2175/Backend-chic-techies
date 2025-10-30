// Firebase Firestore collection types

export interface User {
  id: string;
  email: string;
  displayName: string;
  role: 'candidate' | 'recruiter';
  createdAt: Date;
  lastActive: Date;
}

export interface Question {
  id: string;
  title: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  description: string;
  examples: {
    input: string;
    output: string;
    explanation?: string;
  }[];
  constraints: string[];
  category: string;
  createdAt: Date;
}

export interface Language {
  id: string;
  name: string; // e.g., 'python3', 'javascript', 'java'
  version: string;
  starterCode: string;
  enabled: boolean;
}

export interface TestInput {
  id: string;
  questionId: string;
  input: string;
  expectedOutput: string;
  isVisible: boolean;
  isLocked: boolean;
  weight: number;
}

export interface UserAnswer {
  id: string;
  userId: string;
  questionId: string;
  code: string;
  language: string;
  submittedAt: Date;
  status: 'pending' | 'evaluating' | 'completed' | 'error';
}

export interface EvaluationResult {
  id: string;
  answerI: string;
  userId: string;
  questionId: string;
  testCases: {
    testId: string;
    passed: boolean;
    actualOutput: string;
    expectedOutput: string;
    executionTime: number;
    memoryUsed: number;
  }[];
  overallScore: number;
  completedAt: Date;
}

export interface Metric {
  id: string;
  userId: string;
  questionId?: string;
  metric_type: 'code_quality' | 'efficiency' | 'correctness' | 'overall';
  value: number;
  details: Record<string, any>;
  calculatedAt: Date;
}

export interface AIAnalysis {
  id: string;
  userId: string;
  questionId?: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  overallRating: number;
  generatedAt: Date;
}

export interface GPTPrompt {
  id: string;
  promptType: 'evaluation' | 'summary' | 'feedback';
  prompt: string;
  response: string;
  tokens: number;
  createdAt: Date;
}

export interface ActivityLog {
  id: string;
  userId: string;
  action: string;
  details: Record<string, any>;
  timestamp: Date;
  ipAddress?: string;
}
