import React from 'react';
import { useTranslation } from "react-i18next";

export default function BrandHeader() {
    const { t } = useTranslation();
    return (
        <div className="w-full max-w-5xl mx-auto mb-8 mt-0">
            <h2 className="text-5xl md:text-6xl font-extrabold text-white mb-1 leading-tight drop-shadow-lg tracking-wide text-center">
                {t('brand')}
            </h2>
            <div className="text-center text-base md:text-lg text-blue-200 mb-2 tracking-widest uppercase font-medium" style={{ letterSpacing: '0.12em' }}>
                {t('slogan')}
            </div>
        </div>
    );
} 