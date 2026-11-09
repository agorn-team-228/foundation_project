import React, { useState, useRef } from 'react';

export default function ChatInput({ onSend }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleInput = (e) => {
    setText(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const handleSubmit = () => {
    if (!text.trim()) return;
    onSend(text.trim()); // Отправляем текст в App.jsx
    setText(''); // Очищаем поле ввода
    if (textareaRef.current) textareaRef.current.style.height = 'auto'; // Сбрасываем высоту
  };

  const handleKeyDown = (e) => {
    // Отправка по Enter (без Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <footer className="p-4 md:px-20 pb-6 max-w-4xl w-full mx-auto flex-shrink-0 bg-white dark:bg-gray-900">
      <div className="flex gap-2 mb-3.5 overflow-x-auto no-scrollbar">
        <button 
          onClick={() => onSend("Составить требование собственнику")}
          className="flex items-center gap-1.5 whitespace-nowrap bg-white dark:bg-gray-800 hover:bg-slate-50 dark:hover:bg-gray-700 text-xs text-slate-700 dark:text-gray-300 border border-slate-200 dark:border-gray-700 px-3.5 py-2 rounded-full shadow-sm transition-colors cursor-pointer"
        >
          📄 Составить требование
        </button>
        <button 
          onClick={() => onSend("Какие доказательства нужно собрать?")}
          className="whitespace-nowrap bg-white dark:bg-gray-800 hover:bg-slate-50 dark:hover:bg-gray-700 text-xs text-slate-700 dark:text-gray-300 border border-slate-200 dark:border-gray-700 px-3.5 py-2 rounded-full shadow-sm transition-colors cursor-pointer"
        >
          Какие доказательства собрать?
        </button>
      </div>

      <div className="border border-slate-200 dark:border-gray-700 rounded-xl p-3 bg-white dark:bg-gray-800 shadow-sm focus-within:border-emerald-600 dark:focus-within:border-emerald-500 transition-colors">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Задайте вопрос или уточните детали..."
          rows={1}
          className="w-full bg-transparent border-none resize-none outline-none text-sm text-slate-800 dark:text-gray-100 placeholder-slate-400 dark:placeholder-gray-500 max-h-40 min-h-[24px]"
        />
        <div className="flex justify-between items-center mt-2 pt-1 border-t border-slate-100 dark:border-gray-700/50">
          <button className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-gray-300 font-medium cursor-pointer">
            📎 Прикрепить документ
          </button>
          <button 
            onClick={handleSubmit}
            disabled={!text.trim()} 
            className={`w-7 h-7 rounded-full flex items-center justify-center text-white transition-all cursor-pointer ${text.trim() ? 'bg-[#0a5c43] hover:bg-[#074432]' : 'bg-slate-100 dark:bg-gray-700 text-slate-300 dark:text-gray-500 cursor-not-allowed'}`}
          >
            ↑
          </button>
        </div>
      </div>

      <p className="text-center text-[11px] text-slate-400 dark:text-gray-500 mt-3">
        AI может ошибаться и не заменяет юриста. Проверяйте важные решения.
      </p>
    </footer>
  );
}
