<!-- 悬浮式对话输入框：Enter 发送，Shift + Enter 换行，生成中可停止 -->
<template>
  <div class="chat-input" :class="{ focus }">
    <textarea
      ref="taRef"
      v-model="text"
      rows="1"
      :placeholder="placeholder"
      @focus="focus = true"
      @blur="focus = false"
      @input="autoResize"
      @keydown.enter="onEnter"
    ></textarea>
    <div class="bar">
      <div class="hint">
        <slot name="left" />
      </div>
      <button v-if="loading" class="send stop" title="停止生成" @click="emit('stop')">
        <span class="sq"></span>
      </button>
      <button v-else class="send" :disabled="!text.trim()" title="发送" @click="send">
        <el-icon :size="16"><Promotion /></el-icon>
      </button>
    </div>
  </div>
</template>

<script setup>
import { nextTick, ref } from 'vue'

/**
 * @prop loading     是否正在生成回答
 * @prop placeholder 占位文字
 * @emits send(text) 发送消息
 * @emits stop       停止生成
 */
defineProps({
  loading: Boolean,
  placeholder: { type: String, default: '输入你的问题，Enter 发送，Shift + Enter 换行' },
})
const emit = defineEmits(['send', 'stop'])

const text = ref('')
const focus = ref(false)
const taRef = ref()

/** 根据内容自动调整高度（最多 200px） */
function autoResize() {
  const el = taRef.value
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 200) + 'px'
}

/**
 * 回车处理：Shift+Enter 换行；输入法组字中不发送
 * @param {KeyboardEvent} e
 */
function onEnter(e) {
  if (e.shiftKey || e.isComposing) return
  e.preventDefault()
  send()
}

/** 发送消息并清空输入框 */
function send() {
  const value = text.value.trim()
  if (!value) return
  emit('send', value)
  text.value = ''
  nextTick(autoResize)
}

/**
 * 外部设置输入内容（如点击推荐问题）
 * @param {string} value
 */
function setText(value) {
  text.value = value
  nextTick(() => {
    autoResize()
    taRef.value.focus()
  })
}

defineExpose({ setText })
</script>

<style scoped lang="scss">
.chat-input {
  background: var(--bg-surface);
  border: 1px solid var(--border-strong);
  border-radius: 20px;
  padding: 14px 14px 10px 18px;
  box-shadow: var(--shadow-md);
  transition: border-color 0.2s, box-shadow 0.2s;

  &.focus {
    border-color: rgba(59, 108, 246, 0.5);
    box-shadow: 0 0 0 4px rgba(59, 108, 246, 0.08), var(--shadow-md);
  }

  textarea {
    width: 100%;
    border: none;
    outline: none;
    resize: none;
    font-size: 15px;
    line-height: 1.6;
    font-family: inherit;
    color: var(--text-1);
    background: transparent;
    max-height: 200px;

    &::placeholder {
      color: var(--text-4);
    }
  }

  .bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 6px;
  }
  .hint {
    font-size: 12px;
    color: var(--text-3);
  }
  .send {
    width: 36px;
    height: 36px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    color: #fff;
    background: var(--primary-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(59, 108, 246, 0.3);
    transition: all 0.2s;

    &:hover:not(:disabled) {
      transform: translateY(-1px);
    }
    &:disabled {
      background: #e3e7ee;
      box-shadow: none;
      cursor: not-allowed;
    }
    &.stop {
      background: var(--text-1);
      box-shadow: none;
    }
    .sq {
      width: 11px;
      height: 11px;
      border-radius: 3px;
      background: #fff;
    }
  }
}
</style>
