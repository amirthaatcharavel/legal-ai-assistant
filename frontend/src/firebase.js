import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore"; // ✅ ADD

const firebaseConfig = {
  apiKey: "AIzaSyD2H8NkBriw5szOmM8XMJyviWVY-ouFReg",
  authDomain: "legal-ai-d063c.firebaseapp.com",
  projectId: "legal-ai-d063c",
  storageBucket: "legal-ai-d063c.appspot.com",
  messagingSenderId: "581808982083",
  appId: "1:581808982083:web:9f26a41758d4b5b1156cf6"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app); // ✅ EXPORT DB