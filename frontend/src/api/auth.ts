import client from './client';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  username: string;
  password: string;
  email?: string;
}

export interface ChangePasswordParams {
  old_password: string;
  new_password: string;
}

export async function login(params: LoginParams) {
  const res = await client.post('/auth/login', params);
  return res.data; // { access_token, token_type, user }
}

export async function register(params: RegisterParams) {
  const res = await client.post('/auth/register', params);
  return res.data;
}

export async function changePassword(params: ChangePasswordParams) {
  const res = await client.post('/auth/change-password', params);
  return res.data;
}

export async function getCurrentUser() {
  const res = await client.get('/auth/me');
  return res.data;
}
