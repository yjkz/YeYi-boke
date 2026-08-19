<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { mcpApi, type MCPApiKey, type MCPOverview, type MCPRequestLog, type MCPSettings } from '@/api/mcp'

const activeTab = ref('overview')
const loading = ref(false)
const saving = ref(false)
const logsLoading = ref(false)
const cleanupLoading = ref(false)
const overview = ref<MCPOverview | null>(null)
const logs = ref<MCPRequestLog[]>([])
const keys = ref<MCPApiKey[]>([])
const keyDialogOpen = ref(false)
const keySaving = ref(false)
const keyForm = reactive({ name: '', api_key: '' })
const total = ref(0)
const selectedLog = ref<MCPRequestLog | null>(null)
const detailOpen = ref(false)

const form = reactive({
  enabled: false,
  rate_limit: 120,
  rate_window: 60,
  allowed_hosts: [] as string[],
  allowed_origins: [] as string[],
  log_retention_days: 90,
})
const filters = reactive({
  page: 1,
  page_size: 20,
  tool_name: '',
  success: undefined as boolean | undefined,
  client_ip: '',
  api_key_id: undefined as number | undefined,
  date_range: [] as string[],
})

const endpoint = computed(() => overview.value?.settings.public_url || '')
const configuredKey = computed(() => {
  if (!keys.value.length) return '未配置'
  const enabled = keys.value.filter((key) => key.enabled).length
  return `已配置 ${keys.value.length} 个 · ${enabled} 个启用`
})

const copySettings = (settings: MCPSettings) => {
  form.enabled = settings.enabled
  form.rate_limit = settings.rate_limit
  form.rate_window = settings.rate_window
  form.allowed_hosts = [...settings.allowed_hosts]
  form.allowed_origins = [...settings.allowed_origins]
  form.log_retention_days = settings.log_retention_days
}

const fetchKeys = async () => {
  const { data } = await mcpApi.getKeys()
  keys.value = data.items
}

const fetchOverview = async () => {
  loading.value = true
  try {
    const { data } = await mcpApi.getOverview()
    overview.value = data
    copySettings(data.settings)
  } finally {
    loading.value = false
  }
}

const fetchLogs = async () => {
  logsLoading.value = true
  try {
    const { data } = await mcpApi.getLogs({
      page: filters.page,
      page_size: filters.page_size,
      tool_name: filters.tool_name || undefined,
      success: filters.success,
      client_ip: filters.client_ip || undefined,
      api_key_id: filters.api_key_id,
      start_at: filters.date_range[0] ? new Date(filters.date_range[0]).toISOString() : undefined,
      end_at: filters.date_range[1] ? new Date(filters.date_range[1]).toISOString() : undefined,
    })
    logs.value = data.items
    total.value = data.total
  } finally {
    logsLoading.value = false
  }
}

const applyFilters = () => {
  filters.page = 1
  fetchLogs()
}

const handleSave = async () => {
  saving.value = true
  try {
    const { data } = await mcpApi.updateSettings({
      ...form,
    })
    overview.value = { ...overview.value!, settings: data }
    copySettings(data)
    ElMessage.success('MCP 设置已保存')
  } finally {
    saving.value = false
  }
}

const openKeyDialog = () => {
  keyForm.name = ''
  keyForm.api_key = ''
  keyDialogOpen.value = true
}

const createKey = async () => {
  keySaving.value = true
  try {
    await mcpApi.createKey({ name: keyForm.name, api_key: keyForm.api_key })
    keyDialogOpen.value = false
    ElMessage.success('MCP Key 已添加')
    await fetchKeys()
  } finally {
    keySaving.value = false
  }
}

const toggleKey = async (key: MCPApiKey, enabled: boolean) => {
  try {
    await mcpApi.updateKey(key.id, { enabled })
    key.enabled = enabled
    ElMessage.success(enabled ? 'Key 已启用' : 'Key 已停用')
  } catch {
    key.enabled = !enabled
  }
}

