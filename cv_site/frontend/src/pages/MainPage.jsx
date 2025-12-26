import ClassPanel from '../components/ClassPanel';
import ModelSelector from '../components/ModelSelector';
import DragDropBox from '../components/DragDropBox';
import { useState } from 'react';

export default function MainPage({ files, setFiles, results, setResults, loadings, setLoadings, progresses, setProgresses, selectedClass, setSelectedClass, selectedModel, setSelectedModel, inputRef, t, i18n, uploadFile, handleDownloadJPG, handleDownloadJSON, handlePreviewJPG }) {
    return (
        <div className="flex flex-col md:flex-row w-full flex-1 h-full items-stretch">
            {/* Левая панель */}
            <div className="w-full md:w-64 flex-shrink-0 flex flex-col justify-center items-start h-full mt-0 md:mt-[-60px] md:overflow-visible">
                <ClassPanel selectedClass={selectedClass} setSelectedClass={setSelectedClass} />
            </div>
            {/* Центр */}
            <main className="flex-1 flex flex-col items-center justify-center px-2 md:px-4 h-full w-full">
                <DragDropBox
                    files={files}
                    setFiles={setFiles}
                    results={results}
                    setResults={setResults}
                    loadings={loadings}
                    setLoadings={setLoadings}
                    progresses={progresses}
                    setProgresses={setProgresses}
                    selectedModel={selectedModel}
                    onUpload={uploadFile}
                    handleDownloadJPG={handleDownloadJPG}
                    handleDownloadJSON={handleDownloadJSON}
                    handlePreviewJPG={handlePreviewJPG}
                    selectedClass={selectedClass}
                    t={t}
                    inputRef={inputRef}
                />
            </main>
            {/* Правая панель */}
            <div className="w-full md:w-64 flex-shrink-0 flex flex-col justify-center items-end h-full mt-0 md:mt-[-60px] md:overflow-visible">
                <ModelSelector selectedModel={selectedModel} setSelectedModel={setSelectedModel} />
            </div>
        </div>
    );
} 