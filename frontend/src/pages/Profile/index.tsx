import { useState } from 'react';
import { Card, Form, Input, Button, Typography, message } from 'antd';
import { LockOutlined } from '@ant-design/icons';
import { changePassword } from '../../api/auth';

const { Title } = Typography;

export default function Profile() {
  const [loading, setLoading] = useState(false);

  const handleChangePassword = async (values: { old_password: string; new_password: string }) => {
    if (values.new_password.length < 6) {
      message.error('新密码至少 6 位');
      return;
    }
    setLoading(true);
    try {
      await changePassword(values);
      message.success('密码修改成功！');
    } catch (err: any) {
      message.error(err.response?.data?.detail || '修改失败');
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: 24, maxWidth: 600, margin: '0 auto' }}>
      <Title level={4} style={{ marginBottom: 24 }}>⚙️ 个人设置</Title>

      <Card title="修改密码" style={{ borderRadius: 12 }}>
        <Form layout="vertical" onFinish={handleChangePassword} size="large">
          <Form.Item
            name="old_password"
            label="旧密码"
            rules={[{ required: true, message: '请输入旧密码' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="输入旧密码" />
          </Form.Item>

          <Form.Item
            name="new_password"
            label="新密码"
            rules={[{ required: true, min: 6, message: '新密码至少 6 位' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="输入新密码 (至少6位)" />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认新密码"
            dependencies={['new_password']}
            rules={[
              { required: true, message: '请确认新密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('new_password') === value) return Promise.resolve();
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="再次输入新密码" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              修改密码
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
