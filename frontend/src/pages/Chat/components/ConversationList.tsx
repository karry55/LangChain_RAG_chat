import { List, Typography, Popconfirm } from 'antd';
import { MessageOutlined, DeleteOutlined } from '@ant-design/icons';
import type { Conversation } from '../../../api/chat';

const { Text } = Typography;

interface Props {
  conversations: Conversation[];
  currentId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function ConversationList({ conversations, currentId, onSelect, onDelete }: Props) {
  return (
    <List
      dataSource={conversations}
      locale={{ emptyText: '暂无会话' }}
      renderItem={(conv) => (
        <List.Item
          onClick={() => onSelect(conv.id)}
          style={{
            cursor: 'pointer',
            padding: '12px 16px',
            background: conv.id === currentId ? '#e6f4ff' : 'transparent',
            borderLeft: conv.id === currentId ? '3px solid #1677ff' : '3px solid transparent',
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = conv.id === currentId ? '#e6f4ff' : '#fafafa')}
          onMouseLeave={(e) => (e.currentTarget.style.background = conv.id === currentId ? '#e6f4ff' : 'transparent')}
        >
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <MessageOutlined style={{ color: '#1677ff', fontSize: 12 }} />
              <Text ellipsis style={{ flex: 1, fontSize: 14 }}>
                {conv.title}
              </Text>
            </div>
            <Text type="secondary" style={{ fontSize: 11, marginLeft: 20 }}>
              {conv.message_count} 条消息
            </Text>
          </div>
          <Popconfirm
            title="确定删除这个会话？"
            onConfirm={(e) => {
              e?.stopPropagation();
              onDelete(conv.id);
            }}
            onCancel={(e) => e?.stopPropagation()}
          >
            <DeleteOutlined
              onClick={(e) => e.stopPropagation()}
              style={{ color: '#999', fontSize: 14, padding: 4 }}
            />
          </Popconfirm>
        </List.Item>
      )}
    />
  );
}
