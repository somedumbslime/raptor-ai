import React from 'react';
import { render, screen } from '@testing-library/react';
import MainPage from '../src/pages/MainPage';
import { vi } from 'vitest';
vi.mock('../src/icons/upload.svg?react', () => ({ default: () => <svg /> }), { virtual: true });
vi.mock('../src/icons/test.svg?react', () => ({ default: () => <svg /> }), { virtual: true });
// Удалены локальные моки SVG

describe.skip('MainPage', () => {
    it('renders ClassPanel, DragDropBox, ModelSelector', () => {
        render(<MainPage files={[]} setFiles={() => { }} results={[]} setResults={() => { }} loadings={[]} setLoadings={() => { }} progresses={[]} setProgresses={() => { }} selectedClass={null} setSelectedClass={() => { }} selectedModel={null} setSelectedModel={() => { }} inputRef={{ current: null }} t={k => k} i18n={{}} uploadFile={() => { }} handleDownloadJPG={() => { }} handleDownloadJSON={() => { }} handlePreviewJPG={() => { }} />);
        expect(screen.getByText(/class_panel_title/i)).toBeInTheDocument();
        expect(screen.getByText(/drag_drop/i)).toBeInTheDocument();
        expect(screen.getByText(/model_panel_title/i)).toBeInTheDocument();
    });
}); 