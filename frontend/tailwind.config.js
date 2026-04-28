/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',   // ✅ THIS LINE FIXES YOUR ISSUE

  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],

  theme: {
    extend: {
      colors: {
        primary: "#0b1b2b",
        accent: "#facc15",
        card: "#112233",

        // ✅ ADD LIGHT THEME COLORS (IMPORTANT)
        lightBg: "#f5f2eb",
        lightCard: "#ffffff",
        lightText: "#1f2937"
      },

      fontFamily: {
        serif: ['"Playfair Display"', 'serif'],
        sans: ['Inter', 'sans-serif'],
      }
    },
  },

  plugins: [],
}