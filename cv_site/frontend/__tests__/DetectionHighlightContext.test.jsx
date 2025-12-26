import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { DetectionHighlightProvider, useDetectionHighlight } from '../src/components/DetectionHighlightContext';
import { act } from 'react';

describe('DetectionHighlightContext', () => {
    function TestComponent() {
        const { highlightClass, setHighlightClass, highlightIdx, setHighlightIdx } = useDetectionHighlight();
        return (
            <>
                <button onClick={() => setHighlightClass('person')}>SetClass</button>
                <button onClick={() => setHighlightIdx(2)}>SetIdx</button>
                <span data-testid="class">{highlightClass}</span>
                <span data-testid="idx">{highlightIdx}</span>
            </>
        );
    }
    it('provides and updates context values', async () => {
        render(
            <DetectionHighlightProvider>
                <TestComponent />
            </DetectionHighlightProvider>
        );
        expect(screen.getByTestId('class').textContent).toBe('');
        expect(screen.getByTestId('idx').textContent).toBe('');
        await act(async () => {
            screen.getByText('SetClass').click();
        });
        expect(screen.getByTestId('class').textContent).toBe('person');
        await act(async () => {
            screen.getByText('SetIdx').click();
        });
        await waitFor(() => {
            expect(screen.getByTestId('idx').textContent).toBe('2');
        });
    });
}); 