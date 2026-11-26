import { definePreset } from '@primeuix/themes'
import Aura from '@primeuix/themes/aura'

export const IapPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#fbf3f5',
      100: '#f6e9ed',
      200: '#ebc4cf',
      300: '#d993a8',
      400: '#e57a99',
      500: '#7a1737',
      600: '#5e1129',
      700: '#4b0d21',
      800: '#3a0919',
      900: '#2a0612',
      950: '#1b040b',
    },
    colorScheme: {
      light: {
        surface: {
          0: '#ffffff',
          50: '#faf8f4',
          100: '#f5f2ec',
          200: '#eae4d9',
          300: '#d8cfbf',
          400: '#a39987',
          500: '#5c5549',
          600: '#3a3a3a',
          700: '#111111',
          800: '#000000',
          900: '#000000',
          950: '#000000',
        },
        text: {
          color: '#111111',
          hoverColor: '#000000',
          mutedColor: '#3a3a3a',
          hoverMutedColor: '#111111',
        },
      },
      dark: {
        primary: {
          color: '#e57a99',
          contrastColor: '#1b040b',
          hoverColor: '#f09bb4',
          activeColor: '#d45a7d',
        },
        surface: {
          0: '#ffffff',
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#454f59',
          700: '#2e363d',
          800: '#20262b',
          900: '#181d21',
          950: '#0f1316',
        },
      },
    },
  },
})
