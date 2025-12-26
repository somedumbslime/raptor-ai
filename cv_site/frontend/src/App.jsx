import { useState, useRef, useEffect } from "react";
import { Routes, Route, Link, NavLink } from "react-router-dom";
import { useTranslation, Trans } from "react-i18next";
import raw1 from './photos/raw_1.jpg';
import detected1 from './photos/detected_1.jpg';
import raw2 from './photos/raw_2.jpg';
import detected2 from './photos/detected_2.jpg';
import UploadIcon from './icons/upload.svg?react';
import TestIcon from './icons/test.svg?react';
import ClassPanel from './components/ClassPanel';
import ModelSelector from './components/ModelSelector';
import AuthButton from './components/AuthButton';
import DragDropBox from './components/DragDropBox';
import ModelPage from './pages/ModelPage';
import AboutPage from './pages/AboutPage';
import BrandHeader from './components/BrandHeader';
import CLASS_GROUPS from './data/classGroups';
import MainPage from './pages/MainPage';
import { uploadImage, uploadVideo } from './api/inference';
import Profile from './pages/Profile';
import { useAuth0 } from '@auth0/auth0-react';
import { NotificationProvider } from './components/NotificationContext';
import JPGPreviewModal from './components/JPGPreviewModal';
import UAFlag from './icons/flags/ua.svg?react';
import GBFlag from './icons/flags/gb.svg?react';
import RAPTORLogo from './icons/RAPTOR_logo.svg?react';
import RAPTORBg from './icons/RAPTOR_bg.svg?react';

