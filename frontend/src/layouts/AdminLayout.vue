<!-- 管理后台布局：左侧导航栏 + 顶部栏 + 内容区 -->
<template>
  <div class="admin-layout">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="logo-wrap">
        <AppLogo />
      </div>

      <div class="menu-group">管理中心</div>
      <nav class="menu">
        <router-link
          v-for="item in menus"
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: route.path === item.path }"
        >
          <el-icon :size="17"><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </router-link>
      </nav>

      <!-- 进入问答入口卡片 -->
      <div class="chat-entry" @click="router.push('/chat')">
        <div class="entry-icon">
          <el-icon :size="18"><ChatLineRound /></el-icon>
        </div>
        <div class="entry-text">
          <div class="t">智能问答</div>
          <div class="d">进入 AI 对话工作台</div>
        </div>
        <el-icon class="arrow"><ArrowRight /></el-icon>
      </div>
    </aside>

    <!-- 主区域 -->
    <section class="main">
      <header class="header">
        <div class="crumb">
          <span class="root">管理后台</span>
          <el-icon class="sep"><ArrowRight /></el-icon>
          <span class="current">{{ route.meta.title }}</span>
        </div>
        <div class="right">
          <el-tooltip content="智能问答" placement="bottom">
            <div class="icon-btn" @click="router.push('/chat')">
              <el-icon :size="18"><ChatDotRound /></el-icon>
            </div>
          </el-tooltip>
          <el-dropdown trigger="click" @command="onCommand">
            <div class="user-box">
              <el-avatar :size="32" class="avatar">{{ store.displayName.slice(0, 1) }}</el-avatar>
              <div class="info">
                <div class="name">{{ store.displayName }}</div>
                <div class="role">管理员</div>
              </div>
              <el-icon class="caret"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="password" icon="Lock">修改密码</el-dropdown-item>
                <el-dropdown-item command="logout" icon="SwitchButton" divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </section>

    <PasswordDialog v-model="pwdVisible" />
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import AppLogo from '@/components/AppLogo.vue'
import PasswordDialog from '@/components/PasswordDialog.vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const store = useUserStore()
const pwdVisible = ref(false)

/** 根据路由配置生成侧边栏菜单 */
const menus = computed(() => {
  const adminRoute = router.options.routes.find((r) => r.path === '/admin')
  return adminRoute.children.map((c) => ({ path: `/admin/${c.path}`, title: c.meta.title, icon: c.meta.icon }))
})

/**
 * 用户下拉菜单命令处理
 * @param {string} cmd password | logout
 */
async function onCommand(cmd) {
  if (cmd === 'password') {
    pwdVisible.value = true
  } else if (cmd === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', { type: 'warning' })
    store.logout()
    router.replace('/login')
  }
}
</script>

<style scoped lang="scss">
.admin-layout {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
}

// ---------- 侧边栏 ----------
.sidebar {
  width: var(--sidebar-width);
  flex-shrink: 0;
  background: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 0 14px 16px;

  .logo-wrap {
    height: var(--header-height);
    display: flex;
    align-items: center;
    padding: 0 8px;
    margin-bottom: 8px;
  }
  .menu-group {
    font-size: 11.5px;
    color: var(--text-4);
    font-weight: 600;
    letter-spacing: 1px;
    padding: 8px 12px;
  }
  .menu {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .menu-item {
    display: flex;
    align-items: center;
    gap: 12px;
    height: 42px;
    padding: 0 14px;
    border-radius: 10px;
    color: var(--text-2);
    font-weight: 500;
    transition: all 0.2s ease;
    position: relative;

    &:hover {
      background: var(--bg-muted);
      color: var(--text-1);
    }
    &.active {
      background: var(--primary-light);
      color: var(--primary);
      font-weight: 600;

      &::before {
        content: '';
        position: absolute;
        left: -14px;
        top: 11px;
        bottom: 11px;
        width: 3px;
        border-radius: 0 3px 3px 0;
        background: var(--primary);
      }
    }
  }
}

.chat-entry {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #eef3ff 0%, #f3efff 100%);
  border: 1px solid #e3e9fb;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
  }
  .entry-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: var(--primary-gradient);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .entry-text {
    flex: 1;
    .t {
      font-weight: 600;
      color: var(--text-1);
    }
    .d {
      font-size: 12px;
      color: var(--text-3);
      margin-top: 2px;
    }
  }
  .arrow {
    color: var(--text-3);
  }
}

// ---------- 主区域 ----------
.main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.header {
  height: var(--header-height);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);

  .crumb {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13.5px;
    .root {
      color: var(--text-3);
    }
    .sep {
      color: var(--text-4);
      font-size: 12px;
    }
    .current {
      color: var(--text-1);
      font-weight: 600;
    }
  }
  .right {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .icon-btn {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-2);
    cursor: pointer;
    transition: all 0.2s;
    &:hover {
      background: var(--bg-muted);
      color: var(--primary);
    }
  }
  .user-box {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 4px 10px 4px 4px;
    border-radius: 24px;
    cursor: pointer;
    transition: background 0.2s;
    outline: none;
    &:hover {
      background: var(--bg-muted);
    }
    .avatar {
      background: var(--primary-gradient);
      font-weight: 600;
    }
    .name {
      font-size: 13.5px;
      font-weight: 600;
      color: var(--text-1);
      line-height: 1.2;
    }
    .role {
      font-size: 11.5px;
      color: var(--text-3);
    }
    .caret {
      color: var(--text-3);
    }
  }
}

.content {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
}
</style>
