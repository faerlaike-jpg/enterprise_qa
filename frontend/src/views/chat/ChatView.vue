<!-- 智能问答工作台：左侧会话列表 + 右侧沉浸式对话区（参考 ChatGPT / Claude 排版） -->
<template>
  <div class="chat-page">
    <!-- ================= 左侧会话栏 ================= -->
    <aside class="side" :class="{ collapsed }">
      <div class="side-top">
        <AppLogo />
        <button class="icon-btn" title="收起侧栏" @click="collapsed = true">
          <el-icon :size="17"><Fold /></el-icon>
        </button>
      </div>

      <button class="new-chat" @click="newChat">
        <el-icon :size="16"><EditPen /></el-icon>
        新建对话
      </button>

      <div class="session-list">
        <template v-for="group in groupedSessions" :key="group.label">
          <div class="group-label">{{ group.label }}</div>
          <div
            v-for="s in group.items"
            :key="s.id"
            class="session"
            :class="{ active: s.id === currentId }"
            @click="selectSession(s.id)"
          >
            <el-icon class="s-icon"><ChatLineSquare /></el-icon>
            <span class="s-title">{{ s.title }}</span>
            <el-dropdown trigger="click" @command="(c) => onSessionCommand(c, s)" @click.stop>
              <button class="s-more" @click.stop><el-icon><MoreFilled /></el-icon></button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="rename" icon="Edit">重命名</el-dropdown-item>
                  <el-dropdown-item command="delete" icon="Delete">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </template>
        <div v-if="!sessions.length" class="no-session">暂无历史对话</div>
      </div>

      <!-- 用户信息 -->
      <div class="side-user">
        <el-avatar :size="34" class="av">{{ store.displayName.slice(0, 1) }}</el-avatar>
        <div class="u-info">
          <div class="u-name">{{ store.displayName }}</div>
          <div class="u-role">{{ store.isAdmin ? '管理员' : '普通用户' }}</div>
        </div>
        <el-dropdown trigger="click" placement="top-end" @command="onUserCommand">
          <button class="icon-btn"><el-icon :size="17"><Setting /></el-icon></button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="store.isAdmin" command="admin" icon="Monitor">管理后台</el-dropdown-item>
              <el-dropdown-item command="password" icon="Lock">修改密码</el-dropdown-item>
              <el-dropdown-item command="logout" icon="SwitchButton" divided>退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </aside>

    <!-- ================= 右侧对话区 ================= -->
    <section class="main">
      <header class="topbar">
        <div class="left">
          <button v-if="collapsed" class="icon-btn" title="展开侧栏" @click="collapsed = false">
            <el-icon :size="17"><Expand /></el-icon>
          </button>
          <el-select
            v-model="currentKbId"
            class="kb-select"
            placeholder="选择知识库"
            :disabled="streaming"
            @change="onKbChange"
          >
            <template #prefix><el-icon><Collection /></el-icon></template>
            <el-option v-for="kb in kbList" :key="kb.id" :label="kb.name" :value="kb.id">
              <div class="kb-opt">
                <span>{{ kb.name }}</span>
                <span class="cnt">{{ kb.doc_count }} 篇</span>
              </div>
            </el-option>
          </el-select>
        </div>
        <div class="title">{{ currentSession?.title || '新对话' }}</div>
        <div class="right">
          <el-tag effect="plain" round class="model-tag">
            <span class="live"></span>DeepSeek · RAG Agent
          </el-tag>
        </div>
      </header>

      <!-- 消息区 -->
      <div ref="scrollRef" class="scroll" @scroll="onScroll">
        <div class="thread">
          <!-- 空状态：欢迎页 + 推荐问题 -->
          <div v-if="!messages.length && !loadingMessages" class="empty">
            <div class="hero-icon">
              <AppLogo collapse />
            </div>
            <h1>{{ greeting }}，{{ store.displayName }}</h1>
            <p>我是企业知识库助手「智问」，可以帮你快速查询公司制度、IT 指南与报销规范</p>
            <div class="suggests">
              <div v-for="q in suggestions" :key="q.text" class="suggest card-hover" @click="ask(q.text)">
                <div class="sg-icon" :style="{ color: q.color, background: q.color + '14' }">
                  <el-icon><component :is="q.icon" /></el-icon>
                </div>
                <div class="sg-text">{{ q.text }}</div>
                <el-icon class="sg-arrow"><Right /></el-icon>
              </div>
            </div>
          </div>

          <div v-loading="loadingMessages" class="msg-list">
            <MessageBubble v-for="(m, i) in messages" :key="m.id || `tmp-${i}`" :message="m" @feedback="onFeedback" />
          </div>
        </div>
      </div>

      <!-- 回到底部 -->
      <transition name="fade-slide">
        <button v-show="showToBottom" class="to-bottom" @click="scrollToBottom(true)">
          <el-icon><Bottom /></el-icon>
        </button>
      </transition>

      <!-- 输入区 -->
      <div class="composer">
        <ChatInput ref="inputRef" :loading="streaming" @send="ask" @stop="stop">
          <template #left>
            <span class="kb-hint">
              <el-icon><Collection /></el-icon>
              {{ currentKb ? `基于「${currentKb.name}」回答` : '请先选择知识库' }}
            </span>
          </template>
        </ChatInput>
        <div class="disclaimer">AI 生成内容仅供参考，重要事项请以公司正式文件为准</div>
      </div>
    </section>

    <PasswordDialog v-model="pwdVisible" />
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppLogo from '@/components/AppLogo.vue'
import ChatInput from '@/components/ChatInput.vue'
import MessageBubble from '@/components/MessageBubble.vue'
import PasswordDialog from '@/components/PasswordDialog.vue'
import { getKbList } from '@/api/kb'
import {
  createSession,
  deleteSession,
  getMessages,
  getSessions,
  sendFeedback,
  streamChat,
  updateSession,
} from '@/api/chat'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const store = useUserStore()

