export interface Message {
  id: number;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isOpen: boolean;
  isLoading: boolean;
}