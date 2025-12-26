import React from 'react';
import { useTranslation } from "react-i18next";
import CLASS_GROUPS from '../data/classGroups';

export default function ClassPanel({ selectedClass, setSelectedClass }) {
    const { t } = useTranslation();
    return (
        <aside className="w-full md:w-64 min-w-0 flex flex-col md:gap-4 gap-2 h-full justify-center md:items-stretch items-center md:flex-col flex-row md:overflow-visible mb-6 md:mb-0 z-10 md:z-auto">
            <h3 className="text-xl font-bold text-blue-300 mb-2 text-center whitespace-nowrap md:whitespace-normal w-full md:w-auto flex-shrink-0">
                {t('class_panel_title')}
            </h3>
            <div className="flex flex-col gap-4 w-full md:flex-col md:gap-4 md:overflow-visible md:justify-start md:pb-0">
                {CLASS_GROUPS.map((group) => (
                    <div key={group.group} className="w-full md:min-w-[140px] md:flex-shrink-0 md:bg-transparent md:rounded-none md:p-0">
                        <div className="text-blue-200 font-semibold mb-2 text-center md:text-left">{t(group.group)}</div>
                        <ul className={`grid gap-2 w-full
  ${group.classes.length === 1 ? 'grid-cols-1' : ''}
  ${group.classes.length === 2 ? 'grid-cols-2' : ''}
  ${group.classes.length === 3 ? 'grid-cols-3' : ''}
  ${group.classes.length >= 4 ? 'grid-cols-4' : ''}
  md:flex md:flex-row md:flex-wrap md:justify-start`}
                        >
                            {group.classes.map((cls, idx) => {
                                // Определяем позицию тултипа
                                let tooltipPosition = 'left-1/2 -translate-x-1/2';
                                if (group.classes.length > 1) {
                                    if (idx === 0) tooltipPosition = 'left-0 translate-x-0'; // слева
                                    else if (idx === group.classes.length - 1) tooltipPosition = 'right-0 translate-x-0'; // справа
                                }
                                return (
                                    <li key={cls.key} className="relative group">
                                        <button
                                            className={`flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors
  bg-gray-700/80 hover:bg-blue-800 text-blue-100
  md:bg-transparent md:hover:bg-blue-700/40 md:text-blue-200 md:border md:border-blue-300 md:hover:text-white md:hover:border-blue-400 md:focus-visible:bg-blue-700/40 md:focus-visible:text-white md:focus-visible:border-blue-400
  w-full md:w-auto ${selectedClass === cls.key ? 'bg-blue-600 text-white' : ''}`}
                                            onClick={() => setSelectedClass(selectedClass === cls.key ? null : cls.key)}
                                            tabIndex={0}
                                            aria-describedby={cls.key + '-hint'}
                                            style={{ pointerEvents: 'auto' }}
                                        >
                                            <span>{cls.icon}</span> {t(cls.key) || cls.label}
                                        </button>
                                        {/* Tooltip: адаптивная ширина, позиция зависит от кнопки */}
                                        <div
                                            id={cls.key + '-hint'}
                                            className={`absolute mt-2 z-50 p-3 rounded-xl bg-gray-900/80 text-white text-sm shadow-xl border border-blue-700 opacity-0 group-hover:opacity-100 group-focus-within:opacity-100 pointer-events-none transition-all duration-200 w-max max-w-xs md:max-w-sm whitespace-pre-line break-words ${tooltipPosition} md:w-64 md:left-0 md:translate-x-0 md:max-w-[320px]`}
                                            style={{ minWidth: 120 }}
                                        >
                                            {t(cls.key + '_hint')}
                                        </div>
                                    </li>
                                );
                            })}
                        </ul>
                    </div>
                ))}
            </div>
        </aside>
    );
} 