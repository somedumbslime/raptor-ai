import React from 'react';
import BrandHeader from '../components/BrandHeader';
import { useTranslation, Trans } from 'react-i18next';
import raw1 from '../photos/raw_1.jpg';
import detected1 from '../photos/detected_1.jpg';
import raw2 from '../photos/raw_2.jpg';
import detected2 from '../photos/detected_2.jpg';
import RAPTORBg from '../icons/RAPTOR_bg.svg?react';

export default function ModelPage() {
    const { t } = useTranslation();
    return (
        <div className="flex flex-col items-center min-h-[60vh] w-full relative">
            {/* Большой фон логотипа RAPTOR */}
            <div className="absolute left-1/2 top-[170px] -translate-x-1/2 w-[80vw] md:w-[60vw] max-w-3xl pointer-events-none select-none z-0" style={{ height: '60vw', maxHeight: '600px' }}>
                <RAPTORBg className="w-full h-full" />
            </div>
            <BrandHeader />
            <div className="w-full max-w-5xl mb-10">
                <div className="text-lg md:text-xl text-blue-100 leading-relaxed space-y-4">
                    <p>
                        <span className="font-bold text-blue-400">{t('brand')}</span> <Trans i18nKey="brand_description" />
                    </p>
                    <p>
                        <Trans i18nKey="current_model">
                            На даний момент наша модель впевнено ідентифікує <span className="font-bold text-green-300">солдатів</span> на різних ландшафтах та за різної погоди. Модель оптимізована для швидкої роботи та інтеграції у системах моніторингу, аналізу БПЛА, ситуаційної обізнаності.
                        </Trans>
                    </p>
                    <p>
                        {t('future_classes')}
                    </p>
                    <ul className="mt-2 ml-6 space-y-1 list-none">
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-blue-400"></span><span className="text-blue-400 font-semibold">{t('class_civilian')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-yellow-300"></span><span className="text-yellow-300 font-semibold">{t('class_vehicle')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-orange-400"></span><span className="text-orange-400 font-semibold">{t('class_armor')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-pink-400"></span><span className="text-pink-400 font-semibold">{t('class_mrls')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-red-400"></span><span className="text-red-400 font-semibold">{t('class_aa')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-teal-300"></span><span className="text-teal-300 font-semibold">{t('class_heli')}</span></li>
                        <li className="flex items-center gap-2"><span className="inline-block w-2 h-2 rounded-full bg-purple-400"></span><span className="text-purple-400 font-semibold">{t('class_plane')}</span></li>
                    </ul>
                    <p>
                        <span className="font-bold text-green-300">{t('ukr_context')}</span>
                    </p>
                </div>
            </div>
            <div className="px-6 pt-6 pb-2 text-left">
                <h3 className="text-2xl font-bold text-blue-300 mb-2">{t('model_params')}</h3>
            </div>
            <div className="w-full max-w-2xl mx-auto rounded-2xl shadow-2xl overflow-hidden bg-gray-800 mb-8">
                <table className="w-full text-center">
                    <thead>
                        <tr className="bg-gradient-to-r from-blue-900 via-gray-900 to-blue-900">
                            <th className="p-3 text-lg font-bold text-blue-200">{t('param')}</th>
                            <th className="p-3 text-lg font-bold text-blue-200">{t('value')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className="bg-gray-900/30 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_arch')}</td>
                            <td className="p-2 text-blue-50 text-left">YOLO12s, 9.4M parameters</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_task')}</td>
                            <td className="p-2 text-blue-50 text-left">{t('task_detection')}</td>
                        </tr>
                        <tr className="bg-gray-900/30 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_classes')}</td>
                            <td className="p-2 text-blue-50 text-left">1 (soldier)</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_input')}</td>
                            <td className="p-2 text-blue-50 text-left">640×640</td>
                        </tr>
                        <tr className="bg-gray-900/30 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_amp')}</td>
                            <td className="p-2 text-blue-50 text-left">{t('amp_on')}</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_video')}</td>
                            <td className="p-2 text-blue-50 text-left">{t('video_supported')}</td>
                        </tr>
                        <tr className="bg-gray-900/30 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_recommend')}</td>
                            <td className="p-2 text-blue-50 text-left">{t('recommend_conf')}</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-blue-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-blue-100">{t('param_formats')}</td>
                            <td className="p-2 text-blue-50 text-left">{t('formats')}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="px-6 pt-6 pb-2 text-left">
                <h3 className="text-2xl font-bold text-green-300 mb-2">{t('metrics')}</h3>
            </div>
            <div className="w-full max-w-2xl mx-auto rounded-2xl shadow-2xl overflow-hidden bg-gray-800 mt-2 mb-12">
                <table className="w-full text-center">
                    <thead>
                        <tr className="bg-gradient-to-r from-green-900 via-gray-900 to-green-900">
                            <th className="p-3 text-lg font-bold text-green-200 tracking-wide">{t('metric')}</th>
                            <th className="p-3 text-lg font-bold text-green-200 tracking-wide">{t('value')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr className="bg-gray-900/30 hover:bg-green-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-green-100">{t('precision')}</td>
                            <td className="p-2 text-green-50 text-left font-mono text-lg">0.712</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-green-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-green-100">{t('recall')}</td>
                            <td className="p-2 text-green-50 text-left font-mono text-lg">0.576</td>
                        </tr>
                        <tr className="bg-gray-900/30 hover:bg-green-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-green-100">{t('map50')}</td>
                            <td className="p-2 text-green-50 text-left font-mono text-lg">0.621</td>
                        </tr>
                        <tr className="bg-gray-800/60 hover:bg-green-900/30 transition-colors">
                            <td className="p-2 font-semibold text-left text-green-100">{t('map50_95')}</td>
                            <td className="p-2 text-green-50 text-left font-mono text-lg">0.334</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="w-full max-w-5xl mx-auto mt-16">
                <h3 className="text-2xl font-bold text-blue-400 mb-6 text-center">{t('examples')}</h3>
                <div className="flex flex-col gap-12 items-center">
                    <div className="w-full max-w-3xl flex flex-col md:flex-row items-center bg-gray-800 rounded-3xl shadow-xl overflow-hidden">
                        <div className="flex-1 flex flex-col items-center p-6">
                            <span className="text-blue-300 font-semibold mb-2 text-xl">{t('before')}</span>
                            <img src={raw1} alt="raw_1" className="rounded-xl w-full max-w-md object-contain shadow-md" />
                        </div>
                        <div className="flex-1 flex flex-col items-center p-6 border-t md:border-t-0 md:border-l border-gray-700">
                            <span className="text-green-300 font-semibold mb-2 text-xl">{t('after')}</span>
                            <img src={detected1} alt="detected_1" className="rounded-xl w-full max-w-md object-contain shadow-md" />
                        </div>
                    </div>
                    <div className="w-full max-w-3xl flex flex-col md:flex-row items-center bg-gray-800 rounded-3xl shadow-xl overflow-hidden">
                        <div className="flex-1 flex flex-col items-center p-6">
                            <span className="text-blue-300 font-semibold mb-2 text-xl">{t('before')}</span>
                            <img src={raw2} alt="raw_2" className="rounded-xl w-full max-w-md object-contain shadow-md" />
                        </div>
                        <div className="flex-1 flex flex-col items-center p-6 border-t md:border-t-0 md:border-l border-gray-700">
                            <span className="text-green-300 font-semibold mb-2 text-xl">{t('after')}</span>
                            <img src={detected2} alt="detected_2" className="rounded-xl w-full max-w-md object-contain shadow-md" />
                        </div>
                    </div>
                </div>
            </div>
            <div className="w-full max-w-4xl mx-auto mt-20 mb-10">
                <h3 className="text-2xl font-bold text-green-400 mb-8 text-center">{t('advantages')}</h3>
                <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">⚡</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_speed')}</span>
                    </li>
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">🎥</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_video')}</span>
                    </li>
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">🇺🇦</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_ua')}</span>
                    </li>
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">🔌</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_easy')}</span>
                    </li>
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">💾</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_formats')}</span>
                    </li>
                    <li className="flex items-center gap-4 bg-gray-800 rounded-2xl shadow-lg p-6">
                        <span className="text-3xl">🌐</span>
                        <span className="text-lg font-semibold text-blue-100">{t('adv_open')}</span>
                    </li>
                </ul>
            </div>
        </div>
    );
} 