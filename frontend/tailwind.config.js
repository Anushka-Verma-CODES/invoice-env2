export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f3f7ff",
          100: "#e7efff",
          500: "#1d4ed8",
          700: "#1e3a8a"
        }
      },
      boxShadow: {
        soft: "0 12px 30px -12px rgba(15, 23, 42, 0.25)"
      }
    }
  },
  plugins: [],
};
