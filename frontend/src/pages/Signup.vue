<template>
  <div class="auth-page">

    <div class="auth-card">

      <div class="icon-circle">⚖️</div>

      <h1 class="title">Create your workspace</h1>
      <p class="subtitle">
        Premium legal research, free to start.
      </p>

      <!-- FORM -->
      <form @submit.prevent="signup">

        <label>Full Name</label>
        <input v-model="name" placeholder="Jane Counsel" class="input" required />

        <label class="mt-4">Email</label>
        <input v-model="email" type="email" placeholder="you@firm.law" class="input" required />

        <label class="mt-4">Password</label>
        <input v-model="password" type="password" placeholder="At least 6 characters" class="input" required />

        <label class="mt-4">Confirm Password</label>
        <input v-model="confirmPassword" type="password" placeholder="Re-enter password" class="input" required />

        <!-- TERMS -->
        <div class="terms-box">
          <input type="checkbox" v-model="agree" />
          <span>
            I agree to the
            <span class="link" @click="showTerms = true">Terms</span>
            and
            <span class="link" @click="showTerms = true">Privacy Policy</span>
          </span>
        </div>

        <button type="submit" class="btn-primary mt-4">
          Create account
        </button>

      </form>

      <div class="divider">OR SIGN UP WITH</div>

      <!-- GOOGLE SIGNUP -->
      <div class="flex justify-center">
        <button 
          @click="googleSignup"
          class="social-btn flex items-center gap-2 px-6 py-2"
        >

          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" class="w-5 h-5">
            <path fill="#EA4335" d="M24 9.5c3.3 0 6.3 1.1 8.6 3.3l6.4-6.4C34.6 2.2 29.6 0 24 0 14.6 0 6.6 5.8 2.6 14.2l7.6 5.9C12.3 13.3 17.7 9.5 24 9.5z"/>
            <path fill="#4285F4" d="M46.5 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.7c-.5 2.9-2.1 5.4-4.5 7l7 5.4c4.1-3.8 6.3-9.4 6.3-16.9z"/>
            <path fill="#FBBC05" d="M10.2 28.1c-1-2.9-1-6.1 0-9l-7.6-5.9C.9 17.1 0 20.4 0 24c0 3.6.9 6.9 2.6 9.8l7.6-5.7z"/>
            <path fill="#34A853" d="M24 48c6.5 0 12-2.1 16-5.7l-7-5.4c-2 1.4-4.6 2.3-9 2.3-6.3 0-11.7-3.8-13.8-9.2l-7.6 5.7C6.6 42.2 14.6 48 24 48z"/>
          </svg>

          Continue with Google
        </button>
      </div>

      <p class="bottom-text">
        Already have an account?
        <router-link to="/login" class="link">Sign in</router-link>
      </p>

    </div>

    <!-- TERMS MODAL -->
    <div v-if="showTerms" class="modal">
      <div class="modal-content">

        <h2 class="font-serif text-xl mb-4">Terms & Conditions</h2>

        <p class="text-sm text-gray-600 dark:text-gray-300">
          • This platform is for legal research assistance only.<br><br>
          • AI-generated responses should not be treated as legal advice.<br><br>
          • Users must verify all legal references independently.<br><br>
          • We do not permanently store sensitive legal data.<br><br>
          • Misuse may result in suspension or termination.<br><br>
          • Accounts violating policies will be removed.
        </p>

        <button @click="showTerms = false" class="btn-primary mt-4">
          Close
        </button>

      </div>
    </div>

  </div>
</template>

<script>
import { auth } from "../firebase";
import { 
  createUserWithEmailAndPassword, 
  updateProfile, 
  GoogleAuthProvider, 
  signInWithPopup 
} from "firebase/auth";

export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      agree: false,
      showTerms: false
    };
  },

  methods: {
    async signup() {

      if (!this.agree) {
        alert("Please accept terms");
        return;
      }

      if (this.password !== this.confirmPassword) {
        alert("Passwords do not match");
        return;
      }

      if (this.password.length < 6) {
        alert("Password must be at least 6 characters");
        return;
      }

      try {
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          this.email,
          this.password
        );

        await updateProfile(userCredential.user, {
          displayName: this.name
        });

        alert("Account created successfully!");
        this.$router.push("/login");

      } catch (error) {
        if (error.code === "auth/email-already-in-use") {
          alert("Email already in use");
        } else if (error.code === "auth/invalid-email") {
          alert("Invalid email");
        } else if (error.code === "auth/weak-password") {
          alert("Weak password");
        } else {
          alert(error.message);
        }
      }
    },

    async googleSignup() {
      const provider = new GoogleAuthProvider();

      try {
        await signInWithPopup(auth, provider);
        alert("Signed in with Google!");
        this.$router.push("/");
      } catch (error) {
        console.error(error);
        alert("Google sign-in failed");
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

.social-btn {
  @apply border border-gray-300 dark:border-[#1f3b55]
         rounded-full flex items-center justify-center;
}

.divider {
  @apply text-center text-gray-500 my-6 text-sm;
}

.link {
  @apply text-yellow-500 cursor-pointer;
}

.bottom-text {
  @apply text-center mt-6 text-gray-500 dark:text-gray-400;
}

.terms-box {
  @apply flex items-center gap-2 mt-4 text-sm text-gray-500 dark:text-gray-400;
}

.modal {
  @apply fixed inset-0 bg-black/70 flex items-center justify-center;
}

.modal-content {
  @apply p-6 rounded-xl w-[400px] border
         bg-white border-gray-200
         dark:bg-[#0d2235] dark:border-[#1f3b55];
}

.icon-circle {
  @apply w-12 h-12 mx-auto flex items-center justify-center
         rounded-full text-yellow-500
         bg-gray-200 dark:bg-[#13293d];
}
</style>