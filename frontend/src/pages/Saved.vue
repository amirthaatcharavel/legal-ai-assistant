<template>
  <div class="min-h-screen transition-all duration-500
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white px-6 md:px-16 lg:px-32 xl:px-48 py-16">

```
<!-- HEADER -->
<div class="max-w-4xl">
  <p class="text-xs tracking-widest text-yellow-500 mb-3 uppercase font-bold">
    Library
  </p>

  <h1 class="text-5xl md:text-6xl font-serif">
    Saved Cases
  </h1>

  <p class="mt-4 text-gray-600 dark:text-gray-400 text-lg">
    Your personal repository of legal precedents and bookmarked research.
  </p>
</div>

<!-- 🔍 SEARCH BAR -->
<div class="mt-10 max-w-md">
  <input
    v-model="searchQuery"
    placeholder="Search saved cases..."
    class="w-full p-3 rounded-xl border
           bg-gray-100 text-gray-700
           dark:bg-[#13293d] dark:text-white
           dark:border-[#1f3b55]"
  />
</div>

<!-- LOADING -->
<div v-if="loading" class="mt-20 flex flex-col items-center justify-center">
  <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-yellow-500 mb-4"></div>
  <p class="text-gray-500 dark:text-gray-400">Loading your library...</p>
</div>

<!-- LIST -->
<div v-else-if="filteredItems.length > 0" class="mt-12 grid gap-6">

  <div v-for="item in filteredItems" :key="item.id"
       class="p-8 rounded-3xl border shadow-sm transition-all hover:shadow-md
              bg-white border-gray-200
              dark:bg-[#0d2235] dark:border-[#1f3b55] group">

    <!-- HEADER -->
    <div class="flex justify-between items-start mb-4">
      <div class="flex-1">
        <h3 class="text-2xl font-bold text-gray-800 dark:text-gray-100 leading-tight">
          {{ item.caseTitle }}
        </h3>
      </div>

      <div class="flex items-center gap-2">
        <Bookmark class="w-5 h-5 text-yellow-500 fill-yellow-500/20" />

        <!-- DELETE -->
        <button @click="deleteCase(item.id)"
                class="text-red-500 hover:text-red-400 text-xs">
          ✕
        </button>
      </div>
    </div>

    <!-- SUMMARY -->
    <p class="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed whitespace-pre-wrap">
      {{ item.summary }}
    </p>

    <!-- ACTIONS -->
    <div class="flex items-center justify-between flex-wrap gap-3">

      <!-- LEFT INFO -->
      <div class="flex items-center gap-4 flex-wrap">
        <div v-if="item.court"
             class="text-xs font-semibold text-gray-500 dark:text-gray-400
                    bg-gray-100 dark:bg-[#13293d] px-3 py-1 rounded-full uppercase">
          {{ item.court }}
        </div>

        <div v-if="item.year"
             class="text-xs font-semibold text-gray-500 dark:text-gray-400
                    bg-gray-100 dark:bg-[#13293d] px-3 py-1 rounded-full">
          {{ item.year }}
        </div>
      </div>

      <!-- RIGHT ACTIONS -->
      <div class="flex items-center gap-4">

        <!-- 🔥 VIEW FULL CASE -->
        <a v-if="item.link"
           :href="item.link"
           target="_blank"
           class="text-yellow-500 text-sm font-medium hover:underline">
          View Full Case →
        </a>

        <!-- DATE -->
        <div class="flex items-center gap-1 text-[11px] font-bold text-gray-400 dark:text-gray-500 uppercase">
          <Clock class="w-3.5 h-3.5" />
          <span>{{ formatDate(item.createdAt) }}</span>
        </div>

      </div>

    </div>

  </div>
</div>

<!-- EMPTY STATE -->
<div v-else class="mt-12">
  <div class="rounded-3xl p-16 text-center shadow-xl border
              bg-white border-gray-200
              dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
              dark:border-[#1f3b55]">

    <div class="w-24 h-24 mx-auto mb-8 rounded-3xl
                flex items-center justify-center
                bg-gray-100 text-yellow-500
                dark:bg-[#13293d]">
      <Bookmark class="w-10 h-10" />
    </div>

    <h2 class="text-3xl font-serif mb-4">
      No saved cases yet
    </h2>

    <p class="text-gray-600 dark:text-gray-400 max-w-md mx-auto mb-10 text-lg">
      Start exploring the legal database or use the AI assistant to find and bookmark important cases.
    </p>

    <div class="flex justify-center gap-4 flex-wrap">
      <router-link to="/cases">
        <button class="flex items-center gap-2 px-8 py-4 rounded-full font-bold
                       text-white bg-yellow-500 hover:bg-yellow-400">
          <Scale class="w-5 h-5" />
          Browse Cases
        </button>
      </router-link>

      <router-link to="/chat">
        <button class="px-8 py-4 rounded-full border border-gray-300 text-gray-700
                       font-bold hover:bg-gray-50
                       dark:border-[#1f3b55] dark:text-white dark:hover:bg-[#13293d]">
          Ask AI Assistant
        </button>
      </router-link>
    </div>

  </div>
</div>
```

  </div>
