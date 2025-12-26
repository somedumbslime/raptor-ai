import React from 'react';
import { useTranslation } from "react-i18next";
import MODELS from '../data/models';

export default function ModelSelector({ selectedModel, setSelectedModel }) {
    const { t } = useTranslation();
    return (
        <aside className="w-full md:w-64 min-w-0 flex flex-col md:gap-4 gap-2 h-full justify-center md:items-stretch items-center md:flex-col flex-row md:overflow-visible mt-6 md:mt-0">
            <h3 className="text-xl font-bold text-green-300 mb-2 text-center whitespace-nowrap md:whitespace-normal w-full md:w-auto flex-shrink-0">{t('model_panel_title')}</h3>
            {/* Сетка 2x2 на мобильных, flex-col на md+ */}
            <ul className="grid grid-cols-2 grid-rows-2 gap-2 w-full md:flex md:flex-col md:gap-2">
                {MODELS.map((model) => (
                    <li key={model.key} className="w-full">
                        <button
                            className={`w-full flex flex-col items-start px-3 py-2 rounded-lg border transition-colors ${selectedModel === model.key ? 'border-green-400 bg-green-900/60 text-white' : 'border-gray-700 bg-gray-800/80 text-green-100 hover:bg-green-800/60'}`}
                            onClick={() => setSelectedModel(model.key)}
                        >
                            <span className="font-semibold text-lg">{model.label}</span>
                            <span className="text-xs text-green-300">{t(model.desc)}</span>
                            <span className="text-xs text-blue-200 mt-1">{t('model_size')}: {model.size}</span>
                            <span className="text-xs text-blue-200">{t('model_speed')}: {model.speed}</span>
                        </button>
                    </li>
                ))}
            </ul>
        </aside>
    );
} 