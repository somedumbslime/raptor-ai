import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NotificationProvider, useNotification } from '../src/components/NotificationContext';

function TestComponent() {
    const { addNotification } = useNotification();
    return <button onClick={() => addNotification('Test message', 'success', 100)}>Show</button>;
}

describe('NotificationContext', () => {
    it('shows and hides notification', () => {
        vi.useFakeTimers();
        render(
            <NotificationProvider>
                <TestComponent />
            </NotificationProvider>
        );
        act(() => {
            screen.getByText('Show').click();
        });
        expect(screen.getByText('Test message')).toBeInTheDocument();
        act(() => {
            vi.advanceTimersByTime(100);
        });
        expect(screen.queryByText('Test message')).not.toBeInTheDocument();
        vi.useRealTimers();
    });
}); 