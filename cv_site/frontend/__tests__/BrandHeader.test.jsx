import React from 'react';
import { render, screen } from '@testing-library/react';
import BrandHeader from '../src/components/BrandHeader';

describe('BrandHeader', () => {
    it('renders brand and slogan', () => {
        render(<BrandHeader />);
        expect(screen.getByText(/brand/i)).toBeInTheDocument();
        expect(screen.getByText(/slogan/i)).toBeInTheDocument();
    });
}); 