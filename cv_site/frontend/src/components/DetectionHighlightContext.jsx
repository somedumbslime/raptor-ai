import React, { createContext, useContext, useState } from 'react';

const DetectionHighlightContext = createContext();

export function DetectionHighlightProvider({ children }) {
    const [highlightClass, setHighlightClass] = useState(null);
    const [highlightIdx, setHighlightIdx] = useState(null);

    const value = {
        highlightClass,
        setHighlightClass,
        highlightIdx,
        setHighlightIdx,
    };
    return (
        <DetectionHighlightContext.Provider value={value}>
            {children}
        </DetectionHighlightContext.Provider>
    );
}

export function useDetectionHighlight() {
    return useContext(DetectionHighlightContext);
} 