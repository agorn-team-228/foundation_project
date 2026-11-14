import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatHeader from './components/ChatHeader';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';
import SourceViewer from './components/SourceViewer';
import { mockDocuments } from './data/mockDocuments';

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [selectedSource, setSelectedSource] = useState(null); // { document, highlightHeader }

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'user',
      time: '12:40',
      text: 'Съезжаю с квартиры. Собственник не хочет возвращать залог: говорит, что нужен клининг, хотя повреждений нет. Что мне делать?'
    },
    {
      id: 2,
      sender: 'ai',
      time: '12:41',
      verdict: 'Самого желания провести клининг недостаточно для удержания залога.',
      intro: 'Если квартира находится в России, начните с договора и фиксации её состояния. Вот что можно сделать:',
      steps: [
        { num: 1, title: "Проверьте договор", text: "Посмотрите, как в договоре названа сумма и в каких случаях её можно удержать." },
        { num: 2, title: "Зафиксируйте состояние квартиры", text: "Сделайте фото и видео, сохраните переписку. При передаче ключей предложите подписать акт." },
        { num: 3, title: "Попросите обосновать удержание", text: "Направьте собственнику письменное требование вернуть деньги." }
      ],
      prompt: 'Есть ли в договоре условие об оплате уборки при выезде? Можете прислать его текст без личных данных.'
    }
  ]);

  const handleSendMessage = (text) => {
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const newUserMessage = { id: Date.now(), sender: 'user', time: timeNow, text: text };
    setMessages(prev => [...prev, newUserMessage]);

    setTimeout(() => {
      const newAiMessage = {
        id: Date.now() + 1,
        sender: 'ai',
        time: timeNow,
        verdict: 'Принято. Я анализирую ваш запрос...',
        intro: `Вы спросили: "${text}". Сейчас этот фронтенд готов к интеграции с бэкендом.`,
        steps: [],
        prompt: 'Бэкендер может подключить контроллер к этому состоянию.'
      };
      setMessages(prev => [...prev, newAiMessage]);
    }, 1000);
  };

  // Демо-ссылки на источники (имитируют то, что бэкенд вернёт в поле sources)
  const sourceRefs = [
    { docId: 'doc-1', header: 'Раздел 4. Обеспечительный платёж > п. 4.4', label: 'Договор № А-12/2025, п. 4.4' },
    { docId: 'doc-1', header: 'Раздел 4. Обеспечительный платёж > п. 4.3', label: 'Договор № А-12/2025, п. 4.3' },
    { docId: 'doc-2', header: 'Статья 687. Расторжение договора найма', label: 'ГК РФ, ст. 687' },
  ];

  const openSource = (ref) => {
    const document = mockDocuments.find(d => d.id === ref.docId);
    setSelectedSource({ document, highlightHeader: ref.header });
  };

  return (
    <div className={`flex h-screen w-screen overflow-hidden ${isDarkMode ? 'dark bg-gray-900 text-gray-100' : 'bg-white text-slate-800'}`}>
      <Sidebar isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />

      {/* Контейнер: чат + панель-просмотр */}
      <div className="flex flex-1 h-full min-w-0">
        <main className="flex flex-col flex-1 h-full min-w-0 bg-white dark:bg-gray-900">
          <ChatHeader />
          <div className="flex-1 overflow-y-auto px-4 md:px-20 py-6 max-w-4xl w-full mx-auto">
            <ChatMessages messages={messages} />

            {/* Блок кликабельных источников ответа */}
            <div className="mt-4 flex flex-wrap gap-2 items-center">
              <span className="text-xs text-slate-500 dark:text-gray-400">📎 Подтверждающие документы:</span>
              {sourceRefs.map((ref, i) => (
                <button
                  key={i}
                  onClick={() => openSource(ref)}
                  className="text-xs px-3 py-1 rounded-full bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-900 hover:bg-emerald-100 dark:hover:bg-emerald-900/60 transition-colors"
                >
                  {ref.label}
                </button>
              ))}
            </div>
          </div>
          <ChatInput onSend={handleSendMessage} />
        </main>

        {/* Панель-просмотр справа (появляется при клике на источник) */}
        {selectedSource && (
          <SourceViewer
            document={selectedSource.document}
            highlightHeader={selectedSource.highlightHeader}
            onClose={() => setSelectedSource(null)}
          />
        )}
      </div>
    </div>
  );
}
