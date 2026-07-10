const config = {
  content: ['./src/**/*.{html,js,svelte,ts}'],
  theme: {
    extend: {
      colors: {
        ink: '#08111d',
        steel: '#0d1726',
        grid: '#162235',
        glow: '#35f2c8',
        amberline: '#ffb95e',
        signal: '#89ff5d',
        alarm: '#ff6c7c',
        mist: '#c1d2e9'
      },
      fontFamily: {
        display: ['"Space Grotesk"', '"Segoe UI"', 'sans-serif'],
        body: ['"IBM Plex Sans"', '"Segoe UI"', 'sans-serif'],
        mono: ['"IBM Plex Mono"', '"Cascadia Code"', 'monospace']
      },
      boxShadow: {
        panel: '0 24px 80px rgba(0, 0, 0, 0.35)'
      },
      backgroundImage: {
        screen:
          'radial-gradient(circle at top left, rgba(53, 242, 200, 0.14), transparent 34%), radial-gradient(circle at top right, rgba(255, 185, 94, 0.14), transparent 26%), linear-gradient(180deg, rgba(5, 12, 22, 0.95), rgba(7, 11, 18, 1))'
      }
    }
  },
  plugins: []
};

export default config;