const collapsed = ref(false)
const pwdVisible = ref(false)
const kbList = ref([])
const sessions = ref([])
const currentId = ref(null)
const currentKbId = ref(null)
const messages = ref([])
const loadingMessages = ref(false)
const streaming = ref(false)
const scrollRef = ref()
const inputRef = ref()
const showToBottom = ref(false)
let controller = null
let stickToBottom = true

// Agent 工具名称与中文状态映射
const TOOL_TEXT = {
  search_knowledge: '正在检索知识库…',
  get_current_time: '正在获取当前时间…',
}

const suggestions = [
  { icon: 'Calendar', color: '#3b6cf6', text: '入职满 3 年，年假有几天？' },
  { icon: 'Wallet', color: '#f59e0b', text: '去上海出差住宿费报销标准是多少？' },
  { icon: 'OfficeBuilding', color: '#14b8d4', text: '会议室怎么预订？单次最长可以订多久？' },
  { icon: 'Present', color: '#7c5cff', text: '公司有哪些员工福利？' },
]

/** 当前会话对象 */
const currentSession = computed(() => sessions.value.find((s) => s.id === currentId.value))
/** 当前知识库对象 */
const currentKb = computed(() => kbList.value.find((k) => k.id === currentKbId.value))

/** 问候语 */
const greeting = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? '早上好' : h < 18 ? '下午好' : '晚上好'
})

/** 会话按时间分组：今天 / 近 7 天 / 更早 */
const groupedSessions = computed(() => {
  const now = new Date()
  const todayStr = now.toISOString().slice(0, 10)
  const weekAgo = new Date(now.getTime() - 7 * 86400000)
  const groups = { 今天: [], '近 7 天': [], 更早: [] }
  sessions.value.forEach((s) => {
    const t = new Date((s.update_time || s.create_time).replace(' ', 'T'))
    if (s.update_time?.slice(0, 10) === todayStr) groups['今天'].push(s)
    else if (t > weekAgo) groups['近 7 天'].push(s)
    else groups['更早'].push(s)
  })
  return Object.entries(groups)
    .filter(([, items]) => items.length)
    .map(([label, items]) => ({ label, items }))
})

