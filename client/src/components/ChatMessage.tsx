import React from 'react';
import { ChatMessageProps } from '../types';

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
    const isUser = message.role === 'user';
    
    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div className={`max-w-[70%] rounded-lg p-4 ${
                isUser 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-200 text-gray-800'
            }`}>
                <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
        </div>
    );
};

export default ChatMessage; 