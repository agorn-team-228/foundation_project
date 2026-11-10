import React from 'react';

export default function ChatMessages({ messages }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="text-center text-xs text-slate-400 dark:text-gray-500 my-1">Разбираемся в вашей ситуации</div>
      <div className="text-center text-xs text-slate-400 dark:text-gray-500 my-1">
        Сегодня <span className="ml-1 text-slate-300 dark:text-gray-700">|</span> 📍 Россия
      </div>

      {messages.map((msg) => {
        if (msg.sender === 'user') {
          return (
            <div key={msg.id} className="flex flex-col items-end">
              <span className="text-[11px] text-slate-400 dark:text-gray-500 mb-1">Вы · {msg.time}</span>
              <div className="max-w-[80%] text-right text-[14px] text-slate-800 dark:text-gray-200 font-normal leading-relaxed">
                {msg.text}
              </div>
            </div>
          );
        }

        return (
          <div key={msg.id} className="flex flex-col items-start mt-2">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-sm">⚖️</span>
              <span className="font-semibold text-[14px]">Право</span>
              <span className="text-[9px] font-bold bg-slate-100 dark:bg-gray-800 text-slate-500 dark:text-gray-400 px-1.5 py-0.5 rounded tracking-wider">
                AI-АССИСТЕНТ
              </span>
            </div>

            {msg.verdict && (
              <h3 className="text-xl md:text-2xl font-bold text-slate-900 dark:text-white leading-tight mb-4">
                {msg.verdict}
              </h3>
            )}

            {msg.intro && (
              <p className="text-[14px] text-slate-700 dark:text-gray-300 mb-5">
                {msg.intro}
              </p>
            )}

            {msg.steps && msg.steps.length > 0 && (
              <div className="flex flex-col gap-5 w-full mb-6">
                {msg.steps.map((item) => (
                  <div key={item.num} className="flex gap-4">
                    <div className="w-6 h-6 rounded-full bg-slate-100 dark:bg-gray-800 flex items-center justify-center font-semibold text-xs flex-shrink-0 text-slate-600 dark:text-gray-300">
                      {item.num}
                    </div>
                    <div className="flex-1">
                      <strong className="block text-[14px] font-semibold text-slate-900 dark:text-white mb-1">{item.title}</strong>
                      <p className="text-[13.5px] text-slate-600 dark:text-gray-400 leading-relaxed">{item.text}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {msg.prompt && (
              <div className="w-full bg-emerald-50/70 dark:bg-emerald-950/20 border border-emerald-100/50 dark:border-emerald-900/20 rounded-xl p-4 flex gap-3 mb-4">
                <span className="text-emerald-700 dark:text-emerald-400 text-lg">💡</span>
                <p className="text-[13.5px] text-emerald-900 dark:text-emerald-300 font-normal leading-relaxed">
                  {msg.prompt}
                </p>
              </div>
            )}

            <div className="flex gap-3 items-center w-full text-slate-400">
              <button className="hover:text-slate-600 dark:hover:text-gray-300 text-sm">📋 Копировать</button>
              <button className="hover:text-slate-600 dark:hover:text-gray-300 text-sm">👍</button>
              <button className="hover:text-slate-600 dark:hover:text-gray-300 text-sm">🔄</button>
              <span className="text-[11px] text-slate-400 dark:text-gray-500 ml-auto">{msg.time}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
