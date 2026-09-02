/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── SICP shared brand palette ─────────────────────────────────────
        // Primary — Jharkhand forest green, used for CTAs and headings
        primary: {
          50:  '#edf8f1',
          100: '#d7f0df',
          200: '#b1dfc0',
          300: '#82c99a',
          400: '#50aa70',
          500: '#27844d',
          600: '#176c3b',
          700: '#115a32',
          800: '#0e482a',
          900: '#09331e',
        },
        // Accent — warm gold from the SICP mark
        accent: {
          50:  '#fff8e8',
          100: '#feefc7',
          200: '#fcdfa0',
          300: '#f9c968',
          400: '#f4ad31',
          500: '#e89112',
          600: '#c97309',
          700: '#a65309',
          800: '#86410e',
          900: '#713710',
        },
        // Status colours — shared across /citizen, /university, /admin
        status: {
          new:         '#6366f1',   // indigo
          'in-progress': '#f59e0b', // amber
          resolved:    '#10b981',   // emerald
          duplicate:   '#6b7280',   // gray
        },
        // Surface tokens — keeps cards off pure white
        surface: {
          DEFAULT: '#f8fafc',
          card:    '#ffffff',
          border:  '#e2e8f0',
          muted:   '#f1f5f9',
        },
        // Text tokens
        ink: {
          DEFAULT: '#0f172a',
          muted:   '#64748b',
          subtle:  '#94a3b8',
        },
      },
      fontFamily: {
        sans: ['"Inter"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        xl:  '0.875rem',
        '2xl': '1.25rem',
      },
      boxShadow: {
        card:  '0 1px 3px 0 rgb(0 0 0 / .07), 0 1px 2px -1px rgb(0 0 0 / .05)',
        'card-hover': '0 4px 12px -2px rgb(0 0 0 / .10), 0 2px 6px -2px rgb(0 0 0 / .06)',
      },
    },
  },
  plugins: [],
}
