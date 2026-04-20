<template>
  <div class="app-container">
    <LoadingScreen v-if="matchesStore.loading" />

    <!-- 一般使用者模式 -->
    <UserMode
      v-else-if="!isLoggedIn"
      class="main-container"
      @login="showLoginDialog"
    />
    <AdminMode v-else class="main-container" @logout="handleLogout" />
    <!-- 管理員模式 -->
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Swal from "sweetalert2";
import LoadingScreen from "./components/LoadingScreen.vue";
import UserMode from "./components/UserMode.vue";

// Firebase imports
import { initializeApp } from "firebase/app";
import AdminMode from "./components/AdminMode.vue";
import { useMatchesStore } from "@/stores/matches.js";

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

const matchesStore = useMatchesStore();

try {
  initializeApp(firebaseConfig);
  console.log("✅ Firebase App 初始化成功");
} catch (error) {
  console.error("❌ Firebase 初始化失敗:", error);
}

// 狀態管理
const isLoggedIn = ref(false);

const ADMIN_PASSWORD = "admin123";

// 初始化：監聽 Firebase 資料變化
onMounted(() => {
  console.log("📱 Component mounted，開始監聽 Firebase...");
  matchesStore.startSync();
});

// 清理監聽器
onUnmounted(() => {
  matchesStore.stopSync();
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
