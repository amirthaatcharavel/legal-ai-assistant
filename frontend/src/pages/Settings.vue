<template>
  <div class="min-h-screen px-6 md:px-16 lg:px-32 xl:px-48 py-16
              bg-[#f5f2eb] text-[#1f2937]
              dark:bg-[#0b1b2b] dark:text-white transition-all duration-500">

    <!-- HEADER -->
    <div class="max-w-3xl">
      <p class="text-xs tracking-widest text-yellow-500 mb-3">WORKSPACE</p>

      <h1 class="text-5xl md:text-6xl font-serif">Settings</h1>

      <p class="mt-4 text-gray-600 dark:text-gray-400 text-lg">
        Tailor the assistant to your practice. Changes are saved locally to this browser.
      </p>
    </div>

    <!-- ================= PROFILE ================= -->
    <div class="card mt-10">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><User /></div>
        <div>
          <h2 class="section-title">Profile</h2>
          <p class="section-desc">How you appear inside the workspace.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6">

  <div class="flex items-center gap-6">

    <!-- Avatar -->
    <div class="avatar">
      {{ email ? email[0].toUpperCase() : "Z" }}
    </div>

    <!-- Inputs -->
    <div class="flex gap-4 w-full">

      <input 
        class="input flex-1"
        v-model="name"
        placeholder="Display name"
      />

      <input 
        class="input flex-1"
        v-model="email"
        placeholder="Email"
      />

    </div>

  </div>

</div>

      </div>

    <!-- ================= APPEARANCE ================= -->
    <div class="card mt-8">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><Palette /></div>
        <div>
          <h2 class="section-title">Appearance</h2>
          <p class="section-desc">Theme for the interface.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6 flex gap-4">

<button
  @click="setTheme('dark')"
  :class="[
    'toggle-btn flex items-center gap-2 px-6 py-2 rounded-full border transition',
    isDark ? 'active-dark' : 'bg-white text-gray-700'
  ]"
>
  <Moon class="w-4 h-4" />
  Dark
</button>

<button
  @click="setTheme('light')"
  :class="[
    'toggle-btn flex items-center gap-2 px-6 py-2 rounded-full border transition',
    !isDark ? 'active-light' : 'bg-white text-gray-700'
  ]"
>
  <Sun class="w-4 h-4" />
  Light
</button>

      </div>

    </div>

    <!-- ================= RETRIEVAL ================= -->
    <div class="card mt-8">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><Database /></div>
        <div>
          <h2 class="section-title">Retrieval & AI</h2>
          <p class="section-desc">Tune how deeply the assistant searches and responds.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6">

        <select class="input w-full mb-6">
          <option>Balanced — recommended</option>
        </select>

        <div class="toggle-row">
          <div>
            <p class="font-medium">Always include citations</p>
            <p class="desc">Append source case references to every answer.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="includeCitations" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="toggle-row mt-4">
          <div>
            <p class="font-medium">Stream responses</p>
            <p class="desc">Show tokens as they arrive.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="streamResponse" />
            <span class="slider"></span>
          </label>
        </div>

      </div>

    </div>

    <!-- ================= NOTIFICATIONS ================= -->
    <div class="card mt-8">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><Bell /></div>
        <div>
          <h2 class="section-title">Notifications</h2>
          <p class="section-desc">Decide what reaches your inbox.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6 space-y-4">

        <div class="toggle-row">
          <div>
            <p>Email alerts</p>
            <p class="desc">Important notifications.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="emailAlerts" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="toggle-row">
          <div>
            <p>Product updates</p>
            <p class="desc">New features and updates.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="productUpdates" />
            <span class="slider"></span>
          </label>
        </div>

        <div class="toggle-row">
          <div>
            <p>Weekly digest</p>
            <p class="desc">Summary of activity.</p>
          </div>
          <label class="switch">
            <input type="checkbox" v-model="weeklyDigest" />
            <span class="slider"></span>
          </label>
        </div>

      </div>

    </div>

    <!-- ================= SECURITY ================= -->
    <div class="card mt-8">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><Lock /></div>
        <div>
          <h2 class="section-title">Security</h2>
          <p class="section-desc">Manage password and authentication.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6 grid md:grid-cols-3 gap-4">

        <input type="password" v-model="currentPassword" class="input" placeholder="Current password" />
        <input type="password" v-model="newPassword" class="input" placeholder="New password" />
        <input type="password" v-model="confirmPassword" class="input" placeholder="Confirm password" />

      </div>

      <button class="btn-secondary mt-4">Update password</button>

      <div class="toggle-row mt-6">
        <div>
          <p>Two-factor authentication</p>
          <p class="desc">Extra security layer.</p>
        </div>
        <label class="switch">
          <input type="checkbox" v-model="twoFactor" />
          <span class="slider"></span>
        </label>
      </div>

    </div>

    <!-- ================= DATA ================= -->
    <div class="card mt-8">

      <div class="flex items-center gap-3 mb-6">
        <div class="icon-circle"><AlertTriangle /></div>
        <div>
          <h2 class="section-title">Data & Account</h2>
          <p class="section-desc">Manage stored data.</p>
        </div>
      </div>

      <div class="border-t border-gray-200 dark:border-[#1f3b55] pt-6 space-y-4">

        <div class="flex justify-between items-center">
          <div>
            <p>Clear search history</p>
            <p class="desc">Delete stored queries.</p>
          </div>
          <button class="btn-secondary" @click="clearHistory">Clear history</button>
        </div>

        <div class="flex justify-between items-center border border-red-300 rounded-xl p-4">
          <div>
            <p class="text-red-500 font-medium">Delete account</p>
            <p class="desc">Remove all data permanently.</p>
          </div>
          <button class="btn-danger" @click="deleteAccount">Delete account</button>
        </div>

      </div>

    </div>

    <!-- FOOTER -->
    <div class="flex justify-end gap-4 mt-10">
      <button class="text-gray-500" @click="resetSettings">Reset to defaults</button>
      <button class="btn-primary" @click="saveSettings">Save changes</button>
    </div>

  </div>
