import React from 'react';
import { render, screen } from '@testing-library/react';
import AboutPage from '../src/pages/AboutPage';
import { vi } from 'vitest';
vi.mock('../icons/gmail.svg?react', () => ({ default: () => <svg /> }), { virtual: true });
vi.mock('../icons/telegram.svg?react', () => ({ default: () => <svg /> }), { virtual: true });

describe.skip('AboutPage', () => {
    it('renders team title and contacts', () => {
        render(<AboutPage />);
        expect(screen.getByText(/team_title/i)).toBeInTheDocument();
        expect(screen.getByText(/sanekvseok228@gmail.com/i)).toBeInTheDocument();
        expect(screen.getByText(/@somedumbslime/i)).toBeInTheDocument();
    });
}); 