import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import JPGPreviewModal from '../src/components/JPGPreviewModal';
import { vi } from 'vitest';

const results = [
    {
        id: 1,
        result: {
            filename: 'test.jpg',
            detections: [
                { class: 'person', confidence: 0.9, bbox: [10, 10, 100, 100] },
            ],
        },
        imgDims: { width: 200, height: 200 },
    },
];

describe('JPGPreviewModal', () => {
    it('renders image, overlay and detections', () => {
        render(
            <JPGPreviewModal id={1} results={results} onClose={vi.fn()} />
        );
        expect(screen.getByAltText('Result')).toBeInTheDocument();
        expect(screen.getByText(/detections/i)).toBeInTheDocument();
        expect(screen.getAllByText(/person/i).length).toBeGreaterThan(0);
    });

    it('calls onClose when close button clicked', () => {
        const onClose = vi.fn();
        render(
            <JPGPreviewModal id={1} results={results} onClose={onClose} />
        );
        fireEvent.click(screen.getAllByRole('button')[0]);
        expect(onClose).toHaveBeenCalled();
    });

    it('returns null if no result', () => {
        const { container } = render(
            <JPGPreviewModal id={999} results={results} onClose={vi.fn()} />
        );
        expect(container.firstChild).toBeNull();
    });
}); 