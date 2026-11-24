import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

export const IapPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#fbf3f5',
      100: '#f5e3e8',
      200: '#ebc4cf',
      300: '#d993a8',
      400: '#9a3f5c',
      500: '#7a1737',
      600: '#66122d',
      700: '#530f25',
      800: '#410b1d',
      900: '#300815',
      950: '#20050e',
    },
    colorScheme: {
      light: {
        surface: {
          0: '#ffffff',
          50: '#faf8f4',
          100: '#f3efe8',
          200: '#e8e1d5',
          300: '#d6ccbc',
          400: '#b3a894',
          500: '#8c826f',
          600: '#6b6354',
          700: '#4f493e',
          800: '#36322a',
          900: '#221f1a',
          950: '#141210',
        },
      },
    },
  },
})
