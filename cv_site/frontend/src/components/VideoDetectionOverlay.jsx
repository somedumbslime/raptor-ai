import React, { useRef, useEffect, useState } from 'react';

/**
 * Overlay для отображения bbox-ов поверх видео по кадрам
 * @param {Object} props
 * @param {string} src - путь к видео
 * @param {Array} detections - массив bbox-ов по кадрам [{frame, detections: [{class, confidence, bbox}]}]
 * @param {number} width - ширина видео
 * @param {number} height - высота видео
 */
export default function VideoDetectionOverlay({ src, detections, width = 640, height = 360 }) {
    const videoRef = useRef();
    const [currentFrame, setCurrentFrame] = useState(0);
    const [videoDims, setVideoDims] = useState({ width, height });

    // Синхронизация текущего кадра
    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;
        const onTimeUpdate = () => {
            const frame = Math.floor(video.currentTime * (video.fps || 25));
            setCurrentFrame(frame);
        };
        video.addEventListener('timeupdate', onTimeUpdate);
        return () => video.removeEventListener('timeupdate', onTimeUpdate);
    }, []);

    // Получаем bbox-ы для текущего кадра
    const frameDetections = detections?.find(f => f.frame === currentFrame)?.detections || [];

    // Обновляем размеры видео
    const onLoadedMetadata = (e) => {
        setVideoDims({ width: e.target.videoWidth, height: e.target.videoHeight });
    };

    return (
        <div style={{ position: 'relative', display: 'inline-block', width: videoDims.width, height: videoDims.height }}>
            <video
                ref={videoRef}
                src={src}
                width={videoDims.width}
                height={videoDims.height}
                controls
                onLoadedMetadata={onLoadedMetadata}
                style={{ display: 'block', borderRadius: 8 }}
                data-testid="video-element"
            />
            <svg
                width={videoDims.width}
                height={videoDims.height}
                style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
            >
                {frameDetections.map((det, idx) => (
                    <g key={idx}>
                        <rect
                            x={det.bbox[0]}
                            y={det.bbox[1]}
                            width={det.bbox[2]}
                            height={det.bbox[3]}
                            fill="none"
                            stroke="#00FF00"
                            strokeWidth={2}
                        />
                        <text
                            x={det.bbox[0] + 4}
                            y={det.bbox[1] + 18}
                            fill="#00FF00"
                            fontSize={18}
                            fontWeight="bold"
                            stroke="#222"
                            strokeWidth={0.5}
                        >
                            {det.class} ({(det.confidence * 100).toFixed(1)}%)
                        </text>
                    </g>
                ))}
            </svg>
        </div>
    );
} 