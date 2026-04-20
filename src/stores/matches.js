import {
  ref as dbRef,
  getDatabase,
  onValue,
  set,
  update,
} from "firebase/database";
import { defineStore } from "pinia";
import { ref } from "vue";
// 如果資料庫是空的，初始化預設資料
const defaultData = {
  mainTitle: "🏸 中正盃即時場次",
  courts: {
    A: { title: "A場", matches: [] },
    B: { title: "B場", matches: [] },
    C: { title: "C場", matches: [] },
    D: { title: "D場", matches: [] },
  },
};

// Firebase 資料庫的根節點路徑
const ROOT_PATH = "zhongzhengCup";

export const useMatchesStore = defineStore("matches", () => {
  const mainTitle = ref("");
  const courts = ref({});
  const loading = ref(true);

  let unsubscribe = null;

  function startSync() {
    console.log("📱 Store 開始監聽 Firebase...");
    loading.value = true;

    const db = getDatabase();
    const dataRef = dbRef(db, ROOT_PATH); // 監聽根節點

    unsubscribe = onValue(
      dataRef,
      (snapshot) => {
        console.log("📊 Store 收到 Firebase 資料變化");
        const data = snapshot.val();

        if (data) {
          // 更新主標題
          if (data.mainTitle) {
            mainTitle.value = data.mainTitle;
          }

          // 更新場地資料
          if (data.courts) {
            // 確保每個場地都有 matches 屬性
            Object.keys(data.courts).forEach((courtId) => {
              if (!data.courts[courtId].matches) {
                data.courts[courtId].matches = [];
              }
            });
            courts.value = data.courts;
          }
        } else {
          console.log("⚠️ 資料庫是空的，初始化預設資料...");

          // 更新本地
          mainTitle.value = defaultData.mainTitle;
          courts.value = defaultData.courts;

          // 寫入 Firebase
          set(dataRef, defaultData)
            .then(() => console.log("✅ 預設資料寫入成功"))
            .catch((error) => console.error("❌ 寫入失敗:", error));
        }

        loading.value = false;
      },
      (error) => {
        console.error("❌ 監聽 Firebase 時發生錯誤:", error);
        loading.value = false;
      },
    );
  }

  function stopSync() {
    if (unsubscribe) {
      unsubscribe();
      unsubscribe = null;
      console.log("🛑 Store 停止監聽");
    }
  }

  // ============ actions（寫入 Firebase）============
  function updateMainTitle(newTitle) {
    const db = getDatabase();
    update(dbRef(db, ROOT_PATH), { mainTitle: newTitle });
  }

  function updateCourtTitle(courtId, newTitle) {
    const db = getDatabase();
    update(dbRef(db, `${ROOT_PATH}/courts/${courtId}`), { title: newTitle });
  }

  function addMatch(courtId, matchNumber) {
    const db = getDatabase();
    const newMatches = [...courts.value[courtId].matches, matchNumber];
    set(dbRef(db, `${ROOT_PATH}/courts/${courtId}/matches`), newMatches);
  }

  function updateMatch(courtId, index, newValue) {
    const db = getDatabase();
    const newMatches = [...courts.value[courtId].matches];
    newMatches[index] = newValue;
    set(dbRef(db, `${ROOT_PATH}/courts/${courtId}/matches`), newMatches);
  }

  function removeMatch(courtId, index) {
    const db = getDatabase();
    const newMatches = courts.value[courtId].matches.filter(
      (_, i) => i !== index,
    );
    set(dbRef(db, `${ROOT_PATH}/courts/${courtId}/matches`), newMatches);
  }

  function getMatchAt(courtId, index) {
    return courts.value[courtId]?.matches?.[index] ?? "";
  }

  // ============ 暴露給元件 ============
  return {
    // state
    mainTitle,
    courts,
    loading,
    // sync control
    startSync,
    stopSync,
    // actions
    updateMainTitle,
    updateCourtTitle,
    addMatch,
    updateMatch,
    removeMatch,
    getMatchAt,
  };
});
