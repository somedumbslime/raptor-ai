import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { uploadImage } from '../src/api/inference';

describe('api/inference', () => {
    beforeEach(() => {
        global.fetch = vi.fn();
    });
    afterEach(() => {
        vi.resetAllMocks();
    });
    it('returns json on success', async () => {
        fetch.mockResolvedValue({ ok: true, json: async () => ({ filename: 'a.jpg' }) });
        const res = await uploadImage(new File([''], 'a.jpg', { type: 'image/jpeg' }), 'small');
        expect(res.filename).toBe('a.jpg');
    });
    it('throws error on failure', async () => {
        fetch.mockResolvedValue({ ok: false, text: async () => 'fail', status: 400 });
        await expect(uploadImage(new File([''], 'a.jpg', { type: 'image/jpeg' }), 'small')).rejects.toThrow('fail');
    });
}); 