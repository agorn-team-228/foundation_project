import React from 'react';

export default function ChatHeader() {
  return (
    <header className="h-[60px] border-b border-slate-200 dark:border-gray-800 flex items-center justify-between px-6 bg-white dark:bg-gray-900 z-10 flex-shrink-0">
      <div className="flex flex-col">
        <h2 className="text-[14px] font-semibold leading-tight">Возврат залога за квартиру</h2>
        <span className="text-xs text-slate-400 dark:text-gray-500">Жилищные вопросы</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-gray-800 border border-slate-200 dark:border-gray-700 px-2.5 py-1 rounded-md">
          Гостевой диалог
        </span>
        <button className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 text-xl font-bold">
          ···
        </button>
      </div>
    </header>
  );
}
