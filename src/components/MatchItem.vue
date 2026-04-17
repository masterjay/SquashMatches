<template>
  <div :class="['admin-match-item']">
    <div class="match-row">
      <div class="match-label" :style="{ opacity: label ? 1 : 0 }">
        {{ label || "佔位" }}
      </div>
      <!-- 編輯中顯示輸入框 -->
      <input
        v-if="isEditing"
        type="number"
        inputmode="numeric"
        v-model="inputValue"
        @keydown.enter.prevent="save"
        @keydown.esc.prevent="cancelEditMatch"
        @blur="save"
        class="match-input"
        placeholder="輸入場次"
        autofocus
        ref="inputRef"
      />
      <!-- 顯示場次號碼,可點擊編輯 -->
      <div
        v-else-if="match !== ''"
        :class="['match-number', 'editable']"
        @click="startEdit"
      >
        {{ match }}
      </div>
      <div v-else class="match-empty">-</div>
    </div>

    <!-- 按鈕區 -->
    <div class="match-actions">
      <button v-if="match != ''" @click="emit('remove')" class="btn-remove">
        −
      </button>
      <button v-else-if="isShowAddButton" @click="addMatch" class="btn-add">
        +
      </button>
    </div>
  </div>
</template>
<script setup lang="ts">
import { nextTick, ref, watch } from "vue";

const props = defineProps<{
  match: string; // 場次號碼，用來顯示
  label: string | null; // 標籤文字
  isShowAddButton: boolean; // 是否顯示 + 按鈕
  autoEdit: boolean;
}>();

const isEditing = ref(false);
const inputValue = ref(""); //使用者在 input 裡正在打的內容
const inputRef = ref<HTMLInputElement | null>(null); //input 元件

const emit = defineEmits(["add", "remove", "save"]);

// 新增場次 - 改進版：直接在原地新增輸入框
const addMatch = () => {
  isEditing.value = true;
  inputValue.value = "";
  emit("add");
  // 立即進入編輯模式
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus();
      // 滾動到輸入框位置,避免被鍵盤遮擋
      inputRef.value.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
};

const cancelEditMatch = () => {
  // 如果正在編輯空的新增場次,刪除它
  isEditing.value = false;
  inputValue.value = "";
};
// 場次編輯
const startEdit = () => {
  isEditing.value = true;
  inputValue.value = props.match;
  editing();
};

const editing = () => {
  nextTick(() => {
    if (inputRef.value) {
      inputRef.value.focus();
      // 在手機上選取全部文字
      if (inputRef.value.select) {
        inputRef.value.select();
      }
      // 滾動到輸入框位置
      inputRef.value.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
};

const save = () => {
  isEditing.value = false;
  emit("save", inputValue.value);
};

watch(
  () => props.autoEdit,
  (newVal) => {
    console.log("newVal", newVal);
    if (newVal) {
      isEditing.value = true;
      editing();
    }
  },
);
</script>

<style scoped>
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

@media (max-width: 640px) {
  /* 縮小場次標籤和號碼的字體 */
  .admin-match-item .match-label {
    font-size: 1rem;
  }

  .admin-match-item .match-number {
    font-size: 1.25rem;
  }

  /* 縮小場次卡片內部的gap */
  .admin-match-item .match-row {
    gap: 0.5rem;
  }
  /* 手機上的輸入框調整 */
  .match-input {
    font-size: 1.25rem;
    padding: 0.25rem;
  }

  /* 縮小按鈕 */
  .btn-add,
  .btn-remove {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    min-width: 2rem;
  }

  /* 縮小場次卡片的padding */
  .admin-match-item {
    padding: 0.375rem 0.5rem;
  }

  .match-empty {
    font-size: 1rem;
  }
}
</style>
