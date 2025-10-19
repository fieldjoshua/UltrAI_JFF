module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Terminal color scheme
        'terminal-bg': '#0c0c0c',
        'terminal-green': '#00ff00',
        'terminal-green-dim': '#008800',
        'terminal-green-dark': '#004400',
      },
    },
  },
  plugins: [],
}
