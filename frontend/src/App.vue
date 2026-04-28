<script>
import { Scale, Moon, Sun } from "lucide-vue-next";
import { auth } from "./firebase";
import { onAuthStateChanged, signOut } from "firebase/auth";

export default {
  components: { Scale, Moon, Sun },

  data() {
    return {
      isDark: false,
      user: null,
      showMenu: false
    };
  },

  methods: {
    toggleTheme() {
      this.isDark = !this.isDark;

      if (this.isDark) {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      } else {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      }
    },

    async logout() {
      await signOut(auth);
      this.showMenu = false;
      this.$router.push("/login");
    }
  },

  mounted() {
    // 🔥 THEME
    const saved = localStorage.getItem("theme");

    if (saved === "dark") {
      this.isDark = true;
      document.documentElement.classList.add("dark");
    }

    // 🔥 AUTH LISTENER
    onAuthStateChanged(auth, (currentUser) => {
      this.user = currentUser;
    });
  }
};
</script>

<template>
  <div class="min-h-screen transition-all duration-500
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white">

    <!-- NAVBAR -->
    <nav class="sticky top-0 z-50 flex justify-between items-center px-10 py-4
                border-b transition-all duration-300
                bg-[#f5f2eb] border-gray-200
                dark:bg-gradient-to-r dark:from-[#0b1b2b] dark:to-[#0d2235] dark:border-[#1f3b55]">

      <!-- LOGO -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center
                    bg-gray-200 dark:bg-[#13293d]">
          <Scale class="w-5 h-5 text-yellow-500" />
        </div>

        <h1 class="font-serif text-lg">
          Legal <span class="text-yellow-500">AI</span>
        </h1>
      </div>

      <!-- CENTER MENU -->
      <div class="flex gap-2 px-2 py-1 rounded-full border
                  bg-white border-gray-300
                  dark:bg-[#0f2a3f] dark:border-[#1f3b55]">

        <router-link to="/" class="nav-pill" active-class="active">Home</router-link>
        <router-link to="/chat" class="nav-pill" active-class="active">Chat</router-link>
        <router-link to="/cases" class="nav-pill" active-class="active">Cases</router-link>
        <router-link to="/history" class="nav-pill" active-class="active">History</router-link>
        <router-link to="/saved" class="nav-pill" active-class="active">Saved</router-link>
        <router-link to="/about" class="nav-pill" active-class="active">About</router-link>
        <router-link to="/settings" class="nav-pill" active-class="active">Settings</router-link>

      </div>

      <!-- RIGHT SIDE -->
      <div class="flex items-center gap-4">

        <!-- THEME BUTTON -->
        <button
          @click="toggleTheme"
          class="w-10 h-10 rounded-full border flex items-center justify-center transition
                 bg-white border-gray-300 hover:bg-gray-100
                 dark:bg-[#0f2a3f] dark:border-[#1f3b55] dark:hover:bg-[#13293d]">

          <Sun v-if="!isDark" class="w-5 h-5 text-yellow-500" />
          <Moon v-else class="w-5 h-5 text-yellow-400" />

        </button>

        <!-- 🔥 NOT LOGGED IN -->
        <router-link
          v-if="!user"
          to="/login"
          class="px-5 py-2 rounded-full text-white font-medium
                 bg-gradient-to-r from-yellow-400 to-orange-500
                 hover:opacity-90 transition shadow-md"
        >
          Sign in
        </router-link>

        <!-- 🔥 LOGGED IN -->
        <div v-else class="relative">

          <!-- PROFILE CIRCLE -->
          <div
            @click="showMenu = !showMenu"
            class="w-10 h-10 rounded-full bg-yellow-500 text-black
                   flex items-center justify-center font-bold cursor-pointer">

            {{ user.displayName?.charAt(0)?.toUpperCase() || user.email.charAt(0).toUpperCase() }}

          </div>

          <!-- DROPDOWN -->
          <div
            v-if="showMenu"
            class="absolute right-0 mt-2 w-32 bg-white dark:bg-[#13293d]
                   border border-gray-200 dark:border-[#1f3b55]
                   rounded-lg shadow-lg p-2">

            <button
              @click="logout"
              class="w-full text-left px-3 py-2 text-sm hover:bg-gray-100
                     dark:hover:bg-[#1f3b55] rounded"
            >
              Logout
            </button>

          </div>

        </div>

      </div>

    </nav>

    <!-- PAGE -->
    <main class="pt-6 px-4">
      <router-view />
    </main>

  </div>
</template>

<style scoped>

/* NAV PILLS */
.nav-pill {
  padding: 8px 18px;
  border-radius: 999px;
  font-size: 14px;
  transition: all 0.3s ease;
  color: #374151;
}

.dark .nav-pill {
  color: #cbd5e1;
}

.nav-pill:hover {
  color: #facc15;
}

.active {
  background: #fde68a;
  color: black;
}

.dark .active {
  background: #1e3a5f;
  color: #facc15;
}

</style>