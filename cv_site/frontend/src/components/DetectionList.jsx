import React, { useRef } from 'react';
import CLASS_GROUPS from '../data/classGroups';
import { useTranslation } from 'react-i18next';
import { useDetectionHighlight } from './DetectionHighlightContext';

function groupDetectionsByClass(detections) {
    const grouped = {};
    detections.forEach((det, idx) => {
        if (!grouped[det.class]) grouped[det.class] = [];
        grouped[det.class].push({ ...det, idx });
    });
    return grouped;
}

export default function DetectionList({ detections = [] }) {
    const { t } = useTranslation();
    const { highlightClass, setHighlightClass, highlightIdx, setHighlightIdx } = useDetectionHighlight();
    const grouped = groupDetectionsByClass(detections);

    // Получаем метаданные классов (иконка, label)
    const classMeta = {};
    CLASS_GROUPS.forEach(group => {
        group.classes.forEach(cls => {
            classMeta[cls.key] = cls;
        });
    });

    return (
        <div className="flex flex-col gap-3">
            {Object.entries(grouped).map(([cls, dets]) => {
                const classBlockRef = useRef();
                return (
                    <div
                        key={cls}
                        ref={classBlockRef}
                        className={`rounded-lg border transition-colors px-3 py-2 mb-1 ${highlightClass === cls ? 'border-yellow-400 bg-yellow-900/30' : 'border-gray-700 bg-gray-800/80 hover:bg-yellow-800/20'}`}
                        onMouseEnter={() => { setHighlightClass(cls); setHighlightIdx(null); }}
                        onMouseLeave={() => { setHighlightClass(null); setHighlightIdx(null); }}
                    >
                        <div className="flex items-center gap-2 mb-1">
                            <span className="text-xl">{classMeta[cls]?.icon}</span>
                            <span className="font-semibold text-lg">{t(cls) || classMeta[cls]?.label || cls}</span>
                            <span className="ml-auto text-xs text-yellow-300 bg-yellow-900/40 rounded px-2 py-0.5">{dets.length} шт.</span>
                        </div>
                        <div className="flex flex-wrap gap-2 mt-1">
                            {dets.map((det) => (
                                <button
                                    key={det.idx}
                                    className={`px-2 py-1 rounded text-xs font-mono border transition-colors ${highlightIdx === det.idx ? 'border-orange-400 bg-orange-900/60 text-white' : 'border-gray-600 bg-gray-900/60 text-yellow-100 hover:bg-orange-800/40'}`}
                                    onMouseEnter={() => { setHighlightClass(null); setHighlightIdx(det.idx); }}
                                    onMouseLeave={e => {
                                        setHighlightIdx(null);
                                        // Если курсор всё ещё внутри блока класса — снова активируем highlightClass
                                        if (classBlockRef.current && classBlockRef.current.contains(e.relatedTarget)) {
                                            setHighlightClass(cls);
                                        }
                                    }}
                                >
                                    {det.confidence ? `${(det.confidence * 100).toFixed(1)}%` : '?'}
                                </button>
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
    );
} 