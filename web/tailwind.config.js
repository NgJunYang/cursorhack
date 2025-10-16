/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'groq-blue': '#00A8E8',
        'groq-dark': '#1a1a1a',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}