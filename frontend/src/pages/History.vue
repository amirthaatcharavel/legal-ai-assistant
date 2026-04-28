<template>
  <div class="min-h-screen px-6 md:px-16 lg:px-32 xl:px-48 py-12
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white transition-all duration-500">

    <!-- HEADER -->
    <div class="mb-10">
      <p class="text-sm tracking-widest text-yellow-600 dark:text-yellow-400 mb-2 uppercase">
        Workspace
      </p>
      <h1 class="text-5xl font-serif mb-3">Chat History</h1>
      <p class="text-gray-600 dark:text-gray-400">
        Review your past legal queries and AI generated responses.
      </p>
    </div>

    <!-- LOADING STATE -->
    <div v-if="loading" class="flex flex-col items-center justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mb-4"></div>
      <p class="text-gray-500 dark:text-gray-400 font-medium">Fetching history...</p>
    </div>

    <!-- LIST -->
    <div v-else-if="history.length > 0" class="grid gap-6">
      <div v-for="(item, index) in history" :key="index"
           class="p-6 rounded-2xl border shadow-sm transition-all hover:shadow-md
                  bg-white border-gray-200
                  dark:bg-[#0d2235] dark:border-[#1f3b55] group">
        
        <div class="flex items-start gap-4">
          <div class="mt-1 p-3 rounded-xl bg-yellow-50 dark:bg-yellow-900/20 group-hover:bg-yellow-100 dark:group-hover:bg-yellow-900/30 transition-colors">
            <MessageSquare class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
          </div>
          <div class="flex-1">
            <div class="flex justify-between items-start mb-3">
              <h3 class="font-bold text-xl text-gray-800 dark:text-gray-100 tracking-tight pr-4">
                {{ item.question }}
              </h3>
              <!-- DELETE BUTTON -->
              <button 
                @click="deleteHistoryItem(item.id, index)"
                class="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all focus:outline-none"
                title="Delete History"
              >
                <Trash2 class="w-5 h-5" />
              </button>
            </div>
            <div class="p-4 rounded-xl bg-gray-50 dark:bg-[#13293d]/50 border border-gray-100 dark:border-[#1f3b55]/50">
              <p class="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap">
                {{ item.answer }}
              </p>
            </div>
            <div class="mt-4 flex items-center justify-between">
              <div class="flex items-center gap-2 text-xs font-medium text-gray-400 dark:text-gray-500">
                <Clock class="w-3.5 h-3.5" />
                <span>{{ formatDate(item.createdAt) }}</span>
              </div>
              <span class="text-[10px] uppercase tracking-widest font-bold text-yellow-600/50 dark:text-yellow-400/30">
                Legal AI Assistant
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- EMPTY STATE -->
    <div v-else class="rounded-3xl p-12 text-center border shadow-lg
                bg-white border-gray-200
                dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
                dark:border-[#1f3b55]">

      <div class="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center
                  bg-gray-100 text-yellow-600
                  dark:bg-[#13293d] dark:text-yellow-400">
        <HistoryIcon class="w-10 h-10" />
      </div>

      <h2 class="text-3xl font-serif mb-3">No history found</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
        Your legal research history will appear here once you start asking questions.
      </p>

      <router-link to="/chat">
        <button class="px-8 py-4 rounded-full text-black font-bold
                       bg-yellow-500 hover:bg-yellow-400 
                       transition-all shadow-[0_4px_14px_0_rgba(234,179,8,0.39)] 
                       hover:shadow-[0_6px_20px_rgba(234,179,8,0.23)]">
          Start a new Session
        </button>
      </router-link>
    </div>

  </div>
</template>

<script>
import { db, auth } from "../firebase";
import { collection, getDocs, query, orderBy, deleteDoc, doc } from "firebase/firestore";
import { History as HistoryIcon, MessageSquare, Clock, Trash2 } from "lucide-vue-next";

export default {
  components: {
    HistoryIcon,
    MessageSquare,
    Clock,
    Trash2
  },
  data() {
    return {
      history: [],
      loading: true
    };
  },
  async created() {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        await this.fetchHistory(user.uid);
      } else {
        this.loading = false;
        this.history = [];
      }
    });
  },
  methods: {
    async fetchHistory(userId) {
      try {
        const historyRef = collection(db, "users", userId, "history");
        const q = query(historyRef, orderBy("createdAt", "desc"));
        
        const snapshot = await getDocs(q);
        this.history = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
      } catch (error) {
        console.error("Error fetching history:", error);
      } finally {
        this.loading = false;
      }
    },
    async deleteHistoryItem(docId, index) {
      const userId = auth.currentUser?.uid;
      if (!userId) return;

      // Optimistic update: remove from UI instantly
      this.history.splice(index, 1);

      try {
        // Delete from: users/{userId}/history/{docId}
        await deleteDoc(doc(db, "users", userId, "history", docId));
      } catch (error) {
        console.error("Error deleting history item:", error);
        // If error occurs, re-fetch history to sync UI
        await this.fetchHistory(userId);
      }
    },
    formatDate(timestamp) {
      if (!timestamp) return "Just now";
      const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
      return new Intl.DateTimeFormat('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }).format(date);
    }
  }
};
</script>

<style scoped>
/* Scoped styles can be added here */
</style>