import React from 'react';
import { render, screen } from '@testing-library/react';
import VideoDetectionOverlay from '../src/components/VideoDetectionOverlay';

describe('VideoDetectionOverlay', () => {
    const detections = [
        {
            frame: 0, detections: [
                { class: 'person', confidence: 0.9, bbox: [10, 10, 100, 100] },
            ]
        },
    ];
    it('renders video and overlay', () => {
        render(<VideoDetectionOverlay src="test.mp4" detections={detections} width={320} height={240} />);
        expect(screen.getByTestId('video-element')).toBeDefined();
    });
    it('renders detection class and confidence', () => {
        render(<VideoDetectionOverlay src="test.mp4" detections={detections} width={320} height={240} />);
        expect(screen.getByText(/person/i)).toBeInTheDocument();
        expect(screen.getByText(/90.0%/)).toBeInTheDocument();
    });
}); 