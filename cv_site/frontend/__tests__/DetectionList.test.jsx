import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import DetectionList from '../src/components/DetectionList';
import { DetectionHighlightProvider } from '../src/components/DetectionHighlightContext';

describe('DetectionList', () => {
    const detections = [
        { class: 'person', confidence: 0.95, bbox: [10, 10, 100, 100] },
        { class: 'car', confidence: 0.8, bbox: [50, 50, 80, 80] },
        { class: 'person', confidence: 0.7, bbox: [20, 20, 50, 50] },
    ];

    it('groups detections by class and shows confidence', () => {
        render(
            <DetectionHighlightProvider>
                <DetectionList detections={detections} />
            </DetectionHighlightProvider>
        );
        expect(screen.getByText(/person/)).toBeInTheDocument();
        expect(screen.getByText(/car/)).toBeInTheDocument();
        expect(screen.getByText(/95.0%/)).toBeInTheDocument();
        expect(screen.getByText(/80.0%/)).toBeInTheDocument();
        expect(screen.getByText(/70.0%/)).toBeInTheDocument();
    });

    it('highlights class on hover (no crash)', () => {
        render(
            <DetectionHighlightProvider>
                <DetectionList detections={detections} />
            </DetectionHighlightProvider>
        );
        const personBlock = screen.getAllByText(/person/)[0].closest('div');
        fireEvent.mouseEnter(personBlock);
        fireEvent.mouseLeave(personBlock);
    });
});
