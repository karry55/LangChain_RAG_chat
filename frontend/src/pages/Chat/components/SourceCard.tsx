import { Card, Tag, Typography } from 'antd';
import { LinkOutlined, FileTextOutlined } from '@ant-design/icons';
import type { SourceItem } from '../../../api/chat';

const { Text, Paragraph } = Typography;

interface Props {
  sources: SourceItem[];
}

export default function SourceCard({ sources }: Props) {
  if (!sources || sources.length === 0) return null;

  return (
    <div style={{ maxWidth: '85%', marginBottom: 20, marginLeft: 44 }}>
      <Card
        size="small"
        title={
          <span>
            <LinkOutlined style={{ marginRight: 8 }} />
            参考来源 ({sources.length})
          </span>
        }
        style={{
          borderRadius: 12,
          background: '#fafafa',
          border: '1px solid #f0f0f0',
        }}
      >
        {sources.map((source, idx) => (
          <div key={idx} style={{ marginBottom: idx < sources.length - 1 ? 12 : 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
              <Tag color="blue">来源 {idx + 1}</Tag>
              <FileTextOutlined style={{ color: '#999', fontSize: 12 }} />
              <Text strong style={{ fontSize: 13 }}>{source.document_title}</Text>
              <Text type="secondary" style={{ fontSize: 12 }}>
                片段 {source.chunk_index} · 相关度 {source.score.toFixed(2)}
              </Text>
            </div>
            <Paragraph
              ellipsis={{ rows: 2, expandable: true, symbol: '展开' }}
              style={{
                margin: 0,
                padding: '8px 12px',
                background: '#fff',
                borderRadius: 8,
                fontSize: 12,
                color: '#666',
                border: '1px solid #f5f5f5',
              }}
            >
              {source.content}
            </Paragraph>
          </div>
        ))}
      </Card>
    </div>
  );
}
