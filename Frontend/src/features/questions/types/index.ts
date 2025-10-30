export interface Question {
  id: number;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  completed: boolean;
  description: string;
  examples: {
    input: string;
    output: string;
    explanation?: string;
  }[];
  constraints: string[];
}

export interface QuestionExample {
  input: string;
  output: string;
  explanation?: string;
}