import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DragDropBox from '../src/components/DragDropBox';
import { NotificationProvider } from '../src/components/NotificationContext';
import { vi } from 'vitest';
vi.mock('../src/icons/upload.svg?react', () => ({ default: () => <svg /> }), { virtual: true });
vi.mock('../src/icons/test.svg?react', () => ({ default: () => <svg /> }), { virtual: true });

const files = Array.from({ length: 6 }, (_, i) => new File([''], `file${i}.jpg`, { type: 'image/jpeg' }));

describe.skip('Integration: DragDropBox + NotificationContext', () => {
    it('shows notification on too many files', () => {
        render(
            <NotificationProvider>
                <DragDropBox
                    files={[]}
                    setFiles={vi.fn()}
                    results={[]}
                    setResults={vi.fn()}
                    loadings={[]}
                    setLoadings={vi.fn()}
                    progresses={[]}
                    setProgresses={vi.fn()}
                    selectedModel="small"
                    onUpload={vi.fn()}
                    handleDownloadJPG={vi.fn()}
                    handleDownloadJSON={vi.fn()}
                    selectedClass={null}
                    t={k => k}
                    inputRef={{ current: null }}
                    handleFileChange={vi.fn()}
                />
            </NotificationProvider>
        );
        const input = screen.getByLabelText(/drag_drop/i) || screen.getByTestId('file-input');
        fireEvent.change(input, { target: { files } });
        expect(screen.getByText(/maximum|максимум|больше 5/i)).toBeInTheDocument();
    });
}); 