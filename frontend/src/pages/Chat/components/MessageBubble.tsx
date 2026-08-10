import { Avatar, Typography } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { Message } from '../../../api/chat';

const { Text } = Typography;

interface Props {
  message: Message & { isStreaming?: boolean };
  isStreaming?: boolean;
}

/** 格式化时间显示 */
function formatTime(isoStr: string): string {
  if (!isoStr) return '';
  const date = new Date(isoStr);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  const hours = date.getHours().toString().padStart(2, '0');
  const minutes = date.getMinutes().toString().padStart(2, '0');
  if (isToday) {
    return `${hours}:${minutes}`;
  }
  const month = (date.getMonth() + 1).toString().padStart(2, '0');
  const day = date.getDate().toString().padStart(2, '0');
  return `${month}-${day} ${hours}:${minutes}`;
}

export default function MessageBubble({ message, isStreaming }: Props) {
  const isUser = message.role === 'user';
  const timeStr = isStreaming ? '' : formatTime(message.created_at);

  return (
    <div style={{
      display: 'flex',
      gap: 12,
      marginBottom: 20,
      flexDirection: isUser ? 'row-reverse' : 'row',
      maxWidth: '90%',
      marginLeft: isUser ? 'auto' : 0,
      marginRight: isUser ? 0 : 'auto',
    }}>
      <Avatar
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{
          backgroundColor: isUser ? '#1677ff' : '#52c41a',
          flexShrink: 0,
        }}
      />
      <div>
        <div style={{
          background: isUser ? '#1677ff' : '#fff',
          color: isUser ? '#fff' : '#333',
          padding: '12px 16px',
          borderRadius: 12,
          borderTopRightRadius: isUser ? 4 : 12,
          borderTopLeftRadius: isUser ? 12 : 4,
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
          minWidth: 60,
        }}>
          {isUser ? (
            <div style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {message.content}
            </div>
          ) : (
            <div className="markdown-content" style={{ lineHeight: 1.7 }}>
              {isStreaming && message.content === '' ? (
                <Text type="secondary">思考中...</Text>
              ) : (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {message.content}
                </ReactMarkdown>
              )}
              {isStreaming && (
                <span className="cursor-blink" style={{
                  display: 'inline-block',
                  width: 2,
                  height: 18,
                  background: '#1677ff',
                  marginLeft: 2,
                  verticalAlign: 'text-bottom',
                }} />
              )}
            </div>
          )}
        </div>
        {/* 时间戳 */}
        {timeStr && (
          <div style={{
            textAlign: isUser ? 'right' : 'left',
            marginTop: 4,
            paddingLeft: 4,
            paddingRight: 4,
          }}>
            <Text type="secondary" style={{ fontSize: 11 }}>
              {timeStr}
            </Text>
          </div>
        )}
      </div>
    </div>
  );
}
