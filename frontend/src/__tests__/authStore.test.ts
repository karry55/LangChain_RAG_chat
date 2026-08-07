import { describe, it, expect, beforeEach } from 'vitest';

// localStorage mock (Node 环境无浏览器 API)
const store = new Map<string, string>();
globalThis.localStorage = {
  getItem: (key: string) => store.get(key) ?? null,
  setItem: (key: string, value: string) => { store.set(key, value); },
  removeItem: (key: string) => { store.delete(key); },
  clear: () => { store.clear(); },
} as Storage;

import { useAuthStore } from '../stores/authStore';

describe('authStore', () => {
  beforeEach(() => {
    store.clear();
    useAuthStore.setState({
      token: null,
      user: null,
      isAuthenticated: false,
      isAdmin: false,
    });
  });

  describe('初始状态', () => {
    it('初始时未认证', () => {
      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isAdmin).toBe(false);
      expect(state.token).toBeNull();
      expect(state.user).toBeNull();
    });
  });

  describe('login', () => {
    it('登录后设置 token 和用户信息', () => {
      useAuthStore.getState().login('test-token-abc', {
        id: 'user_1',
        username: 'testuser',
        email: 'test@test.com',
        role: 'user',
      });

      const state = useAuthStore.getState();
      expect(state.token).toBe('test-token-abc');
      expect(state.isAuthenticated).toBe(true);
      expect(state.user?.username).toBe('testuser');
      expect(state.user?.role).toBe('user');
      expect(state.isAdmin).toBe(false);
    });

    it('管理员登录后 isAdmin 为 true', () => {
      useAuthStore.getState().login('admin-token', {
        id: 'admin_1',
        username: 'admin',
        email: 'admin@test.com',
        role: 'admin',
      });

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.isAdmin).toBe(true);
    });

    it('登录后 token 和 user 持久化到 localStorage', () => {
      useAuthStore.getState().login('persist-token', {
        id: 'user_2',
        username: 'persist_user',
        email: '',
        role: 'user',
      });

      expect(store.get('token')).toBe('persist-token');
      const storedUser = JSON.parse(store.get('user') || '{}');
      expect(storedUser.username).toBe('persist_user');
    });
  });

  describe('logout', () => {
    it('登出后清除所有认证状态', () => {
      useAuthStore.getState().login('token-to-clear', {
        id: 'user_3',
        username: 'logout_user',
        email: '',
        role: 'user',
      });

      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.token).toBeNull();
      expect(state.user).toBeNull();
      expect(state.isAuthenticated).toBe(false);
      expect(state.isAdmin).toBe(false);
    });

    it('登出后清除 localStorage', () => {
      useAuthStore.getState().login('token-to-clear', {
        id: 'user_4',
        username: 'clear_user',
        email: '',
        role: 'admin',
      });
      useAuthStore.getState().logout();

      expect(store.get('token')).toBeUndefined();
      expect(store.get('user')).toBeUndefined();
    });
  });

  describe('loadFromStorage', () => {
    it('从 localStorage 恢复登录状态', () => {
      store.set('token', 'stored-token');
      store.set('user', JSON.stringify({
        id: 'user_5',
        username: 'stored_user',
        email: '',
        role: 'admin',
      }));

      useAuthStore.getState().loadFromStorage();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.isAdmin).toBe(true);
      expect(state.token).toBe('stored-token');
      expect(state.user?.username).toBe('stored_user');
    });

    it('localStorage 无数据时保持未认证状态', () => {
      useAuthStore.getState().loadFromStorage();

      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(false);
      expect(state.token).toBeNull();
    });

    it('localStorage 有损坏数据时不会崩溃', () => {
      store.set('token', 'damaged-token');
      store.set('user', 'not-valid-json{{{');

      expect(() => useAuthStore.getState().loadFromStorage()).not.toThrow();
    });
  });
});
