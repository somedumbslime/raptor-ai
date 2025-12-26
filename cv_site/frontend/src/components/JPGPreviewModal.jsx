import React from 'react';
import ReactDOM from 'react-dom';
import DetectionOverlay from './DetectionOverlay';
import DetectionList from './DetectionList';
import { API_URL } from '../api/inference';
import { DetectionHighlightProvider } from './DetectionHighlightContext';
import { useTranslation } from 'react-i18next';

export default function JPGPreviewModal({ id, results, onClose }) {
    const { t } = useTranslation();
    console.log('JPGPreviewModal render', { id, results, onClose });
    const resObj = results.find(r => r.id === id);
    const result = resObj?.result;
    const imgDims = resObj?.imgDims;
    if (!result || !result.filename) return null;

    // Масштабирование: изображение максимально по высоте окна, но не шире 60vw (чтобы справа был блок)
    // Детекции только для этого изображения
    return ReactDOM.createPortal(
        <DetectionHighlightProvider>
            <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-80 animate-fade-in">
                <div className="relative bg-gray-900 rounded-2xl md:rounded-3xl shadow-2xl flex flex-col md:flex-row w-full max-w-full md:max-w-6xl mx-0 md:mx-4 max-h-full md:max-h-[90vh] border border-blue-700/30">
                    {/* Кнопка закрытия */}
                    <button onClick={onClose} className="absolute top-2 right-2 md:top-4 md:right-4 z-10 px-3 py-2 md:px-2 md:py-1 bg-red-700 rounded-lg text-white text-xl md:text-base font-bold shadow-md hover:bg-red-800 transition-all" style={{ minWidth: 36, minHeight: 36 }}>
                        ×
                    </button>
                    {/* Изображение с overlay */}
                    <div className="flex-1 flex items-center justify-center p-2 md:p-6 min-w-0">
                        <div style={{ position: 'relative', width: '100%', height: '100%' }}>
                            <img
                                src={`${API_URL}/outputs/${result.filename}`}
                                alt="Result"
                                className="block max-h-[40vh] md:max-h-[80vh] w-full md:max-w-[60vw] rounded shadow-lg mx-auto"
                                style={{ objectFit: 'contain', width: '100%', height: 'auto', background: '#222' }}
                            />
                            {imgDims && (
                                <DetectionOverlay
                                    detections={result.detections}
                                    width={imgDims.width}
                                    height={imgDims.height}
                                />
                            )}
                        </div>
                    </div>
                    {/* Блок детекций */}
                    <div className="w-full md:w-80 max-w-full md:max-w-xs bg-gray-800/90 border-t md:border-t-0 md:border-l border-gray-700 p-4 md:p-6 overflow-y-auto flex flex-col rounded-b-2xl md:rounded-b-none md:rounded-r-3xl">
                        <h3 className="text-lg md:text-xl font-bold text-green-300 mb-3 md:mb-4">{t('detections')}</h3>
                        <DetectionList detections={result.detections} />
                    </div>
                </div>
            </div>
        </DetectionHighlightProvider>,
        document.body
    );
} 