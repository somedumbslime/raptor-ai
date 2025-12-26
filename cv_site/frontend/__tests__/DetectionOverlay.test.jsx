import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import DetectionOverlay from '../src/components/DetectionOverlay';
import { DetectionHighlightProvider } from '../src/components/DetectionHighlightContext';

describe('DetectionOverlay', () => {
    it('does not render svg if no detections', () => {
        const { container } = render(
            <DetectionHighlightProvider>
                <DetectionOverlay detections={[]} width={100} height={100} />
            </DetectionHighlightProvider>
        );
        expect(container.querySelector('svg')).toBeNull();
    });

    it('renders detection classes and confidences', () => {
        const detections = [
            { class: 'person', confidence: 0.95, bbox: [10, 10, 100, 100] },
            { class: 'car', confidence: 0.8, bbox: [50, 50, 80, 80] },
        ];
        render(
            <DetectionHighlightProvider>
                <DetectionOverlay detections={detections} width={200} height={200} />
            </DetectionHighlightProvider>
        );
        expect(screen.getByText(/person/)).toBeInTheDocument();
        expect(screen.getByText(/car/)).toBeInTheDocument();
        expect(screen.getByText(/95.0%/)).toBeInTheDocument();
        expect(screen.getByText(/80.0%/)).toBeInTheDocument();
    });
});