const removeKey = async (key: MCPApiKey) => {
  await ElMessageBox.confirm(`删除后 ${key.name} 将立即失效，历史日志仍会保留。是否继续？`, '删除 MCP Key', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  await mcpApi.deleteKey(key.id)
  ElMessage.success('MCP Key 已删除')
  await fetchKeys()
}

const exportKeyUrl = async (key: MCPApiKey) => {
  const { data } = await mcpApi.exportKeyUrl(key.id)
  try {
    await navigator.clipboard.writeText(data.url)
    ElMessage.success('MCP 接入地址已复制')
  } catch {
    await ElMessageBox.alert(data.url, 'MCP 接入地址', { confirmButtonText: '关闭' })
  }
}

const showLogDetail = async (row: MCPRequestLog) => {
  const { data } = await mcpApi.getLog(row.id)
  selectedLog.value = data
  detailOpen.value = true
}

const cleanupLogs = async () => {
  await ElMessageBox.confirm('将按当前保留期删除过期 MCP 请求日志，是否继续？', '清理过期日志', {
    type: 'warning',
    confirmButtonText: '清理',
    cancelButtonText: '取消',
  })
  cleanupLoading.value = true
  try {
    const { data } = await mcpApi.cleanupLogs()
    ElMessage.success(`已清理 ${data.deleted_count} 条过期日志`)
    await Promise.all([fetchOverview(), fetchLogs()])
  } finally {
    cleanupLoading.value = false
  }
}

const formatTime = (value: string | null) => value ? new Date(value).toLocaleString('zh-CN', { hour12: false }) : '-'
const resourceLabel = (log: MCPRequestLog) => log.resource_id || log.resource_slug || '-'

onMounted(async () => {
  await Promise.all([fetchOverview(), fetchLogs(), fetchKeys()])
})
</script>

<template>
  <div class="max-w-[1280px] space-y-6" v-loading="loading">
    <el-tabs v-model="activeTab" class="mcp-tabs" @tab-change="(tab: string) => tab === 'logs' ? fetchLogs() : tab === 'keys' ? fetchKeys() : undefined">
      <el-tab-pane label="概览" name="overview">
        <div class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm">
            <p class="text-sm text-rocom-text-secondary">服务状态</p>
            <p class="mt-2 text-xl font-semibold" :class="overview?.settings.enabled ? 'text-rocom-success' : 'text-rocom-danger'">
              {{ overview?.settings.enabled ? '已启用' : '已停用' }}
            </p>
          </section>
          <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm">
            <p class="text-sm text-rocom-text-secondary">近 24 小时调用</p>
            <p class="mt-2 text-xl font-semibold text-rocom-text-strong">{{ overview?.last_24h_total ?? 0 }}</p>
          </section>
          <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm">
            <p class="text-sm text-rocom-text-secondary">成功 / 失败</p>
            <p class="mt-2 text-xl font-semibold text-rocom-text-strong">{{ overview?.last_24h_success ?? 0 }} / {{ overview?.last_24h_failure ?? 0 }}</p>
          </section>
          <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm">
            <p class="text-sm text-rocom-text-secondary">当前限流</p>
            <p class="mt-2 text-xl font-semibold text-rocom-text-strong">{{ overview?.settings.rate_limit ?? '-' }} / {{ overview?.settings.rate_window ?? '-' }} 秒</p>
          </section>
        </div>

        <section class="mt-5 space-y-4 rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
          <div>
            <h3 class="text-base font-semibold text-rocom-text-strong">连接信息</h3>
            <p class="mt-1 text-sm text-rocom-text-secondary">配置 MCP 客户端时使用此地址，并在密钥管理页签选择一个有效 Key。</p>
          </div>
          <div class="grid gap-4 md:grid-cols-2">
            <div><p class="text-xs text-rocom-text-secondary">接口地址</p><code class="mt-1 block break-all rounded-md bg-rocom-control px-2 py-1.5 text-sm">{{ endpoint }}</code></div>
            <div><p class="text-xs text-rocom-text-secondary">连接格式</p><code class="mt-1 block break-all rounded-md bg-rocom-control px-2 py-1.5 text-sm">{{ endpoint }}?tavilyApiKey=&lt;your-key&gt;</code></div>
            <div><p class="text-xs text-rocom-text-secondary">默认 Key 状态</p><p class="mt-1 text-sm">{{ configuredKey }}</p></div>
            <div><p class="text-xs text-rocom-text-secondary">允许 Host</p><p class="mt-1 text-sm">{{ overview?.settings.allowed_hosts.length ? overview.settings.allowed_hosts.join('，') : '未限制' }}</p></div>
            <div><p class="text-xs text-rocom-text-secondary">日志保留期</p><p class="mt-1 text-sm">{{ overview?.settings.log_retention_days ?? 90 }} 天</p></div>
          </div>
        </section>
      </el-tab-pane>

      <el-tab-pane label="服务设置" name="settings">
        <section class="max-w-3xl rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
          <el-form label-position="top">
            <el-form-item label="启用 MCP 服务">
              <el-switch v-model="form.enabled" />
              <p class="ml-3 text-xs text-rocom-text-secondary">停用后 MCP 端点会返回服务不可用。</p>
            </el-form-item>
            <div class="grid gap-4 md:grid-cols-2">
              <el-form-item label="限流次数"><el-input-number v-model="form.rate_limit" :min="1" :max="10000" class="!w-full" /></el-form-item>
              <el-form-item label="限流窗口（秒）"><el-input-number v-model="form.rate_window" :min="1" :max="86400" class="!w-full" /></el-form-item>
            </div>
            <el-form-item label="允许的 Host">
              <el-select v-model="form.allowed_hosts" multiple filterable allow-create default-first-option class="w-full" placeholder="输入域名后回车；留空表示不限制" />
            </el-form-item>
            <el-form-item label="允许的 Origin">
              <el-select v-model="form.allowed_origins" multiple filterable allow-create default-first-option class="w-full" placeholder="输入 Origin 后回车；留空表示不限制" />
            </el-form-item>
            <el-form-item label="请求日志保留天数"><el-input-number v-model="form.log_retention_days" :min="1" :max="3650" /></el-form-item>
            <el-form-item><el-button type="primary" :loading="saving" @click="handleSave">保存 MCP 设置</el-button></el-form-item>
          </el-form>
        </section>
      </el-tab-pane>

      <el-tab-pane label="密钥管理" name="keys">
        <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h3 class="text-base font-semibold text-rocom-text-strong">MCP API Keys</h3>
              <p class="mt-1 text-sm text-rocom-text-secondary">支持通过 <code>tavilyApiKey</code> 查询参数或请求头接入；明文只在添加时提交。</p>
            </div>
            <el-button type="primary" @click="openKeyDialog">添加 Key</el-button>
          </div>
          <div class="mt-4 -mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
          <el-table class="min-w-[760px]" :data="keys" empty-text="暂无 MCP Key">
            <el-table-column prop="name" label="名称" min-width="160" />
            <el-table-column label="Key 标识" min-width="220"><template #default="{ row }">****{{ row.last4 }} · {{ row.fingerprint }}</template></el-table-column>
            <el-table-column label="状态" width="100"><template #default="{ row }"><el-switch v-model="row.enabled" @change="(value: boolean | string | number) => toggleKey(row, Boolean(value))" /></template></el-table-column>
            <el-table-column prop="usage_count" label="使用次数" width="110" />
            <el-table-column label="最后使用" min-width="170"><template #default="{ row }">{{ formatTime(row.last_used_at) }}</template></el-table-column>
            <el-table-column label="操作" width="170"><template #default="{ row }"><el-button link type="primary" @click="exportKeyUrl(row)">导出地址</el-button><el-button link type="danger" @click="removeKey(row)">删除</el-button></template></el-table-column>
          </el-table>
          </div>
        </section>
      </el-tab-pane>

      <el-tab-pane label="请求日志" name="logs">
        <section class="rounded-xl border border-rocom-outline bg-rocom-surface-paper p-4 shadow-sm sm:p-5">
          <div class="flex flex-wrap items-end gap-3">
            <el-input v-model="filters.tool_name" class="w-full sm:w-52" placeholder="工具名" clearable @clear="applyFilters" />
            <el-input v-model="filters.client_ip" class="w-full sm:w-40" placeholder="客户端 IP" clearable @clear="applyFilters" />
            <el-select v-model="filters.api_key_id" class="w-full sm:w-48" placeholder="API Key" clearable @clear="applyFilters"><el-option v-for="key in keys" :key="key.id" :label="key.name" :value="key.id" /></el-select>
            <el-select v-model="filters.success" class="w-full sm:w-32" placeholder="结果" clearable @clear="applyFilters"><el-option label="成功" :value="true" /><el-option label="失败" :value="false" /></el-select>
            <el-date-picker v-model="filters.date_range" class="!w-full lg:!w-auto" type="datetimerange" value-format="YYYY-MM-DDTHH:mm:ss" range-separator="至" start-placeholder="开始时间" end-placeholder="结束时间" />
            <el-button type="primary" @click="applyFilters">筛选</el-button>
            <el-button :loading="cleanupLoading" @click="cleanupLogs">清理过期日志</el-button>
          </div>
          <div class="mt-4 -mx-4 overflow-x-auto px-4 sm:mx-0 sm:px-0">
          <el-table class="min-w-[980px]" :data="logs" v-loading="logsLoading" @row-click="showLogDetail">
            <el-table-column label="时间" min-width="170"><template #default="{ row }">{{ formatTime(row.created_at) }}</template></el-table-column>
            <el-table-column prop="client_ip" label="IP" min-width="120" />
            <el-table-column prop="tool_name" label="工具" min-width="200"><template #default="{ row }">{{ row.tool_name || row.rpc_method || '-' }}</template></el-table-column>
            <el-table-column prop="api_key_name" label="API Key" min-width="140"><template #default="{ row }">{{ row.api_key_name || '-' }}</template></el-table-column>
            <el-table-column label="结果" width="80"><template #default="{ row }"><el-tag size="small" :type="row.success ? 'success' : 'danger'">{{ row.success ? '成功' : '失败' }}</el-tag></template></el-table-column>
            <el-table-column prop="http_status" label="状态" width="80" />
            <el-table-column label="耗时" width="90"><template #default="{ row }">{{ row.duration_ms == null ? '-' : `${row.duration_ms} ms` }}</template></el-table-column>
            <el-table-column label="资源" min-width="130"><template #default="{ row }">{{ resourceLabel(row) }}</template></el-table-column>
          </el-table>
          </div>
          <div class="mt-4 overflow-x-auto pb-1"><div class="flex min-w-max justify-end"><el-pagination v-model:current-page="filters.page" v-model:page-size="filters.page_size" :total="total" :page-sizes="[20, 50, 100]" layout="total, sizes, prev, pager, next" @current-change="fetchLogs" @size-change="applyFilters" /></div></div>
        </section>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="keyDialogOpen" title="添加 MCP Key" width="min(520px, 92vw)">
      <el-form label-position="top">
        <el-form-item label="名称" required><el-input v-model="keyForm.name" maxlength="120" placeholder="例如：Tavily connector" /></el-form-item>
        <el-form-item label="API Key" required><el-input v-model="keyForm.api_key" type="password" show-password autocomplete="new-password" placeholder="粘贴第三方客户端使用的 Key" /></el-form-item>
        <p class="text-xs text-rocom-text-secondary">保存后不会再次显示明文。客户端地址格式：{{ endpoint }}?tavilyApiKey=&lt;your-key&gt;</p>
      </el-form>
      <template #footer>
        <el-button @click="keyDialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="keySaving" :disabled="!keyForm.name.trim() || keyForm.api_key.length < 8" @click="createKey">添加</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailOpen" title="MCP 请求详情" size="min(560px, 92vw)">
      <el-descriptions v-if="selectedLog" :column="1" border>
        <el-descriptions-item label="时间">{{ formatTime(selectedLog.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="请求 ID">{{ selectedLog.request_id }}</el-descriptions-item>
        <el-descriptions-item label="客户端 IP">{{ selectedLog.client_ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="User-Agent">{{ selectedLog.user_agent || '-' }}</el-descriptions-item>
        <el-descriptions-item label="协议方法">{{ selectedLog.rpc_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="工具">{{ selectedLog.tool_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="API Key">{{ selectedLog.api_key_name || '-' }} · {{ selectedLog.api_key_fingerprint || '-' }}</el-descriptions-item>
        <el-descriptions-item label="结果">{{ selectedLog.success ? '成功' : '失败' }}</el-descriptions-item>
        <el-descriptions-item label="状态 / 耗时">{{ selectedLog.http_status ?? '-' }} / {{ selectedLog.duration_ms ?? '-' }} ms</el-descriptions-item>
        <el-descriptions-item label="资源">{{ selectedLog.resource_type || '-' }} · {{ resourceLabel(selectedLog) }}</el-descriptions-item>
        <el-descriptions-item label="错误">{{ selectedLog.error_message || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-drawer>
  </div>
</template>
