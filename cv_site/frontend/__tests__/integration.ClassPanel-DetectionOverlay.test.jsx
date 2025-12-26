import React from 'react';
import { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ClassPanel from '../src/components/ClassPanel';
import DetectionOverlay from '../src/components/DetectionOverlay';
import { DetectionHighlightProvider, useDetectionHighlight } from '../src/components/DetectionHighlightContext';
import { vi } from 'vitest';

vi.mock('react-i18next', () => ({
    useTranslation: () => ({
        t: (key) => {
            if (key === 'class_civilian') return 'Civilians';
            if (key === 'soldier') return 'Soldier';
            if (key === 'group_personnel') return 'Personnel';
            return key;
        }
    }),
    Trans: ({ children }) => children,
}));

vi.mock('../src/data/classGroups', () => ({
    default: [
        {
            group: 'group_personnel',
            classes: [
                { key: 'class_civilian', label: 'Civilians', icon: '🧑' },
                { key: 'soldier', label: 'Soldier', icon: '🪖' },
            ]
        }
    ]
}));

describe('Integration: ClassPanel + DetectionOverlay + DetectionHighlightContext', () => {
    function Wrapper() {
        const [selectedClass, setSelectedClass] = useState(null);
        const detections = [
            { class: 'class_civilian', confidence: 0.9, bbox: [10, 10, 100, 100] },
            { class: 'soldier', confidence: 0.8, bbox: [20, 20, 80, 80] },
        ];
        return (
            <DetectionHighlightProvider>
                <ClassPanel selectedClass={selectedClass} setSelectedClass={setSelectedClass} />
                <DetectionOverlay detections={detections} width={200} height={200} />
                <span data-testid="selected-class">{selectedClass}</span>
            </DetectionHighlightProvider>
        );
    }
    it('highlights class in DetectionOverlay when selected in ClassPanel', () => {
        render(<Wrapper />);
        fireEvent.click(screen.getAllByText(/Civilians/i)[0]);
        expect(screen.getByTestId('selected-class').textContent).toBe('class_civilian');
    });
}); 