import api from './index'

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: number
  username: string
  email: string | null
  avatar: string | null
  role: string
}

export const authApi = {
  login: (data: LoginRequest) => api.post<TokenResponse>('/api/v1/auth/login', data),
  logout: () => api.post('/api/v1/auth/logout'),
  getMe: () => api.get<User>('/api/v1/auth/me'),
  refresh: (token: string) =>
    api.post<TokenResponse>('/api/v1/auth/refresh', { refresh_token: token }),
}
