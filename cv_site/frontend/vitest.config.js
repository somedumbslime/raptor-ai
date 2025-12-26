import { defineConfig } from 'vitest/config';
import path from 'path';
import svgr from 'vite-plugin-svgr';

export default defineConfig({
    test: {
        environment: 'jsdom',
        globals: true,
        setupFiles: ['./setupTests.js'],
        plugins: [svgr()],
        alias: [
            { find: /\.svg$/, replacement: path.resolve(__dirname, '__mocks__/svgMock.js') },
            { find: /\.svg\?react$/, replacement: path.resolve(__dirname, '__mocks__/svgMock.js') }
        ],
        coverage: {
            provider: 'v8', // или 'istanbul', если хочешь другой формат
            reportsDirectory: './coverage',
            reporter: ['text', 'html'],
            reportOnFailure: true, // <--- ВАЖНО!
            clean: false
        }
    }
});
