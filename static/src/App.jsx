import React from 'react';
import AnimatedBackground from './components/AnimatedBackground';
import QuoteGenerator from './components/QuoteGenerator';
import { ToastProvider } from './components/Toast';
import './App.css';

function App() {
  return (
    <div className="relative h-screen bg-black overflow-hidden">
      {/* Animated Background with Purple Dots */}
      <AnimatedBackground />
      
      {/* Main Content */}
      <main className="relative z-10 h-full">
        <ToastProvider>
          <QuoteGenerator />
        </ToastProvider>
      </main>
    </div>
  );
}

export default App;
