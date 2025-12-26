import '@testing-library/jest-dom';
import i18n from './src/i18n';
import { initReactI18next } from 'react-i18next';
import { vi } from 'vitest';

// Глобальный мок для всех SVG как React-компонентов
vi.mock('*.svg?react', () => ({ default: () => 'svg' }), { virtual: true });
vi.mock('*.svg', () => ({ default: '' }), { virtual: true });

i18n.use(initReactI18next).init({
    lng: 'en',
    fallbackLng: 'ua',
    resources: {
        en: { translation: { main: 'Home', drag_drop: 'Drag & Drop', login: 'Login', loading_auth: 'Loading...' } },
        ua: { translation: { main: 'Головна', drag_drop: 'Перетягни файл', login: 'Увійти', loading_auth: 'Завантаження...' } }
    }
}); 