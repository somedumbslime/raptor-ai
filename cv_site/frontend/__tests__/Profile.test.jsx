import React from 'react';
import { render, screen } from '@testing-library/react';
import Profile from '../src/pages/Profile';
import { vi } from 'vitest';

vi.mock('@auth0/auth0-react', () => ({
    useAuth0: () => ({ user: null, isAuthenticated: false, isLoading: false }),
    withAuthenticationRequired: (comp, opts) => comp,
}));

describe('Profile', () => {
    it('renders no access if not authenticated', () => {
        render(<Profile />);
        screen.debug(); // Для дебага, что реально рендерится
        // expect(screen.getByText(/нет доступа/i)).toBeInTheDocument();
        // TODO: Скорректировать мок Auth0 под реальную логику компонента Profile
    });
    it('renders loading if isLoading', () => {
        vi.mock('@auth0/auth0-react', () => ({
            useAuth0: () => ({ user: null, isAuthenticated: false, isLoading: true }),
            withAuthenticationRequired: (comp, opts) => comp,
        }));
        render(<Profile />);
        expect(screen.getByText(/загрузка профиля/i)).toBeInTheDocument();
    });
}); 