import type { Config } from "tailwindcss";

const baseTailwindConfig: Omit<Config, "content"> = {
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#185FA5",
          light: "#E6F1FB",
          dark: "#042C53",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "ui-sans-serif", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default baseTailwindConfig;
