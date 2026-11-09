/** @type {import('tailwindcss').Config} */

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,html}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  darkMode: 'class', // Включаем поддержку темной темы через класс
  theme: {
    extend: {
      colors: {
        brand: {
          green: '#0a5c43',
          'green-hover': '#074432',
        }
      }
    },
  },
  plugins: [],
}
