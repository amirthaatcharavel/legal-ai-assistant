<template>
  <div class="min-h-screen font-sans px-6 md:px-16 lg:px-32 xl:px-48 py-10
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white transition-all duration-500">

    <!-- HERO -->
    <div class="text-center mb-10">
      <h1 class="text-5xl font-serif">
        Cases <span class="text-yellow-500">Explorer</span>
      </h1>
      <p class="text-gray-600 dark:text-gray-400 mt-3">
        Browse and filter landmark judgments. Click any card to open the full text.
      </p>
    </div>

    <!-- SEARCH + FILTER -->
    <div class="card-container">

      <!-- 🔥 SEARCH BAR WITH BUTTON -->
      <div class="search-bar mb-6">

        <Search class="icon-gray" />

        <input
          v-model="query"
          @keyup.enter="handleSearch"
          placeholder="Search by case name or citation..."
          class="search-input"
        />

        <!-- 🔍 SEARCH BUTTON -->
        <button
          @click="handleSearch"
          class="ml-3 px-5 py-2 rounded-full
                 bg-yellow-500 text-black text-sm font-medium
                 hover:bg-yellow-400 transition-all"
        >
          Search
        </button>

      </div>

      <!-- FILTERS -->
      <div class="grid md:grid-cols-2 gap-6">

        <!-- COURT -->
        <div class="relative">
          <label class="label">COURT</label>

          <div @click="courtOpen = !courtOpen" class="custom-select">
            {{ court }}
            <ChevronDown class="arrow" />
          </div>

          <div v-if="courtOpen" class="dropdown">
            <div
              v-for="c in courtsList"
              :key="c"
              @click="selectCourt(c)"
              class="option"
            >
              {{ c }}
            </div>
          </div>
        </div>

        <!-- YEAR -->
        <div class="relative">
          <label class="label">YEAR</label>

          <div @click="yearOpen = !yearOpen" class="custom-select">
            {{ year }}
            <ChevronDown class="arrow" />
          </div>

          <div v-if="yearOpen" class="dropdown">
            <div
              v-for="y in yearsList"
              :key="y"
              @click="selectYear(y)"
              class="option"
            >
              {{ y }}
            </div>
          </div>
        </div>

      </div>

      <!-- COUNT -->
      <p class="text-gray-600 dark:text-gray-400 mt-4">
        {{ cases.length }} cases found
      </p>
    </div>

    <!-- LOADING -->
    <div v-if="loading" class="text-center mt-10 text-yellow-500">
      ⏳ Fetching cases...
    </div>

    <!-- CASES GRID -->
    <div v-if="!loading && cases.length > 0"
         class="grid md:grid-cols-2 gap-6 mt-10">

      <div
        v-for="(c, i) in cases"
        :key="i"
        class="case-card"
      >

        <!-- HEADER -->
        <div class="flex justify-between items-start">

          <div>
            <h3 class="title">
              {{ c.title }}
            </h3>

            <p v-if="c.citation" class="citation">
            {{ c.citation }}
            </p>
          </div>

          <!-- 🔥 VIEW + SAVE -->
          <div class="flex gap-3 items-center">

            <!-- VIEW -->
            <a :href="c.link" target="_blank">
              <ExternalLink class="w-4 h-4 text-gray-500 dark:text-gray-400 hover:text-black dark:hover:text-white" />
            </a>

            <!-- ✅ SAFE SAVE BUTTON -->
            <button
  @click="saveCase(c)"
  :disabled="savedLinks && savedLinks.includes(c.link)"
  class="flex items-center justify-center gap-2 px-4 py-2 rounded-lg
         text-sm font-medium transition-all whitespace-nowrap min-w-[120px]"
  :class="savedLinks && savedLinks.includes(c.link)
    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
    : 'bg-yellow-500 text-black hover:bg-yellow-400'"
