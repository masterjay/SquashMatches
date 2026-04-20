<template>
  <div class="app-container">
    <LoadingScreen v-if="matchesStore.loading" />

    <!-- 一般使用者模式 -->
    <UserMode v-else-if="!authStore.isLoggedIn" class="main-container" />
    <AdminMode v-else class="main-container" />
    <!-- 管理員模式 -->
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from "vue";
import LoadingScreen from "./components/LoadingScreen.vue";
import UserMode from "./components/UserMode.vue";

// Firebase imports
import { initializeApp } from "firebase/app";
import AdminMode from "./components/AdminMode.vue";
import { useMatchesStore } from "@/stores/matches.js";
import { useAuthStore } from "@/stores/auth.js";

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
const authStore = useAuthStore();

try {
  initializeApp(firebaseConfig);
  console.log("✅ Firebase App 初始化成功");
} catch (error) {
  console.error("❌ Firebase 初始化失敗:", error);
}

// 初始化：監聽 Firebase 資料變化
onMounted(() => {
  console.log("📱 Component mounted，開始監聽 Firebase...");
  matchesStore.startSync();
});

// 清理監聽器
onUnmounted(() => {
  matchesStore.stopSync();
});
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
