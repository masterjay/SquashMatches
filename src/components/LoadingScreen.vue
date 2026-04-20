<template>
  <div class="loading-screen">
      <div class="loading-content">
        <div class="spinner"></div>
        <p class="loading-text">載入中...</p>
      </div>
    </div>
</template>

<script setup>
</script>

<style scoped>
/* 載入畫面 */
.loading-screen {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}

.loading-content {
  text-align: center;
}

.spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 1.125rem;
  font-weight: 500;
}
</style>