function App() {
  console.log('App mounted');
  const [files, setFiles] = useState([]); // [{file, id}]
  const [results, setResults] = useState([]); // [{result, id}]
  const [loadings, setLoadings] = useState([]); // [{loading, id}]
  const [progresses, setProgresses] = useState([]); // [{progress, id}]
  const [selectedClass, setSelectedClass] = useState(null);
  const [selectedModel, setSelectedModel] = useState('small');
  const progressRef = useRef();
  const { t, i18n } = useTranslation();
  const inputRef = useRef();
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [langMenuOpen, setLangMenuOpen] = useState(false);
  const [jpgPreviewId, setJpgPreviewId] = useState(null);
  const globeBtnRef = useRef(null);
  const langMenuRef = useRef(null);

  useEffect(() => {
    console.log('App useEffect []');
    if (!i18n.language || (i18n.language !== 'ua' && i18n.language !== 'en')) {
      i18n.changeLanguage('ua');
    }
  }, [i18n]);

  useEffect(() => {
    if (!langMenuOpen) return;
    function handleClickOutside(e) {
      if (
        langMenuRef.current &&
        !langMenuRef.current.contains(e.target) &&
        globeBtnRef.current &&
        !globeBtnRef.current.contains(e.target)
      ) {
        setLangMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [langMenuOpen]);

  // Анимация прогресса (фейковая)
  const startProgress = () => {
    setProgresses(prev => prev.map(p => ({ ...p, progress: 0 })));
    progressRef.current = setInterval(() => {
      setProgresses(prev => prev.map(p => ({
        ...p,
        progress: Math.min(95, p.progress + Math.random() * 3)
      })));
    }, 100);
  };
  const stopProgress = () => {
    clearInterval(progressRef.current);
    setProgresses(prev => prev.map(p => ({ ...p, progress: 100 })));
    setTimeout(() => setProgresses(prev => prev.map(p => ({ ...p, progress: 0 }))), 800);
  };

  // Drag&Drop и upload
  const API_URL = "http://127.0.0.1:8000";
  const uploadFile = async (selectedFile, model, confidence, iou, id) => {
    setLoadings(prev => [...prev, { loading: true, id }]);
    setResults(prev => prev.filter(r => r.id !== id));
    setProgresses(prev => [...prev, { progress: 0, id }]);
    try {
      let data;
      if (selectedFile.type.startsWith('video')) {
        let token = null;
        if (isAuthenticated) {
          token = await getAccessTokenSilently();
        }
        data = await uploadVideo(selectedFile, model, token, confidence, iou);
      } else {
        data = await uploadImage(selectedFile, model, confidence, iou);
      }
      setResults(prev => [...prev, { result: data, id }]);
    } catch (e) {
      setResults(prev => [...prev, { result: { error: e.message }, id }]);
    }
    setLoadings(prev => prev.filter(l => l.id !== id));
    setProgresses(prev => prev.filter(p => p.id !== id));
  };

  // Скачивание JSON (заглушка)
  const handleDownloadJSON = (id) => {
    const res = results.find(r => r.id === id)?.result;
    if (!res) return;
    const blob = new Blob([JSON.stringify(res, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = (res.filename || 'result') + '.json';
    a.click();
    URL.revokeObjectURL(url);
  };
  // Скачивание JPG (заглушка)
  const handleDownloadJPG = (id) => {
    const res = results.find(r => r.id === id)?.result;
    if (!res || !res.filename) return;
    // Скачивание файла в оригинальном разрешении
    const link = document.createElement('a');
    link.href = `${API_URL}/outputs/${res.filename}`;
    link.download = res.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  const handlePreviewJPG = (id) => {
    console.log('handlePreviewJPG called with id:', id);
    setJpgPreviewId(prev => { console.log('setJpgPreviewId called, prev:', prev, 'new:', id); return id; });
  };

  return (
    <NotificationProvider>
      <div className="min-h-screen w-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-700 text-white p-6 flex flex-col flex-1 h-full">
        {/* Навигация и авторизация */}
        <nav className="w-full flex items-center justify-between mb-10 mt-2 relative">
          {/* Мобильный хедер */}
          <div className="flex md:hidden w-full items-center justify-between">
            <button className="p-2" style={{ background: 'none' }} onClick={() => setMobileMenuOpen(v => !v)} aria-label="Открыть меню">
              <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
            </button>
            {/* центр пустой, логотип ниже */}
            <div className="flex-1 flex justify-center"></div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <button className="p-2" style={{ background: 'none' }} onClick={() => setLangMenuOpen(v => !v)} aria-label="Выбрать язык" aria-haspopup="true" aria-expanded={langMenuOpen}>
                  🌐
                </button>
                {langMenuOpen && (
                  <div className="absolute right-0 mt-2 z-50 min-w-[100px] animate-fade-in flex flex-col items-stretch bg-gray-900 border border-blue-700 rounded-xl shadow-xl overflow-hidden">
                    <button onClick={() => { i18n.changeLanguage('ua'); setLangMenuOpen(false); }} className={`flex items-center gap-2 w-full px-4 py-2 text-left hover:bg-blue-600 border-b border-blue-700 last:border-b-0 transition-all duration-150 bg-white/0 ${i18n.language === 'ua' ? 'bg-blue-700 text-white' : 'text-blue-200'}`}> <UAFlag style={{ width: 20, height: 20, borderRadius: '50%' }} /> UA </button>
                    <button onClick={() => { i18n.changeLanguage('en'); setLangMenuOpen(false); }} className={`flex items-center gap-2 w-full px-4 py-2 text-left hover:bg-blue-600 transition-all duration-150 bg-white/0 ${i18n.language === 'en' ? 'bg-blue-700 text-white' : 'text-blue-200'}`}> <GBFlag style={{ width: 20, height: 20, borderRadius: '50%' }} /> EN </button>
                  </div>
                )}
              </div>
              <AuthButton />
            </div>
          </div>
          {/* Десктопный хедер */}
          <div className="hidden md:flex items-center gap-0 w-full max-w-3xl mx-auto">
            <Link to="/" aria-label="На главную" tabIndex={0} className="flex-shrink-0 flex items-center justify-center focus:outline-none" style={{ width: 100, height: 100 }}>
              <RAPTORLogo className="w-25 h-25 text-white" />
            </Link>
            <nav className="flex-1 flex justify-center">
              <ul className="flex gap-8 bg-transparent rounded-xl mt-2 mb-2 items-center">
                <li>
                  <NavLink
                    to="/"
                    end
                    className={({ isActive }) =>
                      `relative px-4 py-2 rounded-lg font-semibold text-blue-200 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400
                      ${isActive ? 'text-white bg-blue-700/40 shadow font-bold' : 'hover:text-white hover:bg-blue-700/30'}
                      `
                    }
                  >
                    {t('main')}
                    <span className="absolute left-2 right-2 -bottom-1 h-0.5 bg-blue-400 rounded transition-all duration-200 scale-x-0 group-hover:scale-x-100" aria-hidden="true"></span>
                  </NavLink>
                </li>
                <li>
                  <NavLink
                    to="/model"
                    className={({ isActive }) =>
                      `relative px-4 py-2 rounded-lg font-semibold text-blue-200 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400
                      ${isActive ? 'text-white bg-blue-700/40 shadow font-bold' : 'hover:text-white hover:bg-blue-700/30'}
                      `
                    }
                  >
                    {t('model')}
                    <span className="absolute left-2 right-2 -bottom-1 h-0.5 bg-blue-400 rounded transition-all duration-200 scale-x-0 group-hover:scale-x-100" aria-hidden="true"></span>
                  </NavLink>
                </li>
                <li>
                  <NavLink
                    to="/about"
                    className={({ isActive }) =>
                      `relative px-4 py-2 rounded-lg font-semibold text-blue-200 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400
                      ${isActive ? 'text-white bg-blue-700/40 shadow font-bold' : 'hover:text-white hover:bg-blue-700/30'}
                      `
                    }
                  >
                    {t('about')}
                    <span className="absolute left-2 right-2 -bottom-1 h-0.5 bg-blue-400 rounded transition-all duration-200 scale-x-0 group-hover:scale-x-100" aria-hidden="true"></span>
                  </NavLink>
                </li>
              </ul>
            </nav>
          </div>
          <div className="absolute right-0 top-0 mt-2 mr-6 z-50 hidden md:flex items-center gap-2">
            <div className="relative flex flex-col items-center">
              <button
                ref={globeBtnRef}
                className="p-2 rounded-full hover:bg-blue-700/20 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-400"
                aria-label="Выбрать язык"
                aria-haspopup="true"
                aria-expanded={langMenuOpen}
                type="button"
                style={{ background: 'none' }}
                onMouseEnter={() => setLangMenuOpen(true)}
                onFocus={() => setLangMenuOpen(true)}
              >
                <span role="img" aria-label="Глобус" className="text-2xl">🌐</span>
              </button>
              {langMenuOpen && (
                <div
                  ref={langMenuRef}
                  className="absolute top-full mt-2 left-0 right-0 mx-auto z-50 min-w-[120px] animate-fade-in flex flex-col items-stretch bg-gray-900 border border-blue-700 rounded-xl shadow-xl overflow-hidden origin-top"
                  onMouseLeave={() => setLangMenuOpen(false)}
                  onMouseEnter={() => setLangMenuOpen(true)}
                >
                  <button
                    onClick={() => { i18n.changeLanguage('ua'); setLangMenuOpen(false); }}
                    className={`flex items-center gap-2 w-full px-4 py-2 text-left hover:bg-blue-600 transition-colors ${i18n.language === 'ua' ? 'bg-blue-700 text-white' : 'text-blue-200'}`}
                  >
                    <UAFlag style={{ width: 20, height: 20, borderRadius: '50%' }} /> UA
                  </button>
                  <button
                    onClick={() => { i18n.changeLanguage('en'); setLangMenuOpen(false); }}
                    className={`flex items-center gap-2 w-full px-4 py-2 text-left hover:bg-blue-600 transition-colors ${i18n.language === 'en' ? 'bg-blue-700 text-white' : 'text-blue-200'}`}
                  >
                    <GBFlag style={{ width: 20, height: 20, borderRadius: '50%' }} /> EN
                  </button>
                </div>
              )}
            </div>
            <AuthButton />
          </div>
          {/* Мобильное меню */}
          {mobileMenuOpen && (
            <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex flex-row" onClick={() => setMobileMenuOpen(false)}>
              <div className="bg-gray-900 p-6 flex flex-col gap-4 w-3/4 max-w-xs h-full" onClick={e => e.stopPropagation()}>
                <button className="self-end mb-4" onClick={() => setMobileMenuOpen(false)} aria-label="Закрыть меню">
                  <svg width="28" height="28" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
                <Link to="/" className="text-lg font-semibold hover:text-blue-300" onClick={() => setMobileMenuOpen(false)}>{t('main')}</Link>
                <Link to="/model" className="text-lg font-semibold hover:text-blue-300" onClick={() => setMobileMenuOpen(false)}>{t('model')}</Link>
                <Link to="/about" className="text-lg font-semibold hover:text-blue-300" onClick={() => setMobileMenuOpen(false)}>{t('about')}</Link>
              </div>
            </div>
          )}
        </nav>
        {/* Логотип под хедером на мобильных */}
        <div className="flex md:hidden justify-center items-center mb-2 mt-0">
          <Link to="/" aria-label="На главную" tabIndex={0} className="flex items-center justify-center focus:outline-none" style={{ width: 100, height: 100 }}>
            <RAPTORLogo className="w-25 h-25 text-white" />
          </Link>
        </div>
        {/* --- */}
        <div className="flex-1 w-full flex flex-col min-h-screen h-full relative">
          {/* Большой фон логотипа RAPTOR */}
          <div className="absolute left-1/2 top-0 md:top-1/2 -translate-x-1/2 md:-translate-y-1/2 w-[80vw] md:w-[60vw] max-w-3xl pointer-events-none select-none z-0" style={{ height: '60vw', maxHeight: '600px' }}>
            <RAPTORBg className="w-full h-full" />
          </div>
          <Routes>
            <Route path="/" element={
              <>
                <BrandHeader />
                <MainPage
                  files={files}
                  setFiles={setFiles}
                  results={results}
                  setResults={setResults}
                  loadings={loadings}
                  setLoadings={setLoadings}
                  progresses={progresses}
                  setProgresses={setProgresses}
                  selectedClass={selectedClass}
                  setSelectedClass={setSelectedClass}
                  selectedModel={selectedModel}
                  setSelectedModel={setSelectedModel}
                  inputRef={inputRef}
                  t={t}
                  i18n={i18n}
                  handleFileChange={undefined} // handleFileChange больше не нужен
                  uploadFile={uploadFile}
                  handleDownloadJPG={handleDownloadJPG}
                  handlePreviewJPG={handlePreviewJPG}
                  handleDownloadJSON={handleDownloadJSON}
                />
              </>
            } />
            <Route path="/model" element={<ModelPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </div>
        {/* JPG Preview Modal */}
        {console.log('App render jpgPreviewId:', jpgPreviewId)}
        {jpgPreviewId !== null && (
          <JPGPreviewModal
            id={jpgPreviewId}
            results={results}
            onClose={() => setJpgPreviewId(null)}
          />
        )}
      </div>
      <style>{`
@keyframes fade-in { from { opacity: 0; transform: translateY(-10px);} to { opacity: 1; transform: none; } }
.animate-fade-in { animation: fade-in 0.2s ease; }

/* Красивое underline для NavLink */
nav ul li a {
  position: relative;
  overflow: hidden;
  display: inline-block;
}
nav ul li a::after {
  content: '';
  position: absolute;
  left: 20%;
  right: 20%;
  bottom: 0.2em;
  height: 2px;
  background: #60a5fa;
  border-radius: 2px;
  transform: scaleX(0);
  transition: transform 0.2s;
}
nav ul li a:hover::after, nav ul li a.active::after {
  transform: scaleX(1);
}
`}</style>
    </NotificationProvider>
  );
}

export default App;
