import { describe, it, expect } from 'vitest';
import i18n from '../src/i18n';

describe('i18n', () => {
    it('returns translation for en', () => {
        i18n.changeLanguage('en');
        expect(i18n.t('main')).toBe('Home');
    });
    it('returns translation for ua', () => {
        i18n.changeLanguage('ua');
        expect(i18n.t('main')).toBe('Головна');
    });
    it('falls back to ua', () => {
        i18n.changeLanguage('fr');
        expect(i18n.t('main')).toBe('Головна');
    });
}); 