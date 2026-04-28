<script>
import { db, auth } from "../firebase";
import { collection, addDoc } from "firebase/firestore";

import {
  Search,
  Sparkles,
  Scale,
  FileText,
  GitCompare,
  List,
  PenLine,
  Copy,
  ChevronDown,
  Bookmark,
  ExternalLink
} from "lucide-vue-next";

// =========================
// 💾 SAVE CHAT HISTORY
// =========================
async function saveChat(question, answer) {
  try {
    const user = auth.currentUser;
    if (!user) return;

    await addDoc(
      collection(db, "users", user.uid, "history"),
      {
        question,
        answer,
        createdAt: new Date()
      }
    );
  } catch (error) {
    console.error("Error saving chat history:", error);
  }
}

export default {
  components: {
    Search,
    Sparkles,
    Scale,
    FileText,
    GitCompare,
    List,
    PenLine,
    Copy,
    ChevronDown,
    Bookmark,
    ExternalLink
  },

  data() {
    return {
      query: "",
      response: null,
      loading: false,

      courtOpen: false,
      yearOpen: false,

      selectedCourt: "All courts",
      selectedYear: "All years",

      file: null
    };
  },

  mounted() {
    this.response = null;
    this.query = "";
  },

  computed: {
    isFetchCases() {
      return this.response?.tool?.toLowerCase().includes("fetch");
    },

    parsedCases() {
      const text = this.response?.answer;
      if (!text) return [];

      return text.split("Case:")
        .filter(s => s.trim())
        .map(part => {
          const lines = part.trim().split("\n").filter(l => l.trim());

          const title = lines[0] || "Untitled Case";

          const linkLine = lines.find(l =>
            l.toLowerCase().startsWith("link:")
          );

          const sourceLine = lines.find(l =>
            l.toLowerCase().startsWith("source:")
          );

          return {
            title,
            link: linkLine ? linkLine.replace("Link:", "").trim() : null,
            source: sourceLine ? sourceLine.replace("Source:", "").trim() : ""
          };
        })
        .filter(c => c.link);
    },

    parsedSummary() {
      if (!this.response?.answer) return null;

      const text = this.response.answer;

      const sections = {
        facts: "",
        issue: "",
        judgment: "",
        reasoning: ""
      };

      let current = null;

      text.split("\n").forEach(line => {
        // Remove markdown bolding and trim to check if line is a header
        const cleanLine = line.trim().toLowerCase().replace(/[*#]/g, '');

        if (cleanLine.startsWith("facts:") || cleanLine === "facts") current = "facts";
        else if (cleanLine.startsWith("issue:") || cleanLine === "issue") current = "issue";
        else if (cleanLine.startsWith("judgment:") || cleanLine === "judgment") current = "judgment";
        else if (cleanLine.startsWith("reasoning:") || cleanLine === "reasoning") current = "reasoning";
        else if (current && line.trim()) {
          sections[current] += line + "\n";
        }
      });

      // clean text and filter empty sections
      const result = {};
      Object.keys(sections).forEach(key => {
        const cleaned = this.cleanText(sections[key]);
        if (cleaned) {
          result[key] = cleaned;
        }
      });

      return Object.keys(result).length > 0 ? result : null;
    }
  },

  methods: {

    cleanText(text) {
      if (!text) return "";

      return text
        .replace(/\*\*/g, "")
        .replace(/\n\s*\n/g, "\n")
        .trim();
    },

    triggerFile() {
      this.$refs.fileInput.click();
    },

    handleFileUpload(e) {
      const selected = e.target.files[0];
      if (!selected) return;

      this.file = selected;
      this.uploadFile();
    },

    removeFile() {
      this.file = null;
    },

    // =========================
    // 📂 UPLOAD FILE (UNCHANGED)
    // =========================
    async uploadFile() {
      if (!this.file) return;

      const user = auth.currentUser;
      const uid = user?.uid || "guest";

      this.loading = true;
      this.response = null;

      const formData = new FormData();
      formData.append("file", this.file);

      try {
        const res = await fetch("http://127.0.0.1:8000/upload", {
          method: "POST",
          headers: {
            "user-id": uid
          },
          body: formData
        });

        const data = await res.json();

        if (data.error) {
          this.response = {
            tool: "Error",
            answer: data.error
          };
          return;
        }

        this.response = {
          tool: "Upload",
          answer: data.message
        };

      } catch (err) {
        console.error(err);
        this.response = {
          tool: "Error",
          answer: "⚠️ Upload failed"
        };
      } finally {
        this.loading = false;
      }
    },

    // =========================
    // 🔍 ASK API (FIXED)
    // =========================
    async ask() {
      if (!this.query) return;

      const user = auth.currentUser;

      if (!user) {
        alert("⚠️ Please login first");
        return;
      }

      this.loading = true;
      this.response = null;

      try {
        const res = await fetch("http://127.0.0.1:8000/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            question: this.query,
            user_id: user.uid,
            filters: {
              court: this.selectedCourt,
              year: this.selectedYear
            }
          })
        });

        // ✅ HANDLE HTTP ERRORS
        if (!res.ok) {
          throw new Error("Server error");
        }

        const data = await res.json();

        console.log("API RESPONSE:", data); // 🔥 DEBUG

        // ✅ SAFE CHECK (VERY IMPORTANT)
        if (!data || !data.answer) {
          this.response = {
            tool: "Error",
            answer: "⚠️ Invalid response from backend"
          };
          return;
        }

        this.response = data;
        // 🔥 DEBUG (ADD THIS)
        console.log("PARSED:", this.parsedSummary);

        await saveChat(this.query, data.answer || "");

      } catch (error) {
        console.error(error);
        this.response = {
          tool: "Error",
          answer: "⚠️ Backend not responding."
        };
      } finally {
        this.loading = false;
      }
    },

    selectCourt(val) {
      this.selectedCourt = val;
      this.courtOpen = false;
    },

    selectYear(val) {
      this.selectedYear = val;
      this.yearOpen = false;
    },

    suggestQuery(q) {
      this.query = q;
    },

    async saveResponse() {
      try {
        const user = auth.currentUser;

        if (!user) {
          alert("Please login");
          return;
        }

        await addDoc(collection(db, "users", user.uid, "saved"), {
          caseTitle: this.parsedCases?.[0]?.title || "Document",
          summary: this.response?.answer || "",
          court: this.selectedCourt,
          year: this.selectedYear,
          createdAt: new Date()
        });

        alert("✅ Saved successfully");

      } catch (err) {
        console.error(err);
      }
    }
  }
};
</script>

