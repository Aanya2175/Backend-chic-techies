// import { ScrollArea } from "@/components/ui/scroll-area";
// import { Badge } from "@/components/ui/badge";

// interface QuestionData {
//   id: number;
//   title: string;
//   difficulty: "Easy" | "Medium" | "Hard";
//   description: string;
//   examples: {
//     input: string;
//     output: string;
//     explanation?: string;
//   }[];
//   constraints: string[];
// }

// interface QuestionDetailProps {
//   question: QuestionData;
// }

// export function QuestionDetail({ question }: QuestionDetailProps) {
//   const getDifficultyColor = (difficulty: string) => {
//     switch (difficulty) {
//       case "Easy":
//         return "bg-success/20 text-success-foreground border-success/40";
//       case "Medium":
//         return "bg-amber-500/20 text-amber-700 border-amber-500/40";
//       case "Hard":
//         return "bg-destructive/20 text-destructive-foreground border-destructive/40";
//       default:
//         return "bg-muted text-muted-foreground";
//     }
//   };

//   return (
//     <ScrollArea className="h-full">
//       <div className="p-6 space-y-6">
//         <div>
//           <div className="flex items-center gap-3 mb-3">
//             <h1 className="text-2xl font-bold text-foreground">
//               {question.id}. {question.title}
//             </h1>
//             <Badge variant="outline" className={getDifficultyColor(question.difficulty)}>
//               {question.difficulty}
//             </Badge>
//           </div>
//           <p className="text-foreground leading-relaxed whitespace-pre-line">
//             {question.description}
//           </p>
//         </div>

//         {question.examples.map((example, index) => (
//           <div key={index} className="bg-muted/50 rounded-lg p-4 space-y-2">
//             <h3 className="font-semibold text-foreground">Example {index + 1}</h3>
//             <div className="space-y-1">
//               <div>
//                 <span className="font-medium text-sm text-muted-foreground">Input: </span>
//                 <code className="text-sm bg-background px-2 py-1 rounded text-foreground">
//                   {example.input}
//                 </code>
//               </div>
//               <div>
//                 <span className="font-medium text-sm text-muted-foreground">Output: </span>
//                 <code className="text-sm bg-background px-2 py-1 rounded text-foreground">
//                   {example.output}
//                 </code>
//               </div>
//               {example.explanation && (
//                 <div>
//                   <span className="font-medium text-sm text-muted-foreground">Explanation: </span>
//                   <span className="text-sm text-foreground">{example.explanation}</span>
//                 </div>
//               )}
//             </div>
//           </div>
//         ))}

//         <div>
//           <h3 className="font-semibold text-foreground mb-2">Constraints</h3>
//           <ul className="list-disc list-inside space-y-1 text-muted-foreground">
//             {question.constraints.map((constraint, index) => (
//               <li key={index} className="text-sm">{constraint}</li>
//             ))}
//           </ul>
//         </div>
//       </div>
//     </ScrollArea>
//   );
// }
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { useEffect, useState } from "react";
import { db } from "@/firebase";
import { doc, getDoc } from "firebase/firestore";

export function QuestionDetail({ questionId }) {
  const [question, setQuestion] = useState(null);

  useEffect(() => {
    const fetchQuestion = async () => {
      const docRef = doc(db, "questions", String(questionId));
      const snap = await getDoc(docRef);
      if (snap.exists()) setQuestion(snap.data());
    };
    fetchQuestion();
  }, [questionId]);

  if (!question) return <div>Loading...</div>;

  return (
    <ScrollArea className="h-full">
      <div className="p-6 space-y-6">
        <div className="flex items-center gap-3 mb-3">
          <h1 className="text-2xl font-bold text-foreground">{question.title}</h1>
          {/* <Badge 
          variant="outline">{question.difficulty}
          </Badge> */}
        </div>
        <p className="text-foreground">{question.description}</p>
      </div>
    </ScrollArea>
  );
}