</template>

<script>
import {
  User, Palette, Database, Bell,
  Lock, AlertTriangle,
  Moon, Sun
} from "lucide-vue-next";

export default {
  components: {
    User, Palette, Database, Bell,
    Lock, AlertTriangle,
    Moon, Sun
  },

  data() {
    return {
      // 🔥 THEME
      isDark: false,

      // 🔥 PROFILE
      name: "",
      email: "",
      isNameEdited: false, // 👈 important

      // 🔥 RETRIEVAL
      includeCitations: true,
      streamResponse: true,

      // 🔥 NOTIFICATIONS
      emailAlerts: true,
      productUpdates: true,
      weeklyDigest: false
    };
  },

  // 🔥 AUTO EXTRACT NAME FROM EMAIL
  watch: {
    email(newEmail) {
      if (!newEmail) return;

      // ❌ don't override if user already edited name
      if (this.isNameEdited) return;

      const extracted = newEmail.split("@")[0];

      this.name =
        extracted.charAt(0).toUpperCase() + extracted.slice(1);
    },

    // detect manual edit
    name() {
      this.isNameEdited = true;
    }
  },

  methods: {
    // ================= THEME =================
    setTheme(mode) {
      this.isDark = mode === "dark";

      if (this.isDark) {
        document.documentElement.classList.add("dark");
        localStorage.setItem("theme", "dark");
      } else {
        document.documentElement.classList.remove("dark");
        localStorage.setItem("theme", "light");
      }
    },

    // ================= SAVE SETTINGS =================
    saveSettings() {
      const settings = {
        name: this.name,
        email: this.email,
        includeCitations: this.includeCitations,
        streamResponse: this.streamResponse,
        emailAlerts: this.emailAlerts,
        productUpdates: this.productUpdates,
        weeklyDigest: this.weeklyDigest
      };

      localStorage.setItem("settings", JSON.stringify(settings));

      alert("✅ Settings saved!");
    },

    // ================= LOAD SETTINGS =================
    loadSettings() {
      const saved = localStorage.getItem("settings");

      if (saved) {
        const s = JSON.parse(saved);

        this.name = s.name || "";
        this.email = s.email || "";
        this.includeCitations = s.includeCitations ?? true;
        this.streamResponse = s.streamResponse ?? true;
        this.emailAlerts = s.emailAlerts ?? true;
        this.productUpdates = s.productUpdates ?? true;
        this.weeklyDigest = s.weeklyDigest ?? false;
      }
    },

    // ================= CLEAR HISTORY =================
    clearHistory() {
      localStorage.removeItem("lastResponse");
      localStorage.removeItem("lastQuery");

      alert("🧹 Chat history cleared!");
    },

    // ================= RESET =================
    resetSettings() {
      localStorage.removeItem("settings");
      location.reload();
    }
  },

  mounted() {
    // 🔥 LOAD THEME
    const savedTheme = localStorage.getItem("theme");
    this.isDark = savedTheme === "dark";

    if (this.isDark) {
      document.documentElement.classList.add("dark");
    }

    // 🔥 LOAD SETTINGS
    this.loadSettings();
  }
};
</script>

<style scoped>

/* CARD */
.card {
  @apply bg-white dark:bg-gradient-to-b dark:from-[#0d2235] dark:to-[#081521]
         p-8 rounded-2xl border border-gray-200 dark:border-[#1f3b55] shadow-lg;
}

/* ICON */
.icon-circle {
  @apply w-10 h-10 flex items-center justify-center
         rounded-full bg-gray-200 dark:bg-[#13293d] text-yellow-500;
}

/* TEXT */
.section-title { @apply font-serif text-xl; }
.section-desc { @apply text-sm text-gray-500 dark:text-gray-400; }
.desc { @apply text-sm text-gray-500 dark:text-gray-400; }

/* INPUT */
.input {
  @apply w-full px-4 py-3 rounded-xl border border-gray-300
         bg-gray-100 dark:bg-[#13293d] dark:border-[#1f3b55] outline-none;
}

/* BUTTONS */
.btn-primary {
  @apply bg-yellow-500 text-black px-6 py-3 rounded-full;
}

.btn-secondary {
  @apply px-4 py-2 rounded-full border border-gray-300;
}

.btn-danger {
  @apply bg-red-500 text-white px-4 py-2 rounded-full;
}

/* TOGGLE ROW */
.toggle-row {
  @apply flex justify-between items-center bg-gray-100 dark:bg-[#13293d]
         p-4 rounded-xl;
}

/* SWITCH TOGGLE */
.switch {
  position: relative;
  display: inline-block;
  width: 42px;
  height: 22px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  inset: 0;
  background-color: #ccc;
  border-radius: 9999px;
  transition: 0.3s;
}

.slider:before {
  content: "";
  position: absolute;
  height: 16px;
  width: 16px;
  left: 3px;
  top: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

.switch input:checked + .slider {
  background-color: #facc15;
}

.switch input:checked + .slider:before {
  transform: translateX(20px);
}

/* AVATAR */
.avatar {
  @apply w-16 h-16 rounded-xl bg-gradient-to-br from-gray-200 to-gray-400
         flex items-center justify-center text-xl font-bold;
}

/* THEME BUTTON */
.toggle-btn {
  @apply px-6 py-2 rounded-full border border-gray-300;
}

</style>