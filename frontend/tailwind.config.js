/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts,scss}",
  ],
  theme: {
    extend: {
      colors: {
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
      }
    },
  },
  plugins: [],
}
