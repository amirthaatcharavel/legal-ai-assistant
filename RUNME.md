# Run Guide for Legal AI Web Application

## Prerequisites
- **Node.js** (v18 or later) and **npm** installed.
- **Python** (3.11+) if you want to run the optional FastAPI backend.
- A **Firebase project** with Firestore enabled.
- Git (optional, for cloning the repo).

## 1. Clone the repository (if you haven't already)
```bash
git clone https://github.com/your-repo/legal-rag-copy.git
cd legal-rag-copy
```

## 2. Install Front‑end dependencies
```bash
npm ci   # installs exact versions from package-lock.json
```

## 3. Configure Firebase
1. In the Firebase console, create a project and enable **Firestore** and **Authentication**.
2. Copy the Firebase config object (apiKey, authDomain, projectId, etc.).
3. Create a file `frontend/src/firebase.js` (or update the existing one) with:
```js
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_STORAGE_BUCKET",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
```
Replace the placeholder values with the ones from your Firebase console.

## 4. (Optional) Set up the FastAPI backend
If you want to use the local AI backend:
```bash
cd ..   # go to the repository root if you are inside `frontend`
python -m venv venv
source venv/Scripts/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Run the server:
```bash
uvicorn app:app --reload --port 8000
```
The FastAPI server will be available at `http://127.0.0.1:8000`.

## 5. Start the development server (frontend)
```bash
npm run dev
```
The Vite dev server will launch, typically at `http://localhost:5173`. Open that URL in your browser.

## 6. Using the application
- **Sign‑in** (Google, email/password, etc.) – the app uses Firebase Auth.
- Navigate to **Chat**, **Cases**, **Saved**, and **History** pages.
- The **Save** button on the Chat page stores a case in `users/{uid}/saved`.
- The **Saved** page (`Saved.vue`) fetches and displays those saved cases.

## 7. Building for production (optional)
```bash
npm run build   # creates a production‑ready bundle in `dist/`
```
You can then serve the `dist` folder with any static web server (e.g., `npm i -g serve && serve -s dist`).

---
**Tips**
- Keep your Firebase rules tight; only allow authenticated users to read/write their own data.
- Use `npm run lint` (if configured) to keep code style consistent.
- For any environment‑specific variables, create a `.env` file and load it via Vite's `import.meta.env`.

Happy coding! 🎉
