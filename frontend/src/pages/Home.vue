<script setup>
import { Zap, GitCompare, BookOpen } from "lucide-vue-next";
</script>

<template>
  <div class="min-h-screen transition-all duration-500
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white">

    <!-- ================= HERO SECTION ================= -->
    <section class="flex flex-col justify-center items-center text-center px-6 py-20">

      <!-- Badge -->
      <div class="mb-10">
        <div class="flex items-center gap-2 px-6 py-2 rounded-full 
                    bg-gray-200 border border-gray-300 text-sm text-gray-700
                    dark:bg-[#0f2a3f] dark:border-gray-700 dark:text-gray-300
                    shadow-md backdrop-blur-md">

          <span class="text-yellow-500">✨</span>

          <span>
            <span class="text-yellow-500 font-semibold">New</span>
            · retrieval-augmented legal reasoning
          </span>

        </div>
      </div>

      <!-- Title -->
      <h1 class="text-5xl md:text-7xl font-serif leading-tight tracking-wide
                 text-gray-900 dark:text-yellow-400">

        ⚖️ Legal AI Assistant

      </h1>

      <!-- Description -->
      <p class="mt-8 text-gray-600 dark:text-gray-400 text-lg md:text-xl max-w-3xl leading-relaxed">

        A premium AI workspace for lawyers and researchers. Summarize judgments,
        compare precedent, and retrieve real-time cases — all in one elegant interface.

      </p>

      <!-- Buttons -->
      <div class="mt-12 flex flex-wrap justify-center gap-6">

        <router-link to="/chat">
          <button class="bg-yellow-500 text-black px-10 py-4 rounded-full text-lg 
                         hover:scale-105 transition-all duration-300 
                         shadow-lg hover:shadow-yellow-500/40">

            Start Analysis →

          </button>
        </router-link>

        <router-link to="/cases">
          <button class="border px-10 py-4 rounded-full text-lg 
                         border-gray-400 text-gray-700
                         hover:bg-gray-200
                         dark:border-gray-500 dark:text-white dark:hover:bg-gray-800
                         transition-all duration-300">

            Browse Cases

          </button>
        </router-link>

      </div>

    </section>

    <!-- ================= FEATURE CARDS ================= -->
    <section class="pb-20">

      <div class="w-full px-[7%]">

        <div class="grid grid-cols-1 md:grid-cols-3 gap-10">

          <!-- Card 1 -->
          <div class="card">
            <div class="icon-box">
              <Zap class="icon" size="24" />
            </div>

            <h2 class="card-title">Instant Summaries</h2>

            <p class="card-desc">
              Compress lengthy judgments into structured insights.
            </p>
          </div>

          <!-- Card 2 -->
          <div class="card">
            <div class="icon-box">
              <GitCompare class="icon" size="24" />
            </div>

            <h2 class="card-title">Compare Precedent</h2>

            <p class="card-desc">
              Spot doctrinal shifts across leading rulings.
            </p>
          </div>

          <!-- Card 3 -->
          <div class="card">
            <div class="icon-box">
              <BookOpen class="icon" size="24" />
            </div>

            <h2 class="card-title">Cite with Confidence</h2>

            <p class="card-desc">
              Every answer is grounded in real, retrievable cases.
            </p>
          </div>

        </div>

      </div>

    </section>

  </div>
</template>

<style scoped>

/* CARD */
.card {
  @apply bg-white dark:bg-[#112233]
         p-10 rounded-2xl shadow-lg
         border border-gray-200 dark:border-[#1f3b55]
         hover:scale-105 hover:shadow-xl
         transition-all duration-300;
}

/* ICON BOX */
.icon-box {
  @apply bg-gray-200 dark:bg-[#1e3a5f]
         w-14 h-14 flex items-center justify-center
         rounded-full mb-5 shadow-inner;
}

/* ICON */
.icon {
  @apply text-yellow-500;
}

/* TITLE */
.card-title {
  @apply text-2xl font-serif
         text-gray-900 dark:text-yellow-400;
}

/* DESCRIPTION */
.card-desc {
  @apply text-gray-600 dark:text-gray-400 mt-3 leading-relaxed;
}

</style>