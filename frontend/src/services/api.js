import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 120000,
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('nexira_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nexira_token')
      localStorage.removeItem('nexira_user')
    }
    const message = error.response?.data?.error || (error.code === 'ECONNABORTED'
      ? 'The request took too long. Your previous work is safe.'
      : 'NEXIRA could not reach the workspace. Check that the backend is running.')
    return Promise.reject(new Error(message))
  },
)

const unwrap = (response) => response.data.data || response.data

const api = {
  async auth(mode, payload) {
    const result = unwrap(await client.post(`/auth/${mode}`, payload))
    localStorage.setItem('nexira_token', result.token)
    localStorage.setItem('nexira_user', JSON.stringify(result.user))
    return result
  },
  logout() {
    localStorage.removeItem('nexira_token')
    localStorage.removeItem('nexira_user')
  },
  projects: {
    list: async () => unwrap(await client.get('/projects')).projects,
    create: async (payload) => unwrap(await client.post('/projects', payload)).project,
    get: async (id) => unwrap(await client.get(`/projects/${id}`)).project,
  },
  workflow: {
    async action(id, stage, action, payload) {
      const suffix = action === 'edit' ? '/edit' : `/${action}`
      const body = action === 'edit' ? { data: payload } : {}
      return unwrap(await client.post(`/projects/${id}/stages/${stage}${suffix}`, body)).project
    },
  },
  admin: {
    list: async () => unwrap(await client.get('/admin/users')).users,
    setRole: async (id, role) => unwrap(await client.patch(`/admin/users/${id}/role`, { role })).user,
  },
}

export default api
