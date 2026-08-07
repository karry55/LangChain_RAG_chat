import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { login } from '../../api/auth';
import { useAuthStore } from '../../stores/authStore';

const { Title, Text } = Typography;

export default function Login() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const authLogin = useAuthStore((s) => s.login);

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const res = await login(values);
      authLogin(res.access_token, res.user);
      message.success(`欢迎回来，${res.user.username}！`);
      navigate('/chat');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    }}>
      <Card style={{ width: 400, borderRadius: 12, boxShadow: '0 8px 24px rgba(0,0,0,0.15)' }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <Title level={2} style={{ marginBottom: 4 }}>📚 知识库问答系统</Title>
          <Text type="secondary">基于 LangChain + RAG 的智能问答</Text>
        </div>

        <Form layout="vertical" onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: '请输入用户名' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, message: '请输入密码' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              登 录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center' }}>
          <Text>还没有账号？</Text>
          <Link to="/register">立即注册</Link>
        </div>

        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            管理员账户：admin / 123456
          </Text>
        </div>
      </Card>
    </div>
  );
}
