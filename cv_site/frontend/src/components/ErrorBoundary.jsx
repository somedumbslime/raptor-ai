import React from 'react';

export class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.log('ErrorBoundary caught error:', error, errorInfo);
        // Можно логировать ошибку на сервер
        if (this.props.onError) this.props.onError(error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ color: 'red', padding: 32, textAlign: 'center' }}>
                    <h2>Что-то пошло не так.</h2>
                    <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{String(this.state.error)}</pre>
                </div>
            );
        }
        return this.props.children;
    }
} 