<template>
  <div class="min-h-screen transition-all duration-500
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white">

    <!-- HERO -->
    <div class="text-center pt-16 pb-10">
      <div class="badge">
        <Sparkles class="w-4 h-4 text-accent" />
        <span>
          <span class="text-accent font-medium">New</span> · retrieval-augmented legal reasoning
        </span>
      </div>

      <h1 class="hero-title">
        <Scale class="hero-icon" />
        Legal <span class="gold-text">AI</span> Assistant
      </h1>

      <p class="text-gray-600 dark:text-gray-400 mt-4 text-lg">
        Analyze, compare, and explore legal cases with citation-grade precision.
      </p>
    </div>

    <!-- MAIN -->
    <div class="w-full px-6 md:px-16 lg:px-32 xl:px-48">
      <div class="card-container">

        <!-- 🔥 SEARCH BAR WITH + BUTTON -->
        <div class="search-bar">

          <!-- ➕ BUTTON -->
          <button @click="triggerFile"
                  class="text-xl mr-2 text-gray-500 hover:text-black dark:hover:text-white">
            +
          </button>

          <!-- INPUT -->
          <input
            v-model="query"
            placeholder="Ask a legal question..."
            class="search-input"
            @keyup.enter="ask"
          />

          <!-- ASK BUTTON -->
          <button @click="ask" class="ask-btn">
            <Sparkles class="w-4 h-4" />
            Ask AI
          </button>

          <!-- HIDDEN FILE INPUT -->
          <input
            type="file"
            ref="fileInput"
            hidden
            @change="handleFileUpload"
          />
        </div>

        <!-- 🔥 FILE PREVIEW -->
        <div v-if="file"
             class="mt-4 flex items-center justify-between p-3 rounded-xl
                    bg-gray-200 dark:bg-[#13293d]">

          <div class="flex items-center gap-3">
            <div class="w-10 h-10 flex items-center justify-center rounded-lg bg-red-500 text-white">
              📄
            </div>

            <div class="text-sm">
              <p class="font-medium truncate max-w-[200px]">
                {{ file.name }}
              </p>
              <p class="text-xs text-gray-500">PDF</p>
            </div>
          </div>

          <button @click="removeFile"
                  class="text-gray-500 hover:text-red-500">
            ✕
          </button>
        </div>

        <!-- LOADING -->
        <div v-if="loading" class="text-center mt-6 text-yellow-500">
          ⏳ Thinking...
        </div>

        <!-- SUGGESTIONS -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <div @click="suggestQuery('summarize case')" class="action-card">
            <FileText class="action-icon" />
            <p class="title">Summarize Case</p>
            <p class="desc">Condense a judgment</p>
          </div>

          <div @click="suggestQuery('compare cases')" class="action-card">
            <GitCompare class="action-icon" />
            <p class="title">Compare Cases</p>
            <p class="desc">Contrast rulings</p>
          </div>

          <div @click="suggestQuery('list cases')" class="action-card">
            <List class="action-icon" />
            <p class="title">List Cases</p>
            <p class="desc">Find authorities</p>
          </div>

          <div @click="suggestQuery('generate draft')" class="action-card">
            <PenLine class="action-icon" />
            <p class="title">Generate Draft</p>
            <p class="desc">Memo or pleading</p>
          </div>
        </div>

        <!-- FILTERS -->
        <div class="grid md:grid-cols-2 gap-6 mt-6">

          <!-- COURT -->
          <div class="relative">
            <label class="label">COURT</label>

            <div @click="courtOpen = !courtOpen" class="custom-select">
              {{ selectedCourt }}
              <ChevronDown class="arrow" />
            </div>

            <div v-if="courtOpen" class="dropdown">
              <div @click="selectCourt('All courts')" class="option">All courts</div>
              <div @click="selectCourt('Supreme Court')" class="option">Supreme Court</div>
              <div @click="selectCourt('High Court')" class="option">High Court</div>
            </div>
          </div>

          <!-- YEAR -->
          <div class="relative">
            <label class="label">YEAR</label>

            <div @click="yearOpen = !yearOpen" class="custom-select">
              {{ selectedYear }}
              <ChevronDown class="arrow" />
            </div>

            <div v-if="yearOpen" class="dropdown">
              <div @click="selectYear('All years')" class="option">All years</div>
              <div @click="selectYear('2024')" class="option">2024</div>
              <div @click="selectYear('2023')" class="option">2023</div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- RESULTS -->
<div v-if="response"
     class="w-full px-6 md:px-16 lg:px-32 xl:px-48 mt-10">

  <div class="result-card">

    <!-- HEADER -->
    <div class="flex justify-between mb-4">
      <span class="tool-pill">
        ● TOOL · {{ response.tool.toUpperCase() }}
      </span>

      <div class="flex gap-2">
        <button class="copy-btn">
          <Copy class="w-4 h-4" />
          Copy
        </button>

        <button @click="saveResponse" class="save-btn">
          <Bookmark class="w-4 h-4" />
          Save Case
        </button>
      </div>
    </div>

    <h2 class="text-yellow-500 mb-3">{{ response.tool }}</h2>

    <!-- 🔥 SUMMARY -->
    <div v-if="parsedSummary && (
                response.tool.toLowerCase().includes('summarize') ||
                response.tool === 'Document Summary'
              )"
         class="space-y-5 mb-6">

      <div v-for="(val, key) in parsedSummary"
          :key="key"
          class="flex gap-3 items-start">

        <FileText class="w-5 h-5 text-yellow-400 mt-1" />

        <div>
          <h4 class="font-semibold capitalize">{{ key }}</h4>

          <!-- ✅ ONLY CHANGE HERE -->
          <p class="text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
            {{ val }}
          </p>

        </div>

      </div>
    </div>

    <!-- 🔥 FETCH CASES -->
    <div v-else-if="isFetchCases && parsedCases.length > 0"
         class="grid gap-3">

      <div v-for="(c, i) in parsedCases"
           :key="i"
           class="p-4 rounded-xl border hover:border-yellow-500
                  bg-gray-50 border-gray-200
                  dark:bg-[#13293d]/50 dark:border-[#1f3b55]">

        <h4 class="font-bold mb-2">
          {{ c.title }}
        </h4>

        <a :href="c.link" target="_blank"
           class="text-yellow-500 text-sm hover:underline">
          View Full Case
        </a>

      </div>
    </div>

    <!-- 🔥 FALLBACK -->
    <div v-else class="text-gray-600 dark:text-gray-300 whitespace-pre-wrap">
      {{ response.answer }}
    </div>

  </div>
</div>

  </div>
</template>
<style scoped>
.badge { @apply inline-flex items-center gap-2 px-5 py-2 text-sm bg-gray-200 border border-gray-300 text-gray-700 dark:bg-[#0f2437]/80 dark:border-[#1f3b55] dark:text-gray-300 rounded-full mx-auto; }
.hero-title { @apply font-serif text-6xl md:text-7xl font-semibold mt-4; }
.hero-icon { @apply inline w-10 h-10 text-yellow-500 mr-2; }
.card-container { @apply w-full p-6 rounded-3xl shadow-xl bg-white border border-gray-200 dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521] dark:border-[#1f3b55]; }
.search-bar { @apply flex items-center rounded-full px-4 py-3 bg-gray-200 dark:bg-[#13293d]; }
.search-input { @apply flex-1 bg-transparent outline-none ml-2 text-gray-700 dark:text-gray-300; }
.ask-btn { @apply flex items-center gap-2 bg-yellow-500 text-black px-5 py-2 rounded-full; }
.action-card { @apply p-4 rounded-xl text-center cursor-pointer bg-white border border-gray-200 hover:bg-gray-100 dark:bg-[#0f2437] dark:border-[#1f3b55] dark:hover:bg-[#17324a]; }
.action-icon { @apply w-6 h-6 text-yellow-500 mx-auto mb-2; }
.custom-select { @apply w-full p-3 rounded-xl border flex justify-between cursor-pointer bg-gray-200 text-gray-700 border-gray-300 dark:bg-[#13293d] dark:text-white dark:border-[#1f3b55]; }
.dropdown { @apply absolute w-full mt-2 rounded-xl shadow-lg overflow-hidden z-50 bg-white border border-gray-200 dark:bg-[#0f2437] dark:border-[#1f3b55]; }
.option { @apply px-4 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-[#17324a]; }
.result-card { @apply p-6 rounded-2xl border bg-white border-gray-200 dark:bg-[#0d2235] dark:border-[#1f3b55]; }
.save-btn { @apply flex items-center gap-2 bg-yellow-500 text-black px-3 py-1 rounded-lg text-sm font-medium hover:bg-yellow-400 transition-colors; }
.desc { @apply text-gray-500 dark:text-gray-400 text-sm; }
</style>