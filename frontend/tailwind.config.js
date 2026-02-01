/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,ts,jsx,tsx,mdx}',
        './components/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                border: '#e5e7eb',
                background: '#ffffff',
                foreground: '#111827',
                muted: '#f9fafb',
                'muted-foreground': '#6b7280',
                accent: '#f3f4f6',
                'accent-foreground': '#111827',
            },
            borderRadius: {
                DEFAULT: '0px',
            },
        },
    },
    plugins: [],
}
