import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatHeader from './components/ChatHeader';
import ChatMessages from './components/ChatMessages';
import ChatInput from './components/ChatInput';

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(true); // По умолчанию включена тёмная тема, как на скриншоте

  // Динамический массив сообщений чата
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

  // Функция добавления нового сообщения пользователя + имитация ответа AI
  const handleSendMessage = (text) => {
    const timeNow = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // 1. Добавляем сообщение пользователя
    const newUserMessage = {
      id: Date.now(),
      sender: 'user',
      time: timeNow,
      text: text
    };
    
    setMessages(prev => [...prev, newUserMessage]);

    // 2. Имитируем задержку ответа сервера (бэкендер заменит это на fetch/axios запрос)
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

  return (
    <div className={`flex h-screen w-screen overflow-hidden ${isDarkMode ? 'dark bg-gray-900 text-gray-100' : 'bg-white text-slate-800'}`}>
      <Sidebar isDarkMode={isDarkMode} setIsDarkMode={setIsDarkMode} />
      <main className="flex flex-col flex-1 h-full min-w-0 bg-white dark:bg-gray-900">
        <ChatHeader />
        <div className="flex-1 overflow-y-auto px-4 md:px-20 py-6 max-w-4xl w-full mx-auto">
          {/* Передаем динамический массив в компонент вывода */}
          <ChatMessages messages={messages} />
        </div>
        {/* Передаем функцию отправки в поле ввода */}
        <ChatInput onSend={handleSendMessage} />
      </main>
    </div>
  );
}
