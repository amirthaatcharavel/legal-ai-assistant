import { createRouter, createWebHistory } from "vue-router";
import { auth } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";

// Pages
import Home from "../pages/Home.vue";
import Chat from "../pages/Chat.vue";
import Cases from "../pages/Cases.vue";
import About from "../pages/About.vue";
import History from "../pages/History.vue";
import Saved from "../pages/Saved.vue";
import Settings from "../pages/Settings.vue";
import Login from "../pages/Login.vue";
import Signup from "../pages/Signup.vue";

// 🔥 ROUTES
const routes = [
  // ✅ PUBLIC
  { path: "/", component: Home },
  { path: "/about", component: About },
  { path: "/login", component: Login },
  { path: "/signup", component: Signup },

  // 🔒 PROTECTED
  { path: "/chat", component: Chat, meta: { requiresAuth: true } },
  { path: "/cases", component: Cases, meta: { requiresAuth: true } },
  { path: "/history", component: History, meta: { requiresAuth: true } },
  { path: "/saved", component: Saved, meta: { requiresAuth: true } },
  { path: "/settings", component: Settings, meta: { requiresAuth: true } }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});


// 🔥 Wait for Firebase user (IMPORTANT)
function getCurrentUser() {
  return new Promise((resolve, reject) => {
    const unsubscribe = onAuthStateChanged(
      auth,
      (user) => {
        unsubscribe();
        resolve(user);
      },
      reject
    );
  });
}


// 🔥 ROUTE GUARD
router.beforeEach(async (to, from, next) => {

  const user = await getCurrentUser();

  // ❌ If trying protected page without login
  if (to.meta.requiresAuth && !user) {
    next("/login");
  } else {
    next();
  }

});

export default router;