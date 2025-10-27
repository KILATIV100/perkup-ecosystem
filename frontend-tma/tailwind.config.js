/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#6C5CE7',
        'primary-dark': '#5F4FD1',
        secondary: '#00B894',
        background: '#0D0C1D',
        surface: '#161B33',
        border: '#2C3354',
      },
    },
  },
  plugins: [],
}