/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**.j2", "./src/js/**.js"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
}