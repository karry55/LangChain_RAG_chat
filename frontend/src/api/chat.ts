import client from './client';

export interface Conversation {
  id: string;
  title: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: SourceItem[] | null;
  token_count: number;
  feedback: string | null;
  created_at: string;
}

export interface SourceItem {
  document_title: string;
  chunk_index: number;
  content: string;
  score: number;
}

export interface ChatRequest {
  conversation_id: string | null;
  message: string;
  top_k?: number;
}

// SSE 流式对话
export function chatQuery(
  params: ChatRequest,
  onToken: (token: string, conversationId: string) => void,
  onSources: (sources: SourceItem[]) => void,
  onDone: (fullContent: string, sources: SourceItem[]) => void,
  onError: (err: string) => void,
): AbortController {
  const controller = new AbortController();
  const token = localStorage.getItem('token');

  fetch('/api/chat/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(params),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        const err = await response.json();
        onError(err.detail || '请求失败');
        return;
      }

      const reader = response.body?.getReader();
      if (!reader) {
        onError('无法读取响应流');
        return;
      }

      const decoder = new TextDecoder();
      let buffer = '';
      let accumulatedContent = '';
      let finalSources: SourceItem[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'token') {
                accumulatedContent += data.content;
                onToken(data.content, data.conversation_id);
              } else if (data.type === 'sources') {
                finalSources = data.sources || [];
                onSources(data.sources || []);
              } else if (data.type === 'done') {
                onDone(accumulatedContent, finalSources);
              } else if (data.type === 'error') {
                onError(data.content);
              }
            } catch {
              // 忽略 JSON 解析错误
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError(err.message || '网络错误');
      }
    });

  return controller;
}

// 会话管理
export async function getConversations(page = 1, pageSize = 50) {
  const res = await client.get('/conversations', { params: { page, page_size: pageSize } });
  return res.data;
}

export async function getMessages(conversationId: string, page = 1, pageSize = 100) {
  const res = await client.get(`/conversations/${conversationId}/messages`, {
    params: { page, page_size: pageSize },
  });
  return res.data;
}

export async function deleteConversation(conversationId: string) {
  const res = await client.delete(`/conversations/${conversationId}`);
  return res.data;
}

// 反馈
export async function sendFeedback(messageId: string, feedback: 'like' | 'dislike') {
  const res = await client.post('/chat/feedback', { message_id: messageId, feedback });
  return res.data;
}