// ---------------- 滚动控制 ----------------
/** 监听滚动：用户上滑时不再自动跟随到底部 */
function onScroll() {
  const el = scrollRef.value
  const distance = el.scrollHeight - el.scrollTop - el.clientHeight
  stickToBottom = distance < 80
  showToBottom.value = distance > 300
}

/**
 * 滚动到底部
 * @param {boolean} force 是否强制滚动
 */
function scrollToBottom(force = false) {
  nextTick(() => {
    if (!force && !stickToBottom) return
    const el = scrollRef.value
    el.scrollTo({ top: el.scrollHeight, behavior: force ? 'smooth' : 'auto' })
  })
}

// ---------------- 会话管理 ----------------
/** 加载会话列表 */
async function loadSessions() {
  sessions.value = (await getSessions()).data
}

/**
 * 切换会话并加载消息
 * @param {number} id 会话ID
 */
async function selectSession(id) {
  if (streaming.value) return ElMessage.warning('请等待当前回答完成')
  currentId.value = id
  currentKbId.value = currentSession.value?.kb_id || kbList.value[0]?.id
  loadingMessages.value = true
  try {
    messages.value = (await getMessages(id)).data
    stickToBottom = true
    scrollToBottom()
  } finally {
    loadingMessages.value = false
  }
}

/** 新建对话：仅清空界面，发送第一条消息时才真正创建会话 */
function newChat() {
  if (streaming.value) return
  currentId.value = null
  messages.value = []
  if (!currentKbId.value) currentKbId.value = kbList.value[0]?.id
}

/** 切换知识库：已有会话时同步到后端 */
async function onKbChange(kbId) {
  if (currentId.value) {
    await updateSession(currentId.value, { kb_id: kbId })
    if (currentSession.value) currentSession.value.kb_id = kbId
  }
  ElMessage.success(`已切换到「${currentKb.value?.name}」`)
}

/**
 * 会话菜单命令
 * @param {string} cmd rename | delete
 * @param {Object} s 会话
 */
async function onSessionCommand(cmd, s) {
  if (cmd === 'rename') {
    const { value } = await ElMessageBox.prompt('请输入新的会话名称', '重命名', {
      inputValue: s.title,
      inputValidator: (v) => !!v?.trim() || '名称不能为空',
    })
    await updateSession(s.id, { title: value.trim() })
    s.title = value.trim()
  } else {
    await ElMessageBox.confirm(`确定删除对话「${s.title}」吗？`, '提示', { type: 'warning' })
    await deleteSession(s.id)
    sessions.value = sessions.value.filter((x) => x.id !== s.id)
    if (currentId.value === s.id) newChat()
    ElMessage.success('已删除')
  }
}

// ---------------- 问答 ----------------
/**
 * 发送问题并以流式方式接收回答
 * @param {string} question 用户问题
 */
