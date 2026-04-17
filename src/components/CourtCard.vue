<template>
  <div class="court-card admin-court">
    <!-- 標題編輯 -->
    <div class="court-header">
      <div v-if="editingTitle" class="title-edit-container">
        <input
          type="text"
          v-model="titleValue"
          @keydown.enter="saveTitle()"
          @keydown.esc="cancelEditTitle"
          ref="titleInput"
          class="title-input"
        />
        <button @click="saveTitle()" class="btn-check">✓</button>
        <button @click="cancelEditTitle" class="btn-close">✗</button>
      </div>
      <div v-else class="title-display">
        <h2 class="court-title">{{ court.title }}</h2>
        <button @click="startEditTitle()" class="btn-edit">✎</button>
      </div>
    </div>

    <!-- 場次列表 -->
    <div class="admin-matches">
      <!-- 前三個位置 -->
      <MatchItem
        v-for="(match, index) in displayMatches"
        :key="index"
        :match="match"
        :label="index < 3 ? ['目前場次', '下一場次', '下下場次'][index] : null"
        :isShowAddButton="shouldShowAddButton(index)"
        :autoEdit="autoEditIndex === index"
        @add="addMatchHandler"
        @save="(value) => saveMatch(index, value)"
        @remove="removeMatch(index)"
      />

      <!-- 最下方的 [+] 按鈕 -->
      <div
        v-if="court.matches && court.matches.length >= 3"
        class="add-more-container"
      >
        <button @click="addMatchHandler" class="btn-add-more">
          + 新增場次
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from "vue";
import MatchItem from "@/components/MatchItem.vue";

const props = defineProps<{
  court: { title: string; matches: string[] };
  courtId: string;
}>();

const emit = defineEmits(["sync"]);

const editingTitle = ref<boolean>(false);
const titleValue = ref("");
const titleInput = ref(null);
const autoEditIndex = ref<number | null>(null);

const displayMatches = computed(() => {
  const matches = props.court.matches || [];
  // 確保至少有 3 個項目，不足的補空字串
  while (matches.length < 3) {
    return [...matches, ...Array(3 - matches.length).fill("")];
  }
  return matches;
});
// 場地標題編輯
const startEditTitle = () => {
  editingTitle.value = true;
  titleValue.value = props.court.title;
  nextTick(() => {
    if (titleInput.value) {
      titleInput.value.focus();
    }
  });
};

const saveTitle = async () => {
  if (titleValue.value.trim()) {
    props.court.title = titleValue.value.trim();
    editingTitle.value = false;
    emit("sync");
  }
};

const cancelEditTitle = () => {
  editingTitle.value = false;
  titleValue.value = "";
};

const saveMatch = async (index: number, value: string) => {
  console.log("saveMatch called", {
    courtId: props.courtId,
    index,
    matchValue: value,
  });

  const trimmedValue = value ? value.toString().trim() : "";

  if (trimmedValue) {
    // 有輸入值,儲存
    props.court.matches[index] = trimmedValue;
    console.log("已儲存場次:", trimmedValue);
  } else {
    // 沒有輸入值,刪除這個空的場次
    props.court.matches.splice(index, 1);
    console.log("已刪除空場次");
  }
  autoEditIndex.value = null; // 重置，避免下次渲染時又觸發 autoEdit

  try {
    emit("sync");
  } catch (error) {
    console.error("同步失敗:", error);
  }
};

// 刪除場次 - 改進版：移除確認對話框,直接刪除
const removeMatch = async (index: number) => {
  props.court.matches.splice(index, 1);
  autoEditIndex.value = null; // 重置，避免下次渲染時又觸發 autoEdit

  emit("sync");
};

// 判斷是否該顯示新增按鈕
const shouldShowAddButton = (index: number) => {
  const matches = props.court.matches || [];
  if (index === 0) return matches.length === 0;
  if (index === 1) return matches.length === 1;
  if (index === 2) return matches.length === 2;
  return false;
};

const addMatchHandler = function () {
  // 新增一個空字串作為佔位
  props.court.matches.push("");
  nextTick(() => {
    autoEditIndex.value = props.court.matches.length - 1;
    // console.log("autoEditIndex set to", autoEditIndex.value);
  });
  // console.log("addMatchHandler", {
  //   matchesLength: props.court.matches.length,
  //   autoEditIndex: autoEditIndex.value,
  //   displayMatchesLength: displayMatches.value.length,
  // });
  emit("sync");
};
</script>
<style scoped>
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

@media (max-width: 640px) {
  /* 縮小場次卡片的間隔 */
  .admin-matches {
    gap: 0.25rem;
  }
}

.court-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 0.75rem;
}

.court-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}
</style>
