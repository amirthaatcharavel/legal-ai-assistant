<template>
  <div class="auth-page">

    <div class="auth-card">

      <div class="icon-circle">⚖️</div>

      <h1 class="title">Welcome back</h1>
      <p class="subtitle">
        Sign in to continue your legal research.
      </p>

      <!-- FORM -->
      <form @submit.prevent="login">

        <label>Email</label>
        <input
          v-model="email"
          type="email"
          placeholder="you@firm.law"
          class="input"
          required
        />

        <div class="flex justify-between items-center mt-4">
          <label>Password</label>
          <span class="link">Forgot password?</span>
        </div>

        <input
          v-model="password"
          type="password"
          placeholder="••••••••"
          class="input"
          required
        />

        <button type="submit" class="btn-primary mt-6">
          Sign in
        </button>

      </form>

      <div class="divider">OR CONTINUE WITH</div>

      <!-- 🔥 GOOGLE LOGIN -->
      <div class="flex justify-center">
        <button 
          @click="googleLogin"
          class="social-btn flex items-center gap-2 px-6 py-2"
        >
          Continue with Google
        </button>
      </div>

      <p class="bottom-text">
        Don’t have an account?
        <router-link to="/signup" class="link">Sign up</router-link>
      </p>

    </div>
  </div>
</template>

<script>
import { auth } from "../firebase";
import { 
  signInWithEmailAndPassword, 
  GoogleAuthProvider, 
  signInWithPopup 
} from "firebase/auth";

export default {
  data() {
    return {
      email: "",
      password: ""
    };
  },

  methods: {

    // 🔐 EMAIL LOGIN
    async login() {
      try {
        const userCredential = await signInWithEmailAndPassword(
          auth,
          this.email,
          this.password
        );

        console.log("Logged in:", userCredential.user);

        alert("Login successful!");
        this.$router.push("/");

      } catch (error) {
        console.error(error);

        if (error.code === "auth/user-not-found") {
          alert("User not found");
        } else if (error.code === "auth/wrong-password") {
          alert("Wrong password");
        } else {
          alert(error.message);
        }
      }
    },

    // 🔥 GOOGLE LOGIN
    async googleLogin() {
      const provider = new GoogleAuthProvider();

      try {
        const result = await signInWithPopup(auth, provider);

        console.log("Google user:", result.user);

        alert("Logged in with Google!");
        this.$router.push("/");

      } catch (error) {
        console.error(error);
        alert("Google login failed");
      }
    }

  }
};
</script>

<style scoped>

.auth-page {
  @apply min-h-screen flex items-center justify-center
         bg-[#f5f2eb] text-[#1f2937]
         dark:bg-gradient-to-b dark:from-[#061726] dark:to-[#020b16]
         dark:text-white;
}

.auth-card {
  @apply w-full max-w-md p-8 rounded-2xl border shadow-xl
         bg-white border-gray-200
         dark:bg-[#0d2235] dark:border-[#1f3b55];
}

.title { @apply text-3xl text-center font-serif mt-4; }

.subtitle {
  @apply text-gray-600 dark:text-gray-400 text-center mb-6;
}

.input {
  @apply w-full mt-2 px-4 py-3 rounded-xl border
         bg-gray-100 border-gray-300 text-black
         dark:bg-[#13293d] dark:border-[#1f3b55] dark:text-white;
}

.btn-primary {
  @apply w-full bg-gradient-to-r from-yellow-400 to-orange-500
         py-3 rounded-full text-black;
}

.divider {
  @apply text-center text-gray-500 my-6 text-sm;
}

.social-btn {
  @apply border border-gray-300 dark:border-[#1f3b55]
         rounded-full flex items-center justify-center;
}

.link {
  @apply text-yellow-500 cursor-pointer;
}

.bottom-text {
  @apply text-center mt-6 text-gray-500 dark:text-gray-400;
}

.icon-circle {
  @apply w-12 h-12 mx-auto flex items-center justify-center
         rounded-full text-yellow-500
         bg-gray-200 dark:bg-[#13293d];
}

</style>