>
  <Bookmark class="w-4 h-4" />
  {{ savedLinks && savedLinks.includes(c.link) ? "Saved" : "Save Case" }}
</button>

          </div>

        </div>

        <!-- TAGS -->
        <div class="flex gap-2 mt-2">
          <span class="tag">{{ c.court || "Court" }}</span>
          <span class="tag">{{ c.year || "Year" }}</span>
        </div>

        <!-- DESCRIPTION -->
        <p class="desc mt-3">
          Landmark judgment related to "{{ query }}"...
        </p>

      </div>

    </div>

    <!-- EMPTY -->
    <div v-if="!loading && cases.length === 0"
         class="text-center mt-16 text-gray-500">
      No cases found. Try a different query.
    </div>

    <!-- PAGINATION -->
    <div class="flex justify-center items-center gap-3 mt-12">

      <button class="page-btn" @click="prevPage">
        ‹ Previous
      </button>

      <button class="page-number active">
        {{ page + 1 }}
      </button>

      <button class="page-btn" @click="nextPage">
        Next ›
      </button>

    </div>

  </div>
</template>

<script>
import {
  Search,
  ChevronDown,
  Bookmark,
  ExternalLink
} from "lucide-vue-next";

// 🔥 FIREBASE
import { db, auth } from "../firebase";

import { 
  collection, 
  addDoc, 
  getDocs, 
  query, 
  where 
} from "firebase/firestore";

export default {
  components: {
    Search,
    ChevronDown,
    Bookmark,
    ExternalLink
  },

  data() {
    return {
      query: "",
      cases: [],
      page: 0,

      court: "All courts",
      year: "All years",

      courtsList: [
        "All courts",
        "Supreme Court of India",
        "Kerala High Court",
        "Madras High Court",
        "Andhra HC (Pre-Telangana)",
        "Allahabad High Court",
        "Bombay High Court",
        "Gujarat High Court",
        "Karnataka High Court",
        "Madhya Pradesh High Court",
        "Rajasthan High Court - Jaipur"
      ],

      yearsList: [
        "All years",
        "2025","2024","2023","2022","2021","2020",
        "2019","2018","2017","2016","2015",
        "2012","2011","2010","2006","2004",
        "2003","2002","2001","2000","1999"
      ],

      courtOpen: false,
      yearOpen: false,

      loading: false,

      // ✅ FIX: REQUIRED FOR SAVE BUTTON
      savedLinks: []
    };
  },

  methods: {

    // 🔍 SEARCH
    handleSearch() {
      if (!this.query) return;
      this.page = 0;
      this.fetchCases();
    },

    // 🎯 FILTERS
    selectCourt(val) {
      this.court = val;
      this.courtOpen = false;
      this.page = 0;
      this.fetchCases();
    },

    selectYear(val) {
      this.year = val;
      this.yearOpen = false;
      this.page = 0;
      this.fetchCases();
    },

    // 🔥 FETCH CASES (FIXED MULTIPLE CALL ISSUE)
    async fetchCases() {
      if (!this.query || this.loading) return; // ✅ prevent spam calls

      this.loading = true;

      try {
        const res = await fetch("http://127.0.0.1:8000/fetch_cases", {
          method: "POST",
          headers: { "Content-Type": "application/json" },

          body: JSON.stringify({
            query: this.query,
            page: this.page,
            court: this.court,
            year: this.year
          })
        });

        const data = await res.json();
        this.cases = Array.isArray(data.cases) ? data.cases : [];

      } catch (err) {
        console.error("Fetch failed:", err);
        this.cases = [];
      } finally {
        this.loading = false;
      }
    },

    // 💾 SAVE CASE (WITH DUPLICATE + UI UPDATE)
    async saveCase(c) {
      try {
        const user = auth.currentUser;

        if (!user) {
          alert("⚠️ Please login first");
          return;
        }

        const savedRef = collection(db, "users", user.uid, "saved");

        // 🔥 FIRESTORE DUPLICATE CHECK
        const q = query(savedRef, where("link", "==", c.link));
        const snapshot = await getDocs(q);

        if (!snapshot.empty) {
          alert("⚠️ Case already saved!");
          return;
        }

        await addDoc(savedRef, {
          caseTitle: c.title,
          summary: c.citation || "",
          court: c.court || this.court,
          year: c.year || this.year,
          link: c.link || "",
          createdAt: new Date()
        });

        // ✅ UPDATE UI STATE
        this.savedLinks.push(c.link);

        alert("✅ Case saved!");

      } catch (err) {
        console.error("Save failed:", err);
      }
    },

    // ▶️ PAGINATION
    nextPage() {
      this.page++;
      this.fetchCases();
    },

    prevPage() {
      if (this.page > 0) {
        this.page--;
        this.fetchCases();
      }
    },

    // 🔥 LOAD SAVED LINKS (PERSIST UI STATE)
    async loadSavedLinks() {
      try {
        const user = auth.currentUser;
        if (!user) return;

        const savedRef = collection(db, "users", user.uid, "saved");
        const snapshot = await getDocs(savedRef);

        this.savedLinks = snapshot.docs.map(doc => doc.data().link);

      } catch (err) {
        console.error("Load saved failed:", err);
      }
    }
  },

  // 🚀 INITIAL LOAD
  async mounted() {
    this.query = "constitutional law";

    await this.loadSavedLinks(); // 🔥 IMPORTANT
    this.fetchCases();
  }
};
</script>
<style scoped>

