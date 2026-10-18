<!-- 文档管理：拖拽上传 + 文档列表 + 向量化状态 -->
<template>
  <div class="doc-page">
    <div class="page-header">
      <div>
        <h2 class="title">文档管理</h2>
        <p class="subtitle">上传后系统将自动完成：文本解析 → 切分 → 向量化 → 写入 Chroma</p>
      </div>
      <el-button type="primary" icon="Upload" @click="openUpload">上传文档</el-button>
    </div>

    <div class="card">
      <div class="toolbar">
        <div class="left">
          <el-select v-model="query.kb_id" placeholder="全部知识库" clearable style="width: 180px" @change="search">
            <el-option v-for="kb in kbList" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
          <el-input
            v-model="query.keyword"
            placeholder="搜索文件名"
            prefix-icon="Search"
            clearable
            style="width: 240px"
            @keyup.enter="search"
            @clear="search"
          />
        </div>
        <div class="right">
          <el-button icon="Refresh" @click="load">刷新</el-button>
        </div>
      </div>

      <div class="table-wrap">
        <el-table v-loading="loading" :data="list">
          <el-table-column label="文件名" min-width="260">
            <template #default="{ row }">
              <div class="file-cell">
                <div class="ft" :class="row.file_type">{{ row.file_type.toUpperCase() }}</div>
                <div>
                  <div class="fname">{{ row.file_name }}</div>
                  <div class="fsize">{{ formatSize(row.file_size) }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="所属知识库" width="150">
            <template #default="{ row }">
              <el-tag effect="plain" type="info">{{ kbName(row.kb_id) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="片段数" prop="chunk_count" width="90" align="center" />
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <el-tooltip :disabled="row.status !== 2" :content="row.error_msg || ''" placement="top">
                <span class="status" :class="`s${row.status}`">
                  <i class="dot"></i>{{ statusText[row.status] }}
                </span>
              </el-tooltip>
            </template>
          </el-table-column>
          <el-table-column label="上传时间" prop="create_time" width="170" />
          <el-table-column label="操作" width="170" fixed="right">
            <template #default="{ row }">
              <el-button
                link
                type="primary"
                :loading="vectorizing === row.id"
                @click="onVectorize(row)"
              >
                {{ row.status === 1 ? '重新向量化' : '向量化' }}
              </el-button>
              <el-button link type="danger" @click="onDelete(row)">删除</el-button>
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

    <!-- 上传弹窗 -->
    <el-dialog v-model="uploadVisible" title="上传文档" width="520px" :close-on-click-modal="!uploading">
      <el-form label-position="top">
        <el-form-item label="目标知识库" required>
          <el-select v-model="uploadKbId" placeholder="请选择知识库" style="width: 100%">
            <el-option v-for="kb in kbList" :key="kb.id" :label="kb.name" :value="kb.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择文件" required>
          <el-upload
            ref="uploadRef"
            class="uploader"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".txt,.md,.pdf,.docx"
            :on-change="(f) => (uploadFile = f.raw)"
            :on-remove="() => (uploadFile = null)"
            :on-exceed="onExceed"
          >
            <div class="up-icon"><el-icon :size="26"><UploadFilled /></el-icon></div>
            <div class="up-text">将文件拖到此处，或 <em>点击选择</em></div>
            <div class="up-tip">支持 TXT / MD / PDF / DOCX，单文件不超过 20MB</div>
          </el-upload>
        </el-form-item>
      </el-form>
      <el-progress v-if="uploading" :percentage="progress" :stroke-width="8" :format="progressText" />
      <template #footer>
        <el-button :disabled="uploading" @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="doUpload">上传并向量化</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getKbList } from '@/api/kb'
import { deleteDocument, getDocuments, uploadDocument, vectorizeDocument } from '@/api/document'

const route = useRoute()
const statusText = { 0: '待处理', 1: '已完成', 2: '失败' }

const loading = ref(false)
const list = ref([])
const total = ref(0)
const kbList = ref([])
const vectorizing = ref(null)
const query = reactive({
  page: 1,
  size: 10,
  kb_id: route.query.kb_id ? Number(route.query.kb_id) : undefined,
  keyword: '',
})

const uploadVisible = ref(false)
const uploadRef = ref()
const uploadKbId = ref()
const uploadFile = ref(null)
const uploading = ref(false)
const progress = ref(0)

/**
 * 格式化文件大小
 * @param {number} size 字节数
 */
function formatSize(size) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

/**
 * 根据知识库ID获取名称
 * @param {number} id 知识库ID
 */
function kbName(id) {
  return kbList.value.find((k) => k.id === id)?.name || '-'
}

/** 加载文档列表 */
async function load() {
  loading.value = true
  try {
    const { data } = await getDocuments(query)
    list.value = data.list
    total.value = data.total
  } finally {
    loading.value = false
  }
}

/** 条件变化时回到第一页查询 */
function search() {
  query.page = 1
  load()
}

/** 打开上传弹窗 */
function openUpload() {
  uploadKbId.value = query.kb_id || kbList.value[0]?.id
  uploadFile.value = null
  progress.value = 0
  uploadRef.value?.clearFiles()
  uploadVisible.value = true
}

/** 超出数量时替换为新文件 */
function onExceed(files) {
  uploadRef.value.clearFiles()
  uploadRef.value.handleStart(files[0])
  uploadFile.value = files[0]
}

/** 上传进度文案：上传完成后显示向量化中 */
function progressText(p) {
  return p >= 100 ? '向量化中…' : `${p}%`
}

/** 执行上传 */
async function doUpload() {
  if (!uploadKbId.value) return ElMessage.warning('请选择知识库')
  if (!uploadFile.value) return ElMessage.warning('请选择文件')

  const fd = new FormData()
  fd.append('kb_id', uploadKbId.value)
  fd.append('file', uploadFile.value)
  uploading.value = true
  try {
    const res = await uploadDocument(fd, (e) => {
      progress.value = Math.round((e.loaded * 100) / (e.total || 1))
    })
    ElMessage.success(res.msg)
    uploadVisible.value = false
  } finally {
    uploading.value = false
    load()
  }
}

/**
 * 向量化 / 重新向量化
 * @param {Object} row 文档
 */
async function onVectorize(row) {
  vectorizing.value = row.id
  try {
    const res = await vectorizeDocument(row.id)
    ElMessage.success(res.msg)
  } finally {
    vectorizing.value = null
    load()
  }
}

/**
 * 删除文档
 * @param {Object} row 文档
 */
async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除「${row.file_name}」及其向量数据吗？`, '提示', { type: 'warning' })
  await deleteDocument(row.id)
  ElMessage.success('删除成功')
  load()
}

onMounted(async () => {
  kbList.value = (await getKbList()).data
  load()
})
</script>

<style scoped lang="scss">
.doc-page {
  max-width: 1400px;
  margin: 0 auto;
}

.file-cell {
  display: flex;
  align-items: center;
  gap: 12px;

  .ft {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10.5px;
    font-weight: 700;
    color: #3b6cf6;
    background: #eef3ff;
    &.pdf {
      color: #ef4444;
      background: #fdecec;
    }
    &.docx {
      color: #2563eb;
      background: #e7efff;
    }
    &.md {
      color: #7c5cff;
      background: #f1edff;
    }
    &.txt {
      color: #4b5565;
      background: #f2f4f8;
    }
  }
  .fname {
    font-weight: 500;
    color: var(--text-1);
  }
  .fsize {
    font-size: 12px;
    color: var(--text-3);
    margin-top: 2px;
  }
}

.status {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;

  &.s0 {
    color: #b45309;
    background: #fff6e6;
    .dot {
      background: #f59e0b;
    }
  }
  &.s1 {
    color: #15803d;
    background: #eaf7ef;
    .dot {
      background: #16a34a;
    }
  }
  &.s2 {
    color: #b91c1c;
    background: #fdecec;
    cursor: help;
    .dot {
      background: #ef4444;
    }
  }
}

.uploader {
  width: 100%;

  :deep(.el-upload-dragger) {
    border-radius: var(--radius-md);
    border: 1.5px dashed var(--border-strong);
    background: var(--bg-page);
    padding: 28px 20px;
    &:hover {
      border-color: var(--primary);
      background: var(--primary-lighter);
    }
  }
  .up-icon {
    width: 52px;
    height: 52px;
    margin: 0 auto 12px;
    border-radius: 14px;
    background: var(--primary-light);
    color: var(--primary);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .up-text {
    color: var(--text-2);
    em {
      color: var(--primary);
      font-style: normal;
    }
  }
  .up-tip {
    margin-top: 6px;
    font-size: 12px;
    color: var(--text-3);
  }
}
</style>
