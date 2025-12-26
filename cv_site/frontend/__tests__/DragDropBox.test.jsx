import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Мокаем Icons.js, чтобы SVG не резолвились
vi.mock('../src/icons/Icons', () => ({
    UploadIcon: () => <span>UploadIcon</span>,
    TestIcon: () => <span>TestIcon</span>
}));

import DragDropBox from '../src/components/DragDropBox';
import { NotificationProvider } from '../src/components/NotificationContext';

describe('DragDropBox', () => {
    it('renders drag area', () => {
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
        expect(screen.getByText('drag_drop')).toBeInTheDocument();
    });
});
