import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ClassPanel from '../src/components/ClassPanel';
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

describe('ClassPanel', () => {
    it('renders class groups and classes', () => {
        render(<ClassPanel selectedClass={null} setSelectedClass={vi.fn()} />);
        expect(screen.getAllByText(/Personnel/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/Civilians/i).length).toBeGreaterThan(0);
        expect(screen.getAllByText(/Soldier/i).length).toBeGreaterThan(0);
    });
    it('calls setSelectedClass on click', () => {
        const setSelectedClass = vi.fn();
        render(<ClassPanel selectedClass={null} setSelectedClass={setSelectedClass} />);
        fireEvent.click(screen.getAllByText(/Civilians/i)[0]);
        expect(setSelectedClass).toHaveBeenCalled();
    });
}); 