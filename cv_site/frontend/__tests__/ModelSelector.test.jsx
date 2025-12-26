import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ModelSelector from '../src/components/ModelSelector';
import { vi } from 'vitest';

vi.mock('../src/data/models', () => ({
    default: [
        { key: 'nano', label: 'Nano', desc: 'desc_nano', size: '3MB', speed: '50ms' },
        { key: 'small', label: 'Small', desc: 'desc_small', size: '8MB', speed: '80ms' },
    ]
}));

describe('ModelSelector', () => {
    it('renders all models', () => {
        render(<ModelSelector selectedModel={null} setSelectedModel={vi.fn()} />);
        expect(screen.getAllByText('Nano').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Small').length).toBeGreaterThan(0);
    });

    it('calls setSelectedModel on click', () => {
        const setSelectedModel = vi.fn();
        render(<ModelSelector selectedModel={null} setSelectedModel={setSelectedModel} />);
        fireEvent.click(screen.getAllByText('Nano')[0]);
        expect(setSelectedModel).toHaveBeenCalledWith('nano');
    });
}); 