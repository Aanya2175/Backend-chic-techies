import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Play, TestTube2, Send } from "lucide-react";

interface CodeEditorProps {
  code: string;
  language: string;
  onCodeChange: (code: string) => void;
  onLanguageChange: (language: string) => void;
  onRunCode: () => void;
  onRunTests: () => void;
  onSubmit: () => void;
  isRunning: boolean;
}

export function CodeEditor({
  code,
  language,
  onCodeChange,
  onLanguageChange,
  onRunCode,
  onRunTests,
  onSubmit,
  isRunning
}: CodeEditorProps) {
  return (
    <div className="flex flex-col h-full bg-card">
      <div className="flex items-center justify-between p-3 border-b border-border bg-muted/30">
        <Select value={language} onValueChange={onLanguageChange}>
          <SelectTrigger className="w-48 bg-background">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="python3">Python 3</SelectItem>
            <SelectItem value="javascript">JavaScript</SelectItem>
            <SelectItem value="java">Java</SelectItem>
            <SelectItem value="cpp">C++</SelectItem>
            <SelectItem value="c">C</SelectItem>
          </SelectContent>
        </Select>
        
        <div className="flex gap-2">
          <Button
            onClick={onRunCode}
            disabled={isRunning}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <Play className="h-4 w-4" />
            Run Code
          </Button>
          <Button
            onClick={onRunTests}
            disabled={isRunning}
            variant="outline"
            size="sm"
            className="gap-2"
          >
            <TestTube2 className="h-4 w-4" />
            Run Tests
          </Button>
          <Button
            onClick={onSubmit}
            disabled={isRunning}
            size="sm"
            className="gap-2 bg-success hover:bg-success/90 text-success-foreground"
          >
            <Send className="h-4 w-4" />
            Submit
          </Button>
        </div>
      </div>
      
      <div className="flex-1 relative">
        <textarea
          value={code}
          onChange={(e) => onCodeChange(e.target.value)}
          className="w-full h-full p-4 bg-editor text-editor-foreground font-mono text-sm resize-none focus:outline-none"
          style={{ lineHeight: "1.6" }}
          spellCheck={false}
          placeholder="# Write your code here..."
        />
      </div>
    </div>
  );
}
