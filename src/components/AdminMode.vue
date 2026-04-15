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
          {{ mainTitle }}
          <span class="admin-badge">(管理模式)</span>
        </h1>
        <button @click="startEditMainTitle" class="btn-edit-main">✎</button>
      </div>

      <button @click="$emit('logout')" class="logout-button">登出</button>
    </div>

    <!-- 場地列表 -->
    <div
      v-for="courtId in ['A', 'B', 'C', 'D']"
      :key="courtId"
      class="court-card admin-court"
    >
      <!-- 標題編輯 -->
      <div class="court-header">
        <div v-if="editingTitle === courtId" class="title-edit-container">
          <input
            type="text"
            v-model="titleValue"
            @keydown.enter="saveTitle(courtId)"
            @keydown.esc="cancelEditTitle"
            ref="titleInput"
            class="title-input"
          />
          <button @click="saveTitle(courtId)" class="btn-check">✓</button>
          <button @click="cancelEditTitle" class="btn-close">✗</button>
        </div>
        <div v-else class="title-display">
          <h2 class="court-title">{{ courts[courtId].title }}</h2>
          <button @click="startEditTitle(courtId)" class="btn-edit">✎</button>
        </div>
      </div>

      <!-- 場次列表 -->
      <div class="admin-matches">
        <!-- 前三個位置 -->
        <div
          v-for="index in [0, 1, 2]"
          :key="index"
          :class="['admin-match-item', `match-${index}`]"
        >
          <div class="match-row">
            <div class="match-label">
              {{ ["目前場次", "下一場次", "下下場次"][index] }}
            </div>
            <!-- 編輯中顯示輸入框 -->
            <input
              v-if="editingMatch === `${courtId}-${index}`"
              type="number"
              inputmode="numeric"
              v-model="matchValue"
              @keydown.enter.prevent="saveMatch(courtId, index)"
              @keydown.esc.prevent="cancelEditMatch"
              @blur="saveMatch(courtId, index)"
              class="match-input"
              placeholder="輸入場次"
              autofocus
            />
            <!-- 顯示場次號碼,可點擊編輯 -->
            <div
              v-else-if="
                courts[courtId].matches &&
                courts[courtId].matches[index] &&
                courts[courtId].matches[index] !== ''
              "
              :class="['match-number', `match-number-${index}`, 'editable']"
              @click="startEditMatch(courtId, index)"
            >
              {{ courts[courtId].matches[index] }}
            </div>
            <div v-else class="match-empty">-</div>
          </div>

          <!-- 按鈕區 -->
          <div class="match-actions">
            <button
              v-if="courts[courtId].matches && courts[courtId].matches[index]"
              @click="removeMatch(courtId, index)"
              class="btn-remove"
            >
              −
            </button>
            <button
              v-else-if="shouldShowAddButton(courtId, index)"
              @click="addMatch(courtId)"
              class="btn-add"
            >
              +
            </button>
          </div>
        </div>

        <!-- 第四個之後的場次 -->
        <div
          v-for="(match, idx) in (courts[courtId].matches || []).slice(3)"
          :key="idx + 3"
          class="admin-match-extra"
        >
          <div class="match-row">
            <!-- 透明的標籤佔位,保持格式對齊 -->
            <div class="match-label" style="opacity: 0">額外場次</div>

            <!-- 編輯中顯示輸入框 -->
            <input
              v-if="editingMatch === `${courtId}-${idx + 3}`"
              type="number"
              inputmode="numeric"
              v-model="matchValue"
              @keydown.enter.prevent="saveMatch(courtId, idx + 3)"
              @keydown.esc.prevent="cancelEditMatch"
              @blur="saveMatch(courtId, idx + 3)"
              class="match-input match-input-extra"
              placeholder="輸入場次"
              autofocus
            />
            <!-- 顯示場次號碼,可點擊編輯 -->
            <div
              v-else-if="match !== ''"
              class="match-number editable"
              @click="startEditMatch(courtId, idx + 3)"
            >
              {{ match }}
            </div>
            <!-- 空場次顯示為空 -->
            <div v-else class="match-number" style="opacity: 0.3">-</div>
          </div>

          <div class="match-actions">
            <button @click="removeMatch(courtId, idx + 3)" class="btn-remove">
              −
            </button>
          </div>
        </div>

        <!-- 最下方的 [+] 按鈕 -->
        <div
          v-if="courts[courtId].matches && courts[courtId].matches.length >= 3"
          class="add-more-container"
        >
          <button @click="addMatch(courtId)" class="btn-add-more">
            + 新增場次
          </button>
        </div>
      </div>
    </div>

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
import { nextTick, ref } from "vue";

