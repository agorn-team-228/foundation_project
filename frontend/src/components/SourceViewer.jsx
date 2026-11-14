import React from 'react';

// Панель справа: показывает полный документ и подсвечивает нужный фрагмент.
export default function SourceViewer({ document, highlightHeader, onClose }) {
  if (!document) return null;

  return (
    <aside className="w-[420px] flex-shrink-0 border-l border-slate-200 dark:border-gray-800 bg-white dark:bg-gray-950 flex flex-col h-full">
      {/* Шапка панели */}
      <div className="p-4 border-b border-slate-200 dark:border-gray-800 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">Источник ответа</p>
          <h2 className="font-semibold text-[15px] leading-tight truncate">{document.doc_name}</h2>
          <p className="text-[11px] text-slate-500 dark:text-gray-400 mt-0.5">
            {document.title} · {document.date} · {document.edition}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-slate-700 dark:hover:text-white text-xl leading-none flex-shrink-0"
          aria-label="Закрыть"
        >
          &times;
        </button>
      </div>

      {/* Тело документа с подсвеченным фрагментом */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {document.sections.map((sec, i) => {
          const isHighlight = highlightHeader && sec.header === highlightHeader;
          return (
            <div
              key={i}
              className={
                'rounded-lg p-3 border transition-colors ' +
                (isHighlight
                  ? 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-400 dark:border-yellow-600'
                  : 'bg-slate-50 dark:bg-gray-900 border-transparent')
              }
            >
              <p className="text-[11px] font-semibold text-slate-500 dark:text-gray-400 mb-1">
                {sec.header} {isHighlight && <span className="text-yellow-600 dark:text-yellow-400">· подтверждает ответ</span>}
              </p>
              <p className="text-[13px] leading-relaxed text-slate-700 dark:text-gray-300">{sec.text}</p>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
