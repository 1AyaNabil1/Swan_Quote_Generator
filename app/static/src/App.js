import React from 'react';
import AnimatedBackground from './components/AnimatedBackground';
import QuoteGenerator from './components/QuoteGenerator';
import './App.css';

function App() {
  return (
    <div className="relative h-screen bg-black overflow-hidden">
      {/* Animated Background with Purple Dots */}
      <AnimatedBackground />
      
      {/* Main Content */}
      <main className="relative z-10 h-full">
        <QuoteGenerator />
      </main>
    </div>
  );
}

export default App;
