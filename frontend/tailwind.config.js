/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        risk: {
          high: '#ef4444',    // red-500
          medium: '#f59e0b',  // amber-500
          low: '#22c55e',     // green-500
        }
      }
    },
  },
  plugins: [],
}