const props = defineProps({
  courts: Object,
  mainTitle: String,
});

const emit = defineEmits(["update:main-title", "logout", "sync"]);

const editingMainTitle = ref(false);
const mainTitleValue = ref("");
const editingTitle = ref(null);
const titleValue = ref("");
const titleInput = ref(null);
const editingMatch = ref(null);
const matchValue = ref("");

// 主標題編輯
const startEditMainTitle = () => {
  mainTitleValue.value = props.mainTitle || "";
  editingMainTitle.value = true;
};

const saveMainTitle = async () => {
  if (mainTitleValue.value.trim()) {
    emit("update:main-title", mainTitleValue.value.trim());
    editingMainTitle.value = false;
    emit("sync");
  }
};

const cancelEditMainTitle = () => {
  editingMainTitle.value = false;
  mainTitleValue.value = "";
};

// 場地標題編輯
const startEditTitle = (courtId) => {
  editingTitle.value = courtId;
  titleValue.value = props.courts[courtId].title;
  nextTick(() => {
    if (titleInput.value && titleInput.value[0]) {
      titleInput.value[0].focus();
    }
  });
};

const saveTitle = async (courtId) => {
  if (titleValue.value.trim()) {
    props.courts[courtId].title = titleValue.value.trim();
    editingTitle.value = null;
    emit("sync");
  }
};

const cancelEditTitle = () => {
  editingTitle.value = null;
  titleValue.value = "";
};

