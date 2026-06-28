/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  theme: {
    extend: {
      fontFamily: {
        brand: ['"Alimama FangYuanTi"', '"Microsoft YaHei"', '"PingFang SC"', 'sans-serif'],
      },
      colors: {
        rocom: {
          bg: 'var(--rocom-bg)',
          'bg-warm': 'var(--rocom-bg-warm)',
          'bg-paper': 'var(--rocom-bg-paper)',
          'bg-parchment': 'var(--rocom-bg-parchment)',
          surface: 'var(--rocom-surface)',
          'surface-paper': 'var(--rocom-surface-paper)',
          'surface-strong': 'var(--rocom-surface-strong)',
          'surface-muted': 'var(--rocom-surface-muted)',
          text: 'var(--rocom-text)',
          'text-strong': 'var(--rocom-text-strong)',
          'text-secondary': 'var(--rocom-text-secondary)',
          'text-muted': 'var(--rocom-text-muted)',
          'text-caption': 'var(--rocom-text-caption)',
          'text-disabled': 'var(--rocom-text-disabled)',
          primary: 'var(--rocom-primary)',
          'primary-soft': 'var(--rocom-primary-soft)',
          'primary-strong': 'var(--rocom-primary-strong)',
          'primary-outline': 'var(--rocom-primary-outline)',
          'accent-orange': 'var(--rocom-accent-orange)',
          'accent-blue': 'var(--rocom-accent-blue)',
          outline: 'var(--rocom-outline)',
          separator: 'var(--rocom-separator)',
          control: 'var(--rocom-control)',
          'control-strong': 'var(--rocom-control-strong)',
          'control-hover': 'var(--rocom-control-hover)',
          'nav-surface': 'var(--rocom-nav-surface)',
        },
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        paper: 'var(--shadow-paper)',
        lg: 'var(--shadow-lg)',
        float: 'var(--shadow-float)',
      },
    },
  },
  plugins: [require('@tailwindcss/forms')],
}
