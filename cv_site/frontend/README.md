# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# Документация по ключевым компонентам

## NotificationContext и NotificationContainer

- **NotificationProvider** — оборачивает всё приложение, чтобы уведомления были доступны глобально.
- **useNotification()** — хук для вызова уведомлений из любого компонента:
  ```js
  const { addNotification } = useNotification();
  addNotification('Текст сообщения', 'error'); // типы: 'info', 'error', 'success'
  ```
- **NotificationContainer** — автоматически подключается внутри провайдера, отображает уведомления с анимацией и кнопкой закрытия.

## DragDropBox (мультизагрузка)
- Поддерживает загрузку до 5 файлов одновременно (drag&drop или через input).
- Для каждого файла отображается отдельный блок результата инференса.
- Можно удалить отдельный файл или очистить все файлы.
- При превышении лимита или ошибке файла появляется уведомление.
- Для интеграции используйте пропсы:
  ```js
  <DragDropBox
    files={files}
    setFiles={setFiles}
    results={results}
    setResults={setResults}
    loadings={loadings}
    setLoadings={setLoadings}
    progresses={progresses}
    setProgresses={setProgresses}
    ...
  />
  ```

---

## Прогресс-бар загрузки
- В текущей реализации реальный прогресс загрузки невозможен, так как используется fetch без поддержки onUploadProgress.
- Для поддержки реального прогресса используйте XMLHttpRequest или axios с onUploadProgress.

# Деплой и переменные окружения

## Переменные окружения (пример .env)
```
VITE_AUTH0_DOMAIN=your-auth0-domain
VITE_AUTH0_CLIENT_ID=your-auth0-client-id
VITE_AUTH0_AUDIENCE=your-auth0-audience (опционально)
```

## Сборка и запуск
```bash
npm install
npm run build
npm run preview # или npm run dev для разработки
```

## Production-рекомендации
- Используйте HTTPS.
- Настройте переменные окружения для production.
- Проверьте корректность CORS на backend.
- Для деплоя на Vercel/Netlify/Render — используйте стандартные инструкции для React/Vite.
- Для деплоя на собственный сервер — раздавайте dist/ как статику через nginx или другой сервер.

# Тесты

## Unit-тесты
- Рекомендуется использовать Jest + React Testing Library.
- Пример теста для NotificationContext и DragDropBox см. в папке __tests__ (создайте при необходимости).

## E2E-тесты
- Рекомендуется использовать Cypress или Playwright для тестирования пользовательских сценариев.
- Пример: загрузка файла, появление уведомления, отображение результата.

## Установка зависимостей (frontend)

```sh
cd frontend
npm install
```

> Для покрытия кода обязательно должен быть установлен пакет:
> 
>     @vitest/coverage-v8

Если он не установился автоматически, добавьте вручную:

```sh
npm install --save-dev @vitest/coverage-v8
```

## Запуск тестов и покрытия (frontend)

- Запуск всех тестов:
  ```sh
  npm test
  ```
- Запуск покрытия:
  ```sh
  npm run coverage
  ```
  После выполнения откройте `coverage/index.html` для просмотра отчёта.
