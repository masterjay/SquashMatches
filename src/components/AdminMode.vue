<template>
  <div>
    <!-- 標題列 -->
    <div class="admin-header">
      <!-- 主標題編輯 -->
      <div v-if="editingMainTitle" class="main-title-edit-container">
        <input
          type="text"
          v-model="mainTitleValue"
          @keydown.enter="saveMainTitle"
          @keydown.esc="cancelEditMainTitle"
          class="main-title-input"
          placeholder="輸入活動標題"
        />
        <button @click="saveMainTitle" class="btn-check">✓</button>
        <button @click="cancelEditMainTitle" class="btn-close">✗</button>
      </div>
      <div v-else class="main-title-display">
        <h1 class="admin-title">
          {{ store.mainTitle }}
          <span class="admin-badge">(管理模式)</span>
        </h1>
        <button @click="startEditMainTitle" class="btn-edit-main">✎</button>
      </div>

      <button @click="authStore.handleLogout" class="logout-button">
        登出
      </button>
    </div>

    <!-- 場地列表 -->
    <CourtCard
      v-for="courtId in ['A', 'B', 'C', 'D']"
      :key="courtId"
      :court="store.courts[courtId]"
      :courtId="courtId"
    />
    <!-- 使用說明 -->
    <div class="help-card">
      <h3 class="help-title">📋 操作說明</h3>
      <ul class="help-list">
        <li>• <strong>編輯場地標題</strong>：點擊場地名稱旁的編輯按鈕</li>
        <li>• <strong>新增場次</strong>：點擊 [+] 按鈕（場次會依序填入）</li>
        <li>
          • <strong>刪除場次</strong>：點擊 [−]
          按鈕（需要確認，後續場次會自動遞補）
        </li>
        <li>• <strong>即時同步</strong>：所有觀看者會立即看到你的更新</li>
        <li>• <strong>場地顯示</strong>：觀看者只會看到有場次的場地</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import CourtCard from "@/components/CourtCard.vue";
import { useMatchesStore } from "@/stores/matches.js";
import { useAuthStore } from "@/stores/auth.js";

const editingMainTitle = ref(false);
const mainTitleValue = ref("");
const store = useMatchesStore();
const authStore = useAuthStore();
// 主標題編輯
const startEditMainTitle = () => {
  mainTitleValue.value = store.mainTitle || "";
  editingMainTitle.value = true;
};

const saveMainTitle = async () => {
  if (mainTitleValue.value.trim()) {
    editingMainTitle.value = false;
    store.updateMainTitle(mainTitleValue.value);
  }
};

const cancelEditMainTitle = () => {
  editingMainTitle.value = false;
  mainTitleValue.value = "";
};
</script>

<style scoped>
/* 管理員模式 */
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.main-title-edit-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.main-title-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 2px solid #2563eb;
  border-radius: 0.5rem;
  font-size: 1.5rem;
  font-weight: bold;
  outline: none;
}

.main-title-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.btn-edit-main {
  background: transparent;
  color: #9ca3af;
  border: none;
  padding: 0.5rem;
  cursor: pointer;
  font-size: 1.125rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.btn-edit-main:hover {
  color: #2563eb;
  background: #eff6ff;
}

.admin-title {
  font-size: 1.875rem;
  font-weight: bold;
  color: #1b4c8d;
  margin: 0;
}

.admin-badge {
  font-size: 1.125rem;
  color: #f97316;
  margin-left: 0.5rem;
}

.logout-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #dc2626;
  color: white;
  font-weight: 600;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.2s;
}

.logout-button:hover {
  background: #b91c1c;
}

/* 說明卡片 */
.help-card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-top: 1.5rem;
}

.help-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.help-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-list li {
  font-size: 0.875rem;
  color: #4b5563;
  margin-bottom: 0.25rem;
}

.btn-check,
.btn-close {
  padding: 0.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.btn-check {
  background: #10b981;
  color: white;
}

.btn-check:hover {
  background: #059669;
}

.btn-close {
  background: #dc2626;
  color: white;
}

.btn-close:hover {
  background: #b91c1c;
}

@media (max-width: 640px) {
  /* 管理員模式 - 手機優化 */
  .admin-title {
    font-size: 1rem;
  }

  .main-title-input {
    font-size: 1rem;
  }

  .admin-badge {
    font-size: 0.875rem;
  }
}
</style>
