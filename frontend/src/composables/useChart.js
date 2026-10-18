/**
 * ECharts 组合式函数
 * 负责图表实例的创建、自适应缩放与销毁
 */
import { onBeforeUnmount, onMounted, shallowRef } from 'vue'
import * as echarts from 'echarts'

/**
 * @param {import('vue').Ref<HTMLElement>} elRef 图表容器 ref
 * @returns {{ setOption: Function }}
 */
export function useChart(elRef) {
  const chart = shallowRef(null)
  let observer = null

  onMounted(() => {
    chart.value = echarts.init(elRef.value)
    // 监听容器尺寸变化，自动 resize
    observer = new ResizeObserver(() => chart.value?.resize())
    observer.observe(elRef.value)
  })

  onBeforeUnmount(() => {
    observer?.disconnect()
    chart.value?.dispose()
  })

  /**
   * 设置图表配置
   * @param {Object} option ECharts 配置项
   */
  function setOption(option) {
    chart.value?.setOption(option, true)
  }

  return { setOption }
}

export { echarts }