async function ask(question) {
  if (streaming.value) return
  if (!currentKbId.value) return ElMessage.warning('请先选择知识库')

  // 首次提问时创建会话
  if (!currentId.value) {
    const { data } = await createSession({ kb_id: currentKbId.value })
    sessions.value.unshift(data)
    currentId.value = data.id
  }
  const session = currentSession.value

  messages.value.push({ role: 'user', content: question })
  messages.value.push({ role: 'assistant', content: '', sources: [], streaming: true, status: '' })
  // 取响应式代理对象，保证流式更新能触发视图刷新
  const answer = messages.value[messages.value.length - 1]
  streaming.value = true
  stickToBottom = true
  scrollToBottom(true)

  controller = new AbortController()
  try {
    await streamChat(
      { session_id: session.id, question },
      (event) => {
        if (event.type === 'tool') {
          answer.status = TOOL_TEXT[event.name] || `正在调用工具 ${event.name}…`
        } else if (event.type === 'tool_done') {
          answer.status = '正在组织回答…'
        } else if (event.type === 'token') {
          answer.status = ''
          answer.content += event.content
          scrollToBottom()
        } else if (event.type === 'error') {
          answer.content += `\n\n> **出错了**：${event.content}`
        } else if (event.type === 'done') {
          answer.id = event.message_id
          answer.sources = event.sources || []
        }
      },
      controller.signal,
    )
  } catch (e) {
    if (e.name === 'AbortError') {
      answer.content += answer.content ? '\n\n*（已停止生成）*' : '*（已停止生成）*'
    } else {
      answer.content = `> **出错了**：${e.message}`
    }
  } finally {
    answer.streaming = false
    answer.status = ''
    streaming.value = false
    controller = null
    // 首次提问后后端会用问题作为标题
    if (session.title === '新对话') session.title = question.slice(0, 30)
    session.update_time = new Date().toLocaleString('sv-SE').replace('T', ' ')
    sessions.value = [session, ...sessions.value.filter((s) => s.id !== session.id)]
    scrollToBottom()
  }
}

/** 停止生成 */
function stop() {
  controller?.abort()
}

/**
 * 点赞 / 点踩
 * @param {Object} message 消息
 * @param {number} type 1 | -1
 */
async function onFeedback(message, type) {
  const { data } = await sendFeedback(message.id, type)
  message.feedback = data.type
  if (data.type) ElMessage.success('感谢你的反馈')
}

// ---------------- 用户菜单 ----------------
/**
 * 用户菜单命令
 * @param {string} cmd admin | password | logout
 */
async function onUserCommand(cmd) {
  if (cmd === 'admin') router.push('/admin/home')
  else if (cmd === 'password') pwdVisible.value = true
  else {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    store.logout()
    router.replace('/login')
  }
}

onMounted(async () => {
  const [kbRes] = await Promise.all([getKbList(), loadSessions()])
  kbList.value = kbRes.data
  currentKbId.value = kbList.value[0]?.id
})
</script>

<style scoped lang="scss">
.chat-page {
  display: flex;
  height: 100vh;
  background: var(--bg-surface);
}

.icon-btn {
  width: 34px;
  height: 34px;
  border: none;
  background: transparent;
  border-radius: 10px;
  color: var(--text-2);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  &:hover {
    background: rgba(16, 24, 40, 0.06);
    color: var(--text-1);
  }
}

// ================= 侧栏 =================
.side {
  width: 272px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: #f7f8fb;
  border-right: 1px solid var(--border);
  padding: 14px 12px;
  transition: margin-left 0.3s ease;

  &.collapsed {
    margin-left: -272px;
  }
  .side-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 4px 16px;
  }
}

.new-chat {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  height: 42px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  background: var(--bg-surface);
  color: var(--text-1);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: var(--shadow-xs);
  transition: all 0.2s;

  &:hover {
    border-color: var(--primary);
    color: var(--primary);
    box-shadow: var(--shadow-sm);
  }
}

.session-list {
  flex: 1;
  overflow-y: auto;
  margin: 14px -4px 10px;
  padding: 0 4px;

  .group-label {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--text-4);
    padding: 14px 10px 6px;
  }
  .no-session {
    text-align: center;
    color: var(--text-4);
    font-size: 13px;
    margin-top: 40px;
  }
}

