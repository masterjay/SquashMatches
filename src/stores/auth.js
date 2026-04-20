import { defineStore } from "pinia";
import { ref } from "vue";
import Swal from "sweetalert2";

const ADMIN_PASSWORD = "admin123";

export const useAuthStore = defineStore("auth", () => {
  // 狀態管理
  const isLoggedIn = ref(false);
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

  return { showLoginDialog, handleLogout, isLoggedIn };
});
