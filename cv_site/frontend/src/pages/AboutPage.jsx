import { useTranslation, Trans } from "react-i18next";
import BrandHeader from '../components/BrandHeader';
import GmailIcon from '../icons/gmail.svg?react';
import TelegramIcon from '../icons/telegram.svg?react';

export default function AboutPage() {
    const { t } = useTranslation();
    return (
        <div className="flex flex-col items-center min-h-[60vh] w-full">
            <BrandHeader />
            <div className="w-full max-w-3xl bg-gray-800/80 rounded-2xl shadow-2xl px-8 py-10 mb-10 animate-fade-in">
                <h2 className="text-4xl md:text-5xl font-extrabold text-blue-300 mb-4 text-center drop-shadow-lg flex items-center justify-center gap-3">
                    <span>{t('team_title')}</span>
                    <span className='text-3xl'>🤖</span>
                </h2>
                <div className="text-lg md:text-xl text-blue-100 leading-relaxed space-y-6 text-center">
                    <p><Trans i18nKey="team_desc1" /></p>
                    <p><Trans i18nKey="team_desc2" /></p>
                    <p><Trans i18nKey="team_desc3" /></p>
                </div>
                <div className="mt-10 flex flex-col items-center gap-4">
                    <div className="flex items-center gap-3 text-blue-200 text-lg">
                        <GmailIcon className="w-7 h-7 text-blue-300" />
                        <a href="mailto:sanekvseok228@gmail.com" className="hover:text-blue-400 underline">sanekvseok228@gmail.com</a>
                    </div>
                    <div className="flex items-center gap-3 text-blue-200 text-lg">
                        <TelegramIcon className="w-7 h-7 text-blue-300" />
                        <a href="https://t.me/somedumbslime" target="_blank" rel="noopener noreferrer" className="hover:text-blue-400 underline">@somedumbslime</a>
                    </div>
                </div>
            </div>
        </div>
    );
} 