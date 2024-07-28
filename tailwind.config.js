/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/**/templates/**/*.html',
        './src/static/lib/flowbite/**/*.js',
    ],
    theme: {
        extend: {},
    },
    variants: {
        extend: {
            blur: ['hover'],
        },
    },
    plugins: [
        require('flowbite/plugin'),
        // require('daisyui'),
    ],
}

