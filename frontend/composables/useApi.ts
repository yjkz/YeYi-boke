export function useApi() {
  const config = useRuntimeConfig()
  const baseURL = config.apiBase || config.public.apiBase

  return {
    get: <T>(url: string, params?: Record<string, any>) =>
      $fetch<T>(url, { baseURL, params }),
    post: <T>(url: string, body?: any) =>
      $fetch<T>(url, { baseURL, method: 'POST', body }),
    put: <T>(url: string, body?: any) =>
      $fetch<T>(url, { baseURL, method: 'PUT', body }),
    del: <T>(url: string) =>
      $fetch<T>(url, { baseURL, method: 'DELETE' }),
  }
}
