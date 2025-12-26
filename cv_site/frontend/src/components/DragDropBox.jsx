import { UploadIcon, TestIcon } from '../icons/Icons';
import DetectionOverlay from './DetectionOverlay';
import DetectionList from './DetectionList';
import { DetectionHighlightProvider, useDetectionHighlight } from './DetectionHighlightContext';
import React from 'react';
import VideoDetectionOverlay from './VideoDetectionOverlay';
import { useTranslation } from 'react-i18next';
import { useNotification } from './NotificationContext';
import { MAX_FILES, MAX_FILE_SIZE } from '../constants';
import { API_URL } from '../api/inference';

export default function DragDropBox({
    files, setFiles, results, setResults, loadings, setLoadings, progresses, setProgresses, selectedModel, onUpload, handleDownloadJPG, handleDownloadJSON, handlePreviewJPG, selectedClass, t, inputRef, handleFileChange
}) {
    const acceptTypes = 'image/*,video/*';
    const { i18n } = useTranslation();
    const { addNotification } = useNotification();
    const [dragActive, setDragActive] = React.useState(false);

    // Проверка на максимальное количество файлов
    const handleFilesAdd = async (newFiles) => {
        if (files.length + newFiles.length > MAX_FILES) {
            addNotification(t('max_files_reached', { max: MAX_FILES }) || `Максимум ${MAX_FILES} файлов за раз`, 'error');
            return;
        }
        for (const { file, id } of newFiles) {
            if (file.type.startsWith('video')) {
                addNotification(t('video_stub'), 'error');
                continue;
            }
            // Автоматически запускаем инференс
            await onUpload(file, selectedModel, 0.5, 0.5, id);
        }
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setDragActive(false);
        const droppedFiles = Array.from(e.dataTransfer.files);
        if (!droppedFiles.length) return;
        if (files.length + droppedFiles.length > MAX_FILES) {
            addNotification(t('max_files_reached', { max: MAX_FILES }) || `Максимум ${MAX_FILES} файлов за раз`, 'error');
            return;
        }
        const validFiles = droppedFiles.filter(f => f.type.startsWith('image') || f.type.startsWith('video'));
        if (validFiles.length !== droppedFiles.length) {
            addNotification(t('unsupported_file_type'), 'error');
        }
        const maxSize = MAX_FILE_SIZE;
        const filtered = validFiles.filter(f => f.size <= maxSize);
        if (filtered.length !== validFiles.length) {
            addNotification(t('file_too_large'), 'error');
        }
        // Отклоняем видео-файлы
        const noVideo = filtered.filter(f => {
            if (f.type.startsWith('video')) {
                addNotification(t('video_stub'), 'error');
                return false;
            }
            return true;
        });
        const newFiles = noVideo.map(f => ({ file: f, id: Date.now() + Math.random() }));
        setFiles(prev => [...prev, ...newFiles]);
        await handleFilesAdd(newFiles);
    };

    const handleFileChangeWrapper = async (e) => {
        const selectedFiles = Array.from(e.target.files);
        if (!selectedFiles.length) return;
        if (files.length + selectedFiles.length > MAX_FILES) {
            addNotification(t('max_files_reached', { max: MAX_FILES }) || `Максимум ${MAX_FILES} файлов за раз`, 'error');
            return;
        }
        const validFiles = selectedFiles.filter(f => f.type.startsWith('image') || f.type.startsWith('video'));
        if (validFiles.length !== selectedFiles.length) {
            addNotification(t('unsupported_file_type'), 'error');
        }
        const maxSize = MAX_FILE_SIZE;
        const filtered = validFiles.filter(f => f.size <= maxSize);
        if (filtered.length !== validFiles.length) {
            addNotification(t('file_too_large'), 'error');
        }
        // Отклоняем видео-файлы
        const noVideo = filtered.filter(f => {
            if (f.type.startsWith('video')) {
                addNotification(t('video_stub'), 'error');
                return false;
            }
            return true;
        });
        const newFiles = noVideo.map(f => ({ file: f, id: Date.now() + Math.random() }));
        setFiles(prev => [...prev, ...newFiles]);
        await handleFilesAdd(newFiles);
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        setDragActive(true);
    };
    const handleDragLeave = (e) => {
        e.preventDefault();
        setDragActive(false);
    };

    const handleRemoveFile = (id) => {
        setFiles(prev => prev.filter(f => f.id !== id));
        setResults(prev => prev.filter(r => r.id !== id));
        setLoadings(prev => prev.filter(l => l.id !== id));
        setProgresses(prev => prev.filter(p => p.id !== id));
    };
    const handleClearAll = () => {
        setFiles([]); setResults([]); setLoadings([]); setProgresses([]);
    };

    return (
        <div className="flex flex-col items-center justify-center flex-1 w-full">
            <h3 className="text-2xl md:text-3xl font-bold text-grey-800 mb-6 text-center drop-shadow-lg flex items-center justify-center gap-3">
                <span className="inline-block align-middle"><TestIcon width={32} height={32} aria-label="Test" /></span>
                {t('test_model')}
            </h3>
            <input
                type="file"
                ref={inputRef}
                style={{ display: 'none' }}
                onChange={handleFileChangeWrapper}
                accept={acceptTypes}
                multiple
            />
            <div
                className={`group w-full max-w-3xl h-64 border-4 border-dashed rounded-2xl flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 shadow-xl relative overflow-hidden ${dragActive ? 'border-yellow-400 bg-yellow-800/30' : files.length ? 'border-green-400 bg-gray-800/60' : 'border-blue-400 hover:border-green-400 bg-gray-800/40'}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={() => inputRef.current && inputRef.current.click()}
                aria-label={t('drag_drop')}
            >
                <span className="flex flex-col items-center justify-center mb-2 animate-fade-in">
                    <span className="transition-transform duration-200 ease-out group-hover:scale-110">
                        <UploadIcon width={56} height={56} className="mb-2 text-blue-300 opacity-80" aria-label="Upload" />
                    </span>
                </span>
                <p className="text-lg opacity-80">
                    {t('drag_drop')}
                </p>
                {files.length > 0 && (
                    <button className="absolute top-2 right-2 px-3 py-1 bg-red-700 rounded text-white text-xs font-bold" onClick={e => { e.stopPropagation(); handleClearAll(); }}>{t('clear_all') || 'Очистить всё'}</button>
                )}
            </div>
            {/* Слайдеры и кнопка отправки */}
            {/*
            <div className="w-full max-w-3xl mt-6 flex flex-col gap-4 bg-gray-900/60 rounded-xl p-4 shadow-lg">
                <div className="flex flex-col md:flex-row gap-4 md:gap-8 items-center justify-center">
                    <label className="flex flex-col items-center flex-1">
                        <span className="mb-1 text-blue-200 font-medium">{t('confidence_threshold') || 'Поріг впевненості'}</span>
                        <div className="flex items-center gap-2 w-full">
                            <input type="range" min={0} max={1} step={0.01} value={confidence} onChange={e => setConfidence(Number(e.target.value))} className="w-full accent-blue-400" />
                            <span className="w-12 text-right tabular-nums">{confidence.toFixed(2)}</span>
                        </div>
                    </label>
                    <label className="flex flex-col items-center flex-1">
                        <span className="mb-1 text-blue-200 font-medium">{t('iou_threshold') || 'Поріг IoU'}</span>
                        <div className="flex items-center gap-2 w-full">
                            <input type="range" min={0} max={1} step={0.01} value={iou} onChange={e => setIoU(Number(e.target.value))} className="w-full accent-blue-400" />
                            <span className="w-12 text-right tabular-nums">{iou.toFixed(2)}</span>
                        </div>
                    </label>
                </div>
                <button
                    className="mt-2 px-6 py-2 rounded-lg bg-blue-700 hover:bg-blue-800 text-white font-semibold text-lg shadow-md transition disabled:opacity-50 disabled:cursor-not-allowed"
                    onClick={async () => { for (const { file, id } of files) await onUpload(file, id); }}
                    disabled={!files.length}
                >
                    {t('send') || 'Відправити'}
                </button>
            </div>
            */}
            {/* Предпросмотр файлов */}
            {files.length > 0 && (
                <div className="w-full max-w-3xl mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                    {files.map(({ file, id }) => {
                        const resObj = results.find(r => r.id === id);
                        const result = resObj?.result;
                        const isLoading = !!loadings.find(l => l.id === id);
                        const progressObj = progresses.find(p => p.id === id);
                        const progress = progressObj ? progressObj.progress : 0;
                        return (
                            <div key={id} className="bg-gray-800 rounded-xl shadow-2xl p-4 relative">
                                <button
                                    className="absolute top-4 right-4 z-10 px-2 py-1 bg-red-700 rounded-lg text-white text-base font-bold shadow-md hover:bg-red-800 transition-all"
                                    style={{ minWidth: 28, minHeight: 28 }}
                                    onClick={() => handleRemoveFile(id)}
                                >
                                    ×
                                </button>
                                <div className="mb-2 flex items-start" style={{ minHeight: 24, paddingRight: 32 }}>
                                    <div className="flex flex-col flex-1 min-w-0">
                                        <span className="font-semibold text-blue-200 break-all">{file.name}</span>
                                        <span className="text-xs text-gray-400 mt-0.5">({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
                                    </div>
                                </div>
                                {file.type.startsWith('image') && false && (
                                    <img src={URL.createObjectURL(file)} alt="preview" className="max-h-40 rounded mb-2 mx-auto" style={{ maxWidth: '100%' }} />
                                )}
                                {isLoading ? (
                                    <div className="w-full">
                                        <p className="text-lg mb-2">{t('loading')}</p>
                                        <div className="w-full h-4 bg-gray-700 rounded-full overflow-hidden shadow-inner">
                                            <div
                                                className="h-full bg-green-400 transition-all duration-200"
                                                style={{ width: `${progress}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                ) : result ? (
                                    <DetectionHighlightProvider>
                                        {result.error ? (
                                            <div className="text-red-400 font-bold">Ошибка: {result.error}</div>
                                        ) : (
                                            <>
                                                <h2 className="text-xl mb-2 font-semibold text-green-300">{t('result')}</h2>
                                                <div className="flex flex-col gap-4">
                                                    {file.type.includes('image') && result.filename && (
                                                        <div className="relative inline-block group">
                                                            <img
                                                                ref={el => { window.__lastImg = el; }}
                                                                src={`${API_URL}/outputs/${result.filename}`}
                                                                alt="Result"
                                                                className="max-w-xl rounded shadow-lg mx-auto"
                                                                style={{ display: 'block', maxWidth: '100%', height: 'auto' }}
                                                                onLoad={e => {
                                                                    const img = e.target;
                                                                    setResults(prev => prev.map(r =>
                                                                        r.id === id ? { ...r, imgDims: { width: img.naturalWidth, height: img.naturalHeight } } : r
                                                                    ));
                                                                }}
                                                            />
                                                            {resObj?.imgDims && (
                                                                <>
                                                                    <DetectionOverlay
                                                                        detections={result.detections}
                                                                        width={resObj.imgDims.width}
                                                                        height={resObj.imgDims.height}
                                                                    />
                                                                    {/* Затемнение при наведении */}
                                                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition pointer-events-none rounded" />
                                                                    {/* Кнопка Детальніше */}
                                                                    <button
                                                                        className="absolute top-2 right-2 z-20 px-3 py-1 bg-white/80 hover:bg-blue-600 hover:text-white text-blue-900 border border-blue-400 rounded-lg shadow-md font-semibold opacity-0 group-hover:opacity-100 transition pointer-events-auto backdrop-blur-sm backdrop-saturate-150 text-sm"
                                                                        onClick={e => { e.stopPropagation(); handlePreviewJPG(id); }}
                                                                        tabIndex={0}
                                                                        aria-label={t('details')}
                                                                        type="button"
                                                                    >
                                                                        {t('details')}
                                                                    </button>
                                                                </>
                                                            )}
                                                        </div>
                                                    )}
                                                    <div className="flex gap-4 mt-2">
                                                        <button onClick={() => handleDownloadJPG(id)} className="px-4 py-2 rounded bg-blue-700 hover:bg-blue-800 text-white font-semibold">JPG</button>
                                                        <button onClick={() => handleDownloadJSON(id)} className="px-4 py-2 rounded bg-green-700 hover:bg-green-800 text-white font-semibold">JSON</button>
                                                    </div>
                                                    <div>
                                                        <h4 className="text-lg font-bold mb-2 text-blue-200">{t('detections')}</h4>
                                                        <DetectionList detections={result.detections} />
                                                    </div>
                                                </div>
                                            </>
                                        )}
                                    </DetectionHighlightProvider>
                                ) : null}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
} 