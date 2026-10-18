<!-- 品牌 Logo 组件：渐变图标 + 产品名称 -->
<template>
  <div class="app-logo" :class="{ light }">
    <div class="mark">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none">
        <path d="M12 3l7.5 4.3v8.6L12 20.2l-7.5-4.3V7.3L12 3z" stroke="#fff" stroke-width="1.8" stroke-linejoin="round" />
        <circle cx="12" cy="11.6" r="2.6" fill="#fff" />
      </svg>
    </div>
    <div v-if="!collapse" class="text">
      <div class="name">智问</div>
      <div class="desc">Enterprise KB</div>
    </div>
  </div>
</template>

<script setup>
/**
 * @prop {Boolean} light 是否在深色背景上使用（文字变白）
 * @prop {Boolean} collapse 是否只显示图标
 */
defineProps({
  light: { type: Boolean, default: false },
  collapse: { type: Boolean, default: false },
})
</script>

<style scoped lang="scss">
.app-logo {
  display: flex;
  align-items: center;
  gap: 10px;

  .mark {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: var(--primary-gradient);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: var(--shadow-primary);
    flex-shrink: 0;
  }
  .name {
    font-size: 17px;
    font-weight: 700;
    color: var(--text-1);
    letter-spacing: 1px;
    line-height: 1.1;
  }
  .desc {
    font-size: 11px;
    color: var(--text-3);
    letter-spacing: 0.4px;
  }
  &.light {
    .name {
      color: #fff;
    }
    .desc {
      color: rgba(255, 255, 255, 0.7);
    }
  }
}
</style>
