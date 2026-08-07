import { create } from 'zustand';
import type { Conversation, Message, SourceItem } from '../api/chat';

interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  streamingContent: string;
  currentSources: SourceItem[];
  abortController: AbortController | null;

  setConversations: (convs: Conversation[]) => void;
  setCurrentConversation: (id: string | null) => void;
  setMessages: (msgs: Message[]) => void;
  addMessage: (msg: Message) => void;
  setStreaming: (v: boolean) => void;
  appendStreamToken: (token: string) => void;
  setSources: (sources: SourceItem[]) => void;
  setAbortController: (ctrl: AbortController | null) => void;
  resetStream: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  conversations: [],
  currentConversationId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  currentSources: [],
  abortController: null,

  setConversations: (convs) => set({ conversations: convs }),
  setCurrentConversation: (id) => set({ currentConversationId: id }),
  setMessages: (msgs) => set({ messages: msgs }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setStreaming: (v) => set({ isStreaming: v }),
  appendStreamToken: (token) =>
    set((s) => ({ streamingContent: s.streamingContent + token })),
  setSources: (sources) => set({ currentSources: sources }),
  setAbortController: (ctrl) => set({ abortController: ctrl }),
  resetStream: () => set({ streamingContent: '', currentSources: [], isStreaming: false, abortController: null }),
}));
