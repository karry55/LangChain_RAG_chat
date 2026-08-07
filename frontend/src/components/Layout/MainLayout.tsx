import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Space, Avatar, Dropdown } from 'antd';
import {
  MessageOutlined,
  DatabaseOutlined,
  UserOutlined,
  LogoutOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../../stores/authStore';

const { Header, Content } = Layout;

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isAdmin, logout } = useAuthStore();

  const selectedKey = location.pathname.startsWith('/knowledge') ? 'knowledge' : 'chat';

  const menuItems = [
    { key: 'chat', icon: <MessageOutlined />, label: '智能问答', path: '/chat' },
  ];

  if (isAdmin) {
    menuItems.push({ key: 'knowledge', icon: <DatabaseOutlined />, label: '知识库管理', path: '/knowledge' });
  }

  const dropdownItems = [
    { key: 'profile', icon: <SettingOutlined />, label: '个人设置', onClick: () => navigate('/profile') },
    { type: 'divider' as const },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录', onClick: () => { logout(); navigate('/login'); } },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: '#fff',
        borderBottom: '1px solid #f0f0f0',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <h1 style={{ margin: 0, fontSize: 18, fontWeight: 700, whiteSpace: 'nowrap' }}>
            📚 RAG 知识库问答
          </h1>
          <Menu
            mode="horizontal"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={({ key }) => {
              const item = menuItems.find((m) => m.key === key);
              if (item) navigate(item.path);
            }}
            style={{ border: 'none', flex: 1 }}
          />
        </div>

        <Dropdown menu={{ items: dropdownItems }} placement="bottomRight">
          <Space style={{ cursor: 'pointer' }}>
            <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#1677ff' }} />
            <span>{user?.username || '用户'}</span>
            {isAdmin && <span style={{ color: '#faad14', fontSize: 12 }}>(管理员)</span>}
          </Space>
        </Dropdown>
      </Header>

      <Content style={{ background: '#f5f5f5' }}>
        {children}
      </Content>
    </Layout>
  );
}
