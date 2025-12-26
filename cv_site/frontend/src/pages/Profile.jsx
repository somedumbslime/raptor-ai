import React from 'react';
import { useAuth0, withAuthenticationRequired } from '@auth0/auth0-react';

function ProfileContent() {
    const { user, isAuthenticated, isLoading } = useAuth0();
    if (isLoading) return <div className="text-blue-300">Загрузка профиля...</div>;
    if (!isAuthenticated) return <div>Нет доступа</div>;
    return (
        <div className="max-w-md mx-auto bg-gray-800 rounded-xl shadow-lg p-6 mt-10 flex flex-col items-center">
            {user?.picture && <img src={user.picture} alt="avatar" className="w-24 h-24 rounded-full border-2 border-blue-400 mb-4" />}
            <div className="text-xl font-bold text-blue-200 mb-2">{user?.name || user?.email}</div>
            <div className="text-sm text-blue-100 mb-1">Email: {user?.email}</div>
            <div className="text-xs text-gray-400">ID: {user?.sub}</div>
        </div>
    );
}

export default withAuthenticationRequired(ProfileContent, {
    onRedirecting: () => <div className="text-blue-300">Перенаправление на страницу входа...</div>,
}); 