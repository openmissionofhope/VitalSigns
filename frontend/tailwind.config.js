/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Risk level colors
        risk: {
          minimal: '#10B981',
          low: '#84CC16',
          moderate: '#F59E0B',
          high: '#F97316',
          critical: '#EF4444',
        },
        // Disease-specific colors
        disease: {
          malaria: '#8B5CF6',
          cholera: '#06B6D4',
          measles: '#EC4899',
          dengue: '#F97316',
          respiratory: '#6366F1',
        },
      },
    },
  },
  plugins: [],
};
