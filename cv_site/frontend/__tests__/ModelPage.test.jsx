import React from 'react';
import { render, screen } from '@testing-library/react';
import ModelPage from '../src/pages/ModelPage';

describe('ModelPage', () => {
    it('renders main sections', () => {
        render(<ModelPage />);
        expect(screen.getAllByText(/brand/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/model_params/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/metrics/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/examples/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/advantages/i).length).toBeGreaterThan(0);
    });
}); 