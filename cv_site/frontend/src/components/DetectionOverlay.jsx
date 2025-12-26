import React, { useRef, useLayoutEffect, useState } from 'react';
import { useDetectionHighlight } from './DetectionHighlightContext';

export default function DetectionOverlay({ detections, width, height, strokeWidth = 2, fontSize = 28, highlightClass, highlightIdx }) {
    const overlayRef = useRef(null);
    const [scale, setScale] = useState({ x: 1, y: 1 });
    const ctx = useDetectionHighlight ? useDetectionHighlight() : {};
    const _highlightClass = highlightClass !== undefined ? highlightClass : ctx.highlightClass;
    const _highlightIdx = highlightIdx !== undefined ? highlightIdx : ctx.highlightIdx;

    useLayoutEffect(() => {
        if (overlayRef.current) {
            const rect = overlayRef.current.getBoundingClientRect();
            setScale({
                x: rect.width / width,
                y: rect.height / height,
            });
        }
    }, [width, height]);

    if (!detections || detections.length === 0) return null;
    return (
        <svg
            ref={overlayRef}
            width="100%"
            height="100%"
            viewBox={`0 0 ${width} ${height}`}
            style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none', zIndex: 2, width: '100%', height: '100%' }}
        >
            {detections.map((det, idx) => {
                const [x, y, w, h] = det.bbox;
                return (
                    <g key={idx}>
                        <rect
                            x={x}
                            y={y}
                            width={w}
                            height={h}
                            fill="none"
                            stroke={_highlightIdx === idx ? '#67e8f9' : _highlightClass && det.class === _highlightClass ? '#22d3ee' : '#4ade80'}
                            rx={4}
                            style={{ strokeWidth: _highlightIdx === idx ? 3 : _highlightClass && det.class === _highlightClass ? 2.5 : strokeWidth, vectorEffect: 'non-scaling-stroke' }}
                        />
                        {(() => {
                            const fontSize = Math.max(10, Math.min(28, Math.round(h * 0.18)));
                            const yText = y - fontSize >= 0 ? y - 4 : y + fontSize;
                            return (
                                <text
                                    x={x + 4}
                                    y={y - fontSize >= 0 ? y - 4 : y + fontSize}
                                    fontWeight="bold"
                                    fill="#4ade80"
                                    stroke="#222"
                                    paintOrder="stroke"
                                    style={{ fontSize, strokeWidth: 0.5, vectorEffect: 'non-scaling-stroke' }}
                                >
                                    {det.class} ({(det.confidence * 100).toFixed(1)}%)
                                </text>
                            );
                        })()}
                    </g>
                );
            })}
        </svg>
    );
} 