<!-- 问答记录：管理员查看全部用户的提问与 AI 回答 -->
<template>
  <div class="records-page">
    <div class="page-header">
      <div>
        <h2 class="title">问答记录</h2>
        <p class="subtitle">审计员工提问与 AI 回答，持续优化知识库内容</p>
      </div>
    </div>

    <div class="card">
      <div class="toolbar">
        <div class="left">
          <el-select v-model="query.kb_id" placeholder="全部知识库" clearable style="width: 180px" @change="search">
            <el-option v-for="kb in kbList" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
          <el-input
            v-model="query.keyword"
            placeholder="搜索问题关键词"
            prefix-icon="Search"
            clearable
            style="width: 260px"
            @keyup.enter="search"
            @clear="search"
          />
        </div>
      </div>

      <div class="table-wrap">
        <el-table v-loading="loading" :data="list">
          <el-table-column label="提问用户" width="150">
            <template #default="{ row }">
              <div class="user-cell">
                <el-avatar :size="28" class="av">{{ (row.nickname || row.username).slice(0, 1) }}</el-avatar>
                <span>{{ row.nickname || row.username }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="问题" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="q">{{ row.question }}</span>
            </template>
          </el-table-column>
          <el-table-column label="回答摘要" min-width="300" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="a">{{ row.answer || '（无回答）' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="知识库" width="130">
            <template #default="{ row }">
              <el-tag effect="plain" type="info">{{ row.kb_name }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="提问时间" prop="create_time" width="170" />
          <el-table-column label="操作" width="90" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="showDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      <div class="pager">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.size"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </div>

    <!-- 详情抽屉 -->
    <el-drawer v-model="drawerVisible" title="问答详情" size="560px">
      <template v-if="current">
        <div class="d-meta">
          <span>{{ current.nickname }}（{{ current.username }}）</span>
          <span>{{ current.kb_name }}</span>
          <span>{{ current.create_time }}</span>
        </div>
        <div class="d-block">
          <div class="d-label">问题</div>
          <div class="d-q">{{ current.question }}</div>
        </div>
        <div class="d-block">
          <div class="d-label">AI 回答</div>
          <div class="d-a markdown-body" v-html="renderMarkdown(current.answer || '（无回答）')"></div>
        </div>
        <div v-if="current.sources.length" class="d-block">
          <div class="d-label">引用来源（{{ current.sources.length }}）</div>
          <SourceCard :sources="current.sources" expanded />
        </div>
      </template>
    </el-drawer>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import SourceCard from '@/components/SourceCard.vue'
import { getKbList } from '@/api/kb'
import { getRecords } from '@/api/chat'
import { renderMarkdown } from '@/utils/markdown'

const loading = ref(false)
const list = ref([])
const total = ref(0)
const kbList = ref([])
const query = reactive({ page: 1, size: 10, kb_id: undefined, keyword: '' })
const drawerVisible = ref(false)
const current = ref(null)

/** 加载问答记录 */
async function load() {
  loading.value = true
  try {
    const { data } = await getRecords(query)
    list.value = data.list
    total.value = data.total
  } finally {
    loading.value = false
  }
}

/** 重新搜索 */
function search() {
  query.page = 1
  load()
}

/**
 * 查看详情
 * @param {Object} row 记录
 */
function showDetail(row) {
  current.value = row
  drawerVisible.value = true
}

onMounted(async () => {
  kbList.value = (await getKbList()).data
  load()
})
</script>

<style scoped lang="scss">
.records-page {
  max-width: 1400px;
  margin: 0 auto;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  .av {
    background: var(--primary-gradient);
    font-size: 12px;
    flex-shrink: 0;
  }
}

.q {
  font-weight: 500;
  color: var(--text-1);
}
.a {
  color: var(--text-3);
}

.d-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
  span {
    font-size: 12px;
    color: var(--text-2);
    background: var(--bg-muted);
    padding: 4px 10px;
    border-radius: 6px;
  }
}
.d-block {
  margin-bottom: 22px;
}
.d-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-3);
  letter-spacing: 0.5px;
  margin-bottom: 8px;
}
.d-q {
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: var(--primary-light);
  color: var(--text-1);
  font-weight: 500;
}
.d-a {
  padding: 14px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--bg-surface);
}
</style>
