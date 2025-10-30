import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, Circle } from "lucide-react";

interface Question {
  id: number;
  title: string;
  difficulty: "Easy" | "Medium" | "Hard";
  completed: boolean;
}

interface QuestionSidebarProps {
  questions: Question[];
  activeQuestionId: number;
  onQuestionSelect: (id: number) => void;
}

export function QuestionSidebar({ questions, activeQuestionId, onQuestionSelect }: QuestionSidebarProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "Easy":
        return "bg-success/20 text-success-foreground border-success/40";
      case "Medium":
        return "bg-amber-500/20 text-amber-700 border-amber-500/40";
      case "Hard":
        return "bg-destructive/20 text-destructive-foreground border-destructive/40";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="w-80 border-r border-border bg-card h-full flex flex-col">
      <div className="p-4 border-b border-border">
        <h2 className="text-lg font-semibold text-foreground">Questions</h2>
        <p className="text-sm text-muted-foreground mt-1">
          {questions.filter(q => q.completed).length} / {questions.length} completed
        </p>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-2">
          {questions.map((question) => (
            <button
              key={question.id}
              onClick={() => onQuestionSelect(question.id)}
              className={`w-full text-left p-3 rounded-lg mb-2 transition-all hover:bg-accent/50 ${
                activeQuestionId === question.id 
                  ? "bg-accent border border-accent-foreground/20" 
                  : "bg-background border border-border"
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div className="flex items-center gap-2 flex-1">
                  {question.completed ? (
                    <CheckCircle2 className="h-5 w-5 text-success flex-shrink-0" />
                  ) : (
                    <Circle className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                  )}
                  <span className="font-medium text-sm text-foreground line-clamp-2">
                    {question.id}. {question.title}
                  </span>
                </div>
              </div>
              <Badge variant="outline" className={`text-xs ${getDifficultyColor(question.difficulty)}`}>
                {question.difficulty}
              </Badge>
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
