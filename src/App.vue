<template>
  <div class="app-container">
    <LoadingScreen v-if="loading" />

    <!-- 一般使用者模式 -->
    <div v-else-if="!isLoggedIn" class="main-container">
      <!-- 標題區 -->
      <div class="header-container">
        <h1 class="main-title">{{ mainTitle }}</h1>
        <!-- 管理員登入按鈕 -->
        <button @click="showLoginDialog" class="admin-login-button" title="管理員登入">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
            <th class="table-header-label">場<br>地</th>
            <th v-for="courtId in ['A', 'B', 'C', 'D']" :key="courtId"
                class="table-header-court">
              {{ courts[courtId].title }}
            </th>
          </tr>
          </thead>
          <tbody>
          <!-- 目前場次 -->
          <tr class="table-row match-0-row">
            <td class="table-cell-label match-0-label">目<br>前</td>
            <td v-for="courtId in ['A', 'B', 'C', 'D']" :key="`match-0-${courtId}`"
                class="table-cell-match match-0-cell">
              <span v-if="courts[courtId].matches && courts[courtId].matches[0]">
                {{ courts[courtId].matches[0] }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
          <!-- 下一場次 -->
          <tr class="table-row match-1-row">
            <td class="table-cell-label match-1-label">下<br>一<br>場</td>
            <td v-for="courtId in ['A', 'B', 'C', 'D']" :key="`match-1-${courtId}`"
                class="table-cell-match match-1-cell">
              <span v-if="courts[courtId].matches && courts[courtId].matches[1]">
                {{ courts[courtId].matches[1] }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
          <!-- 下下場次 -->
          <tr class="table-row match-2-row">
            <td class="table-cell-label match-2-label">下<br>下<br>場</td>
            <td v-for="courtId in ['A', 'B', 'C', 'D']" :key="`match-2-${courtId}`"
                class="table-cell-match match-2-cell">
              <span v-if="courts[courtId].matches && courts[courtId].matches[2]">
                {{ courts[courtId].matches[2] }}
              </span>
              <span v-else class="match-empty-cell">-</span>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 管理員模式 -->
    <div v-else class="main-container">
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

        <button @click="handleLogout" class="logout-button">
          登出
        </button>
      </div>

      <!-- 場地列表 -->
      <div v-for="courtId in ['A', 'B', 'C', 'D']" :key="courtId" class="court-card admin-court">
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
                {{ ['目前場次', '下一場次', '下下場次'][index] }}
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
                v-else-if="courts[courtId].matches && courts[courtId].matches[index] && courts[courtId].matches[index] !== ''"
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
              <div class="match-label" style="opacity: 0;">額外場次</div>

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
              <div v-else class="match-number" style="opacity: 0.3;">-</div>
            </div>

            <div class="match-actions">
              <button @click="removeMatch(courtId, idx + 3)" class="btn-remove">−</button>
            </div>
          </div>

          <!-- 最下方的 [+] 按鈕 -->
          <div v-if="courts[courtId].matches && courts[courtId].matches.length >= 3" class="add-more-container">
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
          <li>• <strong>刪除場次</strong>：點擊 [−] 按鈕（需要確認，後續場次會自動遞補）</li>
          <li>• <strong>即時同步</strong>：所有觀看者會立即看到你的更新</li>
          <li>• <strong>場地顯示</strong>：觀看者只會看到有場次的場地</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick, onMounted, onUnmounted } from 'vue';
import Swal from 'sweetalert2';
import LoadingScreen from './components/LoadingScreen.vue'

// Firebase imports
import { initializeApp } from 'firebase/app';
import { getDatabase, ref as dbRef, set, onValue, off } from 'firebase/database';

// Firebase 設定（請替換成你自己的設定）
const firebaseConfig = {
  apiKey: "AIzaSyDVI-FBnE2ATejjfeN4Iz7LLbPlIr8p_x4",
  authDomain: "squashmatches.firebaseapp.com",
  databaseURL: "https://squashmatches-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "squashmatches",
  storageBucket: "squashmatches.firebasestorage.app",
  messagingSenderId: "386779753475",
  appId: "1:386779753475:web:f57b1c4c2a4ab266e97236"
};

// 初始化 Firebase
console.log('🔥 開始初始化 Firebase...');
console.log('Firebase 設定:', firebaseConfig);

let app, database, dataRef;

try {
  app = initializeApp(firebaseConfig);
  console.log('✅ Firebase App 初始化成功');

  database = getDatabase(app);
  console.log('✅ Database 取得成功');

  dataRef = dbRef(database, 'zhongzhengCup');
  console.log('✅ DataRef 建立成功，路徑: zhongzhengCup');
} catch (error) {
  console.error('❌ Firebase 初始化失敗:', error);
}

// 狀態管理
const loading = ref(false);
const isLoggedIn = ref(false);
const password = ref('');
const loginError = ref('');

const courts = reactive({
  A: { title: 'A場', matches: [] },
  B: { title: 'B場', matches: [] },
  C: { title: 'C場', matches: [] },
  D: { title: 'D場', matches: [] }
});

const mainTitle = ref('🏸 中正盃即時場次');
const editingMainTitle = ref(false);
const mainTitleValue = ref('');

const editingTitle = ref(null);
const titleValue = ref('');
const titleInput = ref(null);

const editingMatch = ref(null);
const matchValue = ref('');

const ADMIN_PASSWORD = 'admin123';

// 同步資料到 Firebase
const syncToFirebase = async () => {
  try {
    await set(dataRef, {
      mainTitle: mainTitle.value,
      courts: courts
    });
  } catch (error) {
    console.error('同步失敗:', error);
    await Swal.fire({
      title: '同步失敗',
      text: '無法儲存資料到雲端，請檢查網路連線',
      icon: 'error',
      confirmButtonText: '確定'
    });
  }
};

// 初始化：監聽 Firebase 資料變化
onMounted(() => {
  console.log('📱 Component mounted，開始監聽 Firebase...');
  loading.value = true;

  try {
    onValue(dataRef, (snapshot) => {
      console.log('📊 收到 Firebase 資料變化');
      const data = snapshot.val();
      console.log('資料內容:', data);

      if (data) {
        console.log('✅ 資料庫有資料，開始更新...');

        // 更新主標題
        if (data.mainTitle) {
          console.log('更新主標題:', data.mainTitle);
          mainTitle.value = data.mainTitle;
        }

        // 更新場地資料
        if (data.courts) {
          console.log('更新場地資料:', data.courts);
          // 確保每個場地都有 matches 屬性
          Object.keys(data.courts).forEach(courtId => {
            if (!data.courts[courtId].matches) {
              data.courts[courtId].matches = [];
            }
          });
          Object.assign(courts, data.courts);
          console.log('場地資料更新完成:', courts);
        }
      } else {
        console.log('⚠️ 資料庫是空的，初始化預設資料...');

        // 如果資料庫是空的，初始化預設資料
        const defaultData = {
          mainTitle: '🏸 中正盃即時場次',
          courts: {
            A: { title: 'A場', matches: ['100', '105', '109', '112'] },
            B: { title: 'B場', matches: ['102', '104'] },
            C: { title: 'C場', matches: [] },
            D: { title: 'D場', matches: ['103', '107', '111'] }
          }
        };

        console.log('預設資料:', defaultData);
        mainTitle.value = defaultData.mainTitle;
        Object.assign(courts, defaultData.courts);
        console.log('本地資料已更新:', courts);

        // 寫入 Firebase
        console.log('嘗試寫入 Firebase...');
        set(dataRef, defaultData)
          .then(() => {
            console.log('✅ 預設資料寫入成功');
          })
          .catch((error) => {
            console.error('❌ 寫入失敗:', error);
            console.error('錯誤代碼:', error.code);
            console.error('錯誤訊息:', error.message);
          });
      }

      loading.value = false;
      console.log('✅ 載入完成');
    }, (error) => {
      console.error('❌ 監聽 Firebase 時發生錯誤:', error);
      console.error('錯誤代碼:', error.code);
      console.error('錯誤訊息:', error.message);
      loading.value = false;
    });
  } catch (error) {
    console.error('❌ 設定監聽器時發生錯誤:', error);
    loading.value = false;
  }
});

// 清理監聽器
onUnmounted(() => {
  off(dataRef);
});

// 登入處理
const showLoginDialog = async () => {
  const result = await Swal.fire({
    title: '管理員登入',
    input: 'password',
    inputLabel: '請輸入管理員密碼',
    inputPlaceholder: '輸入密碼',
    showCancelButton: true,
    confirmButtonText: '登入',
    cancelButtonText: '取消',
    confirmButtonColor: '#2563eb',
    cancelButtonColor: '#6b7280',
    inputValidator: (value) => {
      if (!value) {
        return '請輸入密碼！';
      }
    }
  });

  if (result.isConfirmed) {
    if (result.value === ADMIN_PASSWORD) {
      isLoggedIn.value = true;
    } else {
      await Swal.fire({
        title: '登入失敗',
        text: '密碼錯誤',
        icon: 'error',
        confirmButtonText: '確定'
      });
    }
  }
};

// 登出處理
const handleLogout = async () => {
  const result = await Swal.fire({
    title: '確定要登出？',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: '確定',
    cancelButtonText: '取消',
    confirmButtonColor: '#2563eb',
    cancelButtonColor: '#6b7280'
  });

  if (result.isConfirmed) {
    isLoggedIn.value = false;
  }
};

// 主標題編輯
const startEditMainTitle = () => {
  mainTitleValue.value = mainTitle.value;
  editingMainTitle.value = true;
};

const saveMainTitle = async () => {
  if (mainTitleValue.value.trim()) {
    mainTitle.value = mainTitleValue.value.trim();
    editingMainTitle.value = false;
    await syncToFirebase();
  }
};

const cancelEditMainTitle = () => {
  editingMainTitle.value = false;
  mainTitleValue.value = '';
};

// 場地標題編輯
const startEditTitle = (courtId) => {
  editingTitle.value = courtId;
  titleValue.value = courts[courtId].title;
  nextTick(() => {
    if (titleInput.value && titleInput.value[0]) {
      titleInput.value[0].focus();
    }
  });
};

const saveTitle = async (courtId) => {
  if (titleValue.value.trim()) {
    courts[courtId].title = titleValue.value.trim();
    editingTitle.value = null;
    await syncToFirebase();
  }
};

const cancelEditTitle = () => {
  editingTitle.value = null;
  titleValue.value = '';
};

// 場次編輯
const startEditMatch = (courtId, index) => {
  editingMatch.value = `${courtId}-${index}`;
  matchValue.value = courts[courtId].matches[index] || '';

  nextTick(() => {
    // 等待DOM更新後聚焦
    setTimeout(() => {
      const inputs = document.querySelectorAll('.match-input');
      const lastInput = inputs[inputs.length - 1];
      if (lastInput) {
        lastInput.focus();
        // 在手機上選取全部文字
        if (lastInput.select) {
          lastInput.select();
        }
        // 滾動到輸入框位置
        lastInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  });
};

const saveMatch = async (courtId, index) => {
  console.log('saveMatch called', { courtId, index, matchValue: matchValue.value, editingMatch: editingMatch.value });

  // 防止重複觸發
  if (!editingMatch.value || editingMatch.value !== `${courtId}-${index}`) {
    console.log('編輯狀態不匹配,跳過');
    return;
  }

  const trimmedValue = matchValue.value ? matchValue.value.toString().trim() : '';

  if (trimmedValue) {
    // 有輸入值,儲存
    courts[courtId].matches[index] = trimmedValue;
    console.log('已儲存場次:', trimmedValue);
  } else {
    // 沒有輸入值,刪除這個空的場次
    courts[courtId].matches.splice(index, 1);
    console.log('已刪除空場次');
  }

  editingMatch.value = null;
  matchValue.value = '';

  try {
    await syncToFirebase();
  } catch (error) {
    console.error('同步失敗:', error);
  }
};

const cancelEditMatch = () => {
  // 如果正在編輯空的新增場次,刪除它
  if (editingMatch.value) {
    const [courtId, indexStr] = editingMatch.value.split('-');
    const index = parseInt(indexStr);

    // 如果該場次是空的(剛新增的),則刪除
    if (courts[courtId].matches[index] === '') {
      courts[courtId].matches.splice(index, 1);
      syncToFirebase();
    }
  }

  editingMatch.value = null;
  matchValue.value = '';
};

// 判斷是否該顯示新增按鈕
const shouldShowAddButton = (courtId, index) => {
  const matches = courts[courtId].matches || [];
  if (index === 0) return matches.length === 0;
  if (index === 1) return matches.length === 1;
  if (index === 2) return matches.length === 2;
  return false;
};

// 新增場次 - 改進版：直接在原地新增輸入框
const addMatch = (courtId) => {
  if (!courts[courtId].matches) {
    courts[courtId].matches = [];
  }
  // 新增一個空字串作為佔位
  courts[courtId].matches.push('');
  const newIndex = courts[courtId].matches.length - 1;

  // 立即進入編輯模式
  nextTick(() => {
    editingMatch.value = `${courtId}-${newIndex}`;
    matchValue.value = '';

    // 延遲聚焦確保DOM完全更新
    setTimeout(() => {
      const inputs = document.querySelectorAll('.match-input');
      const lastInput = inputs[inputs.length - 1];
      if (lastInput) {
        lastInput.focus();
        // 滾動到輸入框位置,避免被鍵盤遮擋
        lastInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 150);
  });
};

// 刪除場次 - 改進版：移除確認對話框,直接刪除
const removeMatch = async (courtId, index) => {
  courts[courtId].matches.splice(index, 1);
  await syncToFirebase();
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Noto Sans TC', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #ffd78e 0%, #dac7ee 100%);
  padding: 1rem;
}





/* 主容器 */
.main-container {
  max-width: 1200px;
  margin: 0 auto;
}

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

/* 左上角的「場地」標籤 */
.table-header-label {
  font-size: 1.125rem;
  line-height: 1.3;
  padding: 0.75rem 0.5rem;
}

/* 場地標題 (A場、B場...) */
.table-header-court {
  font-size: 1.25rem;
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

.matches-table tbody tr {
  border-bottom: 1px solid #e5e7eb;
}

.matches-table tbody tr:last-child {
  border-bottom: none;
}

.matches-table tbody tr:hover {
  background: #f9fafb;
}

/* 場次數字格子 */
.table-cell-match {
  padding: 1rem;
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
}

.match-0-cell {
  background: linear-gradient(to right, rgba(234, 88, 12, 0.1) 0%, rgba(251, 146, 60, 0.1) 100%);
  color: #ea580c;
}

.match-1-cell {
  background: linear-gradient(to right, rgba(37, 99, 235, 0.1) 0%, rgba(96, 165, 250, 0.1) 100%);
  color: #2563eb;
}

.match-2-cell {
  background: linear-gradient(to right, rgba(5, 150, 105, 0.1) 0%, rgba(52, 211, 153, 0.1) 100%);
  color: #059669;
}

.match-empty-cell {
  color: #d1d5db;
  font-size: 1.5rem;
}

/* ========== 以下樣式保留給管理員模式使用 ========== */

/* ✅ 新增：2x2 網格佈局（超過2個場地時使用） */
.courts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

/* ✅ 新增：直板佈局（2個或以下場地時使用） */
.courts-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

/* 場地卡片 */
.court-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 0.75rem;
}

/* ✅ 新增：緊湊版場地卡片（用於2x2佈局） */
.court-card-compact {
  padding: 0.75rem;
  margin-bottom: 0;
}

.court-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

/* ✅ 新增：緊湊版標題 */
.court-title-compact {
  font-size: 1.125rem;
  margin-bottom: 0.25rem;
  text-align: center;
}

/* 場次列表 */
.matches-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* ✅ 新增：緊湊版場次容器 */
.matches-container-compact {
  gap: 0.5rem;
}

.match-item {
  border-radius: 0.5rem;
  padding: 0.5rem;
  transition: transform 0.2s;
}

/* ✅ 新增：緊湊版場次項目 */
.match-item-compact {
  padding: 0.25rem;
}

/* 維持原本的漂亮配色 - 改為由左至右從深到淺 */
.match-0 {
  background: linear-gradient(to right, #ea580c 0%, #fb923c 100%);
}

.match-1 {
  background: linear-gradient(to right, #2563eb 0%, #60a5fa 100%);
}

.match-2 {
  background: linear-gradient(to right, #059669 0%, #34d399 100%);
}

.match-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

/* ✅ 新增：緊湊版行 */
.match-row-compact {
  gap: 0.5rem;
}

.match-label {
  font-size: 1.875rem;
  font-weight: bold;
  color: white;
  /*text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);*/
  text-align: left;
}

/* ✅ 新增：緊湊版標籤 */
.match-label-compact {
  font-size: 0.875rem;
}

.match-number {
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
  /*text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);*/
  text-align: center;
  flex: 1;
}

/* ✅ 新增：緊湊版號碼 */
.match-number-compact {
  font-size: 1.5rem;
}

.match-number-0 {
  color: white;
  /*text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);*/
}

.match-number-1 {
  color: white;
  /*text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);*/
}

.match-number-2 {
  color: white;
  /*text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);*/
}

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

/* 管理員場地 */
.admin-court {
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
.admin-match-item.match-0,
.admin-match-item.match-1,
.admin-match-item.match-2,
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

/* 響應式設計 */
@media (max-width: 640px) {
  .main-title {
    font-size: 1.5rem;
  }

  .admin-login-button {
    padding: 0.4rem;
  }

  .admin-login-button svg {
    width: 20px;
    height: 20px;
  }

  /* 表格在手機上的樣式 */
  .matches-table th {
    padding: 0.75rem 0.5rem;
    font-size: 1rem;
  }

  .table-header-label {
    font-size: 0.875rem;
    padding: 0.5rem 0.25rem;
    line-height: 1.2;
  }

  .table-header-court {
    font-size: 1rem;
  }

  .table-cell-label {
    padding: 0.75rem 0.25rem;
    font-size: 0.875rem;
    min-width: 2.5rem;
    line-height: 1.2;
  }

  .table-cell-match {
    padding: 0.75rem 0.5rem;
    font-size: 1.25rem;
  }

  .match-empty-cell {
    font-size: 1rem;
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

  /* 手機上的輸入框調整 */
  .match-input {
    font-size: 1.25rem;
    padding: 0.25rem;
  }

  .match-input-extra {
    font-size: 1.25rem;
  }

  /* 縮小按鈕 */
  .btn-add,
  .btn-remove {
    padding: 0.375rem 0.5rem;
    font-size: 0.875rem;
    min-width: 2rem;
  }

  /* 縮小額外場次的佔位寬度,使其對齊前三個場次 */
  .match-label-placeholder {
    width: 5rem;
  }
}
</style>