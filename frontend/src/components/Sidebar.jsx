import React from 'react';

export default function Sidebar({ isDarkMode, setIsDarkMode }) {
  // Функция для показа информации о "Праве"
  const handleShowInfo = (e) => {
    e.preventDefault(); // Предотвращаем переход по ссылке #
    alert(
      '⚖️ КАК РАБОТАЕТ «ПРАВО»\n\n' +
      'Этот ассистент создан для юристов ПСБ. Его главная особенность — строгая работа с фактами.\n\n' +
      '• Отвечает ТОЛЬКО на основе базы нормативных актов и регламентов банка\n' +
      '• Каждый ответ содержит ссылки на конкретные пункты документов\n' +
      '• Если информации недостаточно — честно сообщает об этом\n' +
      '• Учитывает даты редакций документов\n' +
      '• Не дает советов по противоправным действиям\n\n' +
      'Технология: RAG + LLM DeepSeek V4.1'
    );
  };

  return (
    <aside className="w-[260px] bg-[#f8fafc] dark:bg-gray-950 border-r border-slate-200 dark:border-gray-800 flex flex-col justify-between p-4 flex-shrink-0">
      
      {/* Верхняя часть */}
      <div className="flex flex-col gap-6">
        {/* Логотип */}
        <div className="flex items-center gap-3">
          <span className="text-2xl">⚖️</span>
          <div>
            <h1 className="font-semibold text-[15px] leading-tight">Право</h1>
            <p className="text-xs text-slate-500 dark:text-gray-400">Юридический AI-ассистент</p>
          </div>
        </div>

        {/* Кнопка создания чата */}
        <button className="w-full bg-[#0a5c43] hover:bg-[#074432] text-white rounded-lg py-2.5 px-3.5 font-medium text-sm flex items-center justify-between transition-colors shadow-sm">
          <span className="flex items-center gap-2">
            <span>＋</span> Новый диалог
          </span>
          <span className="text-[10px] bg-white/20 px-1.5 py-0.5 rounded font-mono">⌘ K</span>
        </button>

        {/* История сессий */}
        <div>
          <p className="text-[11px] font-semibold text-slate-400 dark:text-gray-500 tracking-wider mb-2">ТЕКУЩАЯ СЕССИЯ</p>
          <div className="flex items-start gap-2.5 p-2 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg cursor-pointer border border-emerald-100/50 dark:border-emerald-900/20">
            <span className="text-emerald-700 dark:text-emerald-400 text-lg mt-0.5">💬</span>
            <div className="flex flex-col min-w-0">
              <span className="font-medium text-[13px] truncate">Возврат залога за квартиру</span>
              <span className="text-[11px] text-slate-400 dark:text-gray-500">Сегодня</span>
            </div>
          </div>
        </div>
      </div>

      {/* Нижняя часть */}
      <div className="flex flex-col gap-4">
        {/* Карточка гостевого режима */}
        <div className="bg-white dark:bg-gray-900 border border-slate-200 dark:border-gray-800 rounded-lg p-3 flex gap-2.5 shadow-sm">
          <span className="text-xl text-slate-400">👤</span>
          <div>
            <p className="font-semibold text-xs text-slate-700 dark:text-gray-300">Вы в гостевом режиме</p>
            <p className="text-[11px] text-slate-400 dark:text-gray-500 mt-0.5 leading-snug">
              Диалог доступен в этой сессии. Не указывайте личные данные.
            </p>
          </div>
        </div>

        {/* Переключатель тем */}
        <div className="flex bg-slate-100 dark:bg-gray-900 p-1 rounded-lg">
          <button 
            onClick={() => setIsDarkMode(false)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs rounded-md transition-all ${!isDarkMode ? 'bg-white dark:bg-gray-800 shadow-sm font-medium' : 'text-slate-500'}`}
          >
            ☀️ Светлая
          </button>
          <button 
            onClick={() => setIsDarkMode(true)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-1.5 text-xs rounded-md transition-all ${isDarkMode ? 'bg-white dark:bg-gray-800 shadow-sm font-medium' : 'text-slate-500'}`}
          >
            🌙 Тёмная
          </button>
        </div>

        {/* Ссылка "Как работает Право" - ТЕПЕРЬ С РАБОЧИМ ALERT */}
        <a 
          href="#" 
          onClick={handleShowInfo}
          className="flex items-center gap-2 text-xs text-slate-500 dark:text-gray-400 hover:text-slate-800 dark:hover:text-white transition-colors"
        >
          <span>❓</span> Как работает Право
        </a>
      </div>
    </aside>
  );
}