import React from 'react';
import { useState } from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import ModelSelector from '../src/components/ModelSelector';
import DragDropBox from '../src/components/DragDropBox';
import { vi } from 'vitest';
vi.mock('../src/icons/upload.svg?react', () => ({ default: () => <svg /> }), { virtual: true });
vi.mock('../src/icons/test.svg?react', () => ({ default: () => <svg /> }), { virtual: true });

// Удалены локальные моки SVG (если были)

describe.skip('Integration: ModelSelector + DragDropBox', () => {
    function Wrapper() {
        const [selectedModel, setSelectedModel] = useState('nano');
        return (
            <>
                <ModelSelector selectedModel={selectedModel} setSelectedModel={setSelectedModel} />
                <DragDropBox
                    files={[]}
                    setFiles={vi.fn()}
                    results={[]}
                    setResults={vi.fn()}
                    loadings={[]}
                    setLoadings={vi.fn()}
                    progresses={[]}
                    setProgresses={vi.fn()}
                    selectedModel={selectedModel}
                    onUpload={vi.fn()}
                    handleDownloadJPG={vi.fn()}
                    handleDownloadJSON={vi.fn()}
                    selectedClass={null}
                    t={k => k}
                    inputRef={{ current: null }}
                    handleFileChange={vi.fn()}
                />
                <span data-testid="model">{selectedModel}</span>
            </>
        );
    }
    it('changes selectedModel in DragDropBox when ModelSelector clicked', () => {
        render(<Wrapper />);
        fireEvent.click(screen.getAllByText('Small')[0]);
        expect(screen.getByTestId('model').textContent).toBe('small');
    });
}); 