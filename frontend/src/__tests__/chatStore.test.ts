import { describe, it, expect, beforeEach } from 'vitest';
import { useChatStore } from '../stores/chatStore';

describe('chatStore', () => {
  beforeEach(() => {
    useChatStore.setState({
      conversations: [],
      currentConversationId: null,
      messages: [],
      isStreaming: false,
      streamingContent: '',
      currentSources: [],
      abortController: null,
    });
  });

  describe('初始状态', () => {
    it('初始时所有状态为空', () => {
      const s = useChatStore.getState();
      expect(s.conversations).toEqual([]);
      expect(s.messages).toEqual([]);
      expect(s.isStreaming).toBe(false);
      expect(s.streamingContent).toBe('');
      expect(s.currentSources).toEqual([]);
      expect(s.currentConversationId).toBeNull();
      expect(s.abortController).toBeNull();
    });
  });

  describe('会话管理', () => {
    it('设置会话列表', () => {
      const convs = [
        { id: 'c1', title: '第一个会话', message_count: 3, created_at: '', updated_at: '' },
        { id: 'c2', title: '第二个会话', message_count: 1, created_at: '', updated_at: '' },
      ];
      useChatStore.getState().setConversations(convs);
      expect(useChatStore.getState().conversations).toHaveLength(2);
    });

    it('设置当前会话 ID', () => {
      useChatStore.getState().setCurrentConversation('conv_123');
      expect(useChatStore.getState().currentConversationId).toBe('conv_123');
    });

    it('清空当前会话', () => {
      useChatStore.getState().setCurrentConversation('conv_456');
      useChatStore.getState().setCurrentConversation(null);
      expect(useChatStore.getState().currentConversationId).toBeNull();
    });
  });

  describe('消息管理', () => {
    it('设置消息列表', () => {
      const msgs = [
        { id: 'm1', conversation_id: 'c1', role: 'user' as const, content: '你好', sources: null, token_count: 0, feedback: null, created_at: '' },
        { id: 'm2', conversation_id: 'c1', role: 'assistant' as const, content: '你好！', sources: null, token_count: 0, feedback: null, created_at: '' },
      ];
      useChatStore.getState().setMessages(msgs);
      expect(useChatStore.getState().messages).toHaveLength(2);
    });

    it('添加新消息', () => {
      useChatStore.getState().addMessage({
        id: 'm3',
        conversation_id: 'c1',
        role: 'user',
        content: '问题',
        sources: null,
        token_count: 0,
        feedback: null,
        created_at: '',
      });
      useChatStore.getState().addMessage({
        id: 'm4',
        conversation_id: 'c1',
        role: 'assistant',
        content: '答案',
        sources: [],
        token_count: 10,
        feedback: null,
        created_at: '',
      });
      expect(useChatStore.getState().messages).toHaveLength(2);
      expect(useChatStore.getState().messages[0].content).toBe('问题');
      expect(useChatStore.getState().messages[1].content).toBe('答案');
    });
  });

  describe('流式生成状态', () => {
    it('流式开始和结束', () => {
      useChatStore.getState().setStreaming(true);
      expect(useChatStore.getState().isStreaming).toBe(true);

      useChatStore.getState().setStreaming(false);
      expect(useChatStore.getState().isStreaming).toBe(false);
    });

    it('逐步追加流式 token', () => {
      useChatStore.getState().appendStreamToken('你好');
      useChatStore.getState().appendStreamToken('，');
      useChatStore.getState().appendStreamToken('世界');
      expect(useChatStore.getState().streamingContent).toBe('你好，世界');
    });

    it('设置引用来源', () => {
      const sources = [
        { document_title: 'doc1.md', chunk_index: 0, content: '内容片段', score: 0.92 },
      ];
      useChatStore.getState().setSources(sources);
      expect(useChatStore.getState().currentSources).toHaveLength(1);
      expect(useChatStore.getState().currentSources[0].document_title).toBe('doc1.md');
    });

    it('resetStream 清空流式内容但保留消息', () => {
      useChatStore.getState().addMessage({
        id: 'm5', conversation_id: 'c1', role: 'user', content: '问题',
        sources: null, token_count: 0, feedback: null, created_at: '',
      });
      useChatStore.getState().appendStreamToken('流式内容');
      useChatStore.getState().setSources([{ document_title: 'd', chunk_index: 0, content: 'c', score: 1.0 }]);
      useChatStore.getState().setStreaming(true);

      // 重置
      useChatStore.getState().resetStream();

      expect(useChatStore.getState().streamingContent).toBe('');
      expect(useChatStore.getState().currentSources).toEqual([]);
      expect(useChatStore.getState().isStreaming).toBe(false);
      // 消息不应被清除
      expect(useChatStore.getState().messages).toHaveLength(1);
    });
  });

  describe('中断控制', () => {
    it('设置和清除 AbortController', () => {
      const ctrl = new AbortController();
      useChatStore.getState().setAbortController(ctrl);
      expect(useChatStore.getState().abortController).not.toBeNull();

      useChatStore.getState().setAbortController(null);
      expect(useChatStore.getState().abortController).toBeNull();
    });
  });
});
