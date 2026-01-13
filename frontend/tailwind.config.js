/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 베이지/크림 색상
        cream: {
          50: '#FFFBF5',
          100: '#FFF9ED',
          200: '#F5F1E8',
          300: '#F0EBE0',
          400: '#E8E0D5',
        },
        // 오렌지/골드 색상
        gold: {
          400: '#F39C12',
          500: '#E67E22',
          600: '#D68910',
          700: '#B8860B',
        },
        // 다크 브라운
        brown: {
          500: '#8B4513',
          600: '#5D4037',
        },
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px',
      },
    },
  },
  plugins: [],
}
