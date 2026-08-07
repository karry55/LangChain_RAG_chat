import { useEffect, useState } from 'react';
import {
  Table, Button, Upload, Tag, Space, message, Typography, Card, Row, Col, Statistic,
} from 'antd';
import {
  UploadOutlined, DeleteOutlined, FileTextOutlined, ReloadOutlined,
  DatabaseOutlined, FileDoneOutlined, FileExcelOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getDocuments, uploadDocument, deleteDocument, getKnowledgeStats } from '../../api/knowledge';
import type { DocumentItem, KnowledgeStats } from '../../api/knowledge';

const { Title } = Typography;

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [stats, setStats] = useState<KnowledgeStats | null>(null);

  useEffect(() => {
    loadDocuments();
    loadStats();
  }, []);

  // 自动刷新处理中的文档
  useEffect(() => {
    const hasProcessing = documents.some((d) => d.status === 'processing' || d.status === 'pending');
    if (!hasProcessing) return;
    const timer = setInterval(() => {
      loadDocuments();
      loadStats();
    }, 3000);
    return () => clearInterval(timer);
  }, [documents]);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
      setTotal(data.total || 0);
    } catch {
      // ignore
    }
    setLoading(false);
  };

  const loadStats = async () => {
    try {
      const data = await getKnowledgeStats();
      setStats(data);
    } catch {
      // ignore
    }
  };

  const handleUpload = async (file: File) => {
    setUploading(true);
    try {
      const res = await uploadDocument(file);
      message.success(res.message || '上传成功');
      loadDocuments();
      loadStats();
    } catch (err: any) {
      message.error(err.response?.data?.detail || '上传失败');
    }
    setUploading(false);
    return false; // 阻止默认上传行为
  };

  const handleDelete = async (docId: string) => {
    try {
      await deleteDocument(docId);
      message.success('文档已删除');
      loadDocuments();
      loadStats();
    } catch {
      message.error('删除失败');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const statusMap: Record<string, { color: string; text: string }> = {
    pending: { color: 'default', text: '等待处理' },
    processing: { color: 'processing', text: '处理中' },
    completed: { color: 'success', text: '已完成' },
    failed: { color: 'error', text: '失败' },
  };

  const columns: ColumnsType<DocumentItem> = [
    { title: '文档名称', dataIndex: 'title', key: 'title', ellipsis: true,
      render: (t: string) => <><FileTextOutlined style={{ marginRight: 8 }} />{t}</> },
    { title: '类型', dataIndex: 'file_type', key: 'file_type', width: 80,
      render: (t: string) => <Tag>.{t}</Tag> },
    { title: '大小', dataIndex: 'file_size', key: 'file_size', width: 100,
      render: (v: number) => formatFileSize(v) },
    { title: '状态', dataIndex: 'status', key: 'status', width: 100,
      render: (s: string) => {
        const info = statusMap[s] || { color: 'default', text: s };
        return <Tag color={info.color}>{info.text}</Tag>;
      } },
    { title: '分块数', dataIndex: 'chunk_count', key: 'chunk_count', width: 80 },
    { title: '上传时间', dataIndex: 'created_at', key: 'created_at', width: 180,
      render: (t: string) => new Date(t).toLocaleString('zh-CN') },
    {
      title: '操作', key: 'actions', width: 100,
      render: (_, record) => (
        <Button
          type="text"
          danger
          icon={<DeleteOutlined />}
          onClick={() => handleDelete(record.id)}
          disabled={record.status === 'processing'}
        >
          删除
        </Button>
      ),
    },
  ];

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Title level={4} style={{ marginBottom: 24 }}>📚 知识库管理</Title>

      {/* 统计概览 */}
      {stats && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card><Statistic title="文档总数" value={stats.total_documents} prefix={<DatabaseOutlined />} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="已处理" value={stats.processed_documents} prefix={<FileDoneOutlined />} valueStyle={{ color: '#52c41a' }} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="总切块数" value={stats.total_chunks} prefix={<FileExcelOutlined />} /></Card>
          </Col>
          <Col span={6}>
            <Card><Statistic title="总大小" value={formatFileSize(stats.total_file_size)} prefix={<DatabaseOutlined />} /></Card>
          </Col>
        </Row>
      )}

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <Upload
            accept=".pdf,.docx,.xlsx,.csv,.txt,.md"
            showUploadList={false}
            beforeUpload={(file) => { handleUpload(file); return false; }}
          >
            <Button type="primary" icon={<UploadOutlined />} loading={uploading}>
              上传文档
            </Button>
          </Upload>
          <Button icon={<ReloadOutlined />} onClick={() => { loadDocuments(); loadStats(); }}>
            刷新
          </Button>
        </Space>
        <span style={{ marginLeft: 16, color: '#999', fontSize: 12 }}>
          支持 PDF、Word、Excel、CSV、TXT、Markdown 格式，最大 50MB
        </span>
      </Card>

      {/* 文档列表 */}
      <Card>
        <Table
          columns={columns}
          dataSource={documents}
          rowKey="id"
          loading={loading}
          pagination={{ total, pageSize: 20, showTotal: (t) => `共 ${t} 个文档` }}
        />
      </Card>
    </div>
  );
}
