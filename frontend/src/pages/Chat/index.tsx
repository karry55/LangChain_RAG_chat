import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout, Input, Button, Spin, Empty, Typography } from 'antd';
import { SendOutlined, PlusOutlined, StopOutlined } from '@ant-design/icons';
import { useChatStore } from '../../stores/chatStore';
import { chatQuery, getConversations, getMessages, deleteConversation } from '../../api/chat';
import type { Message, SourceItem } from '../../api/chat';
import ConversationList from './components/ConversationList';
import MessageBubble from './components/MessageBubble';
import SourceCard from './components/SourceCard';

const { Sider, Content } = Layout;
const { Text } = Typography;

export default function Chat() {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const store = useChatStore();
  const [inputValue, setInputValue] = useState('');
  const [initialLoading, setInitialLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // 切换会话时加载消息（流式输出中不加载，避免覆盖实时内容）
  useEffect(() => {
    if (store.isStreaming) return;
    if (conversationId) {
      if (conversationId === store.currentConversationId) return;
      store.setCurrentConversation(conversationId);
      setInitialLoading(true);
      getMessages(conversationId)
        .then((data) => store.setMessages(data.messages || []))
        .catch(() => store.setMessages([]))
        .finally(() => setInitialLoading(false));
    } else if (!store.isStreaming) {
      store.setMessages([]);
      store.setCurrentConversation(null);
    }
  }, [conversationId]);

  // 首次加载会话列表
  useEffect(() => {
    getConversations()
      .then((data) => store.setConversations(data.conversations || []))
      .catch(() => {});
  }, []);

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [store.messages, store.streamingContent]);

  const handleSend = () => {
    const msg = inputValue.trim();
    if (!msg || store.isStreaming) return;
    setInputValue('');

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      conversation_id: store.currentConversationId || '',
      role: 'user',
      content: msg,
      sources: null,
      token_count: 0,
      feedback: null,
      created_at: new Date().toISOString(),
    };
    store.addMessage(userMsg);
    store.abortController?.abort();
    store.resetStream();
    store.setStreaming(true);

    const ctrl = chatQuery(
      { conversation_id: store.currentConversationId, message: msg },
      (token, convId) => {
        store.appendStreamToken(token);
        if (convId && !store.currentConversationId) {
          store.setCurrentConversation(convId);
          navigate(`/chat/${convId}`, { replace: true });
        }
      },
      (sources: SourceItem[]) => store.setSources(sources),
      (fullContent: string, finalSources: SourceItem[]) => {
        // onDone: 使用 chatQuery 本地累积的内容，避免 Zustand 快照问题
        const convId = store.currentConversationId || '';
        if (fullContent) {
          store.addMessage({
            id: `ai-${Date.now()}`,
            conversation_id: convId,
            role: 'assistant',
            content: fullContent,
            sources: finalSources,
            token_count: fullContent.length,
            feedback: null,
            created_at: new Date().toISOString(),
          });
        }
        store.resetStream();
        getConversations()
          .then((data) => store.setConversations(data.conversations || []))
          .catch(() => {});
      },
      (err: string) => {
        store.addMessage({
          id: `err-${Date.now()}`,
          conversation_id: store.currentConversationId || '',
          role: 'assistant',
          content: `❌ ${err}`,
          sources: null,
          token_count: 0,
          feedback: null,
          created_at: new Date().toISOString(),
        });
        store.resetStream();
      },
    );

    store.setAbortController(ctrl);
  };

  const handleStop = () => {
    store.abortController?.abort();
    store.resetStream();
  };

  const handleNewChat = () => {
    store.setMessages([]);
    store.setCurrentConversation(null);
    store.resetStream();
    navigate('/chat');
  };

  const handleSelectConversation = (id: string) => {
    navigate(`/chat/${id}`);
  };

  const handleDeleteConversation = async (convId: string) => {
    try {
      await deleteConversation(convId);
      if (store.currentConversationId === convId) handleNewChat();
      getConversations()
        .then((data) => store.setConversations(data.conversations || []))
        .catch(() => {});
    } catch { /* ignore */ }
  };

  const displayMessages: (Message & { isStreaming?: boolean })[] = [
    ...store.messages,
    ...(store.isStreaming && store.streamingContent
      ? [{
          id: 'streaming', conversation_id: '', role: 'assistant' as const,
          content: store.streamingContent, sources: store.currentSources,
          token_count: 0, feedback: null, created_at: '', isStreaming: true,
        }]
      : []),
  ];

  return (
    <Layout style={{ height: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
      <Sider width={280} style={{ background: '#fff', borderRight: '1px solid #f0f0f0', overflow: 'auto' }}>
        <div style={{ padding: 12 }}>
          <Button type="primary" icon={<PlusOutlined />} block onClick={handleNewChat}>新建对话</Button>
        </div>
        <ConversationList
          conversations={store.conversations}
          currentId={store.currentConversationId}
          onSelect={handleSelectConversation}
          onDelete={handleDeleteConversation}
        />
      </Sider>

      <Content style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ flex: 1, overflow: 'auto', padding: '24px 32px' }}>
          {initialLoading ? (
            <div style={{ textAlign: 'center', paddingTop: 100 }}><Spin size="large" /></div>
          ) : displayMessages.length === 0 ? (
            <div style={{ textAlign: 'center', paddingTop: 100 }}>
              <Empty description={<div>
                <div style={{ fontSize: 18, marginBottom: 8 }}>👋 欢迎使用知识库问答</div>
                <Text type="secondary">在下方输入你的问题，AI 将基于知识库为你提供答案</Text>
              </div>} />
            </div>
          ) : (
            displayMessages.map((msg, idx) => (
              <div key={msg.id || idx}>
                <MessageBubble message={msg} isStreaming={msg.isStreaming} />
                {msg.role === 'assistant' && !msg.isStreaming && msg.sources && msg.sources.length > 0 && (
                  <SourceCard sources={msg.sources} />
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={{ padding: '16px 32px 24px', borderTop: '1px solid #f0f0f0', background: '#fff' }}>
          <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', gap: 12 }}>
            <Input.TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={(e) => { if (!e.shiftKey) { e.preventDefault(); handleSend(); } }}
              placeholder="输入你的问题，按 Enter 发送，Shift+Enter 换行..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={store.isStreaming}
              style={{ flex: 1 }}
            />
            {store.isStreaming ? (
              <Button type="primary" danger icon={<StopOutlined />} onClick={handleStop}>停止</Button>
            ) : (
              <Button type="primary" icon={<SendOutlined />} onClick={handleSend} disabled={!inputValue.trim()}>发送</Button>
            )}
          </div>
        </div>
      </Content>
    </Layout>
  );
}
