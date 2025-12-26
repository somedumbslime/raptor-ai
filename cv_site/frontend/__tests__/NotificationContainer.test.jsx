import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import NotificationContainer from '../src/components/NotificationContainer';
import { vi } from 'vitest';

describe('NotificationContainer', () => {
    const notifications = [
        { id: 1, message: 'Test info', type: 'info' },
        { id: 2, message: 'Test error', type: 'error' },
        { id: 3, message: 'Test success', type: 'success' },
    ];
    it('renders all notifications', () => {
        render(<NotificationContainer notifications={notifications} onClose={vi.fn()} />);
        expect(screen.getByText('Test info')).toBeInTheDocument();
        expect(screen.getByText('Test error')).toBeInTheDocument();
        expect(screen.getByText('Test success')).toBeInTheDocument();
    });
    it('calls onClose when close button clicked', () => {
        vi.useFakeTimers();
        const onClose = vi.fn();
        render(<NotificationContainer notifications={notifications} onClose={onClose} />);
        const closeButtons = screen.getAllByRole('button', { name: /close notification/i });
        closeButtons.forEach(btn => fireEvent.click(btn));
        vi.runAllTimers();
        expect(onClose).toHaveBeenCalledTimes(notifications.length);
        vi.useRealTimers();
    });
}); 