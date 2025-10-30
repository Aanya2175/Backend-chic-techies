import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { CheckCircle2, XCircle, Lock } from "lucide-react";

interface TestCase {
  id: number;
  status: "passed" | "failed" | "locked";
  input?: string;
  output?: string;
  expected?: string;
  visible: boolean;
}

interface TestResultsProps {
  testCases: TestCase[];
  customInput: string;
  customOutput: string;
  onCustomInputChange: (value: string) => void;
}

export function TestResults({ 
  testCases, 
  customInput, 
  customOutput,
  onCustomInputChange 
}: TestResultsProps) {
  const passedCount = testCases.filter(tc => tc.status === "passed").length;
  const totalVisible = testCases.filter(tc => tc.visible).length;

  return (
    <div className="h-full bg-card flex flex-col">
      <Tabs defaultValue="results" className="flex-1 flex flex-col">
        <div className="border-b border-border px-4 pt-3">
          <TabsList className="bg-muted">
            <TabsTrigger value="results">Test Results</TabsTrigger>
            <TabsTrigger value="custom">Custom Input</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="results" className="flex-1 m-0">
          <ScrollArea className="h-full">
            <div className="p-4">
              {passedCount === totalVisible && totalVisible > 0 && (
                <div className="mb-4 p-3 bg-success/10 border border-success/30 rounded-lg">
                  <p className="text-success font-medium flex items-center gap-2">
                    <CheckCircle2 className="h-5 w-5" />
                    Compiled successfully. All available test cases passed
                  </p>
                </div>
              )}

              <div className="space-y-3">
                {testCases.map((testCase) => (
                  <div
                    key={testCase.id}
                    className="border border-border rounded-lg p-4 bg-background"
                  >
                    <div className="flex items-center gap-2 mb-3">
                      {testCase.status === "passed" && (
                        <CheckCircle2 className="h-5 w-5 text-success" />
                      )}
                      {testCase.status === "failed" && (
                        <XCircle className="h-5 w-5 text-destructive" />
                      )}
                      {testCase.status === "locked" && (
                        <Lock className="h-5 w-5 text-muted-foreground" />
                      )}
                      <span className="font-medium text-foreground">Test case {testCase.id}</span>
                      <Badge
                        variant="outline"
                        className={
                          testCase.status === "passed"
                            ? "bg-success/20 text-success border-success/40"
                            : testCase.status === "failed"
                            ? "bg-destructive/20 text-destructive border-destructive/40"
                            : "bg-muted text-muted-foreground"
                        }
                      >
                        {testCase.status}
                      </Badge>
                    </div>

                    {testCase.visible && (
                      <div className="space-y-2 text-sm">
                        <div>
                          <span className="text-muted-foreground">Input (stdin): </span>
                          <pre className="mt-1 p-2 bg-muted rounded text-foreground">
                            {testCase.input}
                          </pre>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Your Output (stdout): </span>
                          <pre className="mt-1 p-2 bg-muted rounded text-foreground">
                            {testCase.output}
                          </pre>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Expected Output: </span>
                          <pre className="mt-1 p-2 bg-muted rounded text-foreground">
                            {testCase.expected}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </ScrollArea>
        </TabsContent>

        <TabsContent value="custom" className="flex-1 m-0">
          <div className="p-4 h-full flex flex-col gap-4">
            <div className="flex-1">
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Input (stdin)
              </label>
              <textarea
                value={customInput}
                onChange={(e) => onCustomInputChange(e.target.value)}
                className="w-full h-32 p-3 bg-muted border border-border rounded-lg font-mono text-sm resize-none focus:outline-none focus:ring-2 focus:ring-ring"
                placeholder="Enter your custom input here..."
              />
            </div>
            <div className="flex-1">
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Your Output (stdout)
              </label>
              <pre className="w-full h-32 p-3 bg-background border border-border rounded-lg font-mono text-sm overflow-auto">
                {customOutput || "Run your code to see output"}
              </pre>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