.session {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 6px 0 10px;
  border-radius: 10px;
  cursor: pointer;
  color: var(--text-2);
  transition: background 0.15s;

  .s-icon {
    color: var(--text-4);
    flex-shrink: 0;
  }
  .s-title {
    flex: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    font-size: 13.5px;
  }
  .s-more {
    width: 24px;
    height: 24px;
    border: none;
    background: transparent;
    border-radius: 6px;
    color: var(--text-3);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    &:hover {
      background: rgba(16, 24, 40, 0.08);
    }
  }
  &:hover {
    background: rgba(16, 24, 40, 0.045);
    .s-more {
      opacity: 1;
    }
  }
  &.active {
    background: var(--bg-surface);
    color: var(--text-1);
    font-weight: 500;
    box-shadow: var(--shadow-sm);
    .s-icon {
      color: var(--primary);
    }
  }
}

.side-user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border);

  .av {
    background: var(--primary-gradient);
    font-weight: 600;
    flex-shrink: 0;
  }
  .u-info {
    flex: 1;
    min-width: 0;
  }
  .u-name {
    font-weight: 600;
    font-size: 13.5px;
  }
  .u-role {
    font-size: 11.5px;
    color: var(--text-3);
  }
}

// ================= 主区域 =================
.main {
  position: relative;
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.topbar {
  height: 60px;
  flex-shrink: 0;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #f0f2f6;

  .left {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .title {
    font-weight: 600;
    font-size: 14.5px;
    max-width: 420px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .right {
    display: flex;
    justify-content: flex-end;
  }
  .kb-select {
    width: 200px;
    :deep(.el-select__wrapper) {
      border-radius: 10px;
      box-shadow: none;
      background: var(--bg-muted);
      font-weight: 500;
    }
  }
  .model-tag {
    border-color: var(--border);
    color: var(--text-2);
    .live {
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #16a34a;
      margin-right: 6px;
      box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.15);
    }
  }
}

@media (max-width: 1000px) {
  .topbar .title {
    visibility: hidden;
  }
}

.kb-opt {
  display: flex;
  justify-content: space-between;
  .cnt {
    color: var(--text-4);
    font-size: 12px;
  }
}

.scroll {
  flex: 1;
  overflow-y: auto;
}

.thread {
  max-width: 800px;
  margin: 0 auto;
  padding: 32px 24px 24px;
}

.msg-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
  min-height: 40px;
}

// 空状态
.empty {
  text-align: center;
  padding-top: 8vh;

  .hero-icon {
    display: inline-flex;
    transform: scale(1.5);
    margin-bottom: 26px;
  }
  h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 700;
    background: linear-gradient(90deg, #1d2433 0%, #3b6cf6 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  p {
    margin: 12px 0 36px;
    color: var(--text-3);
    font-size: 14.5px;
  }
}

.suggests {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  text-align: left;

  .suggest {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 16px;
    border-radius: 14px;
    border: 1px solid var(--border);
    background: var(--bg-surface);
    cursor: pointer;
    box-shadow: var(--shadow-xs);
    transition: all 0.2s;

    &:hover {
      border-color: #cfdaf9;
      box-shadow: var(--shadow-md);
      transform: translateY(-2px);
      .sg-arrow {
        opacity: 1;
        transform: translateX(0);
      }
    }
  }
  .sg-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .sg-text {
    flex: 1;
    font-size: 13.5px;
    color: var(--text-1);
  }
  .sg-arrow {
    color: var(--primary);
    opacity: 0;
    transform: translateX(-4px);
    transition: all 0.2s;
  }
}

.to-bottom {
  position: absolute;
  left: 50%;
  bottom: 150px;
  transform: translateX(-50%);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--bg-surface);
  color: var(--text-2);
  box-shadow: var(--shadow-md);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.composer {
  max-width: 800px;
  width: 100%;
  margin: 0 auto;
  padding: 8px 24px 14px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, #fff 24%);

  .kb-hint {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 8px;
    background: var(--bg-muted);
    color: var(--text-2);
  }
  .disclaimer {
    text-align: center;
    font-size: 11.5px;
    color: var(--text-4);
    margin-top: 10px;
  }
}
</style>