// 場次編輯
const startEditMatch = (courtId, index) => {
  editingMatch.value = `${courtId}-${index}`;
  matchValue.value = props.courts[courtId].matches[index] || "";

  nextTick(() => {
    // 等待DOM更新後聚焦
    setTimeout(() => {
      const inputs = document.querySelectorAll(".match-input");
      const lastInput = inputs[inputs.length - 1];
      if (lastInput) {
        lastInput.focus();
        // 在手機上選取全部文字
        if (lastInput.select) {
          lastInput.select();
        }
        // 滾動到輸入框位置
        lastInput.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 100);
  });
};
const saveMatch = async (courtId, index) => {
  console.log("saveMatch called", {
    courtId,
    index,
    matchValue: matchValue.value,
    editingMatch: editingMatch.value,
  });

  // 防止重複觸發
  if (!editingMatch.value || editingMatch.value !== `${courtId}-${index}`) {
    console.log("編輯狀態不匹配,跳過");
    return;
  }

  const trimmedValue = matchValue.value
    ? matchValue.value.toString().trim()
    : "";

  if (trimmedValue) {
    // 有輸入值,儲存
    props.courts[courtId].matches[index] = trimmedValue;
    console.log("已儲存場次:", trimmedValue);
  } else {
    // 沒有輸入值,刪除這個空的場次
    props.courts[courtId].matches.splice(index, 1);
    console.log("已刪除空場次");
  }

  editingMatch.value = null;
  matchValue.value = "";

  try {
    emit("sync");
  } catch (error) {
    console.error("同步失敗:", error);
  }
};

const cancelEditMatch = () => {
  // 如果正在編輯空的新增場次,刪除它
  if (editingMatch.value) {
    const [courtId, indexStr] = editingMatch.value.split("-");
    const index = parseInt(indexStr);

    // 如果該場次是空的(剛新增的),則刪除
    if (props.courts[courtId].matches[index] === "") {
      props.courts[courtId].matches.splice(index, 1);
      emit("sync");
    }
  }

  editingMatch.value = null;
  matchValue.value = "";
};

// 新增場次 - 改進版：直接在原地新增輸入框
const addMatch = (courtId) => {
  if (!props.courts[courtId].matches) {
    props.courts[courtId].matches = [];
  }
  // 新增一個空字串作為佔位
  props.courts[courtId].matches.push("");
  const newIndex = props.courts[courtId].matches.length - 1;

  // 立即進入編輯模式
  nextTick(() => {
    editingMatch.value = `${courtId}-${newIndex}`;
    matchValue.value = "";

    // 延遲聚焦確保DOM完全更新
    setTimeout(() => {
      const inputs = document.querySelectorAll(".match-input");
      const lastInput = inputs[inputs.length - 1];
      if (lastInput) {
        lastInput.focus();
        // 滾動到輸入框位置,避免被鍵盤遮擋
        lastInput.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 150);
  });
};

// 刪除場次 - 改進版：移除確認對話框,直接刪除
const removeMatch = async (courtId, index) => {
  props.courts[courtId].matches.splice(index, 1);
  emit("sync");
};

// 判斷是否該顯示新增按鈕
const shouldShowAddButton = (courtId, index) => {
  const matches = props.courts[courtId].matches || [];
  if (index === 0) return matches.length === 0;
  if (index === 1) return matches.length === 1;
  if (index === 2) return matches.length === 2;
  return false;
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

.court-header {
  margin-bottom: 1rem;
}

.title-edit-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 2px solid #2563eb;
  border-radius: 0.5rem;
  font-size: 1.25rem;
  font-weight: bold;
  outline: none;
}

.title-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-check,
.btn-close,
.btn-edit {
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

.btn-edit {
  background: transparent;
  color: #9ca3af;
}

.btn-edit:hover {
  color: #2563eb;
}

/* 管理員場次列表 */
.admin-matches {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.admin-match-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: 0.5rem;
  gap: 0.5rem;
}

/* 為管理員的場次套用統一的灰色漸層配色 - 由左至右從深到淺 */
.admin-match-item {
  background: linear-gradient(to right, #6b7280 0%, #9ca3af 100%);
}

.admin-match-item .match-row {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.admin-match-item .match-label {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-align: left;
  flex-shrink: 0;
}

.admin-match-item .match-number {
  font-size: 2rem;
  font-weight: bold;
  text-align: center;
  flex: 1;
  color: white;
}

/* 可編輯的場次號碼樣式 */
.match-number.editable {
  cursor: pointer;
  transition: all 0.2s;
  border-radius: 0.25rem;
  padding: 0.25rem;
}

.match-number.editable:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

/* 場次輸入框樣式 */
.match-input {
  flex: 1;
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  background: white;
  border: 2px solid #2563eb;
  border-radius: 0.375rem;
  padding: 0.5rem;
  outline: none;
  width: 100%;
  min-width: 0;
  -webkit-appearance: none;
  appearance: none;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.match-input:focus {
  border-color: #1d4ed8;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.2);
}

.match-input-extra {
  font-size: 2rem;
}

.match-empty {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-align: center;
  flex: 1;
}

.match-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-add,
.btn-remove {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
  transition: all 0.2s;
  min-width: 2.5rem;
}

.btn-add {
  background: #2563eb;
  color: white;
}

.btn-add:hover {
  background: #1d4ed8;
}

.btn-remove {
  background: #dc2626;
  color: white;
}

.btn-remove:hover {
  background: #b91c1c;
}

/* 額外場次 - 使用與前三個相同的結構 */
.admin-match-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: 0.5rem;
  gap: 0.5rem;
  background: linear-gradient(to right, #6b7280 0%, #9ca3af 100%);
}

.admin-match-extra .match-row {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.admin-match-extra .match-label {
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
  text-align: left;
  flex-shrink: 0;
}

.admin-match-extra .match-number {
  font-size: 2rem;
  font-weight: bold;
  text-align: center;
  flex: 1;
  color: white;
}

/* 新增更多按鈕 */
.add-more-container {
  display: flex;
  justify-content: center;
  padding-top: 0.5rem;
}

.btn-add-more {
  background: #1d4ed8;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-add-more:hover {
  background: #1d4ed8;
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

@media (max-width: 640px) {
  /* 手機上的輸入框調整 */
  .match-input {
    font-size: 1.25rem;
    padding: 0.25rem;
  }

  .match-input-extra {
    font-size: 1.25rem;
  }

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

  /* 縮小場次標籤和號碼的字體 */
  .admin-match-item .match-label {
    font-size: 1rem;
  }

  .admin-match-item .match-number {
    font-size: 1.25rem;
  }

  .match-empty {
    font-size: 1rem;
  }

  /* 額外場次 */
  .admin-match-extra {
    padding: 0.375rem 0.5rem;
  }

  .admin-match-extra .match-row {
    gap: 0.5rem;
  }

  .admin-match-extra .match-label {
    font-size: 1rem;
  }

  .admin-match-extra .match-number {
    font-size: 1.25rem;
  }

  /* 縮小按鈕 */
  .btn-add,
  .btn-remove {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    min-width: 2rem;
  }

  /* 縮小場次卡片的間隔 */
  .admin-matches {
    gap: 0.25rem;
  }

  /* 縮小場次卡片的padding */
  .admin-match-item {
    padding: 0.375rem 0.5rem;
  }

  /* 縮小場次卡片內部的gap */
  .admin-match-item .match-row {
    gap: 0.5rem;
  }
}
</style>
