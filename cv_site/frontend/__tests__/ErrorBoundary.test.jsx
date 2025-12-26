import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ErrorBoundary } from '../src/components/ErrorBoundary';

function ProblemChild() {
    throw new Error('Test error');
}

describe('ErrorBoundary', () => {
    it('shows fallback UI on error', () => {
        render(
            <ErrorBoundary>
                <ProblemChild />
            </ErrorBoundary>
        );
        expect(screen.getByText(/Что-то пошло не так/)).toBeInTheDocument();
        expect(screen.getByText(/Test error/)).toBeInTheDocument();
    });
});
