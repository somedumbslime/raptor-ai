import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import AuthButton from '../src/components/AuthButton';
import { MemoryRouter } from 'react-router-dom';

vi.mock('@auth0/auth0-react', () => ({
    useAuth0: () => ({
        isAuthenticated: false,
        loginWithRedirect: vi.fn(),
        logout: vi.fn(),
        user: null,
        isLoading: false,
    })
}));

describe('AuthButton', () => {
    it('renders login button if not authenticated', () => {
        render(
            <MemoryRouter>
                <AuthButton />
            </MemoryRouter>
        );
        expect(screen.getByText(/login/i)).toBeInTheDocument();
    });
}); 