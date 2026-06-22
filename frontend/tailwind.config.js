export default {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["SUIT", "ui-sans-serif", "system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      colors: {
        ink: "#172033",
        navy: "#0b2454",
        mint: "#12b8a6",
        teal: "#009e8e",
        skybrand: "#128ba6",
        aqua: "#ddf7f2",
        moss: "#326454",
        leaf: "#7aa95c",
        river: "#2c7da0",
        clay: "#c87941",
        fog: "#f6f8fb",
      },
      boxShadow: {
        soft: "0 18px 50px rgba(20, 34, 28, 0.12)",
      },
    },
  },
  plugins: [],
};
