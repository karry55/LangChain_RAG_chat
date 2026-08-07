import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { register } from '../../api/auth';
import { useAuthStore } from '../../stores/authStore';

const { Title, Text } = Typography;

export default function Register() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const authLogin = useAuthStore((s) => s.login);

  const onFinish = async (values: { username: string; password: string; email?: string }) => {
    if (values.password.length < 6) {
      message.error('密码至少 6 位');
      return;
    }
    setLoading(true);
    try {
      const res = await register(values);
      authLogin(res.access_token, res.user);
      message.success('注册成功！');
      navigate('/chat');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '注册失败');
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
          <Title level={2} style={{ marginBottom: 4 }}>📝 创建账号</Title>
          <Text type="secondary">注册后即可使用知识库问答</Text>
        </div>

        <Form layout="vertical" onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, min: 2, message: '用户名至少 2 个字符' }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名" />
          </Form.Item>

          <Form.Item name="email">
            <Input prefix={<MailOutlined />} placeholder="邮箱 (选填)" />
          </Form.Item>

          <Form.Item name="password" rules={[{ required: true, min: 6, message: '密码至少 6 位' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码" />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) return Promise.resolve();
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              注 册
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center' }}>
          <Text>已有账号？</Text>
          <Link to="/login">立即登录</Link>
        </div>
      </Card>
    </div>
  );
}
