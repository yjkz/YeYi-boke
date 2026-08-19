import api from './index'

export interface MCPSettings {
  enabled: boolean
  api_key_configured: boolean
  api_key_fingerprint: string | null
  api_key_last4: string | null
  rate_limit: number
  rate_window: number
  allowed_hosts: string[]
  allowed_origins: string[]
  log_retention_days: number
  public_url: string
  updated_at: string | null
}

export interface MCPOverview {
  settings: MCPSettings
  last_24h_total: number
  last_24h_success: number
  last_24h_failure: number
}

export interface MCPRequestLog {
  id: number
  request_id: string
  client_ip: string | null
  user_agent: string | null
  rpc_method: string | null
  tool_name: string | null
  success: boolean
  http_status: number | null
  duration_ms: number | null
  error_message: string | null
  resource_type: string | null
  resource_id: string | null
  resource_slug: string | null
  api_key_id: number | null
  api_key_name: string | null
  api_key_fingerprint: string | null
  created_at: string
}

export interface MCPLogList {
  items: MCPRequestLog[]
  total: number
  page: number
  page_size: number
}

export interface MCPSettingsUpdate {
  enabled?: boolean
  api_key?: string
  rate_limit?: number
  rate_window?: number
  allowed_hosts?: string[]
  allowed_origins?: string[]
  log_retention_days?: number
}

export interface MCPLogFilters {
  page?: number
  page_size?: number
  tool_name?: string
  success?: boolean
  client_ip?: string
  api_key_id?: number
  start_at?: string
  end_at?: string
}

export interface MCPApiKey {
  id: number
  name: string
  fingerprint: string
  last4: string
  enabled: boolean
  usage_count: number
  last_used_at: string | null
  created_at: string
  updated_at: string
}

export const mcpApi = {
  getOverview: () => api.get<MCPOverview>('/api/v1/admin/mcp/overview'),
  getSettings: () => api.get<MCPSettings>('/api/v1/admin/mcp/settings'),
  updateSettings: (data: MCPSettingsUpdate) => api.put<MCPSettings>('/api/v1/admin/mcp/settings', data),
  getLogs: (params: MCPLogFilters) => api.get<MCPLogList>('/api/v1/admin/mcp/logs', { params }),
  getLog: (id: number) => api.get<MCPRequestLog>(`/api/v1/admin/mcp/logs/${id}`),
  cleanupLogs: () => api.post<{ deleted_count: number }>('/api/v1/admin/mcp/logs/cleanup'),
  getKeys: () => api.get<{ items: MCPApiKey[]; total: number }>('/api/v1/admin/mcp/keys'),
  createKey: (data: { name: string; api_key: string }) => api.post<MCPApiKey>('/api/v1/admin/mcp/keys', data),
  updateKey: (id: number, data: { name?: string; enabled?: boolean }) => api.patch<MCPApiKey>(`/api/v1/admin/mcp/keys/${id}`, data),
  exportKeyUrl: (id: number) => api.get<{ url: string }>(`/api/v1/admin/mcp/keys/${id}/export-url`),
  deleteKey: (id: number) => api.delete(`/api/v1/admin/mcp/keys/${id}`),
}
