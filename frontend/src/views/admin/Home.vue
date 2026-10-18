<!-- 管理员首页：欢迎横幅 + 统计卡片 + 数据图表 -->
<template>
  <div class="home" v-loading="loading">
    <!-- 欢迎横幅 -->
    <div class="welcome card">
      <div class="w-text">
        <div class="hello">{{ greeting }}，{{ store.displayName }}</div>
        <div class="w-desc">
          今天是 {{ today }}，知识库已累计回答 <b>{{ cards.question_total }}</b> 个问题，今日新增
          <b>{{ cards.today_question }}</b> 个。
        </div>
      </div>
      <div class="w-actions">
        <el-button icon="Upload" @click="router.push('/admin/documents')">上传文档</el-button>
        <el-button type="primary" icon="ChatLineRound" @click="router.push('/chat')">开始问答</el-button>
      </div>
      <div class="w-deco"></div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats">
      <StatCard label="用户总数" :value="cards.user_count" icon="User" color="#3b6cf6" hint="系统注册用户" />
      <StatCard label="知识库" :value="cards.kb_count" icon="Collection" color="#7c5cff" hint="已创建知识库数量" />
      <StatCard label="知识文档" :value="cards.doc_count" icon="Document" color="#14b8d4">
        已向量化片段 <b class="em">{{ cards.chunk_count }}</b> 个
      </StatCard>
      <StatCard label="今日问答" :value="cards.today_question" icon="ChatDotSquare" color="#f59e0b">
        累计问答 <b class="em">{{ cards.question_total }}</b> 次
      </StatCard>
    </div>

    <!-- 图表第一行 -->
    <div class="row">
      <div class="card chart-card span-2">
        <div class="c-head">
          <div>
            <div class="c-title">问答趋势</div>
            <div class="c-sub">近 7 天用户提问数量</div>
          </div>
          <el-tag effect="plain" round>近 7 天</el-tag>
        </div>
        <div ref="trendRef" class="chart"></div>
      </div>
      <div class="card chart-card">
        <div class="c-head">
          <div>
            <div class="c-title">知识库文档分布</div>
            <div class="c-sub">各知识库文档数量占比</div>
          </div>
        </div>
        <div ref="kbRef" class="chart"></div>
      </div>
    </div>

    <!-- 图表第二行 -->
    <div class="row">
      <div class="card chart-card span-2">
        <div class="c-head">
          <div>
            <div class="c-title">活跃用户排行</div>
            <div class="c-sub">提问次数 Top 5</div>
          </div>
        </div>
        <div ref="rankRef" class="chart"></div>
      </div>
      <div class="card chart-card">
        <div class="c-head">
          <div>
            <div class="c-title">回答满意度</div>
            <div class="c-sub">基于用户点赞 / 点踩反馈</div>
          </div>
        </div>
        <div ref="satRef" class="chart small"></div>
        <div class="sat-legend">
          <span><i class="dot" style="background: #16a34a"></i>点赞 {{ satisfaction.like }}</span>
          <span><i class="dot" style="background: #ef4444"></i>点踩 {{ satisfaction.dislike }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from '@/components/StatCard.vue'
import { getStats } from '@/api/dashboard'
import { useUserStore } from '@/stores/user'
import { echarts, useChart } from '@/composables/useChart'

const router = useRouter()
const store = useUserStore()
const loading = ref(false)

const cards = reactive({
  user_count: 0,
  kb_count: 0,
  doc_count: 0,
  chunk_count: 0,
  question_total: 0,
  today_question: 0,
})
const satisfaction = reactive({ like: 0, dislike: 0, rate: 100 })

const trendRef = ref()
const kbRef = ref()
const rankRef = ref()
const satRef = ref()
const trendChart = useChart(trendRef)
const kbChart = useChart(kbRef)
const rankChart = useChart(rankRef)
const satChart = useChart(satRef)

/** 根据时间生成问候语 */
const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 6) return '夜深了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

/** 今天日期 */
const today = computed(() =>
  new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }),
)

// 图表通用样式
const axisStyle = {
  axisLine: { lineStyle: { color: '#e8ecf2' } },
  axisTick: { show: false },
  axisLabel: { color: '#8a94a6', fontSize: 12 },
  splitLine: { lineStyle: { color: '#f0f2f6', type: 'dashed' } },
}
const tooltip = {
  backgroundColor: '#fff',
  borderColor: '#e8ecf2',
  borderWidth: 1,
  padding: [8, 12],
  textStyle: { color: '#1d2433', fontSize: 12 },
  extraCssText: 'box-shadow:0 8px 24px rgba(16,24,40,.08);border-radius:10px;',
}
const palette = ['#3b6cf6', '#7c5cff', '#14b8d4', '#f59e0b', '#16a34a', '#ef4444']

/**
 * 渲染问答趋势折线图
 * @param {{dates:string[], counts:number[]}} trend
 */
