<template>
  <div>
    <!-- 標題區 -->
    <div class="header-container">
      <h1 class="main-title">{{ store.mainTitle }}</h1>
      <!-- 管理員登入按鈕 -->
      <button
        @click="authStore.showLoginDialog"
        class="admin-login-button"
        title="管理員登入"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </button>
    </div>

    <!-- 場次表格 -->
    <div class="matches-table-container">
      <table class="matches-table">
        <thead>
          <tr>
            <th class="table-header-label">場<br />地</th>
            <th
              v-for="courtId in ['A', 'B', 'C', 'D']"
              :key="courtId"
              class="table-header-court"
            >
              {{ store.courts[courtId].title }}
            </th>
          </tr>
        </thead>
        <tbody>
          <!-- 目前場次 -->
          <tr class="table-row match-0-row">
            <td class="table-cell-label match-0-label">目<br />前</td>
            <td
              v-for="courtId in ['A', 'B', 'C', 'D']"
              :key="`match-0-${courtId}`"
              class="table-cell-match match-0-cell"
            >
              <span v-if="store.getMatchAt(courtId, 0)">
                {{ store.getMatchAt(courtId, 0) }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
          <!-- 下一場次 -->
          <tr class="table-row match-1-row">
            <td class="table-cell-label match-1-label">下<br />一<br />場</td>
            <td
              v-for="courtId in ['A', 'B', 'C', 'D']"
              :key="`match-1-${courtId}`"
              class="table-cell-match match-1-cell"
            >
              <span v-if="store.getMatchAt(courtId, 1)">
                {{ store.getMatchAt(courtId, 1) }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
          <!-- 下下場次 -->
          <tr class="table-row match-2-row">
            <td class="table-cell-label match-2-label">下<br />下<br />場</td>
            <td
              v-for="courtId in ['A', 'B', 'C', 'D']"
              :key="`match-2-${courtId}`"
              class="table-cell-match match-2-cell"
            >
              <span v-if="store.getMatchAt(courtId, 2)">
                {{ store.getMatchAt(courtId, 2) }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { useMatchesStore } from "@/stores/matches.js";
import { useAuthStore } from "@/stores/auth.js";

const store = useMatchesStore();
const authStore = useAuthStore();
</script>

<style scoped>
/* 標題區 */
.header-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  position: relative;
}

.main-title {
  font-size: 2rem;
  font-weight: bold;
  color: #2f2f2f;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  text-align: center;
}

.admin-login-button {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: white;
  padding: 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  right: 0;
}

.admin-login-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

/* ========== 場次表格樣式 (一般使用者模式) ========== */
.matches-table-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.matches-table {
  width: 100%;
  border-collapse: collapse;
}

/* 表頭整列使用黑灰漸層 */
.matches-table thead {
  background: linear-gradient(to right, #374151 0%, #6b7280 100%);
}

.matches-table th {
  padding: 1rem;
  color: white;
  font-weight: bold;
  text-align: center;
  font-size: 1.125rem;
}

/* 場次數字格子 */
.table-cell-match {
  padding: 1rem;
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
}

.match-0-cell {
  background: linear-gradient(
    to right,
    rgba(234, 88, 12, 0.1) 0%,
    rgba(251, 146, 60, 0.1) 100%
  );
  color: #ea580c;
}

.match-1-cell {
  background: linear-gradient(
    to right,
    rgba(37, 99, 235, 0.1) 0%,
    rgba(96, 165, 250, 0.1) 100%
  );
  color: #2563eb;
}

.match-2-cell {
  background: linear-gradient(
    to right,
    rgba(5, 150, 105, 0.1) 0%,
    rgba(52, 211, 153, 0.1) 100%
  );
  color: #059669;
}

.match-empty-cell {
  color: #d1d5db;
  font-size: 1.5rem;
}

.matches-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

.matches-table tbody tr:last-child {
  border-bottom: none;
}

.matches-table tbody tr:hover {
  background: #f9fafb;
}

/* 左側標籤列 (目前/下一場/下下場) - 保持彩色漸層 */
.table-cell-label {
  padding: 1rem 0.5rem;
  font-weight: bold;
  font-size: 1.125rem;
  color: white;
  text-align: center;
  min-width: 3.5rem;
  line-height: 1.3;
}

/* 為左側標籤套用彩色漸層背景 */
.match-0-label {
  background: linear-gradient(to right, #ea580c 0%, #fb923c 100%);
}

.match-1-label {
  background: linear-gradient(to right, #2563eb 0%, #60a5fa 100%);
}

.match-2-label {
  background: linear-gradient(to right, #059669 0%, #34d399 100%);
}

/* 響應式設計 */
@media (max-width: 640px) {
  .admin-login-button {
    padding: 0.4rem;
  }

  .admin-login-button svg {
    width: 20px;
    height: 20px;
  }

  .table-header-label {
    font-size: 0.875rem;
    padding: 0.5rem 0.25rem;
    line-height: 1.2;
  }

  .table-header-court {
    font-size: 1rem;
  }

  /* 表格在手機上的樣式 */
  .matches-table th {
    padding: 0.75rem 0.5rem;
    font-size: 1rem;
  }

  .table-cell-label {
    padding: 0.75rem 0.25rem;
    font-size: 0.875rem;
    min-width: 2.5rem;
    line-height: 1.2;
  }

  .table-cell-match {
    padding: 0.75rem;
    font-size: 1.5rem;
  }
}
</style>
