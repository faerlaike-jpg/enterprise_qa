<!-- 用户管理：增删改查、启用禁用、重置密码 -->
<template>
  <div class="user-page">
    <div class="page-header">
      <div>
        <h2 class="title">用户管理</h2>
        <p class="subtitle">管理系统账号与角色权限，新建用户默认密码为 123456</p>
      </div>
      <el-button type="primary" icon="Plus" @click="openDialog()">新增用户</el-button>
    </div>

    <div class="card">
      <div class="toolbar">
        <div class="left">
          <el-input
            v-model="query.keyword"
            placeholder="搜索账号 / 昵称"
            prefix-icon="Search"
            clearable
            style="width: 240px"
            @keyup.enter="search"
            @clear="search"
          />
          <el-select v-model="query.role" placeholder="全部角色" clearable style="width: 140px" @change="search">
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </div>
      </div>

      <div class="table-wrap">
        <el-table v-loading="loading" :data="list">
          <el-table-column label="用户" min-width="200">
            <template #default="{ row }">
              <div class="user-cell">
                <el-avatar :size="34" class="av" :class="row.role">{{ (row.nickname || row.username).slice(0, 1) }}</el-avatar>
                <div>
                  <div class="nick">{{ row.nickname }}</div>
                  <div class="uname">@{{ row.username }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="部门" prop="department" min-width="120" />
          <el-table-column label="角色" width="120">
            <template #default="{ row }">
              <el-tag :type="row.role === 'admin' ? 'primary' : 'info'" effect="light">
                {{ row.role === 'admin' ? '管理员' : '普通用户' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-switch
                :model-value="row.status === 1"
                :disabled="row.id === store.user?.id"
                @change="(v) => toggleStatus(row, v)"
              />
            </template>
          </el-table-column>
          <el-table-column label="创建时间" prop="create_time" width="170" />
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
              <el-button link type="primary" @click="onReset(row)">重置密码</el-button>
              <el-button link type="danger" :disabled="row.id === store.user?.id" @click="onDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑用户' : '新增用户'" width="480px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="账号" prop="username">
          <el-input v-model="form.username" :disabled="!!form.id" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" placeholder="所属部门" />
        </el-form-item>
        <el-form-item label="角色">
          <el-radio-group v-model="form.role">
            <el-radio-button value="user">普通用户</el-radio-button>
            <el-radio-button value="admin">管理员</el-radio-button>
          </el-radio-group>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, deleteUser, getUsers, resetPassword, updateUser } from '@/api/user'
import { useUserStore } from '@/stores/user'

const store = useUserStore()
const loading = ref(false)
const saving = ref(false)
const list = ref([])
const total = ref(0)
const query = reactive({ page: 1, size: 10, keyword: '', role: '' })

const dialogVisible = ref(false)
const formRef = ref()
const form = reactive({ id: null, username: '', nickname: '', department: '', role: 'user' })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  nickname: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
}

/** 加载用户列表 */
async function load() {
  loading.value = true
  try {
    const { data } = await getUsers(query)
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
 * 打开新增 / 编辑弹窗
 * @param {Object} [row] 编辑的用户
 */
function openDialog(row) {
  Object.assign(form, row ? { ...row } : { id: null, username: '', nickname: '', department: '', role: 'user' })
  dialogVisible.value = true
}

/** 保存用户 */
async function save() {
  await formRef.value.validate()
  saving.value = true
  try {
    const payload = { username: form.username, nickname: form.nickname, department: form.department, role: form.role }
    const res = form.id ? await updateUser(form.id, payload) : await createUser(payload)
    ElMessage.success(res.msg)
    dialogVisible.value = false
    load()
  } finally {
    saving.value = false
  }
}

/**
 * 启用 / 禁用
 * @param {Object} row 用户
 * @param {boolean} enabled 是否启用
 */
async function toggleStatus(row, enabled) {
  await updateUser(row.id, { status: enabled ? 1 : 0 })
  row.status = enabled ? 1 : 0
  ElMessage.success(enabled ? '已启用' : '已禁用')
}

/**
 * 重置密码
 * @param {Object} row 用户
 */
async function onReset(row) {
  await ElMessageBox.confirm(`确定将「${row.nickname}」的密码重置为 123456 吗？`, '提示', { type: 'warning' })
  const res = await resetPassword(row.id)
  ElMessage.success(res.msg)
}

/**
 * 删除用户
 * @param {Object} row 用户
 */
async function onDelete(row) {
  await ElMessageBox.confirm(`确定删除用户「${row.nickname}」吗？`, '提示', { type: 'warning' })
  await deleteUser(row.id)
  ElMessage.success('删除成功')
  load()
}

onMounted(load)
</script>

<style scoped lang="scss">
.user-page {
  max-width: 1400px;
  margin: 0 auto;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;

  .av {
    flex-shrink: 0;
    font-weight: 600;
    background: linear-gradient(135deg, #8a94a6, #b5bdca);
    &.admin {
      background: var(--primary-gradient);
    }
  }
  .nick {
    font-weight: 600;
    color: var(--text-1);
  }
  .uname {
    font-size: 12px;
    color: var(--text-3);
    margin-top: 2px;
  }
}
</style>
