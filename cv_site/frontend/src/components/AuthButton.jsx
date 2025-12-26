import React from 'react';
import { useTranslation } from "react-i18next";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from 'react-router-dom';

export default function AuthButton() {
    const { t } = useTranslation();
    const { isAuthenticated, user, loginWithRedirect, logout, isLoading, error } = useAuth0();
    const navigate = useNavigate();

    if (isLoading) return <span className="text-blue-300 px-4">{t('loading_auth')}</span>;
    if (error) return <span className="text-red-400 px-4">{t('auth_error', { error: error.message || String(error) })}</span>;

    return isAuthenticated ? (
        <div className="flex items-center gap-2 ml-4">
            <div className="flex items-center gap-2 cursor-pointer group" onClick={() => navigate('/profile')} title={t('profile_tooltip')}>
                {user?.picture && <img src={user.picture} alt="avatar" className="w-8 h-8 rounded-full border border-blue-400 group-hover:ring-2 group-hover:ring-blue-400 transition" />}
                <span className="text-blue-200 font-semibold text-sm group-hover:underline">{user?.name || user?.email}</span>
            </div>
            <button
                className="px-3 py-1 rounded-lg font-semibold bg-red-500 hover:bg-red-600 text-white ml-2"
                onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            >
                {t('logout')}
            </button>
        </div>
    ) : (
        <button
            className="px-4 py-2 rounded-lg font-semibold bg-blue-500 hover:bg-blue-600 text-white ml-4"
            onClick={() => loginWithRedirect()}
        >
            {t('login')}
        </button>
    );
} 