</template>


<script>
import { db, auth } from "../firebase";
import { 
  collection, 
  getDocs, 
  query, 
  orderBy,
  deleteDoc,
  doc 
} from "firebase/firestore";

import { Bookmark, Scale, Clock } from "lucide-vue-next";

export default {
  components: {
    Bookmark,
    Scale,
    Clock
  },

  data() {
    return {
      savedItems: [],
      loading: true,
      searchQuery: "" // 🔥 NEW (for search)
    };
  },

  // =========================
  // 🔐 AUTH + FETCH
  // =========================
  async created() {
    auth.onAuthStateChanged(async (user) => {
      if (user) {
        await this.fetchSavedItems(user.uid);
      } else {
        this.savedItems = [];
        this.loading = false;
      }
    });
  },

  computed: {
    // =========================
    // 🔍 SEARCH FILTER
    // =========================
    filteredItems() {
      if (!this.searchQuery) return this.savedItems;

      return this.savedItems.filter(item =>
        (item.caseTitle || "")
          .toLowerCase()
          .includes(this.searchQuery.toLowerCase())
      );
    }
  },

  methods: {

    // =========================
    // 📥 FETCH SAVED CASES
    // =========================
    async fetchSavedItems(userId) {
      try {
        const savedRef = collection(db, "users", userId, "saved");
        const q = query(savedRef, orderBy("createdAt", "desc"));

        const snapshot = await getDocs(q);

        this.savedItems = snapshot.docs.map(docSnap => {
          const data = docSnap.data();

          return {
            id: docSnap.id,

            // 🔥 SMART TITLE
            caseTitle:
              data.caseTitle ||
              data.question ||
              (data.cases?.[0]?.title) ||
              "Untitled Case",

            // 🔥 SUMMARY
            summary:
              data.summary ||
              data.answer ||
              "No summary available.",

            tool: data.tool || "",

            court: data.court || "",
            year: data.year || "",

            createdAt: data.createdAt || null,

            // 🔥 ADD LINK SUPPORT (IMPORTANT)
            link:
              data.link ||
              (data.cases?.[0]?.link) ||
              null,

            // future use
            cases: data.cases || []
          };
        });

      } catch (error) {
        console.error("Error fetching saved cases:", error);
      } finally {
        this.loading = false;
      }
    },

    // =========================
    // 🗑 DELETE CASE
    // =========================
    async deleteCase(itemId) {
      try {
        const user = auth.currentUser;
        if (!user) return;

        await deleteDoc(doc(db, "users", user.uid, "saved", itemId));

        // instant UI update
        this.savedItems = this.savedItems.filter(i => i.id !== itemId);

      } catch (err) {
        console.error("Delete failed:", err);
      }
    },

    // =========================
    // 📅 FORMAT DATE
    // =========================
    formatDate(timestamp) {
      if (!timestamp) return "Recently";

      try {
        const date = timestamp.toDate 
          ? timestamp.toDate() 
          : new Date(timestamp);

        return new Intl.DateTimeFormat('en-US', {
          month: 'short',
          day: 'numeric',
          year: 'numeric'
        }).format(date);

      } catch {
        return "Recently";
      }
    }
  }
};
</script>
<style scoped>
/* Scoped styles can be added here if needed */
</style>