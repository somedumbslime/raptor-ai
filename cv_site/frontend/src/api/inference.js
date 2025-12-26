export const API_URL = "https://192.168.1.100:5173";

function handleApiError(res) {
    return res.text().then(text => {
        const error = new Error(text || res.statusText);
        error.status = res.status;
        throw error;
    });
}

export async function uploadImage(file, model, confidence, iou) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", model);
    if (confidence !== undefined) formData.append("confidence", confidence);
    if (iou !== undefined) formData.append("iou", iou);
    const res = await fetch(`${API_URL}/infer-image`, {
        method: "POST",
        body: formData,
    });
    if (!res.ok) await handleApiError(res);
    return await res.json();
}

/**
 * Отправка видео на инференс
 * @param {File} file - видеофайл
 * @param {string} model - название модели
 * @param {string} token - JWT токен
 * @returns {Promise<{filename: string, detections: Array<{frame: number, detections: Array<{class: string, confidence: number, bbox: [number, number, number, number]}>}>}>}
 */
export async function uploadVideo(file, model, token, confidence, iou) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", model);
    if (confidence !== undefined) formData.append("confidence", confidence);
    if (iou !== undefined) formData.append("iou", iou);
    const headers = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${API_URL}/infer-video`, {
        method: "POST",
        body: formData,
        headers,
    });
    if (!res.ok) await handleApiError(res);
    return await res.json();
} 