function renderTrend(trend) {
  trendChart.setOption({
    tooltip: { ...tooltip, trigger: 'axis' },
    grid: { left: 36, right: 16, top: 20, bottom: 28 },
    xAxis: { type: 'category', data: trend.dates, boundaryGap: false, ...axisStyle, splitLine: { show: false } },
    yAxis: { type: 'value', minInterval: 1, ...axisStyle, axisLine: { show: false } },
    series: [
      {
        name: '提问数',
        type: 'line',
        smooth: true,
        data: trend.counts,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: '#3b6cf6' },
        itemStyle: { color: '#3b6cf6', borderColor: '#fff', borderWidth: 2 },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59,108,246,0.25)' },
            { offset: 1, color: 'rgba(59,108,246,0.01)' },
          ]),
        },
      },
    ],
  })
}

/**
 * 渲染知识库分布环形图
 * @param {Array<{name:string,value:number}>} data
 */
function renderKb(data) {
  const total = data.reduce((s, d) => s + d.value, 0)
  kbChart.setOption({
    color: palette,
    tooltip: { ...tooltip, trigger: 'item', formatter: '{b}：{c} 篇（{d}%）' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8, textStyle: { color: '#4b5565' } },
    title: {
      text: String(total),
      subtext: '文档总数',
      left: 'center',
      top: '33%',
      textStyle: { fontSize: 26, fontWeight: 700, color: '#1d2433' },
      subtextStyle: { fontSize: 12, color: '#8a94a6' },
    },
    series: [
      {
        type: 'pie',
        radius: ['52%', '72%'],
        center: ['50%', '44%'],
        itemStyle: { borderRadius: 8, borderColor: '#fff', borderWidth: 3 },
        label: { show: false },
        data,
      },
    ],
  })
}

/**
 * 渲染用户提问排行横向柱状图
 * @param {Array<{name:string,value:number}>} data
 */
function renderRank(data) {
  const list = [...data].reverse()
  rankChart.setOption({
    tooltip: { ...tooltip, trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 80, right: 40, top: 10, bottom: 20 },
    xAxis: { type: 'value', minInterval: 1, ...axisStyle, axisLine: { show: false } },
    yAxis: {
      type: 'category',
      data: list.map((d) => d.name),
      ...axisStyle,
      axisLabel: { color: '#4b5565', fontSize: 13 },
      splitLine: { show: false },
    },
    series: [
      {
        type: 'bar',
        data: list.map((d) => d.value),
        barWidth: 14,
        showBackground: true,
        backgroundStyle: { color: '#f5f7fa', borderRadius: 8 },
        label: { show: true, position: 'right', color: '#4b5565' },
        itemStyle: {
          borderRadius: 8,
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#6a8dff' },
            { offset: 1, color: '#3b6cf6' },
          ]),
        },
      },
    ],
  })
}

/**
 * 渲染满意度仪表盘
 * @param {number} rate 满意率
 */
function renderSatisfaction(rate) {
  satChart.setOption({
    series: [
      {
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        radius: '92%',
        center: ['50%', '58%'],
        progress: { show: true, width: 14, roundCap: true, itemStyle: { color: '#3b6cf6' } },
        axisLine: { lineStyle: { width: 14, color: [[1, '#eef1f6']] }, roundCap: true },
        pointer: { show: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: { offsetCenter: [0, '30%'], color: '#8a94a6', fontSize: 12 },
        detail: {
          offsetCenter: [0, '-5%'],
          formatter: '{value}%',
          fontSize: 28,
          fontWeight: 700,
          color: '#1d2433',
        },
        data: [{ value: rate, name: '满意率' }],
      },
    ],
  })
}

/** 加载统计数据 */
async function loadStats() {
  loading.value = true
  try {
    const { data } = await getStats()
    Object.assign(cards, data.cards)
    Object.assign(satisfaction, data.satisfaction)
    renderTrend(data.trend)
    renderKb(data.kb_dist)
    renderRank(data.user_rank)
    renderSatisfaction(data.satisfaction.rate)
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<style scoped lang="scss">
.home {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.welcome {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 26px 30px;
  background: linear-gradient(120deg, #ffffff 0%, #f3f6ff 60%, #ece8ff 100%);

  .hello {
    font-size: 22px;
    font-weight: 700;
    color: var(--text-1);
  }
  .w-desc {
    margin-top: 8px;
    color: var(--text-2);
    b {
      color: var(--primary);
      margin: 0 2px;
    }
  }
  .w-actions {
    position: relative;
    z-index: 1;
    display: flex;
    gap: 10px;
  }
  .w-deco {
    position: absolute;
    right: -60px;
    top: -80px;
    width: 260px;
    height: 260px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(124, 92, 255, 0.18) 0%, transparent 70%);
  }
}

.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;

  .em {
    color: var(--text-1);
    font-weight: 600;
  }
}

.row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;

  .span-2 {
    grid-column: span 2;
  }
}

.chart-card {
  padding: 20px 22px;
  min-width: 0;

  .c-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .c-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-1);
  }
  .c-sub {
    font-size: 12px;
    color: var(--text-3);
    margin-top: 4px;
  }
  .chart {
    height: 280px;
    margin-top: 12px;
    &.small {
      height: 230px;
    }
  }
  .sat-legend {
    display: flex;
    justify-content: center;
    gap: 24px;
    font-size: 13px;
    color: var(--text-2);
  }
}

@media (max-width: 1200px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
  .row {
    grid-template-columns: 1fr;
    .span-2 {
      grid-column: auto;
    }
  }
}
</style>
