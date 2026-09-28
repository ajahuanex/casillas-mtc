/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{html,ts,scss}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#00236f',
          container: '#1e3a8a',
          fixed: '#dce1ff',
          'fixed-dim': '#b6c4ff'
        },
        surface: {
          DEFAULT: '#f8f9ff',
          bright: '#f8f9ff',
          dim: '#cbdbf5',
          container: {
            lowest: '#ffffff',
            low: '#eff4ff',
            DEFAULT: '#e5eeff',
            high: '#dce9ff',
            highest: '#d3e4fe'
          }
        },
        'inverse-surface': '#213145',
        'inverse-on-surface': '#eaf1ff',
        'inverse-primary': '#b6c4ff',
        'on-surface': '#0b1c30',
        'on-surface-variant': '#444651',
        outline: {
          DEFAULT: '#757682',
          variant: '#c5c5d3'
        },
        drtc: {
          50: '#e0f2f1',
          100: '#b2dfdb',
          500: '#00796b',
          700: '#004d40',  // Verde institucional DRTC Puno
          900: '#00251a'
        },
        mtc: {
          blue: '#003366', // Azul MTC
          red: '#d9230f'   // Rojo institucional
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      }
    },
  },
  plugins: [],
}
