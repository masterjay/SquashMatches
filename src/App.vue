<template>
  <div class="app-container">
    <LoadingScreen v-if="loading" />

    <!-- 一般使用者模式 -->
    <UserMode
      v-else-if="!isLoggedIn"
      class="main-container"
      :mainTitle="mainTitle"
      :courts="courts"
      @login="showLoginDialog"
    />
    <AdminMode
      v-else
      class="main-container"
      :main-title="mainTitle"
      :courts="courts"
      @logout="handleLogout"
      @sync="syncToFirebase"
      @update:main-title="(val) => (mainTitle = val)"
    />
    <!-- 管理員模式 -->
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from "vue";
import Swal from "sweetalert2";
import LoadingScreen from "./components/LoadingScreen.vue";
import UserMode from "./components/UserMode.vue";

// Firebase imports
import { initializeApp } from "firebase/app";
import {
  getDatabase,
  ref as dbRef,
  set,
  onValue,
  off,
} from "firebase/database";
import AdminMode from "./components/AdminMode.vue";

// Firebase 設定（請替換成你自己的設定）
const firebaseConfig = {
  apiKey: "AIzaSyDVI-FBnE2ATejjfeN4Iz7LLbPlIr8p_x4",
  authDomain: "squashmatches.firebaseapp.com",
  databaseURL:
    "https://squashmatches-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "squashmatches",
  storageBucket: "squashmatches.firebasestorage.app",
  messagingSenderId: "386779753475",
  appId: "1:386779753475:web:f57b1c4c2a4ab266e97236",
};

// 初始化 Firebase
console.log("🔥 開始初始化 Firebase...");
console.log("Firebase 設定:", firebaseConfig);

let app, database, dataRef;

try {
  app = initializeApp(firebaseConfig);
  console.log("✅ Firebase App 初始化成功");

  database = getDatabase(app);
  console.log("✅ Database 取得成功");

  dataRef = dbRef(database, "zhongzhengCup");
  console.log("✅ DataRef 建立成功，路徑: zhongzhengCup");
} catch (error) {
  console.error("❌ Firebase 初始化失敗:", error);
}

// 狀態管理
const loading = ref(false);
const isLoggedIn = ref(false);

const courts = reactive({
  A: { title: "A場", matches: [] },
  B: { title: "B場", matches: [] },
  C: { title: "C場", matches: [] },
  D: { title: "D場", matches: [] },
});

const mainTitle = ref("🏸 中正盃即時場次");

const ADMIN_PASSWORD = "admin123";

// 同步資料到 Firebase
const syncToFirebase = async () => {
  try {
    await set(dataRef, {
      mainTitle: mainTitle.value,
      courts: courts,
    });
  } catch (error) {
    console.error("同步失敗:", error);
    await Swal.fire({
      title: "同步失敗",
      text: "無法儲存資料到雲端，請檢查網路連線",
      icon: "error",
      confirmButtonText: "確定",
    });
  }
};

// 初始化：監聽 Firebase 資料變化
onMounted(() => {
  console.log("📱 Component mounted，開始監聽 Firebase...");
  loading.value = true;

  try {
    onValue(
      dataRef,
      (snapshot) => {
        console.log("📊 收到 Firebase 資料變化");
        const data = snapshot.val();
        console.log("資料內容:", data);

        if (data) {
          console.log("✅ 資料庫有資料，開始更新...");

          // 更新主標題
          if (data.mainTitle) {
            console.log("更新主標題:", data.mainTitle);
            mainTitle.value = data.mainTitle;
          }

          // 更新場地資料
          if (data.courts) {
            console.log("更新場地資料:", data.courts);
            // 確保每個場地都有 matches 屬性
            Object.keys(data.courts).forEach((courtId) => {
              if (!data.courts[courtId].matches) {
                data.courts[courtId].matches = [];
              }
            });
            Object.assign(courts, data.courts);
            console.log("場地資料更新完成:", courts);
          }
        } else {
          console.log("⚠️ 資料庫是空的，初始化預設資料...");

          // 如果資料庫是空的，初始化預設資料
          const defaultData = {
            mainTitle: "🏸 中正盃即時場次",
            courts: {
              A: { title: "A場", matches: ["100", "105", "109", "112"] },
              B: { title: "B場", matches: ["102", "104"] },
              C: { title: "C場", matches: [] },
              D: { title: "D場", matches: ["103", "107", "111"] },
            },
          };

          console.log("預設資料:", defaultData);
          mainTitle.value = defaultData.mainTitle;
          Object.assign(courts, defaultData.courts);
          console.log("本地資料已更新:", courts);

          // 寫入 Firebase
          console.log("嘗試寫入 Firebase...");
          set(dataRef, defaultData)
            .then(() => {
              console.log("✅ 預設資料寫入成功");
            })
            .catch((error) => {
              console.error("❌ 寫入失敗:", error);
              console.error("錯誤代碼:", error.code);
              console.error("錯誤訊息:", error.message);
            });
        }

        loading.value = false;
        console.log("✅ 載入完成");
      },
      (error) => {
        console.error("❌ 監聽 Firebase 時發生錯誤:", error);
        console.error("錯誤代碼:", error.code);
        console.error("錯誤訊息:", error.message);
        loading.value = false;
      },
    );
  } catch (error) {
    console.error("❌ 設定監聽器時發生錯誤:", error);
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
    title: "管理員登入",
    input: "password",
    inputLabel: "請輸入管理員密碼",
    inputPlaceholder: "輸入密碼",
    showCancelButton: true,
    confirmButtonText: "登入",
    cancelButtonText: "取消",
    confirmButtonColor: "#2563eb",
    cancelButtonColor: "#6b7280",
    inputValidator: (value) => {
      if (!value) {
        return "請輸入密碼！";
      }
    },
  });

  if (result.isConfirmed) {
    if (result.value === ADMIN_PASSWORD) {
      isLoggedIn.value = true;
    } else {
      await Swal.fire({
        title: "登入失敗",
        text: "密碼錯誤",
        icon: "error",
        confirmButtonText: "確定",
      });
    }
  }
};

// 登出處理
const handleLogout = async () => {
  const result = await Swal.fire({
    title: "確定要登出？",
    icon: "question",
    showCancelButton: true,
    confirmButtonText: "確定",
    cancelButtonText: "取消",
    confirmButtonColor: "#2563eb",
    cancelButtonColor: "#6b7280",
  });

  if (result.isConfirmed) {
    isLoggedIn.value = false;
  }
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    "Noto Sans TC",
    -apple-system,
    BlinkMacSystemFont,
    "Segoe UI",
    sans-serif;
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
</style>
