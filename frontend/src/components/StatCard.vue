<!-- 首页统计卡片：图标 + 数值 + 说明 -->
<template>
  <div class="stat-card card card-hover">
    <div class="head">
      <span class="label">{{ label }}</span>
      <div class="icon" :style="{ background: soft, color }">
        <el-icon :size="18"><component :is="icon" /></el-icon>
      </div>
    </div>
    <div class="value">{{ displayValue }}</div>
    <div class="foot">
      <slot>{{ hint }}</slot>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

/**
 * @prop label 标题
 * @prop value 数值
 * @prop icon  Element Plus 图标名
 * @prop color 主题色
 * @prop hint  底部说明文字
 */
const props = defineProps({
  label: String,
  value: { type: Number, default: 0 },
  icon: { type: String, default: 'DataLine' },
  color: { type: String, default: '#3b6cf6' },
  hint: String,
})

/** 图标背景使用主题色的浅色版本 */
const soft = computed(() => `${props.color}14`)

const current = ref(0)
const displayValue = computed(() => current.value.toLocaleString())

/** 数字滚动动画 */
function animate() {
  const target = props.value || 0
  const start = performance.now()
  const step = (now) => {
    const p = Math.min((now - start) / 800, 1)
    current.value = Math.round(target * (1 - Math.pow(1 - p, 3)))
    if (p < 1) requestAnimationFrame(step)
  }
  requestAnimationFrame(step)
}

onMounted(animate)
watch(() => props.value, animate)
</script>

<style scoped lang="scss">
.stat-card {
  padding: 20px 22px;

  .head {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .label {
    font-size: 13px;
    color: var(--text-3);
    font-weight: 500;
  }
  .icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .value {
    margin-top: 10px;
    font-size: 30px;
    font-weight: 700;
    color: var(--text-1);
    letter-spacing: -0.5px;
    font-variant-numeric: tabular-nums;
  }
  .foot {
    margin-top: 8px;
    font-size: 12px;
    color: var(--text-3);
  }
}
</style>
