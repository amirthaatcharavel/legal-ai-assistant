<template>
  <div class="min-h-screen font-sans px-6 md:px-16 lg:px-32 xl:px-48 py-16
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white transition-all duration-500">

    <!-- HERO -->
    <div class="text-center max-w-3xl mx-auto">
      <h1 class="text-5xl md:text-6xl font-serif">
        About the <span class="text-yellow-500">Project</span>
      </h1>

      <p class="text-gray-600 dark:text-gray-400 mt-6 text-lg leading-relaxed">
        Legal AI Assistant is a research-grade workspace built for lawyers, clerks, and academics.
        It combines retrieval-augmented reasoning with a tool-selection layer to deliver answers
        you can actually cite.
      </p>
    </div>

    <!-- FEATURE CARDS -->
    <div class="grid md:grid-cols-2 gap-6 mt-16">

      <!-- CARD 1 -->
      <div class="feature-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="icon-circle">
            <BookOpen />
          </div>
          <span class="badge">RAG</span>
        </div>

        <h2 class="card-title">Document Analysis</h2>
        <p class="card-desc">
          Retrieval-augmented generation grounds every answer in real legal text.
          The model is given the most relevant passages so responses cite, not invent.
        </p>
      </div>

      <!-- CARD 2 -->
      <div class="feature-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="icon-circle">
            <Layers />
          </div>
          <span class="badge">MCP</span>
        </div>

        <h2 class="card-title">Tool Selection</h2>
        <p class="card-desc">
          A model-context protocol layer routes each query to the right tool —
          summarize, compare, list, or draft — so you get the format you actually need.
        </p>
      </div>

      <!-- CARD 3 -->
      <div class="feature-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="icon-circle">
            <Radar />
          </div>
          <span class="badge">LIVE</span>
        </div>

        <h2 class="card-title">Real-time Case Retrieval</h2>
        <p class="card-desc">
          Streaming retrieval against an indexed corpus surfaces leading judgments
          with citation, court, year and a structured summary card.
        </p>
      </div>

      <!-- CARD 4 -->
      <div class="feature-card">
        <div class="flex items-center gap-3 mb-4">
          <div class="icon-circle">
            <ShieldCheck />
          </div>
          <span class="badge">TRUST</span>
        </div>

        <h2 class="card-title">Citation-grade Output</h2>
        <p class="card-desc">
          Every paragraph is paired with the cases it relies on, so you can verify,
          copy, and use the answer in your own research workflow.
        </p>
      </div>

    </div>

    <!-- CTA SECTION -->
    <div class="cta-card mt-16 text-center">

      <h2 class="text-3xl font-serif mb-3">
        Ready to query the corpus?
      </h2>

      <p class="text-gray-600 dark:text-gray-400 mb-6">
        Open the chat workspace and ask your first question — or browse the case library.
      </p>

      <div class="flex justify-center gap-4">

        <router-link to="/chat">
          <button class="btn-primary flex items-center gap-2">
            Open Chat
            <ArrowRight class="w-4 h-4" />
          </button>
        </router-link>

        <router-link to="/cases">
          <button class="btn-secondary">
            Browse Cases
          </button>
        </router-link>

      </div>

    </div>

  </div>
</template>

<script>
import {
  BookOpen,
  Layers,
  Radar,
  ShieldCheck,
  ArrowRight
} from "lucide-vue-next";

export default {
  components: {
    BookOpen,
    Layers,
    Radar,
    ShieldCheck,
    ArrowRight
  }
};
</script>

<style scoped>

/* FEATURE CARD */
.feature-card {
  @apply p-6 rounded-2xl border transition duration-300
         bg-white border-gray-200 hover:border-yellow-500
         dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
         dark:border-[#1f3b55] dark:hover:border-yellow-400;
}

/* ICON */
.icon-circle {
  @apply w-10 h-10 flex items-center justify-center rounded-full
         bg-gray-200 text-yellow-500
         dark:bg-[#13293d] dark:text-yellow-400;
}

/* BADGE */
.badge {
  @apply text-xs px-3 py-1 rounded-full border
         bg-yellow-100 text-yellow-600 border-yellow-300
         dark:bg-yellow-400/10 dark:text-yellow-300 dark:border-yellow-400/30;
}

/* TITLE */
.card-title {
  @apply font-serif text-2xl mb-2
         text-gray-900 dark:text-white;
}

/* DESC */
.card-desc {
  @apply text-gray-600 dark:text-gray-400 text-sm leading-relaxed;
}

/* CTA CARD */
.cta-card {
  @apply p-10 rounded-3xl border
         bg-white border-gray-200
         dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
         dark:border-[#1f3b55];
}

/* BUTTONS */
.btn-primary {
  @apply bg-yellow-500 text-black px-6 py-3 rounded-full font-medium
         hover:opacity-90 transition;
}

.btn-secondary {
  @apply px-6 py-3 rounded-full border transition
         border-gray-300 text-gray-700 hover:bg-gray-100
         dark:border-[#1f3b55] dark:text-white dark:hover:bg-[#13293d];
}

</style>