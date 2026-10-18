<!-- 登录页：左侧品牌展示区 + 右侧登录卡片 -->
<template>
  <div class="login-page">
    <!-- 左侧品牌区 -->
    <section class="brand">
      <div class="grid-bg"></div>
      <div class="glow g1"></div>
      <div class="glow g2"></div>

      <AppLogo light class="brand-logo" />

      <div class="brand-body">
        <div class="badge">
          <span class="pulse"></span>
          LangChain · RAG · Agent
        </div>
        <h1>让企业知识<br />触手可及</h1>
        <p>基于检索增强生成技术的企业内部知识库问答平台，秒级检索制度文档，精准回答员工问题。</p>

        <div class="features">
          <div v-for="f in features" :key="f.title" class="feature">
            <div class="f-icon">
              <el-icon :size="18"><component :is="f.icon" /></el-icon>
            </div>
            <div>
              <div class="f-title">{{ f.title }}</div>
              <div class="f-desc">{{ f.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="brand-foot">© 2026 智问 Enterprise Knowledge Platform</div>
    </section>

    <!-- 右侧登录区 -->
    <section class="form-side">
      <div class="login-card">
        <h2>欢迎回来</h2>
        <p class="tip">请使用企业账号登录系统</p>

        <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="onLogin">
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="请输入账号" prefix-icon="User" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" prefix-icon="Lock" />
          </el-form-item>
          <el-button type="primary" class="submit" :loading="loading" @click="onLogin">登 录</el-button>
        </el-form>

        <div class="quick">
          <div class="quick-title">体验账号（密码均为 123456）</div>
          <div class="quick-list">
            <div class="quick-item" @click="fill('admin')">
              <el-icon><Avatar /></el-icon>
              <span>admin</span>
              <el-tag size="small" type="primary" effect="light">管理员</el-tag>
            </div>
            <div class="quick-item" @click="fill('zhangsan')">
              <el-icon><User /></el-icon>
              <span>zhangsan</span>
              <el-tag size="small" type="info" effect="light">普通用户</el-tag>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import AppLogo from '@/components/AppLogo.vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const store = useUserStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const features = [
  { icon: 'Search', title: '语义检索', desc: 'Chroma 向量库 + 百炼嵌入模型' },
  { icon: 'MagicStick', title: '智能 Agent', desc: 'DeepSeek 大模型自主调用工具' },
  { icon: 'Lock', title: '权限隔离', desc: '管理员 / 普通用户双角色体系' },
]

/**
 * 快速填充体验账号
 * @param {string} username 账号
 */
function fill(username) {
  form.username = username
  form.password = '123456'
}

/** 登录并按角色跳转 */
async function onLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const user = await store.login(form.username, form.password)
    ElMessage.success(`欢迎，${user.nickname || user.username}`)
    const target = route.query.redirect || (user.role === 'admin' ? '/admin/home' : '/chat')
    router.replace(target)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
}

// ---------- 品牌区 ----------
.brand {
  position: relative;
  flex: 1.15;
  overflow: hidden;
  background: linear-gradient(150deg, #0f1b3d 0%, #1b2f6b 55%, #2b4ac0 100%);
  color: #fff;
  display: flex;
  flex-direction: column;
  padding: 40px 64px;

  .grid-bg {
    position: absolute;
    inset: 0;
    background-image: linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
    background-size: 44px 44px;
    mask-image: radial-gradient(ellipse at 30% 40%, #000 30%, transparent 75%);
  }
  .glow {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.55;
  }
  .g1 {
    width: 420px;
    height: 420px;
    background: #4f7bff;
    right: -120px;
    top: -80px;
  }
  .g2 {
    width: 360px;
    height: 360px;
    background: #7c5cff;
    left: -100px;
    bottom: -120px;
    opacity: 0.35;
  }
  .brand-logo,
  .brand-body,
  .brand-foot {
    position: relative;
    z-index: 1;
  }
  .brand-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-width: 520px;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    align-self: flex-start;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12.5px;
    background: rgba(255, 255, 255, 0.1);
    border: 1px solid rgba(255, 255, 255, 0.16);
    backdrop-filter: blur(8px);
  }
  .pulse {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.2);
  }
  h1 {
    font-size: 46px;
    line-height: 1.2;
    font-weight: 700;
    margin: 24px 0 16px;
    letter-spacing: 1px;
    background: linear-gradient(90deg, #fff 0%, #c7d6ff 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }
  p {
    color: rgba(255, 255, 255, 0.72);
    line-height: 1.8;
    font-size: 15px;
    margin: 0 0 36px;
  }
  .features {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .feature {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
  }
  .f-icon {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.12);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .f-title {
    font-weight: 600;
  }
  .f-desc {
    font-size: 12.5px;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 2px;
  }
  .brand-foot {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.45);
  }
}

// ---------- 登录区 ----------
.form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.login-card {
  width: 400px;
  padding: 44px 40px 32px;
  background: var(--bg-surface);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-lg);

  h2 {
    margin: 0;
    font-size: 26px;
    font-weight: 700;
  }
  .tip {
    margin: 8px 0 30px;
    color: var(--text-3);
  }
  .submit {
    width: 100%;
    height: 46px;
    font-size: 15px;
    margin-top: 6px;
    border-radius: 10px;
  }
}

.quick {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px dashed var(--border-strong);

  .quick-title {
    font-size: 12px;
    color: var(--text-3);
    margin-bottom: 12px;
  }
  .quick-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .quick-item {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 10px 12px;
    border-radius: 10px;
    background: var(--bg-muted);
    font-size: 13px;
    color: var(--text-2);
    cursor: pointer;
    transition: all 0.2s;

    span {
      flex: 1;
    }
    &:hover {
      background: var(--primary-light);
      color: var(--primary);
    }
  }
}

@media (max-width: 900px) {
  .brand {
    display: none;
  }
}
</style>
