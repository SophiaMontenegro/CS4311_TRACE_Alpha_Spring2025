import tailwindcssAnimate from "tailwindcss-animate";

/** @type {import('tailwindcss').Config} */
const config = {
  darkMode: ["class"],
  content: ["./src/**/*.{html,js,svelte,ts}"],
  safelist: ["dark"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px"
      }
    },
    extend: {
      colors: {
        border: "var(--border)",
        input: "var(--input)",
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "var(--primary)",
          foreground: "var(--primary-foreground)"
        },
        secondary: {
          DEFAULT: "var(--secondary)",
          foreground: "var(--secondary-foreground)"
        },
        accent: {
          DEFAULT: "var(--accent)",
          foreground: "var(--accent-foreground)"
        },
        accent1: {
          DEFAULT: "var(--accent1)",
          foreground: "var(--accent1-foreground)"
        },
        accent2: {
          DEFAULT: "var(--accent2)",
          foreground: "var(--accent2-foreground)"
        },
        accent3: {
          DEFAULT: "var(--accent3)",
          foreground: "var(--accent3-foreground)",
          hover: "var(--accent3-hover)"
        },
        muted: {
          DEFAULT: "var(--muted)",
          foreground: "var(--muted-foreground)"
        },
        error: {
          DEFAULT: "var(--error)",
          foreground: "var(--error-foreground)",
          hover: "var(--error-hover)",
          outline: "var(--error-outline)"
        },
        success: {
          DEFAULT: "var(--success)",
          foreground: "var(--success-foreground)",
          hover: "var(--success-hover)"
        },
        warning: {
          DEFAULT: "var(--warning)",
          foreground: "var(--warning-foreground)",
          hover: "var(--warning-hover)"
        },
        popover: {
          DEFAULT: "var(--popover)",
          foreground: "var(--popover-foreground)"
        },
        card: {
          DEFAULT: "var(--card)",
          foreground: "var(--card-foreground)"
        },
        background1: {
          DEFAULT: "var(--background1)",
          foreground: "var(--background1-foreground)"
        },
        background2: {
          DEFAULT: "var(--background2)",
          foreground: "var(--background2-foreground)"
        },
        background3: {
          DEFAULT: "var(--background3)",
          foreground: "var(--background3-foreground)"
        }
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"]
      },
      borderWidth: {
        '1.5': "1.5px"
      }
    }
  },
  plugins: [tailwindcssAnimate]
};

export default config;
