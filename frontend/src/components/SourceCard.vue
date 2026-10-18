<!-- 引用来源卡片：展示 RAG 检索到的文档片段，可折叠 -->
<template>
  <div class="source-card">
    <div class="s-head" @click="open = !open">
      <el-icon><Paperclip /></el-icon>
      <span>参考了 {{ fileCount }} 份文档 · {{ sources.length }} 个片段</span>
      <el-icon class="caret" :class="{ open }"><ArrowDown /></el-icon>
    </div>
    <el-collapse-transition>
      <div v-show="open" class="s-list">
        <div v-for="(s, i) in sources" :key="i" class="s-item">
          <div class="s-title">
            <span class="idx">{{ i + 1 }}</span>
            <el-icon><Document /></el-icon>
            <span class="fname">{{ s.file_name }}</span>
          </div>
          <div class="s-content">{{ s.content }}</div>
        </div>
      </div>
    </el-collapse-transition>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

/**
 * @prop sources  引用来源数组 [{file_name, content}]
 * @prop expanded 是否默认展开
 */
const props = defineProps({
  sources: { type: Array, default: () => [] },
  expanded: { type: Boolean, default: false },
})

const open = ref(props.expanded)

/** 去重后的文档数量 */
const fileCount = computed(() => new Set(props.sources.map((s) => s.file_name)).size)
</script>

<style scoped lang="scss">
.source-card {
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: var(--bg-page);
  overflow: hidden;

  .s-head {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 9px 14px;
    font-size: 12.5px;
    color: var(--text-2);
    cursor: pointer;
    user-select: none;

    &:hover {
      color: var(--primary);
    }
    .caret {
      margin-left: auto;
      transition: transform 0.2s;
      &.open {
        transform: rotate(180deg);
      }
    }
  }
  .s-list {
    padding: 0 12px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .s-item {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
  }
  .s-title {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-1);

    .idx {
      width: 18px;
      height: 18px;
      border-radius: 5px;
      background: var(--primary-light);
      color: var(--primary);
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
  }
  .s-content {
    margin-top: 6px;
    font-size: 12.5px;
    line-height: 1.7;
    color: var(--text-3);
    white-space: pre-wrap;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
</style>
