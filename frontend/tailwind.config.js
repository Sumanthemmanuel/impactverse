/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // ── ImpactVerse shared brand palette ──────────────────────────────
        // Primary — deep indigo used for CTAs, active nav, key headings
        primary: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',   // ← base brand colour
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        // Accent — teal, used for map pins, tracker badges, success states
        accent: {
          50:  '#f0fdfa',
          100: '#ccfbf1',
          200: '#99f6e4',
          300: '#5eead4',
          400: '#2dd4bf',
          500: '#14b8a6',   // ← base accent
          600: '#0d9488',
          700: '#0f766e',
          800: '#115e59',
          900: '#134e4a',
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
