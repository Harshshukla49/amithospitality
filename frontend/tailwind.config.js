/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        obsidian: {
          950: '#060709',
          900: '#0B0C10',
          850: '#111218',
          800: '#161822',
        },
        charcoal: {
          900: '#181B22',
          800: '#1F242E',
          700: '#2A303D',
          600: '#3A4254',
        },
        gold: {
          50: '#FAF6EB',
          100: '#F3EACF',
          200: '#E7D59F',
          300: '#DBBF6F',
          400: '#D4AF37', // Master Champagne Gold
          500: '#C5A059',
          600: '#A68424',
          700: '#7E6316',
          800: '#54420A',
        },
        cream: {
          50: '#FDFBF7',
          100: '#FAF6EE',
          200: '#F3EDE0',
          300: '#E8DFC9',
        },
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'luxury': '0 20px 40px -15px rgba(0, 0, 0, 0.7), 0 0 25px rgba(212, 175, 55, 0.08)',
        'gold-glow': '0 0 20px rgba(212, 175, 55, 0.25)',
      },
    },
  },
  plugins: [],
};