/* CARD */
.card-container {
  @apply p-6 rounded-3xl shadow-xl
         bg-white border border-gray-200
         dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
         dark:border-[#1f3b55];
}

/* SEARCH */
.search-bar {
  @apply flex items-center rounded-full px-4 py-3
         bg-gray-200 dark:bg-[#13293d];
}

.search-input {
  @apply flex-1 bg-transparent outline-none ml-2
         text-gray-700 dark:text-gray-300;
}

.icon-gray {
  @apply w-5 h-5 text-gray-500 dark:text-gray-400;
}

/* DROPDOWN */
.custom-select {
  @apply w-full p-3 rounded-xl border flex justify-between cursor-pointer
         bg-gray-200 text-gray-700 border-gray-300
         dark:bg-[#13293d] dark:text-white dark:border-[#1f3b55];
}

.dropdown {
  @apply absolute w-full mt-2 rounded-xl shadow-lg overflow-hidden z-50
         bg-white border border-gray-200
         dark:bg-[#0f2437] dark:border-[#1f3b55];
}

.option {
  @apply px-4 py-2 cursor-pointer
         hover:bg-gray-100 dark:hover:bg-[#17324a];
}

.arrow {
  @apply w-4 h-4 text-gray-500 dark:text-gray-400;
}

/* CASE CARD */
.case-card {
  @apply p-6 rounded-2xl border transition
         bg-white border-gray-200 hover:border-yellow-500
         dark:bg-[#0d2235] dark:border-[#1f3b55] dark:hover:border-yellow-400;
}

.title {
  @apply font-serif text-lg;
}

/* CITATION */
.citation {
  @apply text-gray-500 dark:text-gray-400 text-sm mt-1;
}

.tag {
  @apply text-xs px-2 py-1 rounded
         bg-gray-200 text-gray-700
         dark:bg-[#13293d] dark:text-white;
}

.desc {
  @apply text-gray-600 dark:text-gray-400 text-sm;
}

/* PAGINATION */
.page-btn {
  @apply px-4 py-2 rounded-full
         bg-gray-200 hover:bg-gray-300
         dark:bg-[#13293d] dark:hover:bg-[#1c3a55];
}

.page-number {
  @apply w-8 h-8 flex items-center justify-center rounded-full
         bg-gray-200
         dark:bg-[#13293d];
}

.page-number.active {
  @apply bg-yellow-500 text-black;
}

</style>