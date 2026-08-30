/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#EE5622',
          hover: '#FF6B35',
          light: '#FF8552',
          subtle: 'rgba(238, 86, 34, 0.15)',
        },
        neutral: {
          bg1: '#0A0A0B',
          bg2: '#121215',
          bg3: '#18181C',
          bg4: '#222228',
          bg5: '#2A2A32',
        },
        text: {
          primary: '#FAFAFA',
          secondary: '#A1A1AA',
          muted: '#71717A',
        },
        border: {
          subtle: 'rgba(255, 255, 255, 0.08)',
          DEFAULT: 'rgba(255, 255, 255, 0.12)',
          orange: 'rgba(238, 86, 34, 0.3)',
          strong: 'rgba(255, 255, 255, 0.20)',
        }
      }
    },
  },
  plugins: [],
};
