<!-- 对话消息气泡：用户消息右侧蓝色气泡，AI 消息左侧带头像的 Markdown 排版 -->
<template>
  <div class="msg" :class="message.role">
    <!-- 用户消息 -->
    <template v-if="message.role === 'user'">
      <div class="user-bubble">{{ message.content }}</div>
    </template>

    <!-- AI 消息 -->
    <template v-else>
      <div class="ai-avatar">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none">
          <path d="M12 3l7.5 4.3v8.6L12 20.2l-7.5-4.3V7.3L12 3z" stroke="#fff" stroke-width="1.8" stroke-linejoin="round" />
          <circle cx="12" cy="11.6" r="2.6" fill="#fff" />
        </svg>
      </div>
      <div class="ai-body">
        <!-- Agent 工具调用状态 -->
        <div v-if="message.streaming && message.status" class="tool-status">
          <span class="spinner"></span>{{ message.status }}
        </div>

        <!-- 等待首个 token 时的加载动画 -->
        <div v-if="message.streaming && !message.content && !message.status" class="thinking">
          <i></i><i></i><i></i>
        </div>

        <div
          v-if="message.content"
          class="markdown-body"
          :class="{ typing: message.streaming }"
          v-html="html"
          @click="handleCopyClick"
        ></div>

        <SourceCard v-if="!message.streaming && message.sources?.length" class="sources" :sources="message.sources" />

        <!-- 操作栏 -->
        <div v-if="!message.streaming && message.content" class="actions">
          <el-tooltip content="复制" placement="top">
            <button class="act" @click="copy"><el-icon><CopyDocument /></el-icon></button>
          </el-tooltip>
          <template v-if="message.id">
            <el-tooltip content="有帮助" placement="top">
              <button class="act" :class="{ on: message.feedback === 1 }" @click="emit('feedback', message, 1)">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path d="M7 10v11H4V10h3zm0 0l4-7a2 2 0 012 2v4h5.5a2 2 0 012 2.3l-1.4 8A2 2 0 0117.1 21H7" stroke-linejoin="round" />
                </svg>
              </button>
            </el-tooltip>
            <el-tooltip content="没帮助" placement="top">
              <button class="act" :class="{ on: message.feedback === -1 }" @click="emit('feedback', message, -1)">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.8" style="transform: rotate(180deg)">
                  <path d="M7 10v11H4V10h3zm0 0l4-7a2 2 0 012 2v4h5.5a2 2 0 012 2.3l-1.4 8A2 2 0 0117.1 21H7" stroke-linejoin="round" />
                </svg>
              </button>
            </el-tooltip>
          </template>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ElMessage } from 'element-plus'
import SourceCard from './SourceCard.vue'
import { handleCopyClick, renderMarkdown } from '@/utils/markdown'

/**
 * @prop message 消息对象 {id, role, content, sources, streaming, status, feedback}
 * @emits feedback (message, type) 点赞 / 点踩
 */
const props = defineProps({
  message: { type: Object, required: true },
})
const emit = defineEmits(['feedback'])

/** Markdown 渲染结果 */
const html = computed(() => renderMarkdown(props.message.content))

/** 复制回答原文 */
function copy() {
  navigator.clipboard.writeText(props.message.content).then(() => ElMessage.success('已复制'))
}
</script>

<style scoped lang="scss">
.msg {
  display: flex;
  gap: 14px;
  animation: msg-in 0.3s ease;

  &.user {
    justify-content: flex-end;
  }
}

@keyframes msg-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
}

.user-bubble {
  max-width: 78%;
  padding: 11px 16px;
  border-radius: 18px 18px 4px 18px;
  background: var(--primary-gradient);
  color: #fff;
  font-size: 15px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
  box-shadow: 0 4px 14px rgba(59, 108, 246, 0.22);
}

.ai-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  flex-shrink: 0;
  background: var(--primary-gradient);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-primary);
  margin-top: 2px;
}

.ai-body {
  flex: 1;
  min-width: 0;
  padding-top: 4px;

  .sources {
    margin-top: 14px;
  }
}

.tool-status {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  margin-bottom: 10px;
  border-radius: 20px;
  background: var(--primary-light);
  color: var(--primary);
  font-size: 12.5px;
  font-weight: 500;

  .spinner {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    border: 2px solid rgba(59, 108, 246, 0.25);
    border-top-color: var(--primary);
    animation: spin 0.8s linear infinite;
  }
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.thinking {
  display: flex;
  gap: 5px;
  padding: 10px 0;

  i {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--primary);
    opacity: 0.35;
    animation: bounce 1.2s infinite ease-in-out;
    &:nth-child(2) {
      animation-delay: 0.15s;
    }
    &:nth-child(3) {
      animation-delay: 0.3s;
    }
  }
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.35;
  }
  40% {
    transform: translateY(-5px);
    opacity: 1;
  }
}

.actions {
  display: flex;
  gap: 2px;
  margin-top: 10px;
  opacity: 0.6;
  transition: opacity 0.2s;

  .act {
    width: 30px;
    height: 30px;
    border: none;
    background: transparent;
    border-radius: 8px;
    color: var(--text-3);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.15s;

    &:hover {
      background: var(--bg-muted);
      color: var(--text-1);
    }
    &.on {
      color: var(--primary);
      background: var(--primary-light);
    }
  }
}
.msg:hover .actions {
  opacity: 1;
}
</style>
