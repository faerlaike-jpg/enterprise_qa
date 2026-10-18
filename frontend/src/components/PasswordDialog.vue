<!-- 修改密码弹窗：提交前对新旧密码做 MD5 -->
<template>
  <el-dialog v-model="visible" title="修改密码" width="420px" :close-on-click-modal="false" @closed="reset">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
      <el-form-item label="原密码" prop="oldPassword">
        <el-input v-model="form.oldPassword" type="password" show-password placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="form.newPassword" type="password" show-password placeholder="至少 6 位" />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" show-password placeholder="再次输入新密码" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="submit">确认修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import md5 from 'js-md5'
import { changePassword } from '@/api/auth'

const visible = defineModel({ type: Boolean, default: false })
const formRef = ref()
const loading = ref(false)
const form = reactive({ oldPassword: '', newPassword: '', confirm: '' })

const rules = {
  oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPassword: [{ required: true, min: 6, message: '新密码至少 6 位', trigger: 'blur' }],
  confirm: [
    {
      validator: (_, value, cb) => (value === form.newPassword ? cb() : cb(new Error('两次输入不一致'))),
      trigger: 'blur',
    },
  ],
}

/** 重置表单 */
function reset() {
  formRef.value?.resetFields()
}

/** 提交修改 */
async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await changePassword({ old_password: md5(form.oldPassword), new_password: md5(form.newPassword) })
    ElMessage.success('密码修改成功')
    visible.value = false
  } finally {
    loading.value = false
  }
}
</script>
