import React, { useEffect, useState } from 'react';

export default function NotificationContainer({ notifications, onClose }) {
    const [visible, setVisible] = useState([]);

    useEffect(() => {
        setVisible(notifications.map(n => n.id));
    }, [notifications]);

    const handleClose = (id) => {
        setVisible((prev) => prev.filter(v => v !== id));
        setTimeout(() => onClose(id), 300); // Даем время на анимацию
    };

    return (
        <div style={{ position: 'fixed', top: 20, right: 20, zIndex: 9999, minWidth: 240 }}>
            {notifications.map((n) => (
                <div
                    key={n.id}
                    className={`notification-fade ${visible.includes(n.id) ? 'in' : 'out'}`}
                    style={{
                        marginBottom: 10,
                        padding: '12px 24px',
                        borderRadius: 8,
                        background: n.type === 'error' ? '#f87171' : n.type === 'success' ? '#4ade80' : '#60a5fa',
                        color: '#fff',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                        minWidth: 200,
                        fontWeight: 500,
                        fontSize: 16,
                        position: 'relative',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 12,
                        transition: 'all 0.3s',
                        opacity: visible.includes(n.id) ? 1 : 0,
                        transform: visible.includes(n.id) ? 'translateY(0)' : 'translateY(-20px)',
                    }}
                >
                    {/* Иконка по типу */}
                    <span style={{ fontSize: 22, display: 'flex', alignItems: 'center' }}>
                        {n.type === 'error' ? '⛔' : n.type === 'success' ? '✅' : 'ℹ️'}
                    </span>
                    <span style={{ flex: 1 }}>{n.message}</span>
                    {/* Кнопка закрытия */}
                    <button onClick={() => handleClose(n.id)} style={{
                        background: 'none',
                        border: 'none',
                        color: '#fff',
                        fontSize: 20,
                        cursor: 'pointer',
                        marginLeft: 8,
                        opacity: 0.7,
                        transition: 'opacity 0.2s',
                    }} aria-label="Close notification">×</button>
                </div>
            ))}
            <style>{`
                .notification-fade.in { opacity: 1; transform: translateY(0); transition: all 0.3s; }
                .notification-fade.out { opacity: 0; transform: translateY(-20px); transition: all 0.3s; }
            `}</style>
        </div>
    );
} 