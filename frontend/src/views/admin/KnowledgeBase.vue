<!-- 知识库管理：卡片网格展示，支持新增 / 编辑 / 删除 -->
<template>
  <div class="kb-page">
    <div class="page-header">
      <div>
        <h2 class="title">知识库管理</h2>
        <p class="subtitle">每个知识库对应一个独立的 Chroma 向量集合，可按业务领域划分</p>
      </div>
      <el-button type="primary" icon="Plus" @click="openDialog()">新建知识库</el-button>
    </div>

    <div v-loading="loading" class="kb-grid">
      <div v-for="(kb, i) in list" :key="kb.id" class="kb-card card card-hover">
        <div class="top">
          <div class="icon" :style="iconStyle(i)">
            <el-icon :size="22"><component :is="kb.icon || 'Collection'" /></el-icon>
          </div>
          <el-dropdown trigger="click" @command="(c) => onCommand(c, kb)">
            <el-button text circle icon="MoreFilled" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="edit" icon="Edit">编辑</el-dropdown-item>
                <el-dropdown-item command="delete" icon="Delete" divided>
                  <span style="color: var(--danger)">删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <div class="name">{{ kb.name }}</div>
        <div class="desc">{{ kb.description || '暂无描述' }}</div>
        <div class="meta">
          <span><el-icon><Document /></el-icon>{{ kb.doc_count }} 篇文档</span>
          <span class="col">{{ kb.collection_name }}</span>
        </div>
        <div class="foot">
          <span class="time">{{ kb.create_time?.slice(0, 10) }}</span>
          <el-button size="small" text type="primary" @click="router.push(`/admin/documents?kb_id=${kb.id}`)">
            管理文档 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>

      <!-- 新建占位卡片 -->
      <div class="kb-card add card" @click="openDialog()">
        <el-icon :size="26"><Plus /></el-icon>
        <span>新建知识库</span>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑知识库' : '新建知识库'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="知识库名称" prop="name">
          <el-input v-model="form.name" maxlength="50" placeholder="如：人事制度" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="图标">
          <div class="icon-picker">
            <div
              v-for="ic in icons"
              :key="ic"
              class="ic"
              :class="{ active: form.icon === ic }"
              @click="form.icon = ic"
            >
              <el-icon :size="18"><component :is="ic" /></el-icon>
            </div>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createKb, deleteKb, getKbList, updateKb } from '@/api/kb'

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const list = ref([])
const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({ id: null, name: '', description: '', icon: 'Collection' })
const rules = { name: [{ required: true, message: '请输入知识库名称', trigger: 'blur' }] }

const icons = ['Collection', 'User', 'Monitor', 'Wallet', 'Reading', 'Briefcase', 'Box', 'Cpu', 'Flag', 'Notebook']
const colors = [
  ['#3b6cf6', '#eef3ff'],
  ['#7c5cff', '#f3efff'],
  ['#14b8d4', '#e8f9fc'],
  ['#f59e0b', '#fff6e6'],
  ['#16a34a', '#eaf7ef'],
]

/**
 * 按序号返回图标配色
 * @param {number} i 序号
 */
function iconStyle(i) {
  const [c, bg] = colors[i % colors.length]
  return { color: c, background: bg }
}

/** 加载知识库列表 */
async function load() {
  loading.value = true
  try {
    list.value = (await getKbList()).data
  } finally {
    loading.value = false
  }
}

/**
 * 打开新增 / 编辑弹窗
 * @param {Object} [kb] 编辑时传入知识库对象
 */
function openDialog(kb) {
  Object.assign(form, kb ? { ...kb } : { id: null, name: '', description: '', icon: 'Collection' })
  dialogVisible.value = true
}

/** 保存知识库 */
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    const payload = { name: form.name, description: form.description, icon: form.icon }
    form.id ? await updateKb(form.id, payload) : await createKb(payload)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

/**
 * 卡片菜单命令
 * @param {string} cmd edit | delete
 * @param {Object} kb 知识库
 */
async function onCommand(cmd, kb) {
  if (cmd === 'edit') return openDialog(kb)
  await ElMessageBox.confirm(`删除「${kb.name}」将同时删除其下所有文档与向量数据，确定继续吗？`, '危险操作', {
    type: 'warning',
    confirmButtonText: '确认删除',
  })
  await deleteKb(kb.id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>

<style scoped lang="scss">
.kb-page {
  max-width: 1400px;
  margin: 0 auto;
}

.kb-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 20px;
  min-height: 200px;
}

.kb-card {
  padding: 22px;
  display: flex;
  flex-direction: column;

  .top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .icon {
    width: 46px;
    height: 46px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .name {
    margin-top: 16px;
    font-size: 16px;
    font-weight: 600;
  }
  .desc {
    margin-top: 6px;
    font-size: 13px;
    color: var(--text-3);
    line-height: 1.6;
    height: 42px;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    font-size: 12.5px;
    color: var(--text-2);

    span {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .col {
      font-family: ui-monospace, Consolas, monospace;
      font-size: 11.5px;
      color: var(--text-3);
      background: var(--bg-muted);
      padding: 2px 8px;
      border-radius: 6px;
    }
  }
  .foot {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 14px;
    border-top: 1px solid var(--border);

    .time {
      font-size: 12px;
      color: var(--text-4);
    }
  }

  &.add {
    align-items: center;
    justify-content: center;
    gap: 10px;
    min-height: 236px;
    border: 1.5px dashed var(--border-strong);
    box-shadow: none;
    background: transparent;
    color: var(--text-3);
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-lighter);
    }
  }
}

.icon-picker {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  .ic {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-2);
    cursor: pointer;
    transition: all 0.2s;

    &:hover,
    &.active {
      border-color: var(--primary);
      color: var(--primary);
      background: var(--primary-light);
    }
  }
}
